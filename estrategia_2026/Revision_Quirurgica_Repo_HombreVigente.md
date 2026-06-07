# Revisión Quirúrgica — Repo `josuehernandeztapia/hombrevigente`

**Due diligence honesta de meses de trabajo · Junio 2026**

> Revisé el SSOT completo (v1.2), el código (backend Python + blueprint JS), el modelo financiero (modelofinanciero.html V53.1) y la knowledge base. Esto es lo que hay de verdad, qué vale, qué está frágil, y cómo se reconcilia con la dirección de longevidad.

---

## 1. Qué ES el repo, en realidad

**No es un proyecto de longevidad/péptidos.** Es un **club/clínica de estética masculina premium ("Wellness Club Masculino + AI-native", modelo "Clinic-in-a-Box")**. El catálogo real son **procedimientos estéticos + grooming + cirugía menor + dental**: HIFU, Botox, fillers, Sculptra, láser CO2, RF microneedling, PRP, depilación, corte/barba, blefaroplastia, bichectomía, lipo de papada. **Cero péptidos, cero hormonas, cero NAD+, cero GLP-1.**

Tesis central (válida y afilada): el hombre odia peregrinar entre barbero + clínica + dentista; quiere **un solo lugar premium, simple, orientado a resultados**. Modelo: clínica física (CDMX/QRO, 250 m²) + membresía CLUB (MRR) + línea DTC, con sueño de licenciar "Clinic-in-a-Box" como SaaS/franquicia en Fase 3.

---

## 2. Los activos REALES (lo que vale y se conserva)

1. **La insight de dolor del cliente es real y defendible.** Fragmentación → "todo en un lugar". Es el wedge más sólido del proyecto y sobrevive cualquier pivote.
2. **Encuesta N=442 (real).** ~85% de interés en el concepto, ~50% sensibles a precio, ~28% prefieren pagos diferidos. Es la única evidencia empírica genuina — valida **interés/demanda**, no economía.
3. **Knowledge base clínica (real y buena).** 26 servicios documentados con rigor técnico (mecanismo, fases, profundidades). IP reutilizable. *Caveat:* 11 de 33 archivos tienen tags "[VALIDAR CON DR.: qué máquina/qué marca]" → la clínica es **pre-operativa**, el KB lo escribió un LLM antes de existir la clínica.
4. **Pipeline RAG funcional (real).** OpenAI `text-embedding-3-small` + Pinecone + GPT-4o-mini sobre 319 chunks. `test_results_rag.json` muestra respuestas reales con precios correctos. **Es el mejor pedazo de ingeniería del repo y es portable** (cambias el KB por monografías de péptidos/protocolos y re-embebes).
5. **`financial-engine.js` (real, joya escondida).** Solver IRR Newton-Raphson, churn dinámico por cohorte, LTV=margen/churn, LTV:CAC mezclado, payback, terminal value. **La *metodología* es correcta y reutilizable** — lo que está mal son las *constantes* hardcodeadas.
6. **Conciencia regulatoria por encima del promedio.** Nombra las NOMs correctas, COFEPRIS "Ruta de Equivalencia", quirófano Clase II. Naíf en *tiempos*, no en *existencia* del régimen.
7. **Branding y front-end fuertes.** HTML pulidos, demo Three.js, estética coherente ("El Poder de Ser Vigente").

---

## 3. Las banderas rojas (lo que hay que mirar de frente)

> Esto no es para desanimar — es lo que un inversionista con due diligence encontrará en minutos. Mejor saberlo nosotros primero.

**Narrativa vs realidad:**
1. **Los "9 agentes de IA propietarios" son specs + mocks, no software.** El código mismo lo admite ("MOCK Agent v3.0"): son reglas de Python + `random.uniform()`. El "diagnóstico CNN+térmico" es una *simulación de front-end* con `time.sleep()` fingiendo procesamiento. No hay modelos entrenados ni datos reales. (Su propio doc costea construirlos en ~$205K USD.)
2. **Los datos "validados" son sintéticos.** Generador Faker (seed=42): 5,000 clientes y 10,000 eventos inventados. Los archivos `arquetipos_validados.json` / `servicios_fase1_validados.json` son *semillas de entrada*, no salidas de validación. Lógica circular: supuestos entran → "resultados" salen.
3. **La wiki está vacía.** **72 de 72 archivos .md = 0 bytes.** Y la síntesis para inversionistas cita números precisos ("95.7% disposición a pagar premium", "90.7% intención de compra") con referencias a líneas de esos archivos vacíos. → Estadísticas sin fuente.
4. **"93.6% PMF validado" es intención declarada, no PMF.** Es interés post-descripción del concepto. No hay conversión, depósitos, waitlist ni piloto. (Nota: las cifras 85.08% y 93.6% **no son contradicción** — la encuesta se corrió en **dos plataformas distintas** hasta N=442; cada una arrojó su propio % de interés. Lo que falta no es muestra, es señal *conductual*.)

