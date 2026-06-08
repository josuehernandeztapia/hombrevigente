# Tracker MVP-0 — Setup Sheets (5 min)

**Archivo local:** `estrategia_2026/MVP0_Beta_Tracker.xlsx`  
**Caso #0:** fila #0 ya actualizada en hoja **Pipeline** (2026-06-08)

---

## Pasos

1. Abre Google Drive → **Nuevo → Subir archivo** → `MVP0_Beta_Tracker.xlsx`
2. Abre con **Google Sheets** (convertir si pregunta)
3. Verifica hoja **Pipeline** fila 5: estado `protocolo_entregado`
4. Comparte solo contigo (+ médico view-only cuando exista)
5. Bookmark el link — es tu CRM MVP-0

---

## Hojas

| Hoja | Para qué |
|------|----------|
| Dashboard Sprint | Contadores manuales fin de sprint |
| **Pipeline** | 1 fila por beta |
| **RAG Concierge** | Cada consulta `concierge_mvp.py` |
| Check-ins semanales | Semanas 1–4 por beta |
| Feedback | Semana 4 + intención de pago |

---

## Regenerar fila desde intake

```bash
cd ~/Desktop/hombrevigente/rag-bot
python scripts/tracker_pipeline_row.py fixtures/caso0_intake_p1_entrega.json --tsv
```

Pegar en siguiente fila vacía de Pipeline.

---

*P3 · HV only*