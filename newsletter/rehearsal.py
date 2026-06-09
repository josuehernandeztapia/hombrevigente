"""Pulso Vigente — ensayo del pipeline completo (shadow / post-mortem).

Corre el flujo end-to-end SIN publicar: render, social pack, bridge export,
dry-run RAG. Escribe un informe post-mortem para revisar y finetunear.

Uso:
  python newsletter/rehearsal.py newsletter/issues/2026-06-001.md
  PULSO_MODE=shadow python newsletter/rehearsal.py --issue ...

Salida: newsletter/runs/<issue-stem>-postmortem.md (+ preview.html copia)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).parent
REPO = HERE.parent
RUNS = HERE / "runs"


def parse_issue(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError("sin frontmatter YAML")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def check_sources(body: str) -> list[dict]:
    blocks = []
    for m in re.finditer(r"##\s*[🟢🔬🤖🌍][^\n]+\n(.*?)(?=\n##\s|\Z)", body, re.DOTALL):
        chunk = m.group(0)
        name = re.search(r"##\s*[🟢🔬🤖🌍]\s*([^\n]+)", chunk)
        title = name.group(1).strip() if name else "?"
        fuente = re.search(r"\*Fuente:\s*([^*]+)\*", chunk)
        has_pmid = bool(re.search(r"PMID|DOI|NEJM|ClinicalTrials|bioRxiv|medRxiv", chunk, re.I))
        blocks.append({
            "title": title,
            "fuente": fuente.group(1).strip() if fuente else "",
            "ok": bool(fuente) and has_pmid,
        })
    return blocks


def check_bridge(body: str) -> dict:
    if "Editorial bridge" not in body:
        return {"present": False, "rows_a": 0, "rows_c": 0, "rows_empty": 0}
    rows_a = rows_c = rows_empty = 0
    in_table = False
    for line in body.splitlines():
        if line.startswith("|") and "bloque" in line.lower():
            in_table = True
            continue
        if in_table and line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 6:
                continue
            bridge = cells[5].upper()
            if not any(cells[1:5]) and "A / C" in bridge:
                rows_empty += 1
            elif "A" in bridge and "C" not in bridge.replace("A / C", ""):
                rows_a += 1
            elif "C" in bridge:
                rows_c += 1
    return {"present": True, "rows_a": rows_a, "rows_c": rows_c, "rows_empty": rows_empty}


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd or REPO, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Ensayo shadow del pipeline Pulso")
    ap.add_argument("issue", type=Path, nargs="?", help="Ruta al issue")
    ap.add_argument("--issue", dest="issue_flag", type=Path, help="Alias de issue")
    args = ap.parse_args()
    issue_arg = args.issue_flag or args.issue
    if not issue_arg:
        ap.error("Indica la ruta al issue")

    issue = issue_arg if issue_arg.is_absolute() else REPO / issue_arg
    if not issue.exists():
        sys.exit(f"No existe: {issue}")

    mode = __import__("os").environ.get("PULSO_MODE", "shadow")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    RUNS.mkdir(exist_ok=True)
    stem = issue.stem
    report_path = RUNS / f"{stem}-postmortem.md"

    lines = [
        f"# Post-mortem Pulso — {stem}",
        f"",
        f"- **Modo:** `{mode}` (sin publicación real)",
        f"- **Generado:** {ts}",
        f"- **Issue:** `{issue.relative_to(REPO)}`",
        f"",
        f"## Checklist automático",
        f"",
    ]
    warnings: list[str] = []
    passes: list[str] = []
    meta: dict = {}
    body = ""
    bridge_export_out = ""

    # 1) Parse + fuentes
    try:
        meta, body = parse_issue(issue)
        passes.append("Frontmatter YAML parseable")
        if meta.get("subject"):
            passes.append(f"Subject: {meta['subject'][:60]}")
        else:
            warnings.append("Falta `subject` en frontmatter")
        if "**TLDR:**" in body or "TLDR" in body:
            passes.append("TLDR presente")
        else:
            warnings.append("Sin TLDR")

        blocks = check_sources(body)
        for b in blocks:
            if b["ok"]:
                passes.append(f"Fuente OK: {b['title'][:50]}")
            elif "slot recurrente" in b["title"].lower() or "ej." in body[:200].lower():
                warnings.append(f"Placeholder sin fuente: {b['title'][:50]}")
            else:
                warnings.append(f"Sin fuente verificada: {b['title'][:50]}")

        bridge = check_bridge(body)
        if bridge["present"]:
            passes.append(f"Tabla bridge: {bridge['rows_a']}×A, {bridge['rows_c']}×C, {bridge['rows_empty']} vacías")
            if bridge["rows_a"] == 0:
                warnings.append("Ningún bridge tipo A — RAG no se enriquecerá")
        else:
            warnings.append("Sin tabla Editorial bridge")
    except Exception as e:  # noqa: BLE001
        warnings.append(f"Parse issue: {e}")

    # 2) Render
    code, out = run_cmd([sys.executable, "newsletter/render.py", str(issue.relative_to(REPO))])
    preview_src = HERE / "preview.html"
    preview_dst = RUNS / f"{stem}-preview.html"
    if code == 0 and preview_src.exists():
        preview_dst.write_text(preview_src.read_text(encoding="utf-8"), encoding="utf-8")
        passes.append(f"Render OK → `{preview_dst.relative_to(REPO)}`")
    else:
        warnings.append(f"Render falló: {out[:200]}")

    # 3) Social pack
    code, out = run_cmd([sys.executable, "newsletter/social.py", str(issue.relative_to(REPO))])
    numero = str(meta.get("numero", stem.split("-")[-1])).zfill(3)
    social_dir = HERE / "social" / numero
    if code == 0 and social_dir.exists():
        n = len(list(social_dir.glob("*.md")))
        passes.append(f"Social pack: {n} archivos en `social/{numero}/`")
    else:
        warnings.append(f"Social pack: {out[:150]}")

    # 4) Bridge export dry-run
    code, bridge_export_out = run_cmd([
        sys.executable, "newsletter/bridge_export.py",
        "--issue", str(issue.relative_to(REPO)), "--dry-run",
    ])
    if code == 0:
        if bridge_export_out.strip() == "[]" or ": 0 bridge" in bridge_export_out:
            warnings.append("Bridge export: 0 entradas tipo A")
        else:
            passes.append("Bridge export dry-run OK (ver salida abajo)")
    else:
        warnings.append(f"Bridge export: {bridge_export_out[:150]}")

    # 5) RAG patch dry-run
    code, rag_out = run_cmd(
        [sys.executable, "scripts/process_editorial_bridge.py", "--dry-run"],
        cwd=REPO / "rag-bot",
    )
    if code == 0 and "would patch" in rag_out:
        passes.append("RAG patch dry-run: vería cambios en monografía")
    elif code == 0:
        passes.append("RAG patch dry-run: nada pendiente o ya aplicado")

    # 6) Send shadow (solo valida render, no API)
    if mode == "shadow":
        passes.append("Send: omitido (PULSO_MODE=shadow)")
    else:
        warnings.append("PULSO_MODE != shadow — revisa env antes de enviar")

    lines.append("### ✅ Pass")
    lines.extend(f"- {p}" for p in passes) if passes else lines.append("- _(ninguno)_")
    lines.append("")
    lines.append("### ⚠️ Revisar (post-mortem humano)")
    lines.extend(f"- {w}" for w in warnings) if warnings else lines.append("- _(ninguno)_")
    lines.extend([
        "",
        "## Salida bridge export (dry-run)",
        "```",
        bridge_export_out or "(no corrido)",
        "```",
        "",
        "## Próximo finetune",
        "",
        "1. Corrige warnings arriba en el issue.",
        "2. Vuelve a correr: `python newsletter/rehearsal.py <issue>`",
        "3. Cuando post-mortem limpio → merge a `main` (envío real) o dispatch con `PULSO_MODE=production`.",
        "",
        "## Modos",
        "",
        "| Modo | Envío email | Redes auto | Uso |",
        "|------|-------------|------------|-----|",
        "| `shadow` (default rehearsal) | No | No | Validar flujo + post-mortem |",
        "| `production` | Sí (merge main + secrets) | Sí (carril auto) | Operación real |",
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Post-mortem: {report_path.relative_to(REPO)}")
    print(f"Pass: {len(passes)} · Warnings: {len(warnings)}")
    if warnings:
        print("⚠️  Revisar warnings antes de merge a main.")
        sys.exit(1)
    print("✓ Ensayo shadow OK — listo para merge humano.")


if __name__ == "__main__":
    main()