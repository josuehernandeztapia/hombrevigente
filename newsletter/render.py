"""Renderiza un número (.md con frontmatter) a HTML usando templates/email.html."""
from pathlib import Path
import re
import markdown
import yaml
from jinja2 import Template

HERE = Path(__file__).parent
TEMPLATE = HERE / "templates" / "email.html"


def parse_issue(md_path: Path) -> dict:
    raw = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"{md_path} no tiene frontmatter YAML (---).")
    meta = yaml.safe_load(m.group(1)) or {}
    body_md = m.group(2).strip()
    meta["body_html"] = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
    return meta


def render(md_path: Path) -> dict:
    meta = parse_issue(md_path)
    tpl = Template(TEMPLATE.read_text(encoding="utf-8"))
    html = tpl.render(
        subject=meta.get("subject", "Pulso Vigente"),
        preheader=meta.get("preheader", ""),
        numero=meta.get("numero", ""),
        body_html=meta["body_html"],
    )
    return {
        "subject": meta.get("subject", "Pulso Vigente"),
        "audiencia": meta.get("audiencia", "plus"),
        "html": html,
    }


if __name__ == "__main__":
    import sys
    out = render(Path(sys.argv[1]))
    preview = HERE / "preview.html"
    preview.write_text(out["html"], encoding="utf-8")
    print(f"Preview escrito en {preview} ·", out["subject"])