**Modelo financiero (se contradice solo):**
5. **3 sistemas de arquetipos incompatibles** (4 vs 5 vs 20); "Carlos" tiene LTV de $32,085 / $43,000 / $100,000 según el archivo.
6. **LTV:CAC de 12-73x** ("ratios unicornio"). Un 73x no es fortaleza — le grita al inversionista que el CAC es ficticio.
7. **Aritmética rota del ARPU:** "$22K por cliente" suma mal (mezcla WoM de adquisición con revenue; da ~$14K, no $22K).
8. **CAPEX subcontado:** el doc dice "~$3.2M" (solo equipo) e ignora la remodelación de **$3.75M** (250 m² × $15K). Real all-in ≈ **$6.9M/clínica**.
9. **Membresía 2-4x distinta** entre SSOT ($200-1,000/mes) y modelo ($1,400 Access / $3,800 Elite). El revenue de membresía se contradice dentro del *mismo* doc ($840K vs $6.36M/año).
10. **Salida $403M / IRR 65.4% / múltiplo:** tres múltiplos de salida distintos (8x slider, 10.6x texto, 15x código). Bug de interés (cobra 20% sobre toda la deuda). Sculptra con recompra cada **1.25 meses** (typo → infla LTV premium). Cirugía con adherencia 0.95 para *todos* (un cazador de ofertas no se hace una blefaroplastia el 95% de las veces).

**Riesgo regulatorio subestimado:**
11. **BNPL = préstamo no licenciado.** "RiskGuard AI aprobando crédito" es actividad financiera regulada (SOFOM/buró). Tratado como un toggle de precio.
12. **Cirugía ambulatoria con cirujano "fly-in" 50/50** → responsabilidad, continuidad de cuidado, responsable sanitario COFEPRIS — sin abordar.
13. **Datos biométricos de salud (RGB+térmico) a BigQuery** sin DPIA ni tratamiento LFPDPPP. La categoría de privacidad más riesgosa, tratada como checkbox.

**Timeline:**
14. SSOT fechado jul-2025 planeaba lanzar **ago-2025**, pero su propia ruta regulatoria *fast-track* tarda **5-11 meses**. Imposible desde el día 1. A junio-2026 no hay evidencia de clínica viva en el repo.

---

## 4. Reconciliación con la dirección de longevidad

**Pregunta clave: ¿pivote total, o integración?**

Honestamente, **el repo (estética) es el negocio MÁS aterrizado de los dos**, no el menos:
- Botox/fillers/HIFU son **legales, de alto margen (70-86%), con demanda validada** y proveedores claros.
- Péptidos de longevidad son el **diferenciador**, pero **regulatoriamente más difíciles** en México (zona gris, receta, claims). El pivote a "puro longevidad D2C" sería *más* arriesgado, no menos.

**Lo que transfiere de un lado al otro (≈30% del repo):**
- ✅ Brand "Hombre Vigente" + la insight de dolor + la encuesta N=442.
- ✅ El pipeline RAG (cambias KB estético por protocolos/péptidos).
- ✅ El `financial-engine.js` (metodología agnóstica al producto).
- ✅ El framework de datos sintéticos (para modelar cohortes D2C).
- ✅ El modelo híbrido (la clínica/club física = el "lounge" que venimos diseñando).

**Lo que NO transfiere (≈70%):** quirófano, cirugía, dental, el edificio de 9 agentes, el trabajo COFEPRIS de importación de equipo, el layout de 250 m².

**La síntesis que tiene sentido:** no es "estética O longevidad". Es **un club de estética regenerativa masculina (núcleo legal, alto margen, validado) CON longevidad/optimización como capa premium diferenciadora** — usando el **mismo lounge físico** y el **mismo motor de IA/diagnóstico**. La estética paga las cuentas; la longevidad es el foso y el "wow". El MVP-0 concierge que diseñamos es el antídoto exacto a la enfermedad #1 del repo: **reemplazar datos sintéticos por comportamiento real.**

---

## 5. Veredicto y recomendación

**Lo que lograste en meses:** un **andamiaje narrativo + de marca excelente, algo de código real y reutilizable (RAG + motor financiero), y una insight de dolor validada.** Lo que NO lograste todavía: un negocio validado con comportamiento real, ni un producto que funcione. Eso está bien — es normal en esta etapa. El problema sería *creer* que ya está validado cuando no lo está.

**Keep / Fix / Kill:**

| Mantener | Arreglar | Matar / archivar |
|----------|----------|------------------|
| Brand + insight de dolor | Colapsar 3 arquetipos → 1 | "9 agentes IA" como claim |
| Encuesta N=442 (como interés) | Aritmética ARPU/LTV/CAPEX | "validado/PMF" sin datos reales |
| RAG pipeline (re-KB) | Múltiplos de salida (uno solo) | Wiki vacía (72 archivos) |
| financial-engine.js (método) | Sculptra 1.25m, adherencia cirugía | Cirugía fly-in (replantear) |
| Modelo híbrido / lounge | Lenguaje "production-ready" | TAM inflado/sin fuente |
| Conciencia regulatoria | BNPL → estructura legal real | Stack sobre-ingenierizado (Kafka, etc.) |

**Las 3 acciones de mayor impacto ahora:**
1. **Decide el núcleo:** estética regenerativa (aterrizado) + longevidad como capa premium — un solo relato, un solo lounge.
2. **Consigue 1 dato real** (MVP-0 concierge): 5-10 clientes pagando reemplazan 5,000 sintéticos en credibilidad.
3. **Limpia la narrativa de inversión:** quita todo lo "validado/production-ready/9 agentes" que no resista 10 minutos de due diligence. La honestidad calibrada vende más que el unicornio de papel.

---

*Revisión basada en lectura directa del repo (commit único `d23555b`). Sin acceso a sistemas en vivo. No es consejo legal/financiero.*
