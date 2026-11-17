"""Focused contract/compiler tests. Run with: python -m unittest tools.test_workflow_compiler"""
from __future__ import annotations

import json
import re
import base64
import pathlib
import subprocess
import sys
import tempfile
import unittest

from tools.workflow_compiler import ROOT, WorkflowError, compile_workflow, fingerprint_material, read_json, validate_workflow


def scenario() -> dict:
    return {
        "schemaVersion": "mcpl.workflow/v1",
        "id": "workspace-file-roundtrip",
        "title": "Create and verify a workspace file",
        "parameters": {
            "project_id": {"type": "string", "minLength": 1, "maxLength": 128},
            "prompt": {"type": "string", "minLength": 1, "maxLength": 2048},
        },
        "requires": {
            "actions": ["set_config_value"],
            "bindings": ["project.select", "chat.send", "approval.approve", "page.reload"],
            "events": ["approval.request", "tool.completed", "run.completed"],
            "oracles": ["files.bytes"],
        },
        "steps": [
            {"id": "select-project", "type": "command", "binding": "project.select", "arguments": {"projectId": {"$param": "project_id"}}, "timeoutMs": 10000},
            {"id": "request-edit", "type": "command", "binding": "chat.send", "action": "set_config_value", "arguments": {"projectId": {"$param": "project_id"}, "text": {"$param": "prompt"}}, "timeoutMs": 30000},
            {"id": "approval-requested", "type": "observe", "event": "approval.request", "match": {"action": "set_config_value"}, "timeoutMs": 10000},
            {"id": "approve-once", "type": "command", "binding": "approval.approve", "arguments": {"once": True}, "timeoutMs": 10000},
            {"id": "tool-finished", "type": "observe", "event": "tool.completed", "match": {"action": "set_config_value"}, "timeoutMs": 120000},
            {"id": "run-finished", "type": "observe", "event": "run.completed", "match": {"status": "succeeded"}, "timeoutMs": 120000},
            {"id": "verify-file", "type": "assert", "oracle": "files.bytes", "input": {"projectId": {"$param": "project_id"}, "path": "generated/hello.txt"}, "expected": {"utf8": "Hello from MCPL fixture\n"}},
            {"id": "reload-project", "type": "command", "binding": "page.reload", "arguments": {}, "timeoutMs": 10000},
            {"id": "verify-persisted-file", "type": "assert", "oracle": "files.bytes", "input": {"projectId": {"$param": "project_id"}, "path": "generated/hello.txt"}, "expected": {"utf8": "Hello from MCPL fixture\n"}},
        ],
    }


class WorkflowValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, _ = read_json(ROOT / "extensions/workflows/workflow.schema.json")

    def test_valid_roundtrip_shape(self):
        validate_workflow(scenario(), self.schema)

    def test_unknown_root_and_step_properties_fail(self):
        for mutate in (
            lambda data: data.update({"exec": "import os"}),
            lambda data: data["steps"][0].update({"javascript": "await page.click()"}),
        ):
            data = scenario()
            mutate(data)
            with self.assertRaises(WorkflowError):
                validate_workflow(data, self.schema)

    def test_duplicate_step_ids_fail(self):
        data = scenario()
        data["steps"][1]["id"] = data["steps"][0]["id"]
        with self.assertRaisesRegex(WorkflowError, "duplicate step id"):
            validate_workflow(data, self.schema)

    def test_unknown_parameter_event_binding_or_oracle_fail(self):
        mutations = (
            lambda data: data["steps"][0]["arguments"].update({"projectId": {"$param": "missing"}}),
            lambda data: data["steps"][2].update({"event": "approval.requested"}),
            lambda data: data["steps"][0].update({"binding": "project.unsupported"}),
            lambda data: data["steps"][6].update({"oracle": "files.guess"}),
        )
        for mutate in mutations:
            data = scenario()
            mutate(data)
            with self.subTest(data=data), self.assertRaises(WorkflowError):
                validate_workflow(data, self.schema)

    def test_duplicate_ids_unknown_fields_and_unbounded_timeout_fail_schema(self):
        mutations = (
            lambda data: data["steps"][0].update({"timeoutMs": 120001}),
            lambda data: data["steps"][0].update({"unexpected": True}),
            lambda data: data["steps"][0].update({"id": "NotCanonical"}),
            lambda data: data["requires"]["bindings"].append("page.reload"),
        )
        for mutate in mutations:
            data = scenario()
            mutate(data)
            with self.assertRaises(WorkflowError):
                validate_workflow(data, self.schema)

    def test_inverted_parameter_length_bounds_fail(self):
        data = scenario()
        data["parameters"]["project_id"]["minLength"] = 20
        data["parameters"]["project_id"]["maxLength"] = 10
        with self.assertRaisesRegex(WorkflowError, "minLength exceeds maxLength"):
            validate_workflow(data, self.schema)

    def test_action_reference_cannot_be_unresolved(self):
        data = scenario()
        data["steps"][1]["action"] = "workspace_shell"
        with self.assertRaisesRegex(WorkflowError, "undeclared action"):
            validate_workflow(data, self.schema)


