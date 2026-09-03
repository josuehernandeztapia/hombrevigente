# Panel de Biomarcadores — Optimización (Interpretación educativa)

**Categoría**: Diagnóstico / labs  
**Avenida HV**: 1 (interpretación) / 2 si deriva Rx  
**Evidencia predominante**: E3–E4 (por marcador)  
**Tags**: labs, biomarcadores, BloodGPT, hs-CRP, IGF-1, HbA1c

---

## 📋 Definición

Guía para el Motor de Justificación: cómo **interpretar labs** en lenguaje de optimización, sin diagnosticar patología. Alineado con panel del protocolo fundador y Function Health / Lifeforce como referentes de mercado.

---

## 🔬 Panel recomendado HV (educativo)

### Metabólico
| Marcador | Optimización (educación) | Tier referencia |
|----------|--------------------------|-----------------|
| **Glucosa ayunas** | Control glucémico, eje insulinotrópico | E4 |
| **HbA1c** | Tendencia 3 meses; <5.7% contexto población | E4 |
| **Insulina ayunas** | Resistencia insulínica temprana | E3–E4 |
| **Quantose RI / HOMA-IR** | Sensibilidad insulina (si disponible) | E3 |
| **Leptina** | Señal adiposidad/inflamación; alta con IMC bajo = investigar contexto | E3 |

### Inflamación
| **hs-CRP** | Inflammaging proxy | E3 |
| **IL-6** | Investigación / algunos labs premium | E3 |

### Hormonal / anabólico
| **IGF-1** | Eje GH; monitoreo si secretagogos (Av.2) | E4 |
| **Testosterona total/libre** | Vitalidad masculina; rango edad | E4 |
| **DHEA-S** | Eje adrenal edad | E3 |
| **TSH, T4 libre** | Tiroides | E4 |

### Seguridad
| **AST, ALT, GGT** | Hepático | E4 |
| **Creatinina, eGFR** | Renal (importante con litio) | E4 |
| **PSA** | Hombres >40 screening | E4 guías |
| **Litio sérico** | Si usuario en litio — **médico psiquiatra** | E4 |

### Longevidad avanzado
| **Reloj epigenético** | TruAge, DunedinPACE | E3 |
| **NAD+ plasmático** | Investigación | E3 |
| **ApoB, Lp(a)** | Riesgo cardiovascular longevidad | E4 |

### Oncología screening
| Marcadores según edad/sexo | **No sustituye oncólogo** | E4 |

---

## 🏷️ Plantilla Motor de Justificación

```
DATO: hs-CRP 2.8 mg/L (usuario)
CONTEXTO: Por encima de óptimo poblacional ideal <1 mg/L en prevención agresiva (E3)
MECANISMO: Asociado a inflammaging en literatura (E1, PMID 24833586)
EDUCACIÓN: Estrategias con evidencia de modulación incluyen sueño, ejercicio, omega-3 (E4)
AVENIDA 1: Stack antiinflamatorio nutricional (NMN, resveratrol — E2)
AVENIDA 2: Si persiste + síntomas → médico
DISCLAIMER: [estándar 00_MARCO]
```

---

## 🔗 Integración BloodGPT (buy)

Parseo PDF labs → estructura → RAG. Validar valores con rangos de laboratorio del reporte original.

---

## ⚠️ Límites

- Un lab fuera de rango ≠ enfermedad sin clínico.
- **Litio 0.42** (ejemplo fundador) = subterapéutico → **solo psiquiatra interpreta**.

---

## 📖 FAQ

**¿Cuánto cobrar interpretación?**  
Ver Blueprint (referencia interna, verificar precio vigente antes de citarlo): Valoración Vigente $1,490–2,490 MXN.

---

## Evidencia reciente (Pulso Vigente)

### Evidencia reciente (Pulso Nº001 · 2026-06-09)
- **Accionable — Una sola inyección reescribe tu colesterol (y ya pasó en humanos)** — *NEJM 2026, NEJMoa2601283* · E2.
  - Lo más cerca de un "one-and-done" para el colesterol — pero en investigación, para perfiles específicos. **Lo que SÍ puedes mover hoy:** tu **ApoB** es de los marcadores de mayor evidencia para riesgo cardiovascular. Mídelo, conoce tu número, trabájalo con dieta/ejercicio y —si aplica— lo que tu médico indique.
  - Límite: en investigación / preclínico; no establece efecto en personas.

