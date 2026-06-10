#!/usr/bin/env python3
"""
Test de Configuración - Hombre Vigente Demo
Valida que todas las variables de entorno estén correctamente configuradas
"""

from dotenv import load_dotenv
import os
import sys

# Cargar .env
load_dotenv()

def print_header(text):
    """Print header con estilo"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_var(name, value, required=True):
    """Print variable con formato y validación"""
    if value:
        # Ocultar parte sensible de secrets
        if any(secret in name for secret in ["KEY", "TOKEN", "SECRET", "SID"]):
            if len(value) > 20:
                display = value[:15] + "..." + value[-5:]
            else:
                display = value[:10] + "..."
        else:
            display = value

        print(f"✅ {name:30} {display}")
        return True
    else:
        status = "❌ REQUERIDA" if required else "⚠️  OPCIONAL"
        print(f"{status:4} {name:30} (NO configurada)")
        return not required

def test_openai():
    """Test OpenAI configuration"""
    print_header("🤖 OPENAI API")

    key = os.getenv("OPENAI_API_KEY")
    valid = print_var("OPENAI_API_KEY", key, required=True)

    if valid and key:
        # Validar formato
        if key.startswith("sk-"):
            print("   └─ Formato: ✅ Válido (sk-...)")
        else:
            print("   └─ Formato: ⚠️  No parece clave OpenAI válida")
            valid = False

    return valid

def test_vector_db():
    """Test Vector Database configuration (canonical: local JSON index + optional pgvector)."""
    print_header("🗄️  VECTOR DATABASE")

    db_url = os.getenv("HV_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    has_pgvector = "postgres" in db_url

    # Backend alternativo (opcional)
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    has_qdrant = qdrant_url and qdrant_key

    if has_pgvector:
        print("📍 Backend: PGVECTOR (Postgres)")
        print_var("HV_DATABASE_URL/DATABASE_URL", db_url, required=True)
        return True

    elif has_qdrant:
        print("📍 Backend: QDRANT (alternativo)")
        print_var("QDRANT_URL", qdrant_url, required=True)
        print_var("QDRANT_API_KEY", qdrant_key, required=True)
        return True

    else:
        print("📍 Backend: índice local JSON (knowledge_base/embeddings_local.json) — default sin DB")
        return True

def test_optional_services():
    """Test servicios opcionales (Twilio, Whisper)"""
    print_header("🔌 SERVICIOS OPCIONALES (Fase 2)")

    # Twilio
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")

    if twilio_sid and twilio_token:
        print("📱 Twilio (WhatsApp):")
        print_var("  TWILIO_ACCOUNT_SID", twilio_sid, required=False)
        print_var("  TWILIO_AUTH_TOKEN", twilio_token, required=False)
    else:
        print("⚠️  Twilio: NO configurado (OK para demo inicial)")

    # Whisper
    whisper_key = os.getenv("WHISPER_API_KEY")
    if whisper_key:
        print("\n🎤 Whisper (Transcripción):")
        print_var("  WHISPER_API_KEY", whisper_key, required=False)
    else:
        print("⚠️  Whisper: NO configurado (OK para demo inicial)")

def test_database():
    """Test Database configuration"""
    print_header("💾 DATABASE")

    db_url = os.getenv("DATABASE_URL", "sqlite:///./vigente_v3.db")
    print_var("DATABASE_URL", db_url, required=True)

    if "sqlite" in db_url:
        print("   └─ Tipo: SQLite (desarrollo)")
    elif "postgresql" in db_url:
        print("   └─ Tipo: PostgreSQL (producción)")

    return True

def test_rag_config():
    """Test RAG configuration"""
    print_header("🧠 RAG CONFIGURATION")

    kb_path = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dims = os.getenv("EMBEDDING_DIMENSIONS", "1536")
    chunk_size = os.getenv("CHUNK_SIZE", "1024")
    similarity = os.getenv("SIMILARITY_THRESHOLD", "0.75")
    top_k = os.getenv("TOP_K_RESULTS", "5")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature = os.getenv("LLM_TEMPERATURE", "0.7")

    print_var("KNOWLEDGE_BASE_PATH", kb_path, required=True)
    print_var("EMBEDDING_MODEL", embedding_model, required=True)
    print_var("EMBEDDING_DIMENSIONS", embedding_dims, required=True)
    print_var("CHUNK_SIZE", chunk_size, required=True)
    print_var("SIMILARITY_THRESHOLD", similarity, required=True)
    print_var("TOP_K_RESULTS", top_k, required=True)
    print_var("LLM_MODEL", llm_model, required=True)
    print_var("LLM_TEMPERATURE", temperature, required=True)

    # Verificar que Knowledge Base existe
    if os.path.exists(kb_path):
        servicios_path = os.path.join(kb_path, "servicios")
        if os.path.exists(servicios_path):
            num_servicios = len([f for f in os.listdir(servicios_path) if f.endswith('.md') and not f.startswith('_')])
            print(f"\n   └─ Servicios encontrados: {num_servicios}/26")
        else:
            print("\n   └─ ⚠️  Carpeta servicios/ no encontrada")
    else:
        print(f"\n   └─ ❌ Knowledge Base no encontrada en: {kb_path}")

    return True

def test_agents_config():
    """Test Agents configuration"""
    print_header("🤖 AGENTES CONFIGURATION")

    diagnostico_thermal = os.getenv("DIAGNOSTICO_ENABLE_THERMAL", "True")
    diagnostico_rgb = os.getenv("DIAGNOSTICO_ENABLE_RGB", "True")
    persona_modelo = os.getenv("PERSONA_DEFAULT_MODELO", "arquetipos_modelo_financiero.json")
    opti_bnpl = os.getenv("OPTI_ENABLE_BNPL", "True")
    opti_threshold = os.getenv("OPTI_BNPL_THRESHOLD", "2500")
    chat_rag = os.getenv("CHAT_ENABLE_RAG", "True")

    print_var("DIAGNOSTICO_ENABLE_THERMAL", diagnostico_thermal, required=True)
    print_var("DIAGNOSTICO_ENABLE_RGB", diagnostico_rgb, required=True)
    print_var("PERSONA_DEFAULT_MODELO", persona_modelo, required=True)
    print_var("OPTI_ENABLE_BNPL", opti_bnpl, required=True)
    print_var("OPTI_BNPL_THRESHOLD", opti_threshold, required=True)
    print_var("CHAT_ENABLE_RAG", chat_rag, required=True)

    return True

def test_business_model():
    """Test Business Model configuration"""
    print_header("💰 BUSINESS MODEL")

    access_price = os.getenv("MEMBERSHIP_ACCESS_PRICE", "1400")
    access_discount = os.getenv("MEMBERSHIP_ACCESS_DISCOUNT", "0.15")
    elite_price = os.getenv("MEMBERSHIP_ELITE_PRICE", "3800")
    elite_discount = os.getenv("MEMBERSHIP_ELITE_DISCOUNT", "0.20")
    bnpl_threshold = os.getenv("BNPL_MIN_THRESHOLD", "2500")

    print_var("MEMBERSHIP_ACCESS_PRICE", f"${access_price} MXN", required=True)
    print_var("MEMBERSHIP_ACCESS_DISCOUNT", f"{float(access_discount)*100}%", required=True)
    print_var("MEMBERSHIP_ELITE_PRICE", f"${elite_price} MXN", required=True)
    print_var("MEMBERSHIP_ELITE_DISCOUNT", f"{float(elite_discount)*100}%", required=True)
    print_var("BNPL_MIN_THRESHOLD", f"${bnpl_threshold} MXN", required=True)

    return True

def main():
    """Main test function"""
    print("\n" + "🔍 " + "="*58)
    print("   HOMBRE VIGENTE - VALIDACIÓN DE CONFIGURACIÓN")
    print("="*60)

    results = {
        "OpenAI API": test_openai(),
        "Vector Database": test_vector_db(),
        "Database": test_database(),
        "RAG Config": test_rag_config(),
        "Agents Config": test_agents_config(),
        "Business Model": test_business_model(),
    }

    # Servicios opcionales (no afectan resultado final)
    test_optional_services()

    # Resumen final
    print_header("📊 RESUMEN")

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")

    print("\n" + "="*60)

    if all_passed:
        print("🎉 CONFIGURACIÓN COMPLETA - Listo para desarrollo RAG!")
        print("="*60 + "\n")
        return 0
    else:
        print("⚠️  CONFIGURACIÓN INCOMPLETA - Revisar variables faltantes")
        print("="*60 + "\n")
        print("💡 Ayuda:")
        print("   1. Revisar archivo .env en raíz de DEMO/")
        print("   2. Comparar con .env.example")
        print("   3. Ver documentación: CONFIG_SETUP.md")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
