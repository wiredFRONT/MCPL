#!/usr/bin/env python3
"""Check every MCPL example: action entries, guards, proposals and cases.

Usage: python3 tools/validate.py        (needs: pip install jsonschema)

For each examples/<app>/ folder:
  *.action.json            must match core/action.schema.json
  guards/*.guard.json      must match core/guard.schema.json; every guard an action names must exist
  proposals/valid-*.json   must pass the action's input schema
  proposals/invalid-*.json must be rejected by it
  cases/*.json             the full decision (schema, then guards) must equal the case's `expect`

Links to INCRAM: a guard may list INCRAM rule IDs under `implements`. They are checked against the
INCRAM ID registry when one is found: $INCRAM_REGISTRY, then ../../registry/ids.yaml (MCPL checked out
as INCRAM's modules/mcpl), then ../incram/registry/ids.yaml (sibling checkout). Needs pyyaml for that.

Order of decision, which is the order MCPL itself uses:
  1. input schema  -> rejected by schema
  2. each guard    -> rejected by guard / ask / confirm
  3. otherwise     -> accepted (ready for preview and approval; nothing is applied here)
"""
import importlib.util
import json
import os
import pathlib
import sys

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
state = {"checked": 0, "failed": 0}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def report(ok, path, detail=""):
    state["checked"] += 1
    if not ok:
        state["failed"] += 1
    print(f"{'ok   ' if ok else 'FAIL '} {path.relative_to(ROOT)}{': ' + detail if detail else ''}")


def schema_validator(name):
    schema = load(ROOT / "core" / name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def load_check(guard_file, guard):
    impl = guard_file.parent / guard["implementation"]
    spec = importlib.util.spec_from_file_location(impl.stem, impl)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check


def decide(action, guards, proposal, context):
    """Return the decision for one proposal. Mirrors MCPL's order: schema first, then guards."""
    errors = list(Draft202012Validator(action["tool"]["inputSchema"]).iter_errors(proposal))
    if errors:
        return {"outcome": "rejected", "by": "schema"}, errors[0].message
    for guard_id in action["mcpl"].get("guards", []):
        guard, check = guards[guard_id]
        result = check(proposal, context)
        if result == "fail":
            if guard["on_fail"] == "reject":
                return {"outcome": "rejected", "by": "guard", "guard": guard_id}, guard["fail_message"]
            return {"outcome": "confirm", "guard": guard_id}, guard["fail_message"]
        if result == "unknown":
            if guard["on_unknown"] == "ask":
                return {"outcome": "ask", "guard": guard_id}, guard["ask_message"]
            return {"outcome": "rejected", "by": "guard", "guard": guard_id}, "needed context is missing"
        if result != "pass":
            raise ValueError(f"guard {guard_id} returned {result!r}")
    return {"outcome": "accepted"}, ""


def incram_ids():
    """Return (set of registered INCRAM rule IDs, where they came from), or (None, reason)."""
    candidates = [os.environ.get("INCRAM_REGISTRY"), ROOT / ".." / ".." / "registry" / "ids.yaml", ROOT / ".." / "incram" / "registry" / "ids.yaml"]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).is_file():
            try:
                import yaml
            except ImportError:
                return None, "pyyaml is not installed"
            entries = yaml.safe_load(pathlib.Path(candidate).read_text(encoding="utf-8"))["ids"]
            return {entry["id"] for entry in entries}, str(pathlib.Path(candidate).resolve())
    return None, "no INCRAM checkout found"


registered, registry_source = incram_ids()
implemented = {}

action_validator = schema_validator("action.schema.json")
guard_validator = schema_validator("guard.schema.json")

for app_dir in sorted(p for p in (ROOT / "examples").iterdir() if p.is_dir()):
    guards = {}
    for guard_file in sorted(app_dir.glob("guards/*.guard.json")):
        guard = load(guard_file)
        errors = list(guard_validator.iter_errors(guard))
        report(not errors, guard_file, errors[0].message if errors else "")
        if not errors:
            guards[guard["id"]] = (guard, load_check(guard_file, guard))
            for rule_id in guard.get("implements", []):
                implemented.setdefault(rule_id, []).append(str(guard_file.relative_to(ROOT)))
                if registered is not None and rule_id not in registered:
                    report(False, guard_file, f"implements {rule_id}, which is not in the INCRAM ID registry")

    actions = {}
    for action_file in sorted(app_dir.glob("*.action.json")):
        action = load(action_file)
        errors = list(action_validator.iter_errors(action))
        missing = [g for g in action.get("mcpl", {}).get("guards", []) if g not in guards]
        detail = errors[0].message if errors else (f"names guards that do not exist: {missing}" if missing else "")
        report(not errors and not missing, action_file, detail)
        if not errors and not missing:
            Draft202012Validator.check_schema(action["tool"]["inputSchema"])
            actions[action["tool"]["name"]] = action
            for guard_id in action["mcpl"].get("guards", []):
                if action["tool"]["name"] not in guards[guard_id][0]["applies_to"]:
                    report(False, action_file, f"guard {guard_id} does not list this action in applies_to")

    if len(actions) == 1:
        only = next(iter(actions.values()))
        validator = Draft202012Validator(only["tool"]["inputSchema"])
        for proposal_file in sorted(app_dir.glob("proposals/*.json")):
            errors = list(validator.iter_errors(load(proposal_file)))
            expect_valid = proposal_file.name.startswith("valid-")
            ok = (not errors) if expect_valid else bool(errors)
            detail = "accepted" if not errors else f"rejected ({errors[0].message})"
            report(ok, proposal_file, detail if ok else f"expected {'pass' if expect_valid else 'rejection'}; {detail}")

    for case_file in sorted(app_dir.glob("cases/*.json")):
        case = load(case_file)
        action = actions.get(case["action"])
        if action is None:
            report(False, case_file, f"unknown action {case['action']}")
            continue
        got, why = decide(action, guards, case["proposal"], case.get("context"))
        ok = got == case["expect"]
        report(ok, case_file, json.dumps(got) if ok else f"expected {json.dumps(case['expect'])}, got {json.dumps(got)}")

for rule_id, where in sorted(implemented.items()):
    print(f"link  INCRAM {rule_id} is enforced by {', '.join(where)}")
if implemented:
    print(f"links {'checked against ' + registry_source if registered is not None else 'NOT checked: ' + registry_source}")
print(f"{state['checked']} checked, {state['failed']} failed")
sys.exit(1 if state["failed"] else 0)
