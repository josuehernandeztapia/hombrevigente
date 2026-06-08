# Caso #0 — P1 Entrega (listo para ejecutar)

**Peldaño:** P1 · **Fecha:** 2026-06-08 · **Estado:** protocolo entregado (simulación ops OK; médico en cola)

---

## Qué hacer ahora (15 min)

| # | Acción | Tiempo |
|---|--------|--------|
| 1 | Pegar **mensaje #4** en **Notas / WA personal a ti mismo / email** (sin número HV ni Twilio) | 2 min |
| 2 | Adjuntar o enlazar protocolo: `MVP0_Caso0_Protocolo.md` | 1 min |
| 3 | Pegar fila **Tracker** en Sheets fila #0 | 2 min |
| 4 | Completar **subjetivo día 0** en baseline §5 | 5 min |
| 5 | Programar check-in S1 (mensaje #5) para dentro de 7 días | 1 min |
| 6 | Marcar P1 ✅ en este doc | 1 min |

---

## Mensaje #4 — Entrega (copiar a WhatsApp)

**Canal hoy:** sin número HV · sin Twilio · sin API. Caso #0 = Notas o WA personal contigo.

**Versión final — pegar tal cual** (adjunta PDF/captura de `MVP0_Caso0_Resumen_Entrega.md` si quieres).

```
[Caso #0 — protocolo entregado · canal personal / Notas]

Juan, aquí va tu protocolo personalizado 💪

Ya lo armé con tus datos del Tally, labs (oct-2025) y RM lumbar (feb-2025). Documento completo: estrategia_2026/MVP0_Caso0_Protocolo.md (en el repo / Drive)

🎯 Enfoque 8 semanas
Ciática L4-S1 (discopatía Pfirrmann IV) + recuperar energía + mejorar estética, con base de longevidad.

Stack orientativo: Wolverine + base longevidad oral — pero ojo 👇

🟢 A) Empieza YA — solo lifestyle (sin farmacología)
• Sueño 7-9h, horario fijo
• Movilidad lumbar/piriforme 10 min/día
• Fuerza 2-3x/sem bajo impacto (natación, bici)
• Hidratación constante — clave con litio
• Foto baseline + diario 1-5: energía · sueño · ánimo · dolor

⏳ B/C/D — pendiente psiquiatra (mensaje en MVP0_Caso0_Clearance_Psiquiatra.md)
• C1 orales generales (NMN, resveratrol, spermidine) — gradual, tras OK
• C2 aparte: Cerluten / Endoluten (SNC/sueño) — visto bueno específico, no junto con C1
• D fuera: senolíticos (quercetina↔quetiapina + onco), inyectables (sin datos + Rx), tesamorelin (IGF-1/ayunas vs litio)

📊 Dato importante de tus labs
Litio sérico 0.42 (por debajo del rango terapéutico 0.6-1.2). Vale la pena comentarlo con tu psiquiatra — no toques nada por tu cuenta.

📅 Seguimiento
Check-in semana 1: recordatorio en calendario (mensaje #5 abajo). Re-evaluamos a las 4 semanas.

⚠️ Esto es información educativa, no prescripción médica. Valídalo con tus médicos antes de iniciar cualquier suplemento o cambio. Si algo no se siente bien, paras y consultas.

¿Alguna duda con el protocolo o con lo que puedes empezar hoy?
```

---

## Mensaje #5 — Check-in semana 1 (calendario 15 jun · Notas o WA personal)

```
[HV Caso #0 — check-in semana 1]

Semana 1 ✅ ¿Cómo vas?

Del 1 al 5:
⚡ Energía:
😴 Sueño:
🙂 Ánimo:
💪 Dolor ciática:

¿Foto baseline o semanal? (misma luz/ángulo) 📸 Sí / No

¿Pudiste: sueño 7-9h · movilidad lumbar · hidratación · ejercicio bajo impacto?

Fase actual = solo lifestyle + diario. Stack avanzado = después de médicos.

Respuestas → anota en MVP0_Caso0_Diario.md (o hoja Check-ins del tracker).
```

---

## Tracker — fila #0 (pegar en Sheets)

**Archivo listo:** `MVP0_Caso0_Pipeline_fila0.tsv` — copiar fila y pegar en Sheets fila #0.

Regenerar:

```bash
cd ~/Desktop/hombrevigente/rag-bot
python scripts/tracker_pipeline_row.py fixtures/caso0_intake_p1_entrega.json --tsv --notes "P1 entrega 2026-06-08"
```

---

## Qué incluye la entrega (documentos)

| Archivo | Uso |
|---------|-----|
| `MVP0_Caso0_Protocolo.md` | Protocolo completo (adjunto / PDF manual) |
| `MVP0_Caso0_Baseline.md` | Baseline labs + RM + subjetivo |
| `MVP0_Caso0_Resumen_Entrega.md` | Versión corta si WA no admite adjunto largo |

---

## Modo Caso #0 — qué SÍ puedes empezar hoy (sin clearance)

Mientras médico/psiquiatra revisan el stack completo:

- [ ] Foto baseline (checklist baseline §5)
- [ ] Diario 1–5: energía, sueño, ánimo, dolor ciática
- [ ] Movilidad lumbar/piriforme + natación/ciclismo (bajo impacto)
- [ ] Sueño e hidratación constante (relevante con litio)
- [ ] **No** iniciar: BPC, Tesamorelin, senolíticos, Khavinson, NMN alto sin OK médico

---

## Cola médica (simulación aceptada P1)

| Revisor | Para qué | Estado |
|---------|----------|--------|
| Psiquiatra | Litio 0.42, quetiapina, ánimo si cambia lifestyle | ⏳ Pendiente |
| Médico aliado HV | Firma protocolo educativo | ⏳ Pendiente |
| Columna/especialista | RM L4-S1 — confirma manejo conservador | Opcional |

**P1 no requiere firma para cerrar el peldaño** — requiere entrega + disclaimer + check-in programado.

---

## P1 — Definition of Done

- [x] Protocolo redactado (`MVP0_Caso0_Protocolo.md`)
- [x] Mensaje entrega WA (#4) personalizado
- [x] Mensaje check-in S1 (#5) listo
- [x] Intake entrega + fila tracker generable
- [ ] **Tú:** mensaje enviado/guardado (evidencia)
- [ ] **Tú:** fila #0 en Sheets actualizada
- [ ] **Tú:** subjetivo día 0 completado

Cuando las 3 casillas inferiores estén ✅ → **P1 cerrado**.

**Ya listo en repo:** P2 `MVP0_Template_Beta.md` · P3 `MVP0_Beta_Tracker.xlsx` fila #0 · semana 1 `MVP0_Semana1_Caso0.md`

---

*Operación MVP-0 · ver `MVP0_Como_Avanzar.md`*