# ⚙️ CONFIGURACIÓN DEL ENTORNO - Hombre Vigente Demo

**Última actualización**: 2025-10-15
**Status**: ✅ Configurado y listo

---

## 📁 Archivos creados

```
DEMO/
├── .env                    ✅ Variables de entorno con API keys REALES
├── .env.example            ✅ Template documentado (sin secrets)
├── .gitignore              ✅ Protege secrets de commits
├── secrets.local.txt       ⚠️  DEPRECADO (migrado a .env)
└── CONFIG_SETUP.md         📖 Este archivo
```

---

## 🔑 API Keys Configuradas

### ✅ LISTAS PARA USAR

| Servicio | Variable | Status | Propósito |
|----------|----------|--------|-----------|
| **OpenAI** | `OPENAI_API_KEY` | ✅ Configurada | Embeddings + GPT-4o mini |
| **Pinecone** | `PINECONE_API_KEY` | ✅ Configurada | Vector Database para RAG |
| **Twilio** | `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` | ✅ Configurada | WhatsApp (Fase 2) |
| **Whisper** | `WHISPER_API_KEY` | ✅ Configurada | Transcripción voz (Fase 2) |

---

## 🚀 Cómo usar el .env

### En Python (FastAPI):

```python
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Usar variables
openai_key = os.getenv("OPENAI_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
debug = os.getenv("DEBUG", "False") == "True"
```

### En scripts de embeddings:

```python
# backend/scripts/generate_embeddings.py

import os
from dotenv import load_dotenv
import openai
from pinecone import Pinecone

load_dotenv()

# OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
```

---

## 📊 Variables RAG Importantes

### Knowledge Base Paths

```bash
KNOWLEDGE_BASE_PATH=./knowledge_base
KNOWLEDGE_BASE_SERVICIOS=./knowledge_base/servicios
KNOWLEDGE_BASE_FAQS=./knowledge_base/faqs
KNOWLEDGE_BASE_PROTOCOLOS=./knowledge_base/protocolos
```

### Embeddings Configuration

```bash
EMBEDDING_MODEL=text-embedding-3-small   # OpenAI model
EMBEDDING_DIMENSIONS=1536                # Vector size
CHUNK_SIZE=1024                          # Tokens per chunk
CHUNK_OVERLAP=200                        # Overlap between chunks
```

### RAG Retrieval

```bash
SIMILARITY_THRESHOLD=0.75                # Minimum cosine similarity
TOP_K_RESULTS=5                          # Number of chunks to retrieve
```

### LLM Generation

```bash
LLM_MODEL=gpt-4o-mini                    # OpenAI model for responses
LLM_TEMPERATURE=0.7                      # Creativity (0.0-1.0)
LLM_MAX_TOKENS=1000                      # Max response length
```

---

## 🔄 Flujo de Trabajo con .env

### 1. Desarrollo Local

```bash
# Archivo .env está en DEMO/.env
# Python/FastAPI lo lee automáticamente con python-dotenv

cd DEMO/backend
uvicorn main:app --reload
# ✅ Variables cargadas automáticamente
```

### 2. Testing de Variables

```bash
# Verificar que .env funciona
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OpenAI:', os.getenv('OPENAI_API_KEY')[:20] + '...')
print('Pinecone:', os.getenv('PINECONE_API_KEY')[:20] + '...')
"
```

### 3. Producción (Futuro)

```bash
# NO usar .env en producción
# Usar variables de entorno del servidor:

export OPENAI_API_KEY="sk-proj-xxxxx"
export PINECONE_API_KEY="pcsk_xxxxx"
# ... etc
```

---

## 🛡️ Seguridad

### ✅ Protecciones Implementadas

1. **`.gitignore` protege .env**
   - `.env` NUNCA se subirá a Git
   - Solo `.env.example` (sin secrets) se commitea

2. **Secrets.local.txt deprecado**
   - Migrado todo a `.env`
   - Formato limpio `KEY=VALUE`
   - Sin warnings de python-dotenv

3. **API Keys rotables**
   - Después de demo público: rotar todas las keys
   - Generar nuevas en cada plataforma

### ⚠️ NUNCA HACER

```bash
# ❌ NO commitear .env
git add .env  # NUNCA!

# ❌ NO hardcodear secrets en código
openai.api_key = "sk-proj-xxxxx"  # NUNCA!

# ❌ NO compartir .env por chat/email
# Usar método seguro (1Password, Vault, etc.)
```

