# Entrega cliente MARCADO (con banderas)

**Canal:** WA personal · No usar plantilla verde

---

## Script #3 — Confirmación (marcado)

```
¡Listo [nombre], recibí tus datos! 🙏

Vi que mencionaste [tema de bandera — ej. medicación / antecedente oncológico].
Por seguridad, antes de recomendarte algo concreto lo alineamos contigo y, si hace falta, con tu médico. Eso es parte de cómo trabajamos — no es burocracia.

Te armo un plan educativo conservador. En 24–48h te escribo con los primeros pasos.

¿Te parece si platicamos 5 min si algo no quedó claro en el form?
```

---

## Script #4 — Entrega (marcado · fase 1)

**Fase 1 = lifestyle + plan escrito. Farmacología según clearance.**

```
[nombre], aquí va tu plan personalizado 💪

Por tu perfil de salud ([bandera resumida en 1 línea]), empezamos conservador:

🟢 Empieza YA — solo lifestyle
• Sueño 7–9h · hidratación · movimiento adaptado
• Foto baseline · diario energía / sueño / ánimo 1–5

⏳ Próximo paso (contigo / tu médico)
• Orales o stack avanzado solo tras validación — te explico el porqué si quieres
• Nada de inyectables ni protocolos agresivos sin supervisión

📎 Protocolo educativo completo: [adjunto / resumen]

⚠️ Información educativa, no prescripción. Valida con tus médicos antes de iniciar suplementos o cambios.

¿Dudas?
```

---

## Clearance por tipo de bandera

| Bandera | Mensaje / doc |
|---------|----------------|
| Psiquiatría / litio | `MVP0_Caso0_Clearance_Psiquiatra.md` (adaptar nombre) |
| Onco | Médico tratante / oncólogo |
| Cardio/renal/hepática | Médico cabecera |
| Médico aliado HV | Revisión protocolo antes de entrega completa |

---

## Caso #0 / #1

Peor caso → mensaje B completo con C1/C2 separados. Ver `MVP0_Caso0_Clearance_Psiquiatra.md`.

---

*Confirmar perfil: `python scripts/mvp0_route.py <intake.json>`*