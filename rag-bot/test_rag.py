"""
Script de testing para el sistema RAG
Prueba diferentes tipos de queries y evalúa resultados
"""

import json
from pathlib import Path
from rag_retrieval import rag_query, console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


# Test queries organizadas por categoría
TEST_QUERIES = {
    "Información Básica": [
        "¿Qué es el HIFU?",
        "¿Cuánto dura el efecto del Botox?",
        "¿Qué servicios de grooming ofrecen?",
    ],

    "Pricing": [
        "¿Cuánto cuesta el Botox?",
        "¿Cuál es el precio del corte de pelo?",
        "¿Tienen paquetes o descuentos?",
    ],

    "Candidatos y Contraindicaciones": [
        "¿Soy candidato para HIFU si tengo 35 años?",
        "¿Puedo usar Botox si tomo anticoagulantes?",
        "¿Qué contraindicaciones tiene la blefaroplastia?",
    ],

    "Resultados y Timeline": [
        "¿Cuándo veo resultados del HIFU?",
        "¿Cuánto dura la recuperación de la bichectomía?",
        "¿Los resultados del PRP son permanentes?",
    ],

    "Comparaciones": [
        "¿Qué es mejor: HIFU o RF Microneedling?",
        "Diferencia entre Botox y Fillers",
        "¿Hilos PDO o Sculptra para flacidez?",
    ],

    "Procedimientos Específicos": [
        "¿Cómo es el procedimiento de la liposucción de papada?",
        "¿Qué pasos tiene el tratamiento de RF Microneedling?",
        "¿Cuántas sesiones necesito de PRP?",
    ],

    "Efectos Secundarios": [
        "¿Qué efectos secundarios tiene el Láser CO2?",
        "¿Duele el RF Microneedling?",
        "¿Riesgos de la blefaroplastia?",
    ],

    "Post-operatorio": [
        "¿Qué cuidados necesito después del HIFU?",
        "¿Puedo hacer ejercicio después de Botox?",
        "¿Cuándo puedo volver al trabajo después de blefaroplastia?",
    ],

    "Arquetipos/Target": [
        "¿Qué servicios recomiendan para ejecutivos?",
        "Servicios para hombres de 45 años con poco tiempo",
        "¿Qué tratamientos faciales masculinos tienen?",
    ],

    "Queries Complejas": [
        "Quiero verme más joven sin cirugía, ¿qué opciones tengo?",
        "Necesito algo para la papada y líneas de expresión, ¿qué me recomiendan?",
        "Plan completo de grooming mensual para ejecutivo",
    ],
}


def run_test_queries(save_results: bool = True):
    """Ejecuta todas las queries de prueba"""

    console.print(Panel.fit(
        "[bold cyan]🧪 Testing RAG System[/bold cyan]\n"
        f"Total queries: {sum(len(queries) for queries in TEST_QUERIES.values())}\n"
        f"Categorías: {len(TEST_QUERIES)}",
        border_style="cyan"
    ))

    all_results = {}

    for category, queries in TEST_QUERIES.items():
        console.print(f"\n[bold yellow]📋 {category}[/bold yellow]")
        console.print("=" * 70)

        category_results = []

        for i, query in enumerate(queries, 1):
            console.print(f"\n[cyan]{i}. Query:[/cyan] {query}")

            try:
                # Execute query
                result = rag_query(query, verbose=False)

                # Display results
                console.print(f"[green]✓ Chunks usados:[/green] {result['chunks_used']}")
                console.print(f"[green]✓ Servicios:[/green] {', '.join(set(s['service'] for s in result['sources'][:3]))}")

                # Show answer preview
                answer_preview = result['answer'][:150] + "..." if len(result['answer']) > 150 else result['answer']
                console.print(f"[dim]Respuesta: {answer_preview}[/dim]")

                # Store result
                category_results.append({
                    "query": query,
                    "answer": result['answer'],
                    "sources": result['sources'][:3],
                    "chunks_used": result['chunks_used']
                })

            except Exception as e:
                console.print(f"[red]❌ Error: {str(e)}[/red]")
                category_results.append({
                    "query": query,
                    "error": str(e)
                })

        all_results[category] = category_results

    # Save results
    if save_results:
        output_file = Path("test_results_rag.json")
        output_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
        console.print(f"\n[green]💾 Resultados guardados en: {output_file}[/green]")

    # Summary statistics
    display_summary(all_results)

    return all_results


