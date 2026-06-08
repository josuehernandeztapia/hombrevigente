# MVP-0 — Playbook Operativo "Concierge Manual"

**Hombre Vigente · Validación con 5–10 betas (gratis a cambio de feedback)**
Versión 1.0 · Junio 2026

---

## 0. Qué es MVP-0 y qué estamos validando

MVP-0 es la forma **más rápida y barata** de validar Hombre Vigente: **sin código, sin app**. El "algoritmo" eres tú + un LLM. Recibes datos por un formulario, armas el protocolo a mano con una plantilla, lo entregas por WhatsApp y acompañas semana a semana.

Como la beta es **gratis a cambio de feedback**, no validamos el pago directamente — validamos las **3 cosas que tienen que ser ciertas antes de gastar en construir**:

1. **¿La gente entrega sus datos?** (foto + labs + wearable + cuestionario) → mide fricción real del onboarding.
2. **¿El protocolo se percibe valioso y se sigue?** → mide adherencia y "aha moment".
3. **¿Pagarían por esto?** → se mide con *intención declarada* + comportamiento (referidos, piden continuar), no con cobro.

> **Meta de la fase:** 5–10 betas completando el ciclo de 4 semanas, con feedback estructurado y al menos 3 diciendo "sí pagaría / recomiéndame a alguien". Si eso no pasa, ninguna IA lo arregla — iteramos el concepto antes de construir.

**Duración:** 4–6 semanas. **Costo:** ~$0 (todas las herramientas en plan gratis).

---

## 1. Análisis de herramientas y recomendación

Pediste analizar conveniencia. Esta es la comparación y el veredicto. **Regla rectora: cero costo, lanzable esta semana, operable desde el celular.**

### Formulario de onboarding

| Herramienta | Costo | Subida de archivos (foto + PDF labs) | UX | Veredicto |
|-------------|-------|--------------------------------------|-----|-----------|
| **Tally** | Gratis (ilimitado) | ✅ Sí, en plan gratis | Muy buena, tipo Notion | ✅ **Recomendado** |
| Typeform | Gratis limitado | ✅ Sí | Excelente | ❌ Plan gratis tope ~10 respuestas/mes |
| Google Forms | Gratis | ⚠️ Sí, pero obliga al usuario a iniciar sesión Google para subir | Funcional pero rígida | Alternativa si ya vives en Google |

**→ Usa Tally.** Es el único que combina gratis + ilimitado + subida de archivos sin fricción. Crea el form pegando el cuestionario del archivo `MVP0_Cuestionario.md`.

**Link MVP-0 (vivo):** https://tally.so/r/5BVeRd

### Entrega y seguimiento

| Herramienta | Costo | Por qué |
|-------------|-------|---------|
| **WhatsApp personal (tu cel)** | Gratis | ✅ **Lo que usas hoy.** DM a betas de confianza; scripts copy-paste. Sin número HV ni Twilio todavía. |
| **WhatsApp Business (app)** | Gratis | **Opcional Fase 0** — solo si sacas un número dedicado. Etiquetas + respuestas rápidas. |
| WhatsApp API / Twilio / 360dialog | $ | **Fase 1+.** No operando en MVP-0. |

**→ Hoy:** WA personal + Sheets (estados) + scripts en `MVP0_WhatsApp_Scripts.md`. Número dedicado y API cuando automatices.

### Tracker de betas

| Herramienta | Costo | Veredicto |
|-------------|-------|-----------|
| **Google Sheets** | Gratis | ✅ **Recomendado** para operar (accesible desde el cel, compartible con el médico aliado). Sube el `.xlsx` que te entrego a Drive y ábrelo como Sheet. |
| Excel | — | Mismo archivo; úsalo si prefieres escritorio. |

### Pago (diferido en esta fase)

