# Agentes IA — Valor de Desarrollo (qué construir, qué comprar, qué diferir)

**No es auditoría de autenticidad — es priorización de construcción · Junio 2026**

> Aclaración: los "9 agentes + simulaciones" del repo eran **andamiaje para empezar a construir**, no algo para presentar a un fondo como terminado. La pregunta correcta no es "¿es real?" sino **"¿vale la pena desarrollarlo, y en qué orden?"** — bajo una tesis **AI-native** (el negocio se opera con el loop de datos, no con features sueltas).

---

## El lente: ¿cuál es el problema REAL del negocio?

Tu ejemplo lo clava. La física del negocio de aparatología/estética:
- **Margen altísimo por procedimiento** (HIFU 70-86%) ✅ — *no es el problema*.
- **CapEx alto** (equipo caro) → si la máquina está ociosa, el margen no importa. ❌
- **Negocio transaccional** → baja rotación/retención = muerte lenta. ❌

→ **Los 3 cuellos de botella reales son: RETENCIÓN, UTILIZACIÓN del equipo, y PROTECCIÓN de margen.** El valor de cada agente se mide por **cuánto mueve uno de esos tres**. Lo que solo da "wow" (no mueve ninguno) es lujo, no prioridad.

**AI-native de verdad ≠ 9 agentes bolt-on.** Es **un solo loop de datos**: Diagnóstico → Recomendación → Reserva → Seguimiento → Re-enganche, que aprende. Los "agentes" son funciones de ese loop. Construyes el loop + las 2-3 funciones que mueven retención/utilización/margen; el resto se compra o se difiere.

---

## Matriz de valor

| Agente | Problema real que ataca | ¿Mueve un constraint? | Build / Buy / Defer | Cuándo |
|--------|------------------------|----------------------|---------------------|--------|
| **ChatVigente** (RAG concierge) | Conversión, educación, servicio 24/7, re-enganche | ✅ Retención + conversión | **BUILD (ya existe)** — pulir | **Ya** |
| **PersonaVigente** (segmentación/recomendación) | Qué ofrecer a quién → upsell + retención | ✅ Retención + ticket | **BUILD ligero** (reglas+LLM, crece con datos) | **Ya (v1 simple)** |
| **OptiVigente** (agenda/precio dinámico) | Llenar el equipo caro; revenue por slot | ✅✅ **Utilización** (el constraint #1 del capex) | **BUILD por fases** (reglas → MILP con volumen) | v1 reglas pronto; MILP a escala |
| **RiskGuard** (pisos de margen + viabilidad) | No regalar margen; decidir descuentos | ✅ **Margen** | **BUILD la parte de pisos** (reglas, barato); la parte Z-Score/Monte Carlo = **hoja de cálculo, no agente** | Pisos: ya. Viabilidad: 1 vez |
| **DiagnosticoVigente** (térmico+RGB) | Gancho de adquisición + diferenciación + **data moat** | ✅ Adquisición + foso de datos | **BUILD (es tu IP)** — pero con cuidado (ver Finding térmico) | Fase MVP-1 |
| **AssetVigente** (inventario/insumos) | Eficiencia de ops, mermas | 🟡 Marginal a 1 sede | **DEFER / comprar** (un POS/inventario estándar) | A escala |
| **SafetyVigente** (predicción de incidentes) | Seguridad clínica | 🟡 Lo resuelve SOP + médico, no ML (sin datos) | **DEFER** (SOPs primero) | Post-datos |
| **Virtual Try-On** (GAN estética) | "Wow" / conversión visual | 🟡 Wow, no mueve retención/utilización directo | **BUY** (Perfect Corp/ModiFace ya lo hacen) | Si acaso, comprado |
| **AdvisorVigente** (asesor financiero) | Decisiones de negocio | 🟡 Ya cubierto por `financial-engine.js` | **DEFER** (no es agente, es tu modelo) | — |

---

## El "AI-native core" (lo mínimo que crea el flywheel)

Si solo construyes **3 cosas**, que sean éstas — porque cierran el loop que ataca retención + utilización + margen:

1. **ChatVigente + PersonaVigente = el cerebro de relación.** Recomienda, educa, reserva, re-engancha. (Retención.) *Ya tienes el RAG.*
2. **OptiVigente v1 (reglas) = el cerebro de utilización.** Llena los huecos del equipo caro con la mezcla de servicios correcta y precio/descuento dinámico solo cuando hay capacidad ociosa. (Utilización + margen.) *Empieza simple, no MILP.*
3. **DiagnosticoVigente (térmico+RGB) = el gancho + el data moat.** Trae al cliente, diferencia, y **genera el dato propietario** que hace que 1 y 2 mejoren con el tiempo. (Adquisición + foso.)

**RiskGuard** vive dentro de OptiVigente como un guardarraíl simple (piso de margen), no como agente aparte.

Todo lo demás (AssetVigente, SafetyVigente, Virtual Try-On, AdvisorVigente) = **comprar o diferir**. No mueven los constraints en la etapa actual.

---

## La trampa AI-native a evitar

El error del repo no fue tener la visión de 9 agentes — fue **simularlos todos a la vez** en vez de construir el loop mínimo con datos reales. AI-native bien hecho = **1 loop, 3 funciones, datos reales desde el día 1** (vía MVP-0/concierge). Cada cliente real entrena el loop; eso es el foso. 9 agentes sintéticos no son foso; 1 loop con 200 clientes reales sí.

---

## Veredicto

- **Valiosos para construir:** ChatVigente (✅ ya), PersonaVigente (ligero), OptiVigente (por fases — es el que más valor crea dado tu capex), DiagnosticoVigente (tu IP/foso).
- **Guardarraíl, no agente:** RiskGuard (pisos de margen = reglas).
- **Comprar:** Virtual Try-On (Perfect Corp/ModiFace).
- **Diferir:** AssetVigente, SafetyVigente, AdvisorVigente.

El orden lo dicta el constraint: **utilización y retención primero** (OptiVigente + Chat/Persona), porque ahí es donde tu margen alto se convierte (o no) en negocio. El diagnóstico térmico es el gancho y el foso de datos que hace que todo lo demás mejore.

---
*Valoración estratégica de prioridad de construcción. No es código ni due diligence financiera.*
