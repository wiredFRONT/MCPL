#!/usr/bin/env python3
"""Validate every MCPL action entry and its example proposals.

Usage: python3 tools/validate.py
Exit code 0 only if: each *.action.json matches core/action.schema.json, each
proposals/valid-*.json passes that action's inputSchema, and each
proposals/invalid-*.json is rejected by it.
"""
import json
import pathlib
import sys

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
action_schema = json.loads((ROOT / "core" / "action.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(action_schema)
entry_validator = Draft202012Validator(action_schema)

failures = 0
checked = 0
for action_file in sorted(ROOT.glob("examples/**/*.action.json")):
    entry = json.loads(action_file.read_text(encoding="utf-8"))
    rel = action_file.relative_to(ROOT)
    errors = list(entry_validator.iter_errors(entry))
    checked += 1
    if errors:
        failures += 1
        print(f"FAIL  {rel}: {errors[0].message}")
        continue
    print(f"ok    {rel}")
    input_schema = entry["tool"]["inputSchema"]
    Draft202012Validator.check_schema(input_schema)
    proposal_validator = Draft202012Validator(input_schema)
    for proposal_file in sorted((action_file.parent / "proposals").glob("*.json")):
        proposal = json.loads(proposal_file.read_text(encoding="utf-8"))
        prel = proposal_file.relative_to(ROOT)
        perrors = list(proposal_validator.iter_errors(proposal))
        expect_valid = proposal_file.name.startswith("valid-")
        checked += 1
        if expect_valid and perrors:
            failures += 1
            print(f"FAIL  {prel}: should pass, rejected: {perrors[0].message}")
        elif not expect_valid and not perrors:
            failures += 1
            print(f"FAIL  {prel}: should be rejected, passed")
        elif expect_valid:
            print(f"ok    {prel}: accepted")
        else:
            print(f"ok    {prel}: rejected ({perrors[0].message})")

print(f"{checked} checked, {failures} failed")
sys.exit(1 if failures else 0)
