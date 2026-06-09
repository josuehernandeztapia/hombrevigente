#!/usr/bin/env python3
"""
Golden trajectories HV — multi-paso sin Caso #0 humano.

  python trajectory_runner.py              # todas P0
  python trajectory_runner.py --id TRAJ-HV-006
  python trajectory_runner.py --all          # P0 + P1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

from beta_state import derive_state_from_intake
from rag_retrieval_local import rag_query_local

TRAJ_PATH = _ROOT / "data" / "trajectories-hv.json"


def load_trajectories() -> List[Dict]:
    data = json.loads(TRAJ_PATH.read_text(encoding="utf-8"))
    return data["trajectories"]


def _load_intake(traj: Dict) -> Tuple[Dict, str | None]:
    if traj.get("intake_inline"):
        intake = traj["intake_inline"]
        bid = traj.get("beta_id")
        if not bid:
            from beta_state import beta_id_from_intake

            bid = beta_id_from_intake(intake)
        return intake, bid

    fixture = _ROOT / traj["intake_fixture"]
    intake = json.loads(fixture.read_text(encoding="utf-8"))
    return intake, traj.get("beta_id")


def _run_route(intake: Dict, expect: Dict) -> Tuple[bool, str]:
    from scripts.mvp0_lib import route_profile

    route = route_profile(intake)
    for key, val in expect.items():
        if key == "entrega_not":
            if route.get("entrega") == val:
                return False, f"route.entrega should not be {val!r}"
            continue
        if route.get(key) != val:
            return False, f"route.{key}={route.get(key)!r} expected {val!r}"
    return True, "route OK"


def _run_beta_state(intake: Dict, expect: Dict) -> Tuple[bool, str]:
    state = derive_state_from_intake(intake)
    if expect.get("perfil") and state.perfil != expect["perfil"]:
        return False, f"perfil={state.perfil!r}"
    if expect.get("phase") and state.phase != expect["phase"]:
        return False, f"phase={state.phase!r}"
    if expect.get("slot_protocolo_entregado") is not None:
        got = state.slots.get("protocolo_entregado")
        if got != expect["slot_protocolo_entregado"]:
            return False, f"slot protocolo_entregado={got!r}"
    if expect.get("slot_labs_parseados") is not None:
        got = state.slots.get("labs_parseados")
        if got != expect["slot_labs_parseados"]:
            return False, f"slot labs_parseados={got!r}"
    if expect.get("slot_clearance_medica") is not None:
        got = state.slots.get("clearance_medica")
        if got != expect["slot_clearance_medica"]:
            return False, f"slot clearance_medica={got!r}"
    if expect.get("slot_tally_completo") is not None:
        got = state.slots.get("tally_completo")
        if got != expect["slot_tally_completo"]:
            return False, f"slot tally_completo={got!r}"
    if expect.get("next_action_contains"):
        needle = expect["next_action_contains"].lower()
        if needle not in (state.next_action or "").lower():
            return False, f"next_action missing {needle!r}"
    moat = intake.get("data_moat") or {}
    if expect.get("labs_parse_json_contains"):
        path = moat.get("labs_parse_json") or ""
        needle = expect["labs_parse_json_contains"]
        if needle not in path:
            return False, f"labs_parse_json={path!r} missing {needle!r}"
    if expect.get("labs_parse_json_absent") and moat.get("labs_parse_json"):
        return False, f"labs_parse_json should be absent, got {moat['labs_parse_json']!r}"
    return True, f"phase={state.phase} next={state.next_action[:50]}…"


def _resolve_labs_path(traj: Dict, step: Dict) -> Path:
    rel = step.get("labs_fixture") or traj.get("labs_fixture")
    if not rel:
        raise ValueError("labs_fixture required for labs step")
    return _ROOT / rel


def _run_labs_validate(traj: Dict, step: Dict) -> Tuple[bool, str]:
    from scripts.labs_intake_manual import validate_labs_payload

    path = _resolve_labs_path(traj, step)
    if not path.exists():
        return False, f"labs fixture missing: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_labs_payload(data)
    if errors:
        return False, "; ".join(errors[:3])

    exp = step.get("expect") or {}
    n = len(data.get("biomarkers") or [])
    if exp.get("min_biomarkers") and n < exp["min_biomarkers"]:
        return False, f"biomarkers={n} < {exp['min_biomarkers']}"
    if exp.get("has_patient") and not (data.get("patient") or {}).get("name"):
        return False, "patient.name missing"
    return True, f"OK · {n} biomarcadores · {path.name}"


def _run_labs_merge(intake: Dict, traj: Dict, step: Dict) -> Tuple[Dict, bool, str]:
    from scripts.mvp0_lib import merge_labs_into_intake

    path = _resolve_labs_path(traj, step)
    merged = merge_labs_into_intake(intake, path, root=_ROOT)
    moat = merged.get("data_moat") or {}
    if not moat.get("labs_parse_json"):
        return intake, False, "labs_parse_json not set"
    exp = step.get("expect") or {}
    if exp.get("labs_parse_json_contains"):
        needle = exp["labs_parse_json_contains"]
        if needle not in moat["labs_parse_json"]:
            return intake, False, f"path {moat['labs_parse_json']!r} missing {needle!r}"
    return merged, True, f"merged → {moat['labs_parse_json']}"


def _deep_patch(target: Dict, patch: Dict) -> Dict:
    out = json.loads(json.dumps(target))
    for key, val in patch.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = {**out[key], **val}
        else:
            out[key] = val
    return out


def _run_intake_assert(intake: Dict, expect: Dict) -> Tuple[bool, str]:
    ident = intake.get("identity") or {}
    meta = intake.get("meta") or {}
    if expect.get("nombre_equals") and ident.get("nombre") != expect["nombre_equals"]:
        return False, f"nombre={ident.get('nombre')!r}"
    if expect.get("tally_response_id") and meta.get("tally_response_id") != expect["tally_response_id"]:
        return False, f"tally_response_id={meta.get('tally_response_id')!r}"
    if expect.get("has_objetivos") and not intake.get("objetivos"):
        return False, "objetivos missing"
    if expect.get("has_screening") and not intake.get("screening"):
        return False, "screening missing"
    if expect.get("ciudad_equals") and ident.get("ciudad") != expect["ciudad_equals"]:
        return False, f"ciudad={ident.get('ciudad')!r}"
    if expect.get("objetivo_principal_equals"):
        got = (intake.get("objetivos") or {}).get("principal")
        if got != expect["objetivo_principal_equals"]:
            return False, f"objetivos.principal={got!r}"
    if expect.get("lifestyle_field_equals"):
        for key, val in expect["lifestyle_field_equals"].items():
            got = (intake.get("lifestyle") or {}).get(key)
            if got != val:
                return False, f"lifestyle.{key}={got!r}"
    return True, "intake OK"


def _run_intake_patch(intake: Dict, step: Dict) -> Tuple[Dict, bool, str]:
    patch = step.get("patch") or {}
    if not patch:
        return intake, False, "empty patch"
    merged = _deep_patch(intake, patch)
    return merged, True, f"patched keys: {', '.join(patch.keys())}"


def _run_set_last_active(step: Dict, default_beta_id: str | None) -> Tuple[bool, str]:
    """Fase 4: fuerza last_active_at en el estado persistido para probar reentry temporal."""
    from beta_state import load_state, save_state
    from pathlib import Path
    import json
    import os

    beta_id = step.get("beta_id") or default_beta_id
    if not beta_id:
        return False, "beta_id required for set_last_active"

    ts = step.get("last_active_at") or step.get("ts")
    if not ts:
        return False, "last_active_at (or ts) required"

    # Cargar estado actual (debe existir por pasos previos)
    state = load_state(beta_id)
    if state is None:
        # Crear estado mínimo para poder forzar last_active (útil en tests de reentry)
        from beta_state import BetaState, _utc_now
        state = BetaState(
            beta_id=beta_id,
            phase="onboarding",
            next_action="test",
            slots={},
        )
        state.last_active_at = _utc_now()  # will be overwritten
        # persist minimal
        from beta_state import save_state
        save_state(state)

    # Forzamos el timestamp viejo en el archivo directamente (simula paso del tiempo)
    states_dir = Path(os.environ.get("HV_BETA_STATES_DIR", "data/beta_states"))
    dest = states_dir / f"{beta_id}.json"
    state_dict = state.to_dict()
    state_dict["last_active_at"] = ts
    dest.write_text(json.dumps(state_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    return True, f"last_active_at forced to {ts} for {beta_id}"


def _run_rag(step: Dict, intake: Dict, default_beta_id: str | None) -> Tuple[bool, str]:
    beta_id = step.get("beta_id") or default_beta_id
    use_frozen = step.get("use_frozen", beta_id is not None)
    result = rag_query_local(
        step["question"],
        intake=intake if use_frozen else None,
        beta_id=beta_id,
        use_llm=False,
        log=False,
        channel="trajectory",
    )
    exp = step.get("expect") or {}

    if exp.get("gate_path") and result.get("gate_path") != exp["gate_path"]:
        return False, f"gate_path={result.get('gate_path')!r}"
    if exp.get("gate_path_not") and result.get("gate_path") == exp["gate_path_not"]:
        return False, f"gate_path should not be {exp['gate_path_not']!r}"
    if exp.get("gate") and result.get("gate") != exp["gate"]:
        return False, f"gate={result.get('gate')!r} expected {exp['gate']!r}"
    if exp.get("has_frozen_context") and not result.get("frozen_context"):
        return False, "missing frozen_context"

    return True, f"path={result.get('gate_path')} gate={result.get('gate', '-')}"


def run_trajectory(traj: Dict, *, states_dir: Path | None = None) -> Tuple[bool, List[Dict]]:
    intake, beta_id = _load_intake(traj)
    results: List[Dict] = []
    all_ok = True

    prev_states = os.environ.get("HV_BETA_STATES_DIR")
    if states_dir:
        os.environ["HV_BETA_STATES_DIR"] = str(states_dir)

    try:
        for step in traj["steps"]:
            stype = step["type"]
            if stype == "route":
                ok, detail = _run_route(intake, step.get("expect") or {})
            elif stype == "beta_state":
                ok, detail = _run_beta_state(intake, step.get("expect") or {})
            elif stype == "rag":
                ok, detail = _run_rag(step, intake, beta_id)
            elif stype == "labs_validate":
                ok, detail = _run_labs_validate(traj, step)
            elif stype == "labs_merge":
                intake, ok, detail = _run_labs_merge(intake, traj, step)
            elif stype == "intake_patch":
                intake, ok, detail = _run_intake_patch(intake, step)
            elif stype == "intake_assert":
                ok, detail = _run_intake_assert(intake, step.get("expect") or {})
            elif stype == "set_last_active":
                ok, detail = _run_set_last_active(step, beta_id)
            else:
                ok, detail = False, f"unknown step type {stype}"

            results.append({"step": step["id"], "ok": ok, "detail": detail})
            if not ok:
                all_ok = False
    finally:
        if states_dir is not None:
            if prev_states is None:
                os.environ.pop("HV_BETA_STATES_DIR", None)
            else:
                os.environ["HV_BETA_STATES_DIR"] = prev_states

    return all_ok, results


def main() -> int:
    parser = argparse.ArgumentParser(description="HV golden trajectories")
    parser.add_argument("--id", help="Una trajectory por ID")
    parser.add_argument("--all", action="store_true", help="Incluir P1 además de P0")
    args = parser.parse_args()

    trajs = load_trajectories()
    if args.id:
        trajs = [t for t in trajs if t["id"] == args.id]
        if not trajs:
            print(f"ID {args.id} not found", file=sys.stderr)
            return 1
    elif not args.all:
        trajs = [t for t in trajs if t.get("criticality") == "P0"]

    passed = failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        states_dir = Path(tmp)
        for traj in trajs:
            ok, steps = run_trajectory(traj, states_dir=states_dir)
            head = "PASS" if ok else "FAIL"
            print(f"\n[{head}] {traj['id']} — {traj['title']}")
            for s in steps:
                mark = "✓" if s["ok"] else "✗"
                print(f"  {mark} {s['step']}: {s['detail']}")
            if ok:
                passed += 1
            else:
                failed += 1

    total = passed + failed
    print(f"\nTrajectories: {passed}/{total} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())