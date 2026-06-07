"""
Script para generar embeddings de la Knowledge Base y almacenarlos en Pinecone

Características:
- Chunking inteligente por secciones markdown
- Embeddings con OpenAI text-embedding-3-small
- Almacenamiento en Pinecone con metadata rico
- Progress tracking y manejo de errores
"""

import os
import re
import time
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import json
from dotenv import load_dotenv

# Imports
try:
    from openai import OpenAI
    from pinecone import Pinecone, ServerlessSpec
    from tqdm import tqdm
except ImportError:
    print("❌ Falta instalar dependencias. Ejecuta:")
    print("pip install openai pinecone-client tqdm python-dotenv")
    exit(1)

# Load environment variables
load_dotenv()

# Configuración
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "hombrevigente-kb"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
SERVICIOS_DIR = Path("knowledge_base/servicios")
LONGEVITY_DIR = Path("knowledge_base/longevity")

# Validate API keys
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY no encontrado en .env")
if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY no encontrado en .env")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)


def extract_metadata_from_header(content: str, kb_type: str = "servicios") -> Dict:
    """Extrae metadata del header del documento"""
    metadata = {
        "categoria": "Unknown",
        "fase": "Unknown",
        "precio_base": 0,
        "duracion": "Unknown",
        "frecuencia": "Unknown",
        "kb_type": kb_type,
        "avenida_hv": "Unknown",
        "evidencia": "Unknown",
    }

    if match := re.search(r'\*\*Categoría\*\*:\s*(.+)', content):
        metadata["categoria"] = match.group(1).strip()
    if match := re.search(r'\*\*Fase\*\*:\s*(.+)', content):
        metadata["fase"] = match.group(1).strip()
    if match := re.search(r'\*\*Avenida HV\*\*:\s*(.+)', content):
        metadata["avenida_hv"] = match.group(1).strip()
        metadata["fase"] = metadata["avenida_hv"]
    if match := re.search(r'\*\*Evidencia predominante\*\*:\s*(.+)', content):
        metadata["evidencia"] = match.group(1).strip()
    if match := re.search(r'\*\*Precio base\*\*:\s*\$?([\d,]+)', content):
        precio_str = match.group(1).replace(',', '')
        metadata["precio_base"] = int(precio_str)
    if match := re.search(r'\*\*Duración\*\*:\s*(.+)', content):
        metadata["duracion"] = match.group(1).strip()
    if match := re.search(r'\*\*Frecuencia\*\*:\s*(.+)', content):
        metadata["frecuencia"] = match.group(1).strip()

    return metadata


def chunk_by_sections(content: str, service_id: str, service_name: str) -> List[Dict]:
    """
    Divide el contenido en chunks por secciones markdown (##)
    Mantiene el contexto del servicio en cada chunk
    """
    chunks = []

    # Extract header metadata
    header_end = content.find('\n---\n')
    if header_end == -1:
        header_end = content.find('\n##')

    header = content[:header_end] if header_end > 0 else ""
    body = content[header_end:] if header_end > 0 else content

    # Get service metadata
    kb_type = "longevity" if "longevity" in service_id else "servicios"
    service_metadata = extract_metadata_from_header(header, kb_type=kb_type)

    # Split by sections (##)
    sections = re.split(r'\n## ', body)

    for idx, section in enumerate(sections):
        if not section.strip():
            continue

        # Add ## back if not first section
        if idx > 0:
            section = "## " + section

        # Extract section title
        section_lines = section.split('\n', 1)
        section_title = section_lines[0].replace('## ', '').strip()
        section_content = section_lines[1] if len(section_lines) > 1 else ""

        # Skip very short sections (likely headers only)
        if len(section_content.strip()) < 50:
            continue

        # Create chunk with rich metadata
        chunk = {
            "id": f"{service_id}_section_{idx}",
            "text": f"# {service_name}\n\n{section}",
            "metadata": {
                "service_id": service_id,
                "service_name": service_name,
                "section_title": section_title,
                "section_index": idx,
                "chunk_type": "section",
                **service_metadata
            }
        }

        chunks.append(chunk)

    return chunks