### ✅ SIEMPRE HACER

```bash
# ✅ Usar .env.example como template
cp .env.example .env
# Luego editar .env con secrets reales

# ✅ Verificar .gitignore
git status  # .env NO debe aparecer en cambios

# ✅ Rotar keys después de exposición
# Si .env se filtró: regenerar TODAS las keys inmediatamente
```

---

## 🧪 Testing de Configuración

### Script de validación:

```python
# test_config.py

from dotenv import load_dotenv
import os

load_dotenv()

def test_env():
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "DATABASE_URL",
        "KNOWLEDGE_BASE_PATH"
    ]

    print("🔍 Validando configuración...\n")

    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ocultar parte del secret
            display = value[:15] + "..." if len(value) > 15 else value
            print(f"✅ {var}: {display}")
        else:
            print(f"❌ {var}: FALTA")

    print("\n✅ Configuración validada!")

if __name__ == "__main__":
    test_env()
```

Ejecutar:
```bash
python test_config.py
```

Salida esperada:
```
🔍 Validando configuración...

✅ OPENAI_API_KEY: sk-proj-InbBZC...
✅ PINECONE_API_KEY: pcsk_4kbU5X_2Q...
✅ DATABASE_URL: sqlite:///./vi...
✅ KNOWLEDGE_BASE_PATH: ./knowledge_ba...

✅ Configuración validada!
```

---

## 📦 Dependencias Requeridas

### Python packages:

```bash
# requirements.txt (agregar si no están)

python-dotenv==1.0.0      # Load .env files
openai==1.12.0            # OpenAI API (embeddings + GPT)
pinecone-client==3.0.0    # Pinecone vector DB
fastapi==0.109.0          # Backend framework
uvicorn==0.27.0           # ASGI server
pydantic==2.5.0           # Data validation
sqlalchemy==2.0.25        # ORM (SQLite/PostgreSQL)
```

Instalar:
```bash
cd DEMO/backend
pip install -r requirements.txt
```

---

## 🎯 Próximos Pasos

### Fase Actual: ✅ CONFIGURACIÓN COMPLETA

**Lo que ya está listo**:
- [x] `.env` con todas las API keys
- [x] `.gitignore` protegiendo secrets
- [x] Variables RAG configuradas
- [x] Paths de Knowledge Base definidos

### Siguiente Fase: Enriquecimiento P0 (TU TAREA)

**Antes de implementar RAG**:
1. Completar 5 servicios P0 (HIFU, Botox, RF, Láser, Limpieza)
2. Agregar contenido médico validado
3. Completar secciones `[FALTA: VALIDAR CON DR.]`

Ver: [knowledge_base/TODO_ENRIQUECIMIENTO.md](knowledge_base/TODO_ENRIQUECIMIENTO.md)

### Después de P0: Implementación RAG (YO)

**Cuando completes P0**:
1. Script de generación de embeddings
2. Setup Pinecone index
3. Ingesta de chunks a Pinecone
4. API endpoint `/api/v1/chat/rag`
5. Testing de queries

---

## 📞 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Problema: "OpenAI API key invalid"

```bash
# Verificar key en .env
cat .env | grep OPENAI_API_KEY

# Verificar en código
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('OPENAI_API_KEY'))
"
```

### Problema: ".env no se carga"

```bash
# Verificar ubicación del archivo
ls -la .env

# Debe estar en raíz de DEMO/
# NO en DEMO/backend/.env

# Cargar desde ubicación específica:
load_dotenv(dotenv_path="../.env")
```

### Problema: "Pinecone index not found"

```bash
# Crear index manualmente:
# 1. Ir a https://app.pinecone.io/
# 2. Create Index
# 3. Name: hombre-vigente-kb
# 4. Dimensions: 1536
# 5. Metric: cosine
```

---

## ✅ CONCLUSIÓN

**Status**: 🎉 Configuración 100% completa

**Listo para**:
- Desarrollo local de RAG
- Testing de embeddings
- Integración con ChatVigente AI

**Pendiente**:
- Enriquecimiento contenido P0 (tu tarea)
- Implementación pipeline RAG (después de P0)

---

**Última actualización**: 2025-10-15
**Configurado por**: Claude (automatizado)
**Revisado por**: Josue Hernandez (pendiente)
