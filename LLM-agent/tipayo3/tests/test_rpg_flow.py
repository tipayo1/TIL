# tests/test_rpg_flow.py

import os
import unittest

from state import State
from nodes import compose_rpg, intent_parser, retrieve_rpg
from rpg import DataFlowManager, unit_test_flow_assertions

class TestRPGFlow(unittest.TestCase):
    def test_schema_sanity(self):
        dfm = DataFlowManager()
        issues = unit_test_flow_assertions(dfm)
        self.assertEqual(len(issues), 0, f"Schema issues: {issues}")

    def test_minimal_path(self):
        st: State = State()
        st["messages"] = [{"type": "human", "content": "사내 복무규정 휴가 조항 알려줘"}]
        st["thread_id"] = "ut-1"
        a = compose_rpg(st)
        self.assertIn("retrieval_hints", a)
        st.update(a)
        b = intent_parser(st)
        self.assertIn("refined_query", b)
        st.update(b)
        c = retrieve_rpg(st)
        self.assertIn("retrieval_metrics", c)
        self.assertGreaterEqual(c["retrieval_metrics"].get("k", 0), 1)

if __name__ == "__main__":
    unittest.main()
