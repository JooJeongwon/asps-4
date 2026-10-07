"""Offline checks only: no Google upload, LLM call, or real customer data."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_neofirm as pipeline
from render_neofirm import render, validate
import login_neofirm as login


class NeoFirmChecks(unittest.TestCase):
    def test_login_rejects_anonymous_host_and_requires_server_auth(self):
        context = SimpleNamespace(cookies=lambda urls: [{"name": "NID", "value": "anonymous"}])
        page = SimpleNamespace(url="https://notebook.google.com/", wait_for_timeout=lambda ms: None)
        base = "https://notebook.google.com"
        self.assertFalse(login.google_session_ready(context, page, base))
        with self.assertRaisesRegex(RuntimeError, "시간 초과"):
            login.wait_for_google_session(context, page, base, timeout=0)
        context.cookies = lambda urls: [{"name": "SID", "value": "test-only-not-a-cookie"}]
        page.url = "https://accounts.google.com/"
        self.assertFalse(login.google_session_ready(context, page, base))
        page.url = base + "/"
        login.wait_for_google_session(context, page, base, timeout=0)
        for status, fetched, code in [("ok", False, 0), ("error", True, 0), ("ok", True, 1)]:
            response = SimpleNamespace(returncode=code, stdout=json.dumps(
                {"status": status, "checks": {"token_fetch": fetched}, "details": "must-not-print"}))
            with patch.object(login.subprocess, "run", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "서버 인증 실패"):
                    login.verify_auth("notebooklm")
        response = SimpleNamespace(returncode=0, stdout='{"status":"ok","checks":{"token_fetch":true}}')
        with patch.object(login.subprocess, "run", return_value=response), patch("builtins.print") as out:
            login.verify_auth("notebooklm")
            out.assert_called_once_with('AUTH OK: status=ok, token_fetch=true', flush=True)

    def test_render_and_citation_rejection(self):
        sources = [{"id": "S1", "path": "report.pdf", "pages": 22}]
        slide = {"title": "결과를 책임지는 회사", "message": "작업 배분과 책임을 함께 설계",
                 "seconds": 140, "notes": "새 서비스의 가격과 품질은 아직 검증하지 않았습니다.",
                 "bullets": [{"text": "반복 작업・전문가 판단을 구별한다.", "kind": "fact",
                              "evidence": [{"source": "S1", "location": "p.19"}]}]}
        data = {"slides": [copy.deepcopy(slide) for _ in range(3)]}
        with tempfile.TemporaryDirectory() as directory:
            render(data, sources, Path(directory), 420)
            quality = json.loads((Path(directory) / "quality.json").read_text())
            self.assertEqual(quality["pptx_reopen"], "passed")
            self.assertTrue((Path(directory) / "contact-sheet.png").exists())
            import pymupdf
            with pymupdf.open(Path(directory) / "neofirm-final.pdf") as pdf:
                self.assertNotIn("・", "".join(page.get_text() for page in pdf))
        for field, value in [("source", "S99"), ("location", "p.23")]:
            bad = copy.deepcopy(data)
            bad["slides"][0]["bullets"][0]["evidence"][0][field] = value
            with self.assertRaises(ValueError):
                validate(bad, sources, 420)
        bad = copy.deepcopy(data)
        bad["slides"][0]["bullets"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate(bad, sources, 420)
        for location in ["p.19 과제 C 100건 후 데이터", "p.19–20 / 2026 조사", "p.19, 20 품질"]:
            data["slides"][0]["bullets"][0]["evidence"][0]["location"] = location
            validate(data, sources, 420)
        for location in ["p.19–23", "p.19, 23", "p.0", "p.23", "정의 2026"]:
            data["slides"][0]["bullets"][0]["evidence"][0]["location"] = location
            with self.assertRaises(ValueError):
                validate(data, sources, 420)

    def test_source_reconcile_after_uncertain_write(self):
        source = {"id": "S2", "title": "Original title", "url": "https://example.com/report"}
        calls = []
        def nlm(*args, **kwargs):
            calls.append(args)
            if args[:2] == ("source", "list"):
                return {"sources": [{"id": "remote-source", "title": "Server title", "url": source["url"]}]}
            return {}
        with tempfile.TemporaryDirectory() as directory:
            state = {"input_hash": "ab" * 32, "notebook_id": "nb", "pending_write": "S2 Original title"}
            pipeline.sync_notebook(Path(directory), state, [source], nlm)
            self.assertNotIn("pending_write", state)
            self.assertEqual(source["notebooklm_source_id"], "remote-source")
            self.assertFalse(any(c[:2] == ("source", "add") for c in calls))
            state["pending_write"] = "S3 Missing"
            with self.assertRaisesRegex(RuntimeError, "uncertain"):
                pipeline.sync_notebook(Path(directory), state, [{"id": "S3", "title": "Missing", "url": "https://example.com/absent"}], nlm)

    def test_research_references_and_resume(self):
        calls = []
        def nlm(*args, **kwargs):
            calls.append(args)
            return {"answer": "근거가 있는 조사 [1]", "references": [{"source_id": "remote", "citation_number": 1, "cited_text": "근거"}]}
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            sources = [{"id": "S1", "notebooklm_source_id": "remote"}]
            pipeline.research(run, "nb", sources, nlm)
            pipeline.research(run, "nb", sources, nlm)
            self.assertEqual(len(calls), 3)
            self.assertEqual(json.loads((run / "research-1-citations.json").read_text())[0]["local_source_id"], "S1")
            with self.assertRaisesRegex(ValueError, "unknown reference"):
                pipeline.research(run, "nb", [{"id": "S1", "notebooklm_source_id": "other"}], nlm)

    def test_research_retries_rejected_cache_without_fabricating_citations(self):
        missing = {"answer": "출처가 있는 것처럼 보이는 주장 [S1 p.33]", "references": []}
        valid = {"answer": "원문 근거가 있는 조사 [1]", "references": [
            {"source_id": "remote", "citation_number": 1, "cited_text": "원문 근거"}]}
        sources = [{"id": "S1", "notebooklm_source_id": "remote", "pages": 22}]
        calls = []
        def nlm(*args, **kwargs):
            calls.append(args)
            return missing if len(calls) == 1 else valid
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            pipeline.write(run / "research-1.json", missing)
            pipeline.research(run, "nb", sources, nlm)
            self.assertEqual(len(calls), 4)
            self.assertEqual(json.loads((run / "research-1-rejected-1.json").read_text()), missing)
            self.assertEqual(json.loads((run / "research-1-rejected-2.json").read_text()), missing)
            self.assertEqual(json.loads((run / "research-1.json").read_text()), valid)
            self.assertNotIn("p.33", (run / "research.md").read_text())
            for args in calls:
                self.assertIn("기본 숫자 인용", args[1])
                self.assertNotIn("[S1 p.19]", args[1])
                self.assertEqual(args[args.index("-s") + 1], "remote")
                self.assertNotIn("--new", args)
            pipeline.research(run, "nb", sources, nlm)
            self.assertEqual(len(calls), 4)
        calls.clear()
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            def no_citations(*args, **kwargs):
                calls.append(args)
                return missing
            with self.assertRaisesRegex(ValueError, "after 2 attempts"):
                pipeline.research(run, "nb", sources, no_citations)
            self.assertEqual(len(calls), 2)
            self.assertFalse((run / "research-1.json").exists())
            self.assertFalse((run / "research.md").exists())
            self.assertEqual(len(list(run.glob("research-1-rejected-*.json"))), 2)

    def test_independent_rounds_and_failed_output_not_cached(self):
        calls = []
        def fake(run, name, prompt, *args):
            calls.append((name, prompt))
            text = f"{name} 테스트용 검증 출력." * 10
            pipeline.write(run / f"{name}.md", text)
            return text
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ["requirements", "research", "primary-research"]:
                pipeline.write(run / f"{name}.md", "SOURCE CONTEXT")
            with patch.object(pipeline, "codex", fake):
                pipeline.debate(run, None, "NDA")
            self.assertEqual(len(calls), 10)
            for name, prompt in calls:
                if name.startswith("round-1"):
                    self.assertNotIn("round-1-market 테스트", prompt)
                if name.startswith("round-2"):
                    for role in pipeline.ROLES:
                        self.assertIn(f"round-1-{role}", prompt)
                if name.startswith("round-3"):
                    for role in pipeline.ROLES:
                        self.assertIn(f"round-2-{role}", prompt)
            pipeline.write(run / "bad.md", "partial output must not be trusted")
            with patch.object(pipeline, "command", side_effect=RuntimeError("auth failed")):
                with self.assertRaises(RuntimeError):
                    pipeline.codex(run, "bad", "prompt")
            self.assertTrue((run / "bad.md").exists())
            self.assertFalse((run / "bad.events.jsonl").exists())

    def test_codex_short_json_contract_and_completed_trace_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            schema = run / "audit.schema.json"
            pipeline.write(schema, {"required": ["passed", "issues"], "properties": {"passed": {}, "issues": {}}})
            def trace(answer, success=True):
                return "\n".join(json.dumps(e) for e in [
                    {"type": "item.completed", "item": {"type": "agent_message", "text": answer}},
                    {"type": "turn.completed" if success else "turn.failed"}])
            answer = '{"passed":true,"issues":[]}'
            pipeline.write(run / "prompts/quality-review.txt", "audit prompt")
            pipeline.write(run / "logs/quality-review.json", {"exit_code": 0, "stdout": trace(answer)})
            with patch.object(pipeline, "command", side_effect=AssertionError("no new model call")):
                self.assertEqual(pipeline.codex(run, "quality-review", "audit prompt", schema=schema), answer)
                self.assertEqual(pipeline.codex(run, "quality-review", "audit prompt", schema=schema), answer)
            self.assertEqual((run / "quality-review.md").read_text(), answer)
            self.assertTrue((run / "quality-review.events.jsonl").exists())
            for bad in ['{"passed":"true","issues":[]}', '{"passed":true}', '{"passed":true,"issues":[1]}']:
                with patch.object(pipeline, "command", return_value=trace(bad)):
                    with self.assertRaises(ValueError):
                        pipeline.codex(run, "invalid", "prompt " + bad, schema=schema)
            with patch.object(pipeline, "command", return_value=trace(answer, success=False)):
                with self.assertRaisesRegex(RuntimeError, "no successful"):
                    pipeline.codex(run, "failed", "prompt", schema=schema)

    def test_resume_to_real_pptx_through_actual_cli_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            run = root / "runs/test-resume"
            run.mkdir(parents=True)
            for name in ["inputs/ChatGPT-2026-NeoFirm-Report.pdf", "docs/neofirm-requirements.md",
                         "docs/neofirm-primary-sources.json", "scripts/render_neofirm.py"]:
                pipeline.write(root / name, "hash input")
            pipeline.write(run / "state.json", {"completed": ["inputs", "research", "debate"]})
            for name in ["requirements", "research", "debate", "conclusion", "report", "primary-research"]:
                pipeline.write(run / f"{name}.md", "fixture source context")
            pipeline.write(run / "sources.json", [{"id": "S1", "pages": 22}])
            deck = {"slides": [{"title": "결과 책임", "message": "검증한 범위와 가정을 구별한다", "seconds": 140,
                "notes": "표준 NDA 검토 결과를 제공하는 설계 제안입니다.", "bullets": [{"text": "전문가 승인",
                "kind": "proposal", "evidence": [{"source": "S1", "location": "p.19 과제 C 100건 후 데이터"}]}]}
                for _ in range(3)]}
            model_calls = []
            def cli(args, **kwargs):
                if "exec" not in args:
                    return SimpleNamespace(returncode=0, stdout="fixture version", stderr="")
                model_calls.append(args)
                answer = json.dumps(deck) if "slides.md" in args[args.index("--output-last-message") + 1] else '{"passed":true,"issues":[]}'
                events = "\n".join(json.dumps(e) for e in [
                    {"type": "item.completed", "item": {"type": "agent_message", "text": answer}},
                    {"type": "turn.completed"}])
                return SimpleNamespace(returncode=0, stdout=events, stderr="")
            with patch.object(pipeline, "ROOT", root), patch.object(sys, "argv", ["run", "--resume", str(run)]), \
                    patch.object(pipeline.subprocess, "run", side_effect=cli), \
                    patch.object(pipeline, "sync_notebook", side_effect=AssertionError("completed research must not reconnect")):
                pipeline.main()
            self.assertEqual(len(model_calls), 2)
            self.assertEqual(json.loads((run / "state.json").read_text())["status"], "complete")
            self.assertTrue(json.loads((run / "quality-review.json").read_text())["passed"])
            self.assertTrue((root / "output/test-resume/neofirm-final.pptx").exists())
            self.assertEqual(json.loads((run / "quality.json").read_text())["pptx_reopen"], "passed")

    def test_semantic_rejection_does_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ["requirements", "research", "debate", "conclusion", "report", "primary-research"]:
                pipeline.write(run / f"{name}.md", "test context")
            pipeline.write(run / "sources.json", [{"id": "S1", "pages": 22}])
            data = {"slides": [{"title": "테스트", "message": "검증할 후보", "seconds": 140,
                "notes": "아직 검증하지 않은 설계입니다.", "bullets": [{"text": "결과 책임",
                "kind": "fact", "evidence": [{"source": "S1", "location": "p.19"}]}]} for _ in range(3)]}
            calls = []
            def fake(run, name, *args):
                calls.append((run, name, args[0]))
                pipeline.write(run / f"{name}.md", "rejected response")
                return json.dumps({"passed": False, "issues": ["unsupported claim"]} if name == "quality-review" else data)
            with patch.object(pipeline, "codex", fake):
                with self.assertRaisesRegex(ValueError, "semantic slide audit failed"):
                    pipeline.presentation(run, 7, None)
            self.assertFalse((run / "neofirm-final.pptx").exists())
            self.assertFalse((run / "slides.md").exists())
            candidates = [call for call in calls if call[1] == "slides"]
            self.assertEqual(len(candidates), 3)
            self.assertIn("unsupported claim", candidates[1][2])
            self.assertEqual(len({call[0] for call in candidates}), 3)
            self.assertEqual(len(list((run / "presentation-attempts").glob("*/quality-review.json"))), 3)

    def test_presentation_repairs_format_and_semantics_before_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for name in ["requirements", "research", "debate", "conclusion", "report", "primary-research"]:
                pipeline.write(run / f"{name}.md", "원문과 토론 market-r3-1")
            pipeline.write(run / "sources.json", [{"id": "S1", "pages": 22}])
            valid = {"slides": [{"title": "검증", "message": "미확인은 확인 범위를 밝힌다", "seconds": 140,
                "notes": "현재 자료로 품질은 미확인이며 별도 시험을 제안합니다.", "bullets": [
                {"text": "결과 책임", "kind": "fact", "evidence": [{"source": "S1", "location": "p.19"}]},
                {"text": "품질은 미확인", "kind": "unknown", "evidence": []}]} for _ in range(3)]}
            invalid = copy.deepcopy(valid)
            invalid["slides"][0]["bullets"][0]["evidence"][0]["location"] = "p.33"
            prior = {"passed": False, "issues": ["토론 변경 출처 누락"]}
            pipeline.write(run / "slides.json", invalid)
            pipeline.write(run / "quality-review.json", prior)
            calls, candidates, audits = [], [], []
            def fake(work, name, prompt, *args):
                calls.append((name, prompt))
                pipeline.write(work / f"{name}.md", "model result")
                if name == "slides":
                    candidates.append(work)
                    return json.dumps(invalid if len(candidates) == 1 else valid)
                audits.append(work)
                return json.dumps({"passed": len(audits) == 2,
                    "issues": [] if len(audits) == 2 else ["공급자 매출 구조 누락"]})
            with patch.object(pipeline, "codex", fake), patch("render_neofirm.render") as rendered:
                pipeline.presentation(run, 7, None)
                rendered.assert_called_once_with(valid, [{"id": "S1", "pages": 22}], run, 420)
            self.assertEqual(len(candidates), 3)
            self.assertEqual(len(audits), 2)
            prompts = [prompt for name, prompt in calls if name == "slides"]
            self.assertIn("토론 변경 출처 누락", prompts[0])
            self.assertIn("invalid report page", prompts[1])
            self.assertIn("공급자 매출 구조 누락", prompts[2])
            self.assertEqual(json.loads((run / "presentation-attempts/previous-rejected/slides.json").read_text()), invalid)
            self.assertEqual(json.loads((run / "presentation-attempts/previous-rejected/quality-review.json").read_text()), prior)
            self.assertTrue(json.loads((run / "quality-review.json").read_text())["passed"])


if __name__ == "__main__":
    unittest.main()