def load_documents_from_dir(base_dir: Path, kb_type: str, id_prefix: str = "") -> List[Dict]:
    """Carga documentos markdown numerados desde un directorio"""
    documents = []
    doc_files = sorted(base_dir.glob("[0-9][0-9]_*.md"))

    print(f"📁 {kb_type}: {len(doc_files)} archivos en {base_dir}")

    for file_path in doc_files:
        filename = file_path.stem
        match = re.match(r'(\d+)_(.+)', filename)
        if not match:
            print(f"⚠️  Saltando archivo con formato incorrecto: {filename}")
            continue

        doc_num = match.group(1)
        doc_slug = match.group(2)
        doc_id = f"{id_prefix}{doc_num}" if id_prefix else doc_num

        try:
            content = file_path.read_text(encoding='utf-8')
            first_line = content.split('\n')[0]
            doc_name = first_line.replace('#', '').strip()

            documents.append({
                "id": doc_id,
                "name": doc_name,
                "slug": doc_slug,
                "content": content,
                "file_path": str(file_path),
                "kb_type": kb_type,
            })

        except Exception as e:
            print(f"❌ Error leyendo {filename}: {e}")
            continue

    return documents


def load_services(source: str = "servicios") -> List[Dict]:
    """Carga documentos según fuente: servicios, longevity o all"""
    services = []
    if source in ("servicios", "all"):
        services.extend(load_documents_from_dir(SERVICIOS_DIR, "servicios"))
    if source in ("longevity", "all"):
        services.extend(load_documents_from_dir(LONGEVITY_DIR, "longevity", id_prefix="longevity_"))
    return services