Como la beta es gratis, **no configures pago todavía.** Pero deja listo el camino: cuando conviertas betas a clientes de pago, **Mercado Pago** (link de cobro) es lo más conveniente en México — acepta tarjeta, SPEI y MSI, y es lo que el consumidor mexicano ya conoce. Stripe es alternativa si vendes también fuera de MX.

### Canal de suministro (importante — ruta magistral)

El canal más limpio y profesional para el insumo en México son las **farmacias magistrales** (preparación bajo prescripción médica, con trazabilidad y respaldo legal más sólido que el "research peptide"). En MVP-0 **no vendes producto**, pero ya orienta a los betas hacia esta ruta vía el médico aliado. A mediano plazo, la relación con farmacias magistrales de confianza (CDMX / Querétaro) es el **canal principal** del modelo — no la importación directa ni el gray market.

### Generación del protocolo y análisis de foto

- **Protocolo:** lo armas tú con la plantilla (`MVP0_Plantilla_Protocolo.md`) + un LLM como copiloto. **Revisión del médico aliado antes de enviar** (obligatorio — ver §4).
- **Foto:** en MVP-0 el análisis es **manual** (observas y anotas glow, textura, postura, composición). El escaneo facial AI (Perfect Corp / Haut.AI) entra en MVP-1.

### Stack final recomendado (todo gratis, lanzable esta semana)

> **Tally** (onboarding) → **Google Sheets** (tracker) → **tú + LLM + médico aliado** (protocolo) → **WA personal / Notas** (entrega + seguimiento). Sin API. Pago: diferido (MVP-1+).

---

## 2. El flujo end-to-end (un beta, de principio a fin)

```
Reclutar → Onboarding (Tally) → Screening → Protocolo (tú+LLM) →
Revisión médico → Entrega (WhatsApp) → Check-in semanal x4 → Feedback → ¿Convertiría?
```

