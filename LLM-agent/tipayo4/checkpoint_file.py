# checkpoint_file.py
# 초경량 파일 기반 Checkpointer (의존성 0, 동기 전용 + 보존 개수 제한)

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional, Iterator, Dict, List

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple  # type: ignore
from langchain_core.runnables import RunnableConfig  # type: ignore

def _to_plain_checkpoint(c: Checkpoint) -> Dict[str, Any]:
    """defaultdict 등을 직렬화 가능한 dict로 정규화"""
    return {
        "v": c["v"],
        "ts": c["ts"],
        "channel_values": c["channel_values"],
        "channel_versions": dict(c["channel_versions"]),
        "versions_seen": {k: dict(v) for k, v in c["versions_seen"].items()},
    }

class FileJSONSaver(BaseCheckpointSaver):
    """
    - JSON 단일 파일에 thread별 체크포인트 목록을 저장
    - 동시성: 파일 쓰기 최소 보장을 위해 파일 단위 락
    - 비동기 API는 Base에서 스레드 풀로 위임되어 동기 구현만으로 충분
    - 보존 개수 제한(max_keep)으로 파일 폭증 방지
    """

    def __init__(self, path: str = ".rag/checkpoints/rpg.json", max_keep: int = 20):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._max_keep = max(1, int(max_keep))

    # 내부 스토리지 형식: { thread_id: [ { "checkpoint": {...} }, ... ] }
    def _read_all(self) -> Dict[str, List[dict]]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_all(self, data: Dict[str, List[dict]]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        tmp.replace(self.path)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        conf = (config or {}).get("configurable", {})
        thread_id: str = conf.get("thread_id", "")
        thread_ts: Optional[str] = conf.get("thread_ts")

        with self._lock:
            data = self._read_all()
            entries = data.get(thread_id, [])
            rec = None
            if thread_ts:
                for e in entries:
                    if e["checkpoint"]["ts"] == thread_ts:
                        rec = e
                        break
            else:
                rec = entries[-1] if entries else None

            if not rec:
                return None

            chk = rec["checkpoint"]
            return CheckpointTuple(
                config={"configurable": {"thread_id": thread_id, "thread_ts": chk["ts"]}},
                checkpoint=chk,  # plain dict
                parent_config=None,
            )

    def list(self, config: RunnableConfig) -> Iterator[CheckpointTuple]:
        conf = (config or {}).get("configurable", {})
        thread_id: str = conf.get("thread_id", "")
        with self._lock:
            data = self._read_all()
            for e in data.get(thread_id, []):
                chk = e["checkpoint"]
                yield CheckpointTuple(
                    config={"configurable": {"thread_id": thread_id, "thread_ts": chk["ts"]}},
                    checkpoint=chk,
                    parent_config=None,
                )

    def put(self, config: RunnableConfig, checkpoint: Checkpoint) -> RunnableConfig:
        conf = (config or {}).get("configurable", {})
        thread_id: str = conf.get("thread_id", "")
        normalized = _to_plain_checkpoint(checkpoint)

        with self._lock:
            data = self._read_all()
            lst = data.setdefault(thread_id, [])
            lst.append({"checkpoint": normalized})
            if len(lst) > self._max_keep:
                data[thread_id] = lst[-self._max_keep :]
            self._write_all(data)

        new_conf = dict(config or {})
        new_conf.setdefault("configurable", {})
        new_conf["configurable"].update({"thread_id": thread_id, "thread_ts": normalized["ts"]})
        return new_conf