def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Genera embeddings en batches para optimizar API calls"""
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch,
                encoding_format="float"
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

            # Rate limiting protection
            if i + batch_size < len(texts):
                time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error en batch {i//batch_size}: {e}")
            # Retry once
            time.sleep(2)
            try:
                response = openai_client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch,
                    encoding_format="float"
                )
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)
            except Exception as e2:
                print(f"❌ Error en retry: {e2}")
                # Add empty embeddings to maintain alignment
                all_embeddings.extend([[0.0] * EMBEDDING_DIMENSIONS] * len(batch))

    return all_embeddings


def upsert_to_pinecone(index, chunks: List[Dict], embeddings: List[List[float]]):
    """Almacena chunks y embeddings en Pinecone"""
    vectors = []

    for chunk, embedding in zip(chunks, embeddings):
        # Pinecone metadata must be flat and serializable
        metadata = {
            "text": chunk["text"][:1000],  # Truncate text for metadata (Pinecone limit)
            "service_id": chunk["metadata"]["service_id"],
            "service_name": chunk["metadata"]["service_name"],
            "section_title": chunk["metadata"]["section_title"],
            "section_index": chunk["metadata"]["section_index"],
            "categoria": chunk["metadata"]["categoria"],
            "fase": chunk["metadata"]["fase"],
            "precio_base": chunk["metadata"]["precio_base"],
            "duracion": chunk["metadata"]["duracion"],
            "frecuencia": chunk["metadata"]["frecuencia"],
            "kb_type": chunk["metadata"].get("kb_type", "servicios"),
            "avenida_hv": chunk["metadata"].get("avenida_hv", "Unknown"),
            "evidencia": chunk["metadata"].get("evidencia", "Unknown"),
        }

        vectors.append({
            "id": chunk["id"],
            "values": embedding,
            "metadata": metadata
        })

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
        except Exception as e:
            print(f"❌ Error en upsert batch {i//batch_size}: {e}")
            time.sleep(2)
            try:
                index.upsert(vectors=batch)
            except Exception as e2:
                print(f"❌ Error en retry upsert: {e2}")


def main():
    parser = argparse.ArgumentParser(description="Generar embeddings para Knowledge Base HV")
    parser.add_argument(
        "--source",
        choices=["servicios", "longevity", "all"],
        default="servicios",
        help="KB a procesar (default: servicios). Usar 'longevity' para SSOT longevidad.",
    )
    args = parser.parse_args()

    print("🚀 Iniciando generación de embeddings para Knowledge Base")
    print(f"   Fuente: {args.source}")
    print("=" * 70)

    # 1. Load services
    print("\n📚 Paso 1: Cargando documentos...")
    services = load_services(source=args.source)
    print(f"✅ Cargados {len(services)} servicios")

    # 2. Create chunks
    print("\n✂️  Paso 2: Creando chunks por secciones...")
    all_chunks = []
    for service in services:
        chunks = chunk_by_sections(
            service["content"],
            service["id"],
            service["name"]
        )
        all_chunks.extend(chunks)
        print(f"  • {service['name']}: {len(chunks)} chunks")

    print(f"\n✅ Total chunks generados: {len(all_chunks)}")

    # 3. Generate embeddings
    print("\n🤖 Paso 3: Generando embeddings con OpenAI...")
    print(f"   Modelo: {EMBEDDING_MODEL}")
    print(f"   Dimensiones: {EMBEDDING_DIMENSIONS}")

    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = []

    # Process in batches with progress bar
    batch_size = 100
    with tqdm(total=len(texts), desc="Generando embeddings") as pbar:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = generate_embeddings_batch(batch, batch_size=len(batch))
            embeddings.extend(batch_embeddings)
            pbar.update(len(batch))

    print(f"✅ Generados {len(embeddings)} embeddings")

    # 4. Connect to Pinecone
    print(f"\n📌 Paso 4: Conectando a Pinecone index '{INDEX_NAME}'...")
    try:
        index = pc.Index(INDEX_NAME)
        stats = index.describe_index_stats()
        print(f"✅ Conectado a Pinecone")
        print(f"   Vectores actuales en index: {stats.total_vector_count}")
    except Exception as e:
        print(f"❌ Error conectando a Pinecone: {e}")
        return

    # 5. Upsert to Pinecone
    print("\n💾 Paso 5: Almacenando embeddings en Pinecone...")
    with tqdm(total=len(all_chunks), desc="Uploading to Pinecone") as pbar:
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            upsert_to_pinecone(index, batch_chunks, batch_embeddings)
            pbar.update(len(batch_chunks))

    # 6. Verify upload
    print("\n🔍 Paso 6: Verificando upload...")
    time.sleep(2)  # Wait for indexing
    stats = index.describe_index_stats()
    print(f"✅ Vectores en Pinecone: {stats.total_vector_count}")

    # 7. Save metadata locally
    print("\n💾 Paso 7: Guardando metadata local...")
    metadata_file = Path("knowledge_base/embeddings_metadata.json")
    metadata = {
        "source": args.source,
        "total_services": len(services),
        "total_chunks": len(all_chunks),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimensions": EMBEDDING_DIMENSIONS,
        "index_name": INDEX_NAME,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": [
            {
                "id": s["id"],
                "name": s["name"],
                "chunks": len([c for c in all_chunks if c["metadata"]["service_id"] == s["id"]])
            }
            for s in services
        ]
    }

    metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    print(f"✅ Metadata guardada en: {metadata_file}")

    # Summary
    print("\n" + "=" * 70)
    print("🎉 PROCESO COMPLETADO")
    print("=" * 70)
    print(f"📊 Resumen:")
    print(f"   • Servicios procesados: {len(services)}")
    print(f"   • Chunks generados: {len(all_chunks)}")
    print(f"   • Embeddings creados: {len(embeddings)}")
    print(f"   • Vectores en Pinecone: {stats.total_vector_count}")
    print(f"   • Index name: {INDEX_NAME}")
    print(f"   • Model: {EMBEDDING_MODEL}")
    print("\n✅ Knowledge Base lista para RAG retrieval!")


if __name__ == "__main__":
    main()