**Paso 1 — Reclutar.** Mensaje de invitación (script #1) a tu red: gym, conocidos 35–55, interesados en energía/estética/longevidad. Meta: 5–10 que digan que sí.

**Paso 2 — Onboarding.** Les mandas el link de Tally. Recoge: datos básicos, objetivos, **screening de salud (contraindicaciones)**, foto, PDF de labs (si tienen), datos de wearable (si tienen), y consentimiento.

**Paso 3 — Screening.** Antes de armar nada, revisas las banderas rojas (ver §4). Si hay bandera → no se entrega protocolo sin clearance médico. Esto protege al beta y a ti.

**Paso 4 — Armar protocolo.** Con la plantilla + LLM, generas el protocolo personalizado a partir de sus datos y objetivos. 20–40 min por persona.

**Paso 5 — Revisión médica.** El médico aliado revisa y firma/aprueba cada protocolo antes de enviarlo. Innegociable (ver §4).

**Paso 6 — Entrega.** Envías el protocolo por WhatsApp (PDF o mensaje estructurado) con el script de entrega + disclaimers.

**Paso 7 — Check-ins semanales (x4).** Cada semana: foto de progreso, cómo se siente (energía/sueño/ánimo/dolor), adherencia. Anotas en el tracker.

**Paso 8 — Feedback + intención.** Semana 4: encuesta de feedback estructurada + la pregunta clave: *"¿Pagarías por esto? ¿Cuánto? ¿A quién se lo recomendarías?"*

---

## 3. Métricas de éxito (qué medir en el tracker)

| Métrica | Cómo se mide | Umbral de "buena señal" |
|---------|--------------|--------------------------|
| **Tasa de completitud de onboarding** | % que empieza y termina el Tally | >60% |
| **Subieron labs/foto** | % que adjuntó datos reales | >50% (mide fricción del data moat) |
| **Adherencia semana 1→4** | % que sigue el protocolo cada semana | >50% llega a semana 4 |
| **"Aha moment"** | reportan ≥1 mejora subjetiva (energía/sueño/piel) | ≥3 de los betas |
| **Intención de pago** | dicen "sí pagaría" | ≥3 de los betas |
| **Referidos espontáneos** | recomiendan a alguien sin pedirlo | ≥1 |

> La métrica más valiosa: **referido espontáneo**. Si alguien gratis te manda a un amigo, el producto tiene tracción real.

---

## 4. Guardarraíles de seguridad y compliance (no negociable)

Esto es lo que te separa del gray market — y lo que te protege legalmente. **Léelo y respétalo en cada beta.**

1. **Médico responsable revisa cada protocolo antes de enviarlo.** Sin excepción. Es el desbloqueador de toda la operación; si aún no lo tienes, ese es el paso 0 antes de reclutar.
2. **Lenguaje correcto siempre:** "información educativa / optimización", **nunca** "tratamiento / cura / medicamento". (Art. 309 LGS: publicidad con beneficios de salud requiere autorización COFEPRIS.)
3. **Screening de exclusión obligatorio.** Banderas rojas que requieren clearance médico antes de cualquier protocolo:
   - Embarazo/lactancia, menores de edad.
   - Cáncer activo o en tratamiento; antecedente oncológico reciente.
   - Condiciones psiquiátricas en tratamiento (bipolar, etc.) o medicación con interacciones (litio, etc.).
   - Enfermedad cardiovascular, renal o hepática significativa.
   - Medicación crónica relevante.
4. **Disclaimer en cada entrega:** "Esto es información educativa, no diagnóstico ni prescripción médica. No sustituye a tu médico. Valida con un profesional de salud antes de iniciar."
5. **Datos de salud = sensibles.** Consentimiento explícito en el form; no compartas datos identificables; guarda los archivos en una carpeta privada.
6. **Calidad de insumo:** orienta hacia **farmacias magistrales** (preparación bajo prescripción) como ruta preferente. Si es otra fuente, exige COA por lote y pruebas de esterilidad/endotoxinas. Evita importación directa / gray market.

> En MVP-0 **no vendes producto** — entregas el protocolo educativo y el acompañamiento. El insumo lo consigue el beta por su cuenta, idealmente vía **farmacia magistral con prescripción de su médico** (o el médico aliado). Esto mantiene el riesgo bajo mientras validas el valor.

---

## 5. Plan de las próximas 2 semanas

**Semana 0 (setup, 1–2 días):**
- [ ] Confirmar médico aliado que revisa protocolos.
- [ ] Crear form en Tally (pegar `MVP0_Cuestionario.md`).
- [ ] Scripts en Notas o documento accesible desde el cel (número HV / WA Business = opcional, no bloqueante).
- [ ] Subir el tracker a Google Sheets.
- [x] Tú arrancas tu propio protocolo como **Caso #0** — ver `MVP0_Caso0_Baseline.md` + fila #0 en tracker.

**Semana 1:**
- [ ] Reclutar (script #1) hasta tener 5–10 confirmados.
- [ ] Enviar onboarding; hacer screening; armar y entregar primeros protocolos (con revisión médica).

**Semanas 2–5:**
- [ ] Check-ins semanales; registrar todo en el tracker.
- [ ] Semana 4: feedback + intención de pago.
- [ ] Documentar tu propia transformación (contenido para marca).

**Decisión al final:** si ≥3 betas reportan valor + intención de pago → construir MVP-1 (web + motor de recomendación). Si no → iterar concepto/segmento/oferta.

---

## 6. Archivos del kit

- `MVP0_Cuestionario.md` — preguntas listas para pegar en Tally.
- `MVP0_Plantilla_Protocolo.md` — template para armar cada protocolo.
- `MVP0_WhatsApp_Scripts.md` — todos los mensajes (reclutar, entregar, check-in, feedback).
- `MVP0_Beta_Tracker.xlsx` — seguimiento de los betas.

---

*No constituye consejo médico, legal ni financiero. La operación requiere un médico responsable con cédula y validación legal del ángulo COFEPRIS antes de escalar.*
