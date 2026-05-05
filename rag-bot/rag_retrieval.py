"""
Sistema RAG (Retrieval Augmented Generation) para Knowledge Base Hombre Vigente

Características:
- Búsqueda semántica con embeddings OpenAI
- Retrieval desde Pinecone
- Generación de respuestas con GPT-4o-mini
- Metadata filtering (servicio, categoría, precio)
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

try:
    from openai import OpenAI
    from pinecone import Pinecone
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    print("❌ Instala dependencias: pip install openai pinecone-client rich")
    exit(1)

# Load environment
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("hombrevigente-kb")
console = Console()

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TOP_K = 5  # Number of chunks to retrieve


def create_query_embedding(query: str) -> List[float]:
    """Genera embedding para la query del usuario"""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding


def search_knowledge_base(
    query: str,
    top_k: int = TOP_K,
    filter_dict: Optional[Dict] = None
) -> List[Dict]:
    """
    Busca en Pinecone los chunks más relevantes

    Args:
        query: Pregunta del usuario
        top_k: Número de resultados a retornar
        filter_dict: Filtros metadata (ej: {"service_id": "01"})

    Returns:
        Lista de chunks con metadata y scores
    """
    # Generate query embedding
    query_embedding = create_query_embedding(query)

    # Search in Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )

    # Format results
    chunks = []
    for match in results.matches:
        chunks.append({
            "id": match.id,
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "service_name": match.metadata.get("service_name", "Unknown"),
            "service_id": match.metadata.get("service_id", ""),
            "section_title": match.metadata.get("section_title", ""),
            "categoria": match.metadata.get("categoria", ""),
            "precio_base": match.metadata.get("precio_base", 0),
        })

    return chunks


def generate_answer(query: str, context_chunks: List[Dict]) -> str:
    """
    Genera respuesta usando GPT-4o-mini con contexto de Knowledge Base

    Args:
        query: Pregunta del usuario
        context_chunks: Chunks relevantes del Knowledge Base

    Returns:
        Respuesta generada por el LLM
    """
    # Build context from chunks
    context = "\n\n---\n\n".join([
        f"**{chunk['service_name']}** - {chunk['section_title']}\n{chunk['text'][:3000]}"
        for chunk in context_chunks
    ])

    # System prompt
    system_prompt = """Eres un asistente experto en servicios estéticos y médicos para hombres de Hombre Vigente.

Tu objetivo es responder preguntas basándote en la información proporcionada del Knowledge Base.

Directrices:
- Responde de forma clara, profesional y directa
- Usa bullet points cuando sea apropiado
- Incluye precios cuando sean relevantes (formato: $X,XXX MXN)
- IMPORTANTE: Si la información está presente en el contexto (aunque sea en subsecciones o detalles), úsala para responder
- Si después de revisar TODO el contexto NO encuentras la información, solo entonces di "No tengo esa información específica"
- Usa lenguaje natural y accesible (evita exceso de términos médicos)
- Si mencionas múltiples servicios, compáralos brevemente
- Lee cuidadosamente TODO el contexto proporcionado, incluyendo subsecciones y detalles

Audiencia: Hombres 30-60 años, ejecutivos, interesados en verse mejor."""

    # User prompt with context
    user_prompt = f"""Contexto del Knowledge Base:

{context}

---

Pregunta del usuario: {query}

Responde basándote en el contexto anterior:"""

    # Call LLM
    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content


def rag_query(
    query: str,
    top_k: int = TOP_K,
    filter_dict: Optional[Dict] = None,
    verbose: bool = True
) -> Dict:
    """
    Query completo RAG: Retrieval + Generation

    Args:
        query: Pregunta del usuario
        top_k: Número de chunks a recuperar
        filter_dict: Filtros metadata
        verbose: Mostrar proceso detallado

    Returns:
        Dict con answer, sources, scores
    """
    if verbose:
        console.print(f"\n[bold cyan]🔍 Query:[/bold cyan] {query}")
        console.print("[dim]Buscando en Knowledge Base...[/dim]")

    # 1. Retrieve relevant chunks
    chunks = search_knowledge_base(query, top_k, filter_dict)

    if not chunks:
        return {
            "query": query,
            "answer": "No encontré información relevante en la Knowledge Base.",
            "sources": [],
            "scores": []
        }

    if verbose:
        console.print(f"[green]✓[/green] Encontrados {len(chunks)} chunks relevantes")
        console.print("\n[bold]📚 Fuentes utilizadas:[/bold]")
        for i, chunk in enumerate(chunks[:3], 1):
            console.print(f"  {i}. {chunk['service_name']} - {chunk['section_title']} (score: {chunk['score']:.3f})")

    # 2. Generate answer
    if verbose:
        console.print("\n[dim]Generando respuesta...[/dim]")

    answer = generate_answer(query, chunks)

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "service": chunk["service_name"],
                "section": chunk["section_title"],
                "score": chunk["score"]
            }
            for chunk in chunks
        ],
        "chunks_used": len(chunks)
    }


def interactive_mode():
    """Modo interactivo para hacer queries"""
    console.print(Panel.fit(
        "[bold cyan]🤖 RAG System - Hombre Vigente Knowledge Base[/bold cyan]\n"
        "Haz preguntas sobre servicios, precios, resultados, etc.\n"
        "[dim]Escribe 'salir' para terminar[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            query = console.input("\n[bold yellow]❓ Tu pregunta:[/bold yellow] ")

            if query.lower() in ['salir', 'exit', 'quit']:
                console.print("\n[green]👋 ¡Hasta luego![/green]")
                break

            if not query.strip():
                continue

            # Execute RAG query
            result = rag_query(query, verbose=True)

            # Display answer
            console.print("\n" + "="*70)
            console.print(Panel(
                Markdown(result["answer"]),
                title="[bold green]💬 Respuesta[/bold green]",
                border_style="green"
            ))

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrumpido por usuario[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error: {str(e)}[/red]")


if __name__ == "__main__":
    # Check if running in interactive mode
    import sys

    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        result = rag_query(query, verbose=True)
        console.print("\n" + "="*70)
        console.print(Panel(
            Markdown(result["answer"]),
            title="[bold green]💬 Respuesta[/bold green]",
            border_style="green"
        ))
    else:
        # Interactive mode
        interactive_mode()
