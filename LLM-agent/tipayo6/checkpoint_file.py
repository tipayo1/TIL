# checkpoint_file.py
# - 초경량 파일 기반 Checkpointer (로컬 디버깅 전용)
# - 스튜디오/클라우드에서는 관리형 Checkpointer 사용 권장

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional, Iterator, Dict, List

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple  # type: ignore
from langchain_core.runnables import RunnableConfig  # type: ignore

def _to_plain_checkpoint(c: Checkpoint) -> Dict[str, Any]:
    # 직렬화 가능 형태로 변환
    return {
        "v": c["v"],
        "ts": c["ts"],
        "channel_values": c["channel_values"],
        "channel_versions": dict(c["channel_versions"]),
        "versions_seen": {k: dict(v) for k, v in c["versions_seen"].items()},
    }

class FileJSONSaver(BaseCheckpointSaver):
    """
    JSON 단일 파일에 thread별 체크포인트 목록 저장.
    - 파일 락으로 최소 동시성 보장
    - 보존 개수 제한(max_keep) + 파일 사이즈 회전(max_bytes)
    """
    def __init__(self, path: str = ".rag/checkpoints/rpg.json", max_keep: int = 20, max_bytes: int = 2_000_000):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.max_keep = max(1, int(max_keep))
        self.max_bytes = max(200_000, int(max_bytes))  # 200KB 이상

    def _read_all(self) -> Dict[str, List[dict]]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_all(self, data: Dict[str, List[dict]]) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = (config.get("configurable") or {}).get("thread_id", "default")
        with self.lock:
            data = self._read_all()
            arr = data.get(thread_id, [])
            if not arr:
                return None
            last = arr[-1]
            return (
                last.get("v"),
                last.get("ts"),
                last.get("channel_values"),
                last.get("channel_versions"),
                last.get("versions_seen"),
                {},
            )

    def put(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        thread_id = (config.get("configurable") or {}).get("thread_id", "default")
        with self.lock:
            data = self._read_all()
            arr = data.get(thread_id, [])
            arr.append(_to_plain_checkpoint(checkpoint))
            # 보존 개수 제한
            if len(arr) > self.max_keep:
                arr = arr[-self.max_keep :]
            data[thread_id] = arr
            self._write_all(data)

            # 사이즈 회전 (너무 커지면 절반만 유지)
            if self.path.exists() and self.path.stat().st_size > self.max_bytes:
                data = self._read_all()
                for k in list(data.keys()):
                    data[k] = data[k][-max(1, self.max_keep // 2) :]
                self._write_all(data)

    # 선택 구현: iterator (필요 시)
    def list(self, config: RunnableConfig) -> Iterator[CheckpointTuple]:
        thread_id = (config.get("configurable") or {}).get("thread_id", "default")
        data = self._read_all()
        for it in data.get(thread_id, []):
            yield (
                it.get("v"),
                it.get("ts"),
                it.get("channel_values"),
                it.get("channel_versions"),
                it.get("versions_seen"),
                {},
            )