### Evidencia reciente (Pulso Nº005 · 2026-07-02)
- **Los polifenoles no bajan tu colesterol total, pero sí lo que importa** — *Eur J Nutr, 2026-06-29. PMID 42371155. DOI 10.1007/s00394-026-04027-2* · E3.
  - El estudio es en mujeres posmenopáusicas —extrapolación directa a hombres requiere cautela. Lo que sí aplica a cualquier perfil: **el número LDL-C no cuenta la historia completa**. La oxidación de LDL y el tamaño/densidad de partícula se asocian de forma más robusta con riesgo cardiovascular en la literatura. Si tu médico solo mide LDL-C, pregunta por **ApoB** y, si aplica, por LDL oxidado. Los polifenoles de fuentes alimentarias (cacao >85%, aceite de oliva virgen extra, berries, té verde) siguen siendo una palanca de bajo riesgo mientras la evidencia en hombres madura.

### Evidencia reciente (Pulso Nº006 · 2026-07-09)
- **Sin estatinas no significa sin opciones: lo que el ensayo CLEAR Outcomes dice sobre tu riesgo cardiovascular** — *JAMA Cardiol, 2026-07-01. PMID 42201706. DOI 10.1001/jamacardio.2026.1208* · E3.
  - La intolerancia a estatinas no es el fin del camino lipídico — es el inicio de una conversación más fina. Lo que sí puedes mover hoy: **conoce tu ApoB, no solo tu LDL-C**. El ApoB cuenta el número de partículas aterogénicas, no solo su contenido en colesterol; es el marcador de mayor valor predictivo en riesgo cardiovascular según la evidencia actual. Si eres intolerante a estatinas, la conversación con tu médico sobre alternativas (bempedoico, inhibidores PCSK9, inclisirán) parte de ese número. Sin él, navegas a ciegas.

### Evidencia reciente (Pulso Nº007 · 2026-07-16)
- **El colesterol "malo" tiene un nuevo mapa de gestión (y PCSK9 está en el centro)** — *Semergen, 2026-07-07. PMID 42413166. DOI 10.1016/j.semerg.2026.102799* · E3.
  - Los inhibidores de PCSK9 son herramientas en investigación clínica activa y de uso médico supervisado — no son suplementos de libre acceso. **Lo que SÍ puedes mover hoy:** conoce tu **ApoB**. Es uno de los marcadores con mayor respaldo en la literatura para riesgo cardiovascular a largo plazo y está disponible en un panel de laboratorio estándar. Si tu médico solo te reporta LDL-C, pide que agreguen ApoB y Lp(a) a tu próximo perfil lipídico. La optimización empieza con el número correcto.

### Evidencia reciente (Pulso Nº008 · 2026-07-23)
- **Dapagliflozin y el perfil de VLDL: lo que el estudio cinético revela sobre tus lípidos** — *Diabetologia, 2026-07-17. PMID 42467086. DOI 10.1007/s00125-026-06810-6* · E3.
  - Este es un estudio cinético mecanístico —no un ensayo de eventos cardiovasculares— así que las conclusiones son sobre metabolismo de partículas, no sobre reducción de riesgo clínico. Lo que sí puedes mover hoy, independientemente de si tomas o no un SGLT2: **conoce tu ApoB y tu perfil de VLDL**. El número de partículas (ApoB) tiene mayor poder predictivo que el LDL-C calculado. Si tu médico ya te tiene en un SGLT2, este estudio añade contexto metabólico positivo al perfil lipídico; si no, no es razón para buscarlo. La palanca universal sigue siendo: entrenamiento de resistencia + zona 2 + control de carbohidratos de absorción rápida.

### Evidencia reciente (Pulso Nº009 · 2026-07-30)
- **Las estatinas y la inflamación sistémica: lo que el perfil lipídico no te cuenta solo** — *Autoimmun Rev, 2026-07-29. PMID 42526780. DOI 10.1016/j.autrev.2026.104153* · E3.
  - Este estudio no habla de hombres sanos en optimización, pero sí refuerza un principio operativo de alta evidencia: **ApoB + marcadores inflamatorios (hsCRP, IL-6 si aplica) forman un dúo más informativo que el LDL aislado**. Si tu médico solo mide LDL, pide el panel completo. La inflamación de bajo grado —sin diagnóstico autoinmune— es uno de los pilares del envejecimiento acelerado (*inflammaging*). Mide, conoce tu número, actúa con tu médico.

### Evidencia reciente (Pulso Nº010 · 2026-08-09)
- **Los inhibidores de PCSK9 y la inflamación: más que colesterol** — *JACC Asia, 2026-08-01. PMID 42554391. DOI 10.1016/j.jacasi.2026.05.033* · E3.
  - El colesterol LDL sigue siendo el objetivo principal, pero la narrativa se complejiza: el riesgo cardiovascular es también un problema inflamatorio crónico. **Lo que sí puedes mover hoy:** conoce tu **ApoB** (marcador de partículas aterogénicas totales, con mayor resolución que el LDL-C clásico) y tu **hsCRP** (proxy de inflamación vascular de bajo grado). Ambos son accesibles en laboratorio de rutina. La optimización de lípidos e inflamación no son rutas separadas — se estudia que convergen.
