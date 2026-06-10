"""
Script para verificar que todo esté configurado correctamente
antes de generar embeddings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_api_keys():
    """Verifica que las API keys estén configuradas"""
    print("🔑 Verificando API Keys...")

    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key or openai_key == "":
        print("   ❌ OPENAI_API_KEY no configurada en .env")
        return False
    elif len(openai_key) < 20:
        print("   ❌ OPENAI_API_KEY parece inválida (muy corta)")
        return False
    else:
        print(f"   ✅ OPENAI_API_KEY encontrada (longitud: {len(openai_key)})")

    return True


def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    print("\n🤖 Probando conexión con OpenAI...")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Test with a simple embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )

        print(f"   ✅ Conexión exitosa")
        print(f"   ✅ Embedding generado (dimensiones: {len(response.data[0].embedding)})")
        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False


def check_services_files():
    """Verifica que los archivos de servicios existan"""
    print("\n📁 Verificando archivos de servicios...")

    servicios_dir = Path("knowledge_base/servicios")

    if not servicios_dir.exists():
        print(f"   ❌ Directorio no encontrado: {servicios_dir}")
        return False

    service_files = list(servicios_dir.glob("[0-9][0-9]_*.md"))
    print(f"   ✅ Encontrados {len(service_files)} archivos de servicios")

    if len(service_files) == 0:
        print(f"   ❌ No se encontraron archivos de servicios")
        return False

    # Show first 5
    print(f"   📄 Primeros servicios:")
    for f in sorted(service_files)[:5]:
        print(f"      • {f.name}")

    if len(service_files) > 5:
        print(f"      ... y {len(service_files) - 5} más")

    return True


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("\n📦 Verificando dependencias...")

    required = {
        "openai": "OpenAI SDK",
        "tqdm": "Progress bars",
        "dotenv": "Environment variables"
    }

    missing = []

    for package, description in required.items():
        try:
            __import__(package)
            print(f"   ✅ {description} ({package})")
        except ImportError:
            print(f"   ❌ {description} ({package}) - FALTANTE")
            missing.append(package)

    if missing:
        print(f"\n   💡 Instala dependencias faltantes:")
        print(f"      pip install {' '.join(missing)}")
        return False

    return True


def main():
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE SETUP PARA EMBEDDINGS")
    print("=" * 70)

    checks = []

    # Run all checks
    checks.append(("Dependencias", check_dependencies()))
    checks.append(("API Keys", check_api_keys()))
    checks.append(("Archivos", check_services_files()))
    checks.append(("OpenAI", test_openai_connection()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)

    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")

    all_passed = all(passed for _, passed in checks)

    if all_passed:
        print("\n🎉 TODO LISTO! Puedes ejecutar:")
        print("   python3 embed_kb_local.py --source all")
    else:
        print("\n⚠️  Corrige los errores arriba antes de continuar")
        print("\n💡 Pasos siguientes:")

        if not checks[1][1]:  # API Keys
            print("   1. Actualiza tus API keys en el archivo .env")
            print("      - OpenAI: https://platform.openai.com/api-keys")


if __name__ == "__main__":
    main()
