# MCPL workflows (draft)

**MCPL:** This folder defines the first linear workflow profile. It is a draft extension, not an accepted MCPL standard. It is not a workflow server, runner, approval mechanism, or proof that a person approved an action.

**MCPL:** `workflow.schema.json` accepts an ordered scenario made from `command`, `observe`, and `assert` steps. The authored `expected` value is independent scenario data; it must not be generated from the trace being checked. Every step has a stable ID. Commands have bounded timeouts and JSON arguments only. Parameters are bounded strings supplied by the host's trusted bindings. The only substitution is an exact `{"$param":"name"}` object; no expressions, templates, or source snippets are supported.

**MCPL:** Action names resolve against action descriptor files passed to the compiler. Binding, event, action, and oracle names must be declared and referenced. Unknown fields and references, duplicate step IDs, missing parameter values, and out-of-range timeouts fail closed.

**MCPL:** The deterministic compiler emits a Playwright `.spec.mjs` file. It imports `createBindings({page, request}, testInfo)` from the explicitly selected trusted host module using a relative import. That factory returns `{inputs, capabilities, command, observe, assert, dispose?}`. Capabilities contain arrays named `actions`, `bindings`, `events`, and `oracles`; the generated test checks every requirement before running the first step. Its `inputs` object supplies fixture strings declared by the workflow. The compiler never imports or executes the host module; Playwright executes the generated test and imported module only when an operator runs it. Review both before execution.

## CLI

```powershell
python tools/workflow_compiler.py examples/workflows/configuration-roundtrip.workflow.json `
  --actions examples/app-config/set_config_value.action.json `
  --bindings-module path/to/trusted-bindings.mjs `
  --output path/to/generated/configuration-roundtrip.spec.mjs

# Recompute and compare bytes without overwriting the reviewed artifact:
python tools/workflow_compiler.py examples/workflows/configuration-roundtrip.workflow.json `
  --actions examples/app-config/set_config_value.action.json `
  --bindings-module path/to/trusted-bindings.mjs `
  --output path/to/generated/configuration-roundtrip.spec.mjs --check
```

The generated-file header carries a SHA-256 fingerprint over the workflow bytes, workflow schema bytes, action descriptor bytes, trusted module bytes, and compiler version. `--check` recompiles and compares the complete generated output, so changes to any of those inputs report drift. It does not execute the generated test.

**MCPL:** Run the focused compiler tests with `python -m unittest tools.test_workflow_compiler`. The repository's action/guard examples remain separately checked with `python tools/validate.py`.

**UPSTREAM:** W3C SCXML 1.0 is a general-purpose, event-based state-machine execution environment (Recommendation, 2015-09-01). This draft is a smaller linear test-scenario profile; it does not claim SCXML conformance or replace SCXML. The broader workflows-and-navigation extension still requires the INCRAM ledger's full precedent and cross-check review. See the official [SCXML Recommendation](https://www.w3.org/TR/2015/REC-scxml-20150901/).
