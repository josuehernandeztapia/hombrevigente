# 04 · Financiero (CORE)

## Lo real y reutilizable
`blueprint/core/financial-engine.js`: solver IRR (Newton-Raphson), churn dinámico por cohorte, LTV = margen/churn, LTV:CAC mezclado, payback, terminal value. **La metodología es correcta**; las constantes hardcodeadas son las que fallan.

## Supuestos núcleo (a reconciliar — hay contradicciones en el repo)
- CAPEX: rango canónico $1.98-2.9M MXN (post Imaging Module) **pero ignora ~$3.75M de remodelación** → all-in real ≈ **$6.9M/clínica**.
- Membresía: SSOT $200-1,000/mes @ 50% **vs** modelo $1,400 Access / $3,800 Elite @ 35%/15% → **irreconciliable, elegir uno**.
- Márgenes: HIFU hasta 86%; pisos RiskGuard ≥50% cirugía / ≥30-40% otros.
- Seed: ~$200-250K USD (~$4M MXN), break-even objetivo mes 9.

## Banderas (arreglar antes de mostrar a inversionista)
- 3 sistemas de arquetipos (4/5/20); LTV de "Carlos" = $32K/$43K/$100K según archivo.
- LTV:CAC 12-73x ("unicornio") → señala CAC/churn ficticios.
- ARPU "$22K" suma ~$14K. 3 múltiplos de salida distintos (8x/10.6x/15x). Bug de interés en deuda. Sculptra recompra cada 1.25 meses (typo).

## Acción
Reconstruir el modelo desde `financial-engine.js` con: 1 set de arquetipos, 1 esquema de membresía, CAPAX all-in, supuestos sourceados, 1 múltiplo de salida. Bottom-up (suscriptores × ARPU × retención).
