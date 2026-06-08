# COMPLIANCE.md — Reglas no negociables (Hombre Vigente)

> Para el equipo dev y de contenido. Esto **manda** sobre diseño y copy. Ante la duda, no se publica/entrega.
> No es consejo legal; validar con asesoría (COFEPRIS / LFPDPPP) antes de operar Av.2.

---

## 0. Marca y nomenclatura
- **El trademark es "Hombre Vigente™"** (la marca). Úsese `Hombre Vigente™` donde corresponda.
- **"Índice Vigente" NO lleva ™** (no es la marca registrada) y **aún NO es un modelo construido/validado**. Hasta que exista:
  - Los scores mostrados (ej. 68/100, 64/100) son **ilustrativos/ejemplo** — etiquétalos como tal en la UI.
  - Descríbelo como **compuesto de optimización/bienestar con metodología documentada**, nunca como score diagnóstico.

## 1. Dos avenidas — qué va por dónde
- **Avenida 1 (sin receta):** SOLO suplementos `STACK_VIGENTE` (NMN, Omega-3, Creatina, Vitamina D3+K2, Magnesio, Resveratrol, Espermidina, Fisetina/Quercetina orales). Vendible sin médico.
- **Avenida 2 (vía médica, exclusiva):** TODO item Rx/péptido — **BPC-157, TB-500, Goralatide, Tesamorelin, Khavinson, GHK-Cu inyectable** — requiere valoración + receta + firma de médico responsable + farmacia magistral. **Nunca** seleccionable en el carril sin receta.
- **Regla de ruteo:** cualquier stack que contenga un item Av.2 se gatea a Av.2 completo. (Ojo: el "Metabolic Longevity Stack" con Tesamorelin/Khavinson NO es Av.1.)

## 2. Lenguaje
- **Permitido:** "optimización", "bienestar", "se asocia / se ha estudiado", "lectura objetiva", "informe de optimización".
- **Prohibido:** "diagnóstico", "cura", "trata", "previene", "revierte", "garantiza", "predictivo". **No nombrar condiciones específicas** (ej. "ciática" → "recuperación / dolor / molestias").
- El escaneo térmico (cuando exista) = **ΔT relativo, medición adjunta de bienestar**, no diagnóstico.

## 3. Evidencia
- Cada **claim de intervención** lleva **nivel + fuente (PMID/DOI)**: **Fuerte** (RCT/meta-análisis humano) · **Moderada** (humano temprano) · **Emergente** (preclínico/animal).
- Los **biomarcadores** (hs-CRP, HRV, glucosa…) **NO llevan nivel de evidencia** (un valor de lab no es un claim).
- Fuente primaria verificada o no entra. (Los E1–E5 internos del SSOT no se exponen al usuario.)

## 4. El modelo sugiere; el médico firma
- Toda recomendación de **prescripción** (Av.2) la **decide y firma un médico responsable** — nunca el software de forma autónoma. El copy de ajustes de dosis debe decir "tu médico aprobó", no "el modelo recalibró".

## 5. Privacidad (LFPDPPP) — datos de salud sensibles
- **Consentimiento explícito ANTES** de capturar cualquier dato de salud (el Aviso de Privacidad real debe existir y enlazarse).
- **Cifrado en reposo y en tránsito.** **Control de acceso + log de auditoría** (quién ve datos del paciente, sobre todo el médico).
- **Flujo de borrado real** (el consentimiento promete "borrar mis datos cuando quiera" → debe funcionar). Definir **retención** y **residencia** de datos.
- **Foto de rostro = dato biométrico.** Compartirla con CV de terceros (Haut.AI/Perfect Corp) requiere **DPA con el proveedor + consentimiento específico** para esa transferencia.

---

## Pendientes del mundo real (bloquean Av.2 / captura de datos, no el MVP de Av.1)
1. **Aviso de Privacidad (LFPDPPP)** real.
2. **Responsable sanitario** (médico, cédula, contrato) + **farmacia magistral con contrato**.
3. **DPAs** con proveedores (CV, labs, wearables, WhatsApp, pagos).
4. Validar PMIDs contra el SSOT (`rag-bot/knowledge_base/longevity/`).

> El MVP de **Av.1 puede shippear sin el médico**; Av.2 se enciende cuando #2 esté firmado.