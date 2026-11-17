#!/usr/bin/env python3
"""Validate an MCPL draft linear workflow and emit a deterministic Playwright spec.

The generated test imports one explicitly trusted application binding module. Workflow data
cannot name a module path, source fragment, JavaScript expression, or arbitrary evaluator.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "extensions" / "workflows" / "workflow.schema.json"
COMPILER_VERSION = "mcpl-workflow-compiler/0.1.0-draft"


class WorkflowError(ValueError):
    pass


def read_json(path: pathlib.Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    try:
        return json.loads(raw.decode("utf-8")), raw
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"{path}: invalid UTF-8 JSON: {exc}") from exc


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_workflow(workflow: Any, schema: dict[str, Any]) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(workflow), key=lambda e: list(map(str, e.absolute_path)))
    if errors:
        first = errors[0]
        where = "/" + "/".join(map(str, first.absolute_path)) if first.absolute_path else "/"
        raise WorkflowError(f"workflow schema {where}: {first.message}")

    seen: set[str] = set()
    for step in workflow["steps"]:
        if step["id"] in seen:
            raise WorkflowError(f"duplicate step id: {step['id']}")
        seen.add(step["id"])
    if len(workflow["parameters"]) != len(set(workflow["parameters"])):
        raise WorkflowError("duplicate parameter names")

    declared_params = workflow["parameters"]
    for name, spec in declared_params.items():
        if spec["minLength"] > spec["maxLength"]:
            raise WorkflowError(f"parameter {name!r} minLength exceeds maxLength")
    declared_bindings = set(workflow["requires"]["bindings"])
    declared_actions = set(workflow["requires"]["actions"])
    declared_events = set(workflow["requires"]["events"])
    declared_oracles = set(workflow["requires"]["oracles"])
    used_bindings: set[str] = set()
    used_actions: set[str] = set()
    used_events: set[str] = set()
    used_oracles: set[str] = set()
    used_params: set[str] = set()

    def visit(value: Any, where: str) -> None:
        if isinstance(value, dict):
            if "$param" in value:
                name = value["$param"]
                if name not in declared_params:
                    raise WorkflowError(f"unknown parameter reference {name!r} at {where}")
                used_params.add(name)
                return
            for key, child in value.items():
                visit(child, f"{where}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{where}/{index}")

    for step in workflow["steps"]:
        if step["type"] == "command":
            binding = step["binding"]
            used_bindings.add(binding)
            if binding not in declared_bindings:
                raise WorkflowError(f"command {step['id']} uses undeclared binding {binding!r}")
            if "action" in step:
                action = step["action"]
                used_actions.add(action)
                if action not in declared_actions:
                    raise WorkflowError(f"command {step['id']} uses undeclared action {action!r}")
            visit(step["arguments"], f"steps/{step['id']}/arguments")
        elif step["type"] == "observe":
            used_events.add(step["event"])
            if step["event"] not in declared_events:
                raise WorkflowError(f"observe {step['id']} uses undeclared event {step['event']!r}")
            visit(step["match"], f"steps/{step['id']}/match")
        else:
            used_oracles.add(step["oracle"])
            if step["oracle"] not in declared_oracles:
                raise WorkflowError(f"assert {step['id']} uses undeclared oracle {step['oracle']!r}")
            visit(step["input"], f"steps/{step['id']}/input")
            visit(step["expected"], f"steps/{step['id']}/expected")

    for label, declared, used in (
        ("binding", declared_bindings, used_bindings),
        ("action", declared_actions, used_actions),
        ("event", declared_events, used_events),
        ("oracle", declared_oracles, used_oracles),
        ("parameter", set(declared_params), used_params),
    ):
        unused = declared - used
        if unused:
            raise WorkflowError(f"unused declared {label}(s): {', '.join(sorted(unused))}")


def validate_actions(paths: list[pathlib.Path], required: set[str]) -> tuple[dict[str, Any], dict[str, bytes]]:
    action_schema, _ = read_json(ROOT / "core" / "action.schema.json")
    Draft202012Validator.check_schema(action_schema)
    action_validator = Draft202012Validator(action_schema)
    found: dict[str, Any] = {}
    sources_by_name: dict[str, bytes] = {}
    for path in paths:
        action, raw = read_json(path)
        errors = list(action_validator.iter_errors(action))
        if errors:
            raise WorkflowError(f"action descriptor {path}: {errors[0].message}")
        name = action["tool"]["name"]
        if name in found:
            raise WorkflowError(f"duplicate action descriptor: {name}")
        try:
            Draft202012Validator.check_schema(action["tool"]["inputSchema"])
        except Exception as exc:  # jsonschema's detailed schema exception
            raise WorkflowError(f"action {name!r} has an invalid inputSchema: {exc}") from exc
        found[name] = action
        sources_by_name[name] = raw
    missing = required - found.keys()
    if missing:
        raise WorkflowError(f"missing action descriptor(s): {', '.join(sorted(missing))}")
    return found, sources_by_name


def render(workflow: dict[str, Any], bindings: pathlib.Path, output: pathlib.Path, source_fingerprint: str) -> bytes:
    relative = pathlib.Path(os.path.relpath(bindings.resolve(), output.resolve().parent)).as_posix()
    if not relative.startswith((".", "/")):
        relative = "./" + relative
    payload = base64.b64encode(json.dumps(workflow, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii")
    source = f'''// Generated by {COMPILER_VERSION}; source fingerprint: sha256:{source_fingerprint}
// Review this artifact and its trusted application binding module before running it.
import {{ test }} from "@playwright/test";
import {{ createBindings }} from {json.dumps(relative)};

const workflow = JSON.parse(Buffer.from("{payload}", "base64").toString("utf8"));

function validateInputs(definitions, values) {{
  if (!values || typeof values !== "object" || Array.isArray(values)) throw new Error("binding inputs must be an object");
  const allowed = new Set(Object.keys(definitions));
  for (const key of Object.keys(values)) if (!allowed.has(key)) throw new Error(`unknown fixture input: ${{key}}`);
  for (const [key, spec] of Object.entries(definitions)) {{
    const value = values[key];
    if (typeof value !== "string" || value.length < spec.minLength || value.length > spec.maxLength) {{
      throw new Error(`fixture input ${{key}} must be a string with length ${{spec.minLength}}..${{spec.maxLength}}`);
    }}
  }}
}}

function resolve(value, inputs) {{
  if (Array.isArray(value)) return value.map((item) => resolve(item, inputs));
  if (value && typeof value === "object") {{
    if (Object.keys(value).length === 1 && typeof value.$param === "string") return inputs[value.$param];
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, resolve(item, inputs)]));
  }}
  return value;
}}

function validateCapabilities(bindings, requires) {{
  const capabilities = bindings.capabilities;
  if (!capabilities || typeof capabilities !== "object") throw new Error("binding capabilities are required");
  for (const [kind, required] of Object.entries(requires)) {{
    const available = capabilities[kind];
    if (!Array.isArray(available)) throw new Error(`binding capabilities.${{kind}} must be an array`);
    const availableSet = new Set(available);
    for (const name of required) if (!availableSet.has(name)) throw new Error(`missing ${{kind}} capability: ${{name}}`);
  }}
  if (typeof bindings.command !== "function" || typeof bindings.observe !== "function" || typeof bindings.assert !== "function") {{
    throw new Error("binding command, observe, and assert functions are required");
  }}
}}

test(workflow.title, async ({{ page, request }}, testInfo) => {{
  const bindings = await createBindings({{ page, request }}, testInfo);
  try {{
    validateInputs(workflow.parameters, bindings.inputs);
    validateCapabilities(bindings, workflow.requires);
    for (const step of workflow.steps) {{
      await test.step(step.id, async () => {{
        if (step.type === "command") await bindings.command(step.binding, resolve(step.arguments, bindings.inputs), {{ timeoutMs: step.timeoutMs }});
        else if (step.type === "observe") await bindings.observe(step.event, resolve(step.match, bindings.inputs), {{ timeoutMs: step.timeoutMs }});
        else await bindings.assert(step.oracle, resolve(step.input, bindings.inputs), resolve(step.expected, bindings.inputs));
      }});
    }}
  }} finally {{
    if (typeof bindings.dispose === "function") await bindings.dispose();
  }}
}});
'''
    return source.encode("utf-8")


def fingerprint_material(
    workflow_raw: bytes,
    schema_raw: bytes,
    action_schema_raw: bytes,
    action_sources: dict[str, bytes],
    bindings_raw: bytes,
    bindings_identity: str,
    compiler_source_raw: bytes,
) -> dict[str, Any]:
    """Create content-addressed inputs using names/relative identity, never host roots."""
    return {
        "compiler_version": COMPILER_VERSION,
        "compiler_source_sha256": digest(compiler_source_raw),
        "workflow_sha256": digest(workflow_raw),
        "workflow_schema_sha256": digest(schema_raw),
        "action_schema_sha256": digest(action_schema_raw),
        "action_descriptors": {name: digest(raw) for name, raw in sorted(action_sources.items())},
        "trusted_bindings_module": {bindings_identity.replace("\\", "/"): digest(bindings_raw)},
    }


def compile_workflow(workflow_path: pathlib.Path, actions_paths: list[pathlib.Path], bindings_path: pathlib.Path, output_path: pathlib.Path) -> tuple[bytes, str]:
    workflow, workflow_raw = read_json(workflow_path)
    schema, schema_raw = read_json(SCHEMA_PATH)
    action_schema, action_schema_raw = read_json(ROOT / "core" / "action.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(action_schema)
    validate_workflow(workflow, schema)
    _, action_sources = validate_actions(actions_paths, set(workflow["requires"]["actions"]))
    if not bindings_path.is_file():
        raise WorkflowError(f"trusted bindings module does not exist: {bindings_path}")
    relative_binding = pathlib.Path(os.path.relpath(bindings_path.resolve(), output_path.resolve().parent)).as_posix()
    material = fingerprint_material(
        workflow_raw, schema_raw, action_schema_raw, action_sources,
        bindings_path.read_bytes(), relative_binding, pathlib.Path(__file__).read_bytes(),
    )
    fingerprint = digest(json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return render(workflow, bindings_path, output_path, fingerprint), fingerprint


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=pathlib.Path)
    parser.add_argument("--actions", type=pathlib.Path, action="append", required=True, help="trusted existing MCPL action descriptor; repeat as needed")
    parser.add_argument("--bindings-module", type=pathlib.Path, required=True, help="trusted authored application binding module")
    parser.add_argument("--output", type=pathlib.Path, required=True, help="generated .spec.mjs output")
    parser.add_argument("--check", action="store_true", help="verify output is current without writing")
    args = parser.parse_args(argv)
    try:
        generated, fingerprint = compile_workflow(args.workflow, args.actions, args.bindings_module, args.output)
        if args.check:
            if not args.output.is_file() or args.output.read_bytes() != generated:
                print(f"DRIFT {args.output}: generated artifact is missing or stale", file=sys.stderr)
                return 2
            print(f"CURRENT sha256:{fingerprint} {args.output}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(generated)
        print(f"GENERATED sha256:{fingerprint} {args.output}")
        return 0
    except (WorkflowError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
