# Tarjeta SSOT — Readiness / recuperación (Oura, Whoop)

---
id: wearable-readiness
tipo: Señal-Wearable
nombre: Readiness / Recovery Score
resumen: Métrica compuesta de wearables (HRV, sueño, temperatura, RHR, actividad previa) que estima capacidad de carga ese día. Útil para personalizar intensidad de entrenamiento y recuperación.
mecanismo: Algoritmo propietario pondera señales autonómicas y sueño; score bajo correlaciona con fatiga subjetiva en validaciones internas del fabricante.
señales_que_lo_activan: ["readiness <70 (escala Oura/Whoop)", "HRV bajo", "RHR elevado vs baseline", "sueño malo noche previa", "carga alta días previos"]
dosis_referencia: n/a
evidencia:
  nivel: Observacional + validación dispositivo
  resumen: Correlación moderada con rendimiento subjetivo; mejor uso como tendencia personal que umbral absoluto universal.
  fuentes:
    - Kinnunen H et al., 2020 — Nocturnal HR/HRV vía ring PPG vs ECG (Physiol Meas) — PMID 32217820
    - [FALTA FUENTE — RCT con outcomes de salud (hard endpoints) usando readiness score]
requiere_receta: no
contraindicaciones: ["no sustituye evaluación clínica de fatiga patológica"]
flag_seguridad: ninguno
confianza: media
disclaimer: "Información educativa de optimización. No es diagnóstico ni tratamiento médico. Consulta a un profesional de salud."
version: v0.2
revisado_por: PENDIENTE-MEDICO
fecha: 2026-06-07
---

**Temas relacionados:** `wearable-hrv`, `wearable-sueno`, `26_lifestyle_pilares`