def display_summary(results: dict):
    """Muestra resumen estadístico de los tests"""

    console.print("\n" + "="*70)
    console.print("[bold cyan]📊 RESUMEN DE TESTING[/bold cyan]")
    console.print("="*70)

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Categoría", style="yellow")
    table.add_column("Queries", justify="center")
    table.add_column("Exitosas", justify="center", style="green")
    table.add_column("Errores", justify="center", style="red")

    total_queries = 0
    total_success = 0
    total_errors = 0

    for category, category_results in results.items():
        queries_count = len(category_results)
        success_count = sum(1 for r in category_results if "error" not in r)
        error_count = sum(1 for r in category_results if "error" in r)

        table.add_row(
            category,
            str(queries_count),
            str(success_count),
            str(error_count)
        )

        total_queries += queries_count
        total_success += success_count
        total_errors += error_count

    # Add totals
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_queries}[/bold]",
        f"[bold]{total_success}[/bold]",
        f"[bold]{total_errors}[/bold]",
        style="bold"
    )

    console.print(table)

    # Success rate
    success_rate = (total_success / total_queries * 100) if total_queries > 0 else 0
    console.print(f"\n[bold green]✓ Tasa de éxito: {success_rate:.1f}%[/bold green]")


def test_specific_services():
    """Test queries específicas por servicio"""

    console.print("\n[bold cyan]🎯 Testing por Servicio Específico[/bold cyan]")

    service_queries = {
        "HIFU": "Explícame todo sobre HIFU: qué es, precio, resultados y candidatos",
        "Botox": "Quiero saber sobre Botox: duración, zonas, precio y efectos",
        "Corte Pelo": "Información completa sobre corte de pelo: estilos, precio, frecuencia",
        "Blefaroplastia": "Detalles de blefaroplastia: procedimiento, recuperación, riesgos",
    }

    for service, query in service_queries.items():
        console.print(f"\n[yellow]▶ {service}[/yellow]")
        result = rag_query(query, top_k=3, verbose=False)

        console.print(Panel(
            Markdown(result["answer"]),
            title=f"[bold]{service}[/bold]",
            border_style="green"
        ))


def test_filtering():
    """Test con filtros de metadata"""

    console.print("\n[bold cyan]🔍 Testing con Filtros[/bold cyan]")

    # Test 1: Solo servicios Fase 1
    console.print("\n[yellow]Test: Servicios Fase 1[/yellow]")
    result = rag_query(
        "¿Qué servicios tienen?",
        filter_dict={"fase": "Fase 1"},
        verbose=False
    )
    console.print(f"Chunks encontrados: {result['chunks_used']}")

    # Test 2: Servicios de Grooming
    console.print("\n[yellow]Test: Servicios Grooming[/yellow]")
    result = rag_query(
        "¿Qué servicios de grooming ofrecen?",
        filter_dict={"categoria": "Grooming y Wellness"},
        verbose=False
    )
    console.print(f"Chunks encontrados: {result['chunks_used']}")


if __name__ == "__main__":
    import sys

    if "--full" in sys.argv:
        # Run all tests
        run_test_queries(save_results=True)
        test_specific_services()
        test_filtering()
    elif "--services" in sys.argv:
        # Test specific services only
        test_specific_services()
    elif "--filter" in sys.argv:
        # Test filtering only
        test_filtering()
    else:
        # Default: run basic test queries
        run_test_queries(save_results=True)

    console.print("\n[green]✓ Testing completado[/green]")
