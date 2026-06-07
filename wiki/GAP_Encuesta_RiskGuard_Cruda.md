# GAP RESCATADO · Encuesta cruda + Modelo RiskGuard/OptiVigente

**Fuente:** Drive "Encuesta final, ajustada a HombreVigente RiskGuard AI.docx" (solo el resumen estaba en el SSOT). Reconstruido junio 2026.

## Contexto del instrumento
Club de cuidado masculino en **Querétaro (Centro, cerca de Bernardo Quintana)**. Target del instrumento: ~300 respuestas en esta plataforma; **el total real recolectado fue N=442 combinando dos plataformas distintas.** 1,000 escenarios Monte Carlo. CAPEX modelado: **5 MDP**, equipo mixto, margen bruto 50% cirugías, descuentos -15%/-25%, recuperación <3 años.

## Instrumento (Google Forms, ~5 min)
**S1 Demografía:** edad [30-40/41-50/51-60]; ingreso [<$500K / $500K-$1M / >$1M MXN].
**S3 Servicios y pricing** (interés 1-5 + ¿cuánto pagarías?):
| Servicio | Evidencia citada | Opciones de precio (MXN) |
|----------|------------------|--------------------------|
| Botox | 95% mejora (JAMA Dermatology 2016) | 2,125 / 2,400 / 2,750 / 3,400 |
| Corte de pelo | 95% satisfacción | 255 / 290 / 340 / 380 / 425 |
| Blanqueamiento LED | 88% (J. Dentistry 2017) | 2,125 / 2,300 / 2,550 / 2,725 / 2,975 |
| Depilación láser (hombros/espalda) | 85% reducción | 1,700 / 1,875 / 2,125 / 2,375 / 2,550 |
| Blefaroplastía | 92% (Aesthetic Surgery J. 2019) | 17,000 / 19,125 / 21,375 / 23,375 / 25,500 |
| HIFU | 90% (Dermatologic Surgery 2014) | 2,550 / 2,900 / 3,400 / 3,750 / 4,250 |
**S4 Ubicación:** ¿Centro/Bernardo Quintana? · accesibilidad (oficinas/casa/gym).
**S5 Cultura:** ¿cuidar imagen empodera? (1-5) · ¿compartir experiencias con otros hombres? (1-5).

## Logística
Canales: Instagram (@HombreVigente $1,000) + LinkedIn ($500) + WhatsApp ($500). Costo $2-5K MXN. Incentivo: diagnóstico gratis ($500) a primeros 50.

## Modelo "RiskGuard AI" (Fase 0) — pseudocódigo conservado
Híbrido **Altman Z-Score + Monte Carlo**, optimizado con OptiVigente.
- `calcularZScore(capex, opex, ingresos)`: Z = 0.717·(WC/AT) + 3.107·(EBIT/AT) + 0.998·(ventas/AT); EBIT = ingresos·0.65.
- `simularMonteCarlo(renta, demanda, inflación, desempleo, n=1000)`: ingresos ~N(base,10%) − costos ~N(base,10%); riesgo = P(resultado<0).
- `optimizarUtilizacion(mezcla, cap_equipos, cap_personal, demanda, desc=[-0.15,-0.25])`: descuento dinámico si utilización <80%; piso de margen 50% (cirugía con cogs = 50% del precio).
- `evaluarUbicacion(...)`: viable si puntuación demanda >70, recuperación <36 meses, riesgo quiebra <10%.

**Datos de ejemplo:** renta QRO $40,000/mes; demanda 109,875; CAPEX $5M; mezcla {Botox 0.3, Depilación 0.2, Corte 0.2, Blanqueamiento 0.15, Blefaroplastia 0.15}.

## Tech stack Fase 0 (lo que realmente se planeó, lean)
Google Forms (front) → Python/Colab + NumPy (Z-Score, Monte Carlo, OptiVigente) → Google Sheets (datos). Google Cloud free tier.

## Notas de honestidad
- N=442 real (dos plataformas). Mide **interés + disposición a pagar declarada**, no compra transada.
- Los servicios son **estéticos** (Botox/HIFU/blefaro/depilación) — confirma que el negocio validado es estética masculina, no longevidad/péptidos.
