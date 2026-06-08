"""
Carga y chunking del Knowledge Base — sin Pinecone ni OpenAI.
Compartido por embed_kb_local.py y rag_retrieval_local.py.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

SERVICIOS_DIR = Path("knowledge_base/servicios")
LONGEVITY_DIR = Path("knowledge_base/longevity")

TIER_WEIGHTS = {"E1": 0.85, "E2": 0.70, "E3": 0.80, "E4": 0.95, "E5": 0.90, "E0": 0.30}
CONFIDENCE_WEIGHTS = {"alta": 0.95, "media": 0.75, "baja": 0.50}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# Calibración retrieval — tunable sin redeploy (patrón CMU PARTES_MERCADO_*)
COSINE_HIGH = _env_float("HV_COSINE_HIGH", 0.70)
COSINE_MIN = _env_float("HV_COSINE_MIN", 0.55)
SCORE_COSINE_WEIGHT = _env_float("HV_SCORE_COSINE_WEIGHT", 0.7)
SCORE_META_WEIGHT = _env_float("HV_SCORE_META_WEIGHT", 0.3)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_yaml_field(content: str, field: str) -> Optional[str]:
    if match := re.search(rf"^{re.escape(field)}:\s*(.+)$", content, re.MULTILINE):
        return match.group(1).strip().strip('"').strip("'")
    return None


def _normalize_avenida(raw: str) -> str:
    raw = raw.lower()
    if "1" in raw and "2" in raw:
        return "1-2"
    if "2" in raw:
        return "2"
    if "1" in raw:
        return "1"
    return "unknown"


def _parse_tier(text: str, header: str) -> str:
    for src in (header, text[:800]):
        if match := re.search(r"\*\*Evidencia predominante\*\*:\s*([Ee][0-5])", src):
            return match.group(1).upper()
        if match := re.search(r"\(E([0-5])\)", src):
            return f"E{match.group(1)}"
    return "unknown"


def extract_metadata(content: str, kb_type: str, doc_subtype: str = "monografia") -> Dict:
    header_end = content.find("\n---\n")
    if header_end == -1:
        header_end = content.find("\n##")
    header = content[:header_end] if header_end > 0 else content[:1200]

    meta: Dict = {
        "kb_type": kb_type,
        "doc_subtype": doc_subtype,
        "categoria": "Unknown",
        "avenida_hv": "unknown",
        "evidencia_tier": _parse_tier(content, header),
        "precio_base": 0,
        "confianza": "unknown",
        "flag_seguridad": "ninguno",
        "tarjeta_id": "",
        "has_falta_fuente": "[FALTA FUENTE]" in content,
    }

    if match := re.search(r"\*\*Categoría\*\*:\s*(.+)", header):
        meta["categoria"] = match.group(1).strip()
    if match := re.search(r"\*\*Avenida HV\*\*:\s*(.+)", header):
        meta["avenida_hv"] = _normalize_avenida(match.group(1))
    if match := re.search(r"\*\*Precio base\*\*:\s*\$?([\d,]+)", header):
        meta["precio_base"] = int(match.group(1).replace(",", ""))

    if doc_subtype == "tarjeta":
        meta["tarjeta_id"] = _extract_yaml_field(content, "id") or ""
        meta["categoria"] = _extract_yaml_field(content, "tipo") or meta["categoria"]
        meta["confianza"] = _extract_yaml_field(content, "confianza") or "unknown"
        meta["flag_seguridad"] = _extract_yaml_field(content, "flag_seguridad") or "ninguno"
        meta["avenida_hv"] = "1"
        if meta["flag_seguridad"] in ("alto-riesgo", "precaucion"):
            meta["evidencia_tier"] = "E3"

    return meta


def chunk_document(doc: Dict) -> List[Dict]:
    content = doc["content"]
    doc_id = doc["id"]
    doc_name = doc["name"]
    kb_type = doc["kb_type"]
    subtype = doc.get("doc_subtype", "monografia")

    if subtype == "tarjeta":
        meta = extract_metadata(content, kb_type, "tarjeta")
        text = content
        if meta["has_falta_fuente"]:
            return []
        return [{
            "id": f"{doc_id}_chunk_0",
            "text": text,
            "content_hash": content_hash(text),
            "metadata": {
                **meta,
                "service_id": doc_id,
                "service_name": doc_name,
                "section_title": "tarjeta",
                "section_index": 0,
                "chunk_type": "tarjeta",
                "source_file": doc.get("file_path", ""),
            },
        }]

    header_end = content.find("\n---\n")
    if header_end == -1:
        header_end = content.find("\n##")
    header = content[:header_end] if header_end > 0 else ""
    body = content[header_end:] if header_end > 0 else content
    base_meta = extract_metadata(content, kb_type, "monografia")

    audit_split = body.split("## Auditoría citas")
    body = audit_split[0]

    chunks: List[Dict] = []
    sections = re.split(r"\n## ", body)

    for idx, section in enumerate(sections):
        if not section.strip():
            continue
        if idx > 0:
            section = "## " + section
        lines = section.split("\n", 1)
        section_title = lines[0].replace("## ", "").strip()
        section_content = lines[1] if len(lines) > 1 else ""
        if len(section_content.strip()) < 50:
            continue

        text = f"# {doc_name}\n\n{section}"
        if "[FALTA FUENTE]" in text:
            continue

        chunks.append({
            "id": f"{doc_id}_section_{idx}",
            "text": text,
            "content_hash": content_hash(text),
            "metadata": {
                **base_meta,
                "service_id": doc_id,
                "service_name": doc_name,
                "section_title": section_title,
                "section_index": idx,
                "chunk_type": "section",
                "source_file": doc.get("file_path", ""),
            },
        })

    return chunks


def load_documents_from_dir(base_dir: Path, kb_type: str, id_prefix: str = "") -> List[Dict]:
    documents = []
    for file_path in sorted(base_dir.glob("[0-9][0-9]_*.md")):
        match = re.match(r"(\d+)_(.+)", file_path.stem)
        if not match:
            continue
        doc_num, doc_slug = match.group(1), match.group(2)
        doc_id = f"{id_prefix}{doc_num}" if id_prefix else doc_num
        content = file_path.read_text(encoding="utf-8")
        documents.append({
            "id": doc_id,
            "name": content.split("\n")[0].replace("#", "").strip(),
            "slug": doc_slug,
            "content": content,
            "file_path": str(file_path),
            "kb_type": kb_type,
            "doc_subtype": "monografia",
        })
    return documents


def load_tarjetas_from_dir(base_dir: Path, kb_type: str = "longevity") -> List[Dict]:
    documents = []
    for file_path in sorted(base_dir.glob("*.md")):
        if file_path.name.lower() == "readme.md":
            continue
        content = file_path.read_text(encoding="utf-8")
        tarjeta_id = _extract_yaml_field(content, "id") or file_path.stem
        documents.append({
            "id": f"longevity_tarjeta_{tarjeta_id}",
            "name": _extract_yaml_field(content, "nombre") or file_path.stem,
            "slug": tarjeta_id,
            "content": content,
            "file_path": str(file_path),
            "kb_type": kb_type,
            "doc_subtype": "tarjeta",
        })
    return documents


def load_faq_promoted(faq_path: Path) -> List[Dict]:
    """Carga entradas promovidas por Knowledge Loop (FAQ_PROMOTED.md)."""
    if not faq_path.exists():
        return []
    content = faq_path.read_text(encoding="utf-8")
    chunks: List[Dict] = []
    for idx, block in enumerate(re.split(r"\n## ", content)):
        if idx == 0 or "P:" not in block:
            continue
        route_match = re.search(r"\*\*Ruta KB:\*\*\s*(\w+)", block)
        kb_type = route_match.group(1) if route_match else "longevity"
        q_match = re.search(r"^P:\s*(.+)$", block, re.MULTILINE)
        r_match = re.search(r"^R:\s*(.+)$", block, re.MULTILINE)
        if not q_match or not r_match:
            continue
        text = f"P: {q_match.group(1).strip()}\nR: {r_match.group(1).strip()}"
        chunks.append({
            "id": f"faq_promoted_{idx}",
            "text": text,
            "content_hash": content_hash(text),
            "metadata": {
                "kb_type": kb_type,
                "doc_subtype": "faq_promoted",
                "categoria": "FAQ",
                "avenida_hv": "1",
                "evidencia_tier": "E3",
                "precio_base": 0,
                "confianza": "media",
                "flag_seguridad": "ninguno",
                "tarjeta_id": "",
                "has_falta_fuente": False,
                "service_id": f"faq_{idx}",
                "service_name": "FAQ Promovido",
                "section_title": q_match.group(1).strip()[:80],
                "section_index": idx,
                "chunk_type": "faq",
                "source_file": str(faq_path),
            },
        })
    return chunks


def load_all_chunks(source: str = "all", base_path: Optional[Path] = None) -> List[Dict]:
    root = base_path or Path(".")
    servicios_dir = root / SERVICIOS_DIR
    longevity_dir = root / LONGEVITY_DIR
    faq_path = root / "knowledge_base" / "FAQ_PROMOTED.md"
    chunks: List[Dict] = []

    if source in ("servicios", "all"):
        for doc in load_documents_from_dir(servicios_dir, "servicios"):
            chunks.extend(chunk_document(doc))

    if source in ("longevity", "all"):
        for doc in load_documents_from_dir(longevity_dir, "longevity", id_prefix="longevity_"):
            chunks.extend(chunk_document(doc))
        tarjetas_dir = longevity_dir / "tarjetas"
        if tarjetas_dir.is_dir():
            for doc in load_tarjetas_from_dir(tarjetas_dir):
                chunks.extend(chunk_document(doc))

    if source in ("servicios", "longevity", "all"):
        for faq_chunk in load_faq_promoted(faq_path):
            kb = faq_chunk["metadata"]["kb_type"]
            if source == "all" or source == kb:
                chunks.append(faq_chunk)

    return chunks