class CompilerTests(unittest.TestCase):
    def test_repository_example_passes_schema_and_compiles(self):
        workflow_path = ROOT / "examples/workflows/configuration-roundtrip.workflow.json"
        action = ROOT / "examples/app-config/set_config_value.action.json"
        with tempfile.TemporaryDirectory() as temp:
            bindings = pathlib.Path(temp) / "trusted-bindings.mjs"
            bindings.write_text("export async function createBindings() { return {}; }\n", encoding="utf-8")
            workflow, _ = read_json(workflow_path)
            schema, _ = read_json(ROOT / "extensions/workflows/workflow.schema.json")
            validate_workflow(workflow, schema)
            output = pathlib.Path(temp) / "generated.spec.mjs"
            generated, _ = compile_workflow(workflow_path, [action], bindings, output)
            encoded = re.search(rb'JSON.parse\(Buffer.from\("([A-Za-z0-9+/=]+)", "base64"\)', generated).group(1)
            payload = base64.b64decode(encoded)
            self.assertIn(b"verify-after-reload", payload)
            self.assertIn(b"settings.value", payload)
            self.assertIn(b"validateCapabilities(bindings, workflow.requires)", generated)
            self.assertIn(b"capabilities are required", generated)
            self.assertNotIn(b"file:///", generated)

    def test_deterministic_artifact_fingerprint_and_stale_inputs(self):
        action = ROOT / "examples/app-config/set_config_value.action.json"
        with tempfile.TemporaryDirectory() as temp:
            work = pathlib.Path(temp)
            workflow_path = work / "scenario.json"
            bindings_path = work / "bindings.mjs"
            workflow_path.write_text(json.dumps(scenario(), indent=2) + "\n", encoding="utf-8")
            bindings_path.write_text("export async function createBindings() { return {}; }\n", encoding="utf-8")
            output_path = work / "generated.spec.mjs"
            first, first_fingerprint = compile_workflow(workflow_path, [action], bindings_path, output_path)
            second, second_fingerprint = compile_workflow(workflow_path, [action], bindings_path, output_path)
            self.assertEqual(first, second)
            self.assertEqual(first_fingerprint, second_fingerprint)
            generated = first.decode("utf-8")
            self.assertIn("test.step(step.id", generated)
            self.assertIn("createBindings", generated)
            self.assertIn("Buffer.from(", generated)
            self.assertNotIn("eval(", generated)

            workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace("Create and verify", "Create then verify"), encoding="utf-8")
            changed, changed_fingerprint = compile_workflow(workflow_path, [action], bindings_path, output_path)
            self.assertNotEqual(first_fingerprint, changed_fingerprint)
            self.assertNotEqual(first, changed)

    def test_missing_action_descriptor_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            work = pathlib.Path(temp)
            workflow_path = work / "scenario.json"
            bindings_path = work / "bindings.mjs"
            workflow_path.write_text(json.dumps(scenario()), encoding="utf-8")
            bindings_path.write_text("// trusted fixture\n", encoding="utf-8")
            with self.assertRaisesRegex(WorkflowError, "missing action descriptor"):
                compile_workflow(workflow_path, [], bindings_path, work / "generated.spec.mjs")

    def test_action_catalog_descriptor_must_match_existing_mcpl_schema(self):
        action = ROOT / "examples/app-config/set_config_value.action.json"
        bad_data = scenario()
        bad_data["requires"]["actions"] = ["not-present"]
        with tempfile.TemporaryDirectory() as temp:
            work = pathlib.Path(temp)
            workflow_path = work / "scenario.json"
            bindings_path = work / "bindings.mjs"
            workflow_path.write_text(json.dumps(bad_data), encoding="utf-8")
            bindings_path.write_text("// trusted fixture\n", encoding="utf-8")
            with self.assertRaisesRegex(WorkflowError, "undeclared action"):
                compile_workflow(workflow_path, [action], bindings_path, work / "generated.spec.mjs")

    def test_fingerprint_tracks_compiler_and_schema_source_digests(self):
        base = fingerprint_material(b"workflow", b"workflow-schema", b"action-schema", {"tool": b"action"}, b"module", "../bindings.mjs", b"compiler")
        changed_compiler = fingerprint_material(b"workflow", b"workflow-schema", b"action-schema", {"tool": b"action"}, b"module", "../bindings.mjs", b"compiler changed")
        changed_schema = fingerprint_material(b"workflow", b"workflow-schema changed", b"action-schema", {"tool": b"action"}, b"module", "../bindings.mjs", b"compiler")
        self.assertNotEqual(base["compiler_source_sha256"], changed_compiler["compiler_source_sha256"])
        self.assertNotEqual(base["workflow_schema_sha256"], changed_schema["workflow_schema_sha256"])

    def test_relocated_equivalent_layout_has_same_generated_bytes(self):
        action = ROOT / "examples/app-config/set_config_value.action.json"
        workflow_source = ROOT / "examples/workflows/configuration-roundtrip.workflow.json"
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            outputs = []
            for root in (pathlib.Path(first_dir), pathlib.Path(second_dir)):
                (root / "fixture").mkdir()
                workflow = root / "fixture" / "scenario.json"
                binding = root / "fixture" / "bindings.mjs"
                output = root / "fixture" / "generated.spec.mjs"
                workflow.write_bytes(workflow_source.read_bytes())
                binding.write_text("// same trusted module\n", encoding="utf-8")
                outputs.append(compile_workflow(workflow, [action], binding, output)[0])
            self.assertEqual(outputs[0], outputs[1])

    def test_cli_generate_check_and_drift_detection(self):
        workflow = ROOT / "examples/workflows/configuration-roundtrip.workflow.json"
        action = ROOT / "examples/app-config/set_config_value.action.json"
        compiler = ROOT / "tools/workflow_compiler.py"
        with tempfile.TemporaryDirectory() as temp:
            work = pathlib.Path(temp)
            bindings = work / "trusted-bindings.mjs"
            output = work / "configuration-roundtrip.spec.mjs"
            bindings.write_text("// fixture version one\n", encoding="utf-8")
            common = [sys.executable, str(compiler), str(workflow), "--actions", str(action), "--bindings-module", str(bindings), "--output", str(output)]
            built = subprocess.run(common, capture_output=True, text=True, check=False)
            self.assertEqual(built.returncode, 0, built.stderr)
            current = subprocess.run(common + ["--check"], capture_output=True, text=True, check=False)
            self.assertEqual(current.returncode, 0, current.stderr)
            bindings.write_text("// fixture version two\n", encoding="utf-8")
            drift = subprocess.run(common + ["--check"], capture_output=True, text=True, check=False)
            self.assertEqual(drift.returncode, 2)
            self.assertIn("DRIFT", drift.stderr)


if __name__ == "__main__":
    unittest.main()
