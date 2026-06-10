# Recovered source (G6/b)

These modules existed only as cpython-3.11 bytecode (`__pycache__/*.pyc`); the
original `.py` sources were lost. This directory holds recovery attempts.

## Tooling
- **pycdc (Decompyle++)** — the only decompiler that targets Python 3.11. Built
  from source (`github.com/zrax/pycdc`). It recovers docstrings, imports,
  signatures, and many function bodies, but **truncates on 3.11 constructs it
  can't model**, so its raw output usually does not compile.
- **marshal + dis** — bytecode disassembly (always works). Used to reconstruct
  control flow and exact constants where pycdc gave up.

## Status

| File | Status | Notes |
|------|--------|-------|
| `signal_detector.py` | ✅ **Full, compiles, tested** | Reconstructed from bytecode (marshal+dis). All thresholds (168/72/120/240/96h, progress<0.4), signal types, severities and context shapes are verbatim from `co_consts`. Functionally verified against synthetic states. The two original hard deps (`state_persistence.list_all_betas`, `traces.*`) are **guarded** so it imports/runs standalone. Review before wiring to the live path. |
| `feature_flags.py.partial` | ⚠️ Partial | Docstring + signatures only; bodies not recovered. Small enough to rewrite from the docstring contract (`is_enabled`, `list_active_flags`, env `HV_FEATURE_*`, default ON). |
| `reentry.py.partial` | ⚠️ Partial | TRAJ-HV-010 reentry bands. Note: the live bands already exist inline in `action_handler._compute_resume_message`. |
| `traces.py.partial` | ⚠️ Partial | `build_turn_payload` / `persist_turn_trace`. Superseded in part by `state_persistence.log_trace` (G3) on `hv_agent_traces`. |
| `state_manager.py.partial` | ⚠️ Partial | Largest; superseded by `state_persistence.py` (current SSOT). |
| `beta_state.py.partial` | ⚠️ Partial | Superseded by `state_persistence.py`. |

## Recommendation
Only `signal_detector` has unique, non-superseded logic worth re-adopting (it is
the input layer the proactive loop currently fakes). The rest are either partial
or already replaced by the current `state_persistence.py` / `action_handler.py`.
To fully recover a `.partial`, disassemble the target with
`python -m dis` on its code object (see how `signal_detector.py` was rebuilt) and
reconstruct by hand — automatic 3.11 decompilation is not reliable enough.
