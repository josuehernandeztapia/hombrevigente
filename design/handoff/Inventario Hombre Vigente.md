# Hombre Vigente — Inventario de flujos, assets y copy

> Documento de referencia. Lista todos los entregables en orden del journey, su uso y el **texto exacto** de cada pantalla.
> Marca: dark club premium · negro #08080A · **acento bronce #C6A06A** (base noir) · Montserrat + IBM Plex Mono · grano de película + glow.
> **TM:** la marca registrada es **Hombre Vigente™** — NO "Índice Vigente". Los scores (68/64) son **ilustrativos** hasta que el modelo del Índice exista.
> Compliance de origen: lenguaje de optimización/bienestar, "no es diagnóstico", el médico firma.
> Microcopy legal global (footer de pantallas con dato de salud): **"Optimización y bienestar. No sustituye atención médica."**
> Rev. junio 2026: evidencia en lenguaje plano (Fuerte/Moderada/Emergente) + PMIDs · médico/cédula etiquetados como ejemplo · ajustes Rx framados como "el médico aprueba".

---

## 🗺️ Mapa Vigente.html — índice del producto
**Tipo:** web de escritorio · **Uso:** índice navegable; cada tarjeta abre su prototipo.

- Eyebrow: `Mapa del producto · México`
- Título: **Hombre Vigente**
- Lede: *"El journey completo de longevidad gestionada, de punta a punta. Cada tarjeta abre su prototipo en el teléfono. Recórrelo en orden o salta a cualquier flujo."*
- Etapas: **01 Captación** · **02 Diagnóstico** · **03 Conversión** (Ruta A sin receta · Ruta B médica) · **04 Recurrencia** · **✦ Transversal** (Confianza · Canal)
- Footer: *"Prototipos de diseño en bronce (noir + acento). Contenido ilustrativo. No es diagnóstico ni tratamiento médico — la Avenida 2 requiere valoración y firma de un médico responsable."*

---

## 01 · CAPTACIÓN

### Landing Vigente.html
**Tipo:** web pública · **Uso:** posicionamiento "longevidad gestionada" + captación → WhatsApp.

- Tesis / hero: **"No te vendemos un vial. Te damos un plan con médico."**
- CTA principal: **"Hacer mi Escaneo gratis"** → abre `Onboarding Vigente.html`
- CTA contacto: WhatsApp prellenado
- Secciones: tabla comparativa (mercado gris vs. clínica US vs. Vigente) · loop de 6 pasos (*"el software justifica; el médico firma"*) · Programas con routing Av.1/Av.2 · térmico como **ΔT adjunto** (no diagnóstico) · Caso #1 · disclaimer legal completo en footer.
- Acento: bronce (recoloreado de azul/índigo original).

---

## 02 · DIAGNÓSTICO

### Onboarding Vigente.html — 7 pantallas
**Tipo:** app móvil · **Uso:** diagnóstico que genera el Índice Vigente y rutea a Av.1/Av.2.
**Marca:** el ™ va en **Hombre Vigente™** (la marca), no en "Índice Vigente". **Scores ilustrativos** hasta que exista el modelo.
**Variantes (Tweaks):** UX del paso 3 → Guiado / Tablero / Chat.

**Pantalla 01 — Bienvenida**
- Sobre el título: `Continúas tu conversación de WhatsApp`
- Eyebrow: `Onboarding · Guiado`
- Título: **"Empecemos por los datos, no por opiniones"**
- Sub: *"En 7 pasos construimos tu Índice Vigente: una lectura objetiva de tu punto de partida. Con eso, un protocolo personalizado y, si tu caso lo amerita, la valoración de un médico."*
- Bullets:
  - `Tus datos, no promedios`
  - `Evidencia citada, no marketing`
  - `Un médico responsable detrás`
- CTA: **Comenzar**
- Footer: *"Información de optimización y bienestar. No es diagnóstico ni tratamiento médico."*

**Pantalla 02 — Consentimiento / Privacidad**
- Eyebrow: `Tus datos · Tu control`
- Título: **"Antes de empezar, lo importante"**
- Sub: *"Vas a compartir datos de salud (labs, foto, wearable). Son sensibles y los tratamos como tal."*
- Checkboxes (los 3 obligatorios):
  - `Acepto que mis datos se usen para generar mi protocolo de optimización.`
  - `Entiendo que un médico responsable revisa mi caso cuando aplica.`
  - `He leído el Aviso de Privacidad: cifrado, almacenamiento y cómo borrar mis datos cuando quiera.`
- Nota: *"Nunca vendemos tus datos. Puedes revocar tu consentimiento y eliminarlos en cualquier momento."*
- CTA habilitado: **Acepto y continúo** / deshabilitado: `Marca los N restantes`

**Pantalla 03 — Tu historial**
- Eyebrow: `Tus fuentes · Mínimo 2`
- Título: **"Tu historial"**
- Sub: *"Sube tus datos objetivos. Mientras más fuentes, mejor tu protocolo. Con 2 empezamos."*
- Fuentes (acción → estado "✓ Listo"):
  - **Foto de rostro** · `Computer Vision · glow, textura, daño solar` · acción **Subir**
  - **PDF de laboratorio** · `hs-CRP · glucosa · IGF-1 · panel` · acción **Subir**
  - **Conectar wearable** · `Oura · Whoop · HRV, sueño, recuperación` · acción **Conectar**
- CTA: **Continuar** / deshabilitado: `Sube N fuentes más`
- Footer: *"Foto de cuerpo, opcional. La foto se analiza para piel y optimización, no para diagnóstico."*

**Pantalla 04 — Cuestionario**
- Eyebrow: `2 min · Tu contexto`
- Título: **"¿Qué quieres mover?"**
- Sub: *"Esto afina la prioridad de tu protocolo. Sé honesto, nadie más lo ve."*
- Objetivo principal (multi): `Energía` · `Recomposición` · `Recuperación` · `Piel` · `Longevidad general`
- Campo: `Medicamentos o antecedentes a considerar` (placeholder "Escribe aquí…")
- Opción: **Prefiero hablarlo con el médico**
- Hábitos (escala Bajo/Medio/Alto): `Sueño` · `Ejercicio` · `Alcohol` · `Estrés`
- CTA: **Guardar y seguir**
- Footer: *"Si marcas medicamentos o antecedentes, tu caso pasa a revisión médica antes de cualquier recomendación de prescripción."*

**Pantalla 05 — Análisis**
- Eyebrow: `Procesando · Con evidencia`
- Título: **"Analizando tu Índice Vigente"**
- Líneas rotativas:
  - `Leyendo tus biomarcadores…`
  - `Cruzando con tus señales de wearable…`
  - `Buscando la evidencia que aplica a ti…`
- Footer: *"Cada recomendación se justifica con literatura real. Donde no hay evidencia suficiente, te lo decimos."*

**Pantalla 06 — Tu Índice Vigente**
- Eyebrow: `Tu lectura · Informe de optimización`
- Título: **"Tu Índice Vigente"** · Score: **68 / 100** *(ilustrativo — modelo aún no construido)*
- Sub: *"Tu lectura de partida — un punto de referencia para optimizar y volver a medir. No es un diagnóstico médico."*
- "Punto de partida": *"4 señales clave para optimizar. Volvemos a medir en 8 semanas."*
- Señales (lectura · nota · evidencia · "por qué importa"):
- Señales (lectura · nota · "por qué importa"; **sin tag de evidencia** — un valor de lab no tiene nivel de evidencia):
  - **hs-CRP** · `Rango superior` · Inflamación a vigilar — *"Marca inflamación sistémica de bajo grado. Baja con sueño, omega-3 y movimiento constante."*
  - **HRV** · `48 ms · baja` · Recuperación a mejorar — *"Señal de estrés autonómico. Responde a higiene de sueño y a dosificar la carga de entrenamiento."*
  - **Glow facial** · `62 / 100` · Textura y daño solar moderados — *"Optimizable con rutina de piel, fotoprotección y antioxidantes tópicos."*
  - **Glucosa** · `En rango` · Base metabólica estable — *"Buen punto de partida metabólico. El objetivo aquí es mantener."*
- CTA: **Ver mi plan**
- Footer: *"Las áreas marcadas no significan enfermedad; son oportunidades de optimización."*

**Pantalla 07 — Tu siguiente paso (routing)**
- Eyebrow: `Tu protocolo · Personalizado`
- Título: **"Tu camino Vigente"**
- Sub: *"Según tus datos, este es el siguiente paso."*
- **Ruta A · la mayoría — Optimización:** *"Hábitos + Stack Vigente (suplementos, sin receta)."* · chips: Hábitos guiados · Stack Vigente · Re-medición 8 sem · CTA sólido **"Empezar mi protocolo"** → `Conversion Vigente.html#programa`
- **Ruta B · si calificas — Valoración médica:** *"Tu caso amerita la revisión de un médico responsable antes de cualquier insumo de prescripción (vía magistral)."* · chips: Teleconsulta · Receta · Magistral · CTA secundario **"Agendar teleconsulta"** → `Teleconsulta Vigente.html`
- Footer: *"Ningún insumo de Avenida 2 se entrega sin valoración y firma de un médico. Puedes ajustar o pausar tu protocolo cuando quieras."*

---

## 03 · CONVERSIÓN

### Conversion Vigente.html — 4 pantallas (Av.1 · sin receta)
**Tipo:** app móvil · **Uso:** convertir lead → cliente (suplementos).
*(Entra directo a "Elegir programa" cuando llega desde la Ruta A vía `#programa`.)*

**Pantalla 1 — Resultado del Escaneo (gratis)**
- Eyebrow: `Tu lectura inicial · Gratis`
- Título: **"Tu Escaneo Vigente"** · Score: **64 / 100** *(ilustrativo)*
- Sub: *"Esto es tu punto de partida con los 3 datos que diste. La lectura a fondo viene en el diagnóstico completo."*
- Señales: `Inflamación · a vigilar` · `Recuperación · baja · HRV` · `Energía · optimizable`
- Mini-recomendación (chip "sin receta"): *"Tu prioridad es recuperación y energía. Empezamos sin receta, con tu Stack Vigente."*
- **Stack Vigente:** NMN · Omega-3 · Creatina · Vitamina D3 + K2 · Magnesio glicinato
- CTAs: **Activar mi protocolo** · **Hablar por WhatsApp**
- Footer: *"Lectura de optimización con 3 datos. No es diagnóstico médico."*

**Pantalla 2 — Elegir programa**
- Eyebrow: `Programas`
- Título: **"Elige tu profundidad"**
- Sub: *"Empezaste gratis. Subes según tu objetivo. Lo de prescripción, solo por la vía médica."*
- Tiers:
  - **Escaneo Vigente** · `Gratis` · "Ya lo completaste" (✓ hecho)
  - **Diagnóstico + Stack Vigente** · `$1,490 + $899/mes` · "Labs interpretados + protocolo + suplementos con COA" (recomendado)
  - **Membresía Vigente** · `$899–2,499/mes` · "Seguimiento, ajustes trimestrales, labs incluidos (Plus)"
  - **Protocolo Vigente Pro** · `Bajo prescripción` · "Teleconsulta + receta + magistral. Solo si calificas." (candado → médica)
- CTA: **Continuar con [programa]** / si Av.2: **Agendar valoración médica**
- Footer: *"La Avenida 2 (prescripción) requiere valoración y firma de un médico responsable."*

**Pantalla 3 — Checkout Av.1**
- Eyebrow: `Activación · Av. 1`
- Título: **"Tu protocolo"**
- Sub: *"Diagnóstico hoy + tu Stack Vigente mensual. Cancela cuando quieras."*
- Resumen: **Diagnóstico Vigente** `$1,490` (única vez) · "Labs interpretados + tu Índice" — **Stack Vigente** `$899/mes`
- Métodos de pago: `Tarjeta` · `SPEI` · `OXXO` · `Kueski · MSI`
- Opción: **Diferir el diagnóstico a 3 MSI (Kueski)**
- CTA: **Pagar y activar · $2,389 hoy**
- Footer: *"Pago seguro. Hoy: diagnóstico + 1er mes de Stack. Luego $899/mes hasta que canceles. No es medicamento."*

**Pantalla 4 — Confirmación**
- Eyebrow: `Protocolo activo`
- Título: **"Ya eres Vigente"**
- Sub: *"Tu diagnóstico está en proceso y tu Stack Vigente en camino. Esto es lo que sigue:"*
- Pasos:
  1. `Te escribimos por WhatsApp con tu protocolo en detalle.`
  2. `Tu Stack Vigente se prepara con COA y llega en 3–5 días.`
  3. `A las 4 semanas: tu primer check-in y ajuste con datos reales.`
- CTA: **Ver mi seguimiento** → `Seguimiento Vigente.html`

---

### Teleconsulta Vigente.html — 4 pantallas (Av.2 · vía médica)
**Tipo:** app móvil · **Uso:** vía de prescripción (mayor LTV, diferenciador legal).

**Pantalla 1 — Elegibilidad**
- Eyebrow: `Av. 2 · Vía médica`
- Título: **"Tu caso pasa por médico"**
- Sub: *"No todo se resuelve con suplementos. Cuando hay prescripción de por medio, decide y firma un médico responsable — no un bot."*
- "Por qué te rutamos aquí":
  - `Marcaste antecedentes a considerar en tu cuestionario.`
  - `Tu objetivo requiere insumo de prescripción (vía magistral).`
  - `hs-CRP fuera de rango — conviene criterio clínico.`
- Médico: **Dr. Andrés Lemus** `(ejemplo)` · `Medicina de longevidad · Responsable sanitario` · `Céd. Prof. 7 482 119` — *placeholder; pendiente responsable sanitario real*
- CTA: **Agendar valoración**
- Footer: *"Ningún insumo de Avenida 2 se entrega sin valoración y firma de un médico."*

**Pantalla 2 — Agendar teleconsulta**
- Eyebrow: `Teleconsulta`
- Título: **"Elige tu horario"**
- Sub: *"30 min por videollamada. El médico revisa tus datos antes de la cita."*
- Horarios: `Hoy 7:30 PM` · `Mañana 9:00 AM` · `Mañana 6:00 PM` · `Jue 11 8:00 AM`
- CTA: **Confirmar cita · $890**
- Footer: *"El costo de la teleconsulta se acredita a tu protocolo si continúas."*

**Pantalla 3 — Receta + Magistral**
- Eyebrow: `Receta · Magistral`
- Título: **"Tu protocolo Pro"**
- Sub: *"Tras tu valoración, el médico definió y firmó este protocolo. Se prepara bajo receta, no se importa gris."*
- Receta firmada (sello `Céd. Prof. 7 482 119`): **Protocolo magistral de reparación** · `Péptidos · reparación estructural y nerviosa` · BPC-157 · TB-500 · Goralatide
- Sello: *"Farmacia magistral · preparado con COA por lote"*
- Consentimiento (gate): *"Acepto la receta y el consentimiento informado de optimización con péptidos bajo supervisión médica."*
- CTA: **Activar protocolo Pro · $3,900/mes**
- Footer: *"Optimización bajo prescripción y supervisión médica. No sustituye atención médica integral. Médico y cédula mostrados son un ejemplo — pendiente responsable sanitario real."*

**Pantalla 4 — Confirmación**
- Eyebrow: `Protocolo Pro activo`
- Título: **"El médico ya está contigo"**
- Sub: *"Tu caso quedó bajo seguimiento clínico. Esto es lo que sigue:"*
- Pasos:
  1. `Recibes el enlace de tu teleconsulta por WhatsApp.`
  2. `Tras la valoración, el médico evalúa y firma tu receta.`
  3. `La farmacia magistral prepara tu protocolo con COA y lo envía.`
- CTA: **Ver mi seguimiento** → `Seguimiento Vigente.html`

---

## 04 · RECURRENCIA

### Seguimiento Vigente.html — 4 pantallas
**Tipo:** app móvil · **Uso:** retención y LTV real (data moat).

**Pantalla 1 — Dashboard**
- Estado: `Protocolo activo · Semana 4`
- Eyebrow: `Seguimiento con datos`
- Título: **"Vas avanzando"**
- Sub: *"Computer Vision compara tu progreso real. No promedios — tú."*
- Resultados: **Inflamación −28%** · **Energía +15%** · **Sueño profundo +22 min**
- Térmico antes/después · *"ΔT relativo · medición adjunta de bienestar, no diagnóstico."*
- CTA: **Hacer mi check-in semanal**

**Pantalla 2 — Check-in semanal**
- Eyebrow: `Check-in · por WhatsApp`
- Título: **"Tu reporte de la semana"**
- Sub: *"3 toques. Esto alimenta el modelo y afina tu protocolo."*
- Check-ins:
  - **Foto semanal** · `Computer Vision compara tu progreso`
  - **Sync wearable** · `HRV y sueño de los últimos 7 días`
  - **Check-in de síntomas** · `Energía, recuperación, ánimo, descanso`
- CTA: **Enviar check-in** / `Registra N más`

**Pantalla 3 — Ajuste & Membresía**
- Eyebrow: `Mejora continua · Data moat`
- Título: **"Tu protocolo se ajustó"**
- Sub: *"El modelo sugiere; tu médico aprueba cualquier ajuste de prescripción. Cada vuelta, mejor versión."*
- Ajustes:
  - `Tu médico aprobó subir tu dosis del péptido de reparación`
  - `Sumamos un senolítico los fines de semana (sin receta)`
  - `Mantenemos tu base — tus marcadores responden bien`
- Re-test: *"Re-test trimestral · toca en 8 semanas. Re-medimos y volvemos a calibrar."*
- Membresía:
  - **Esencial** `$899/mes` — Seguimiento continuo · Ajustes trimestrales · Descuentos en insumos
  - **Plus** `$2,499/mes` (recomendado) — Todo lo de Esencial · Labs incluidos · Re-test trimestral · Térmico en lounge
- CTA: **Mantener mi Membresía**
- Footer: *"Puedes ajustar o pausar tu protocolo y membresía cuando quieras."*

**Pantalla 4 — Al día**
- Eyebrow: `Estás al día`
- Título: **"El loop sigue contigo"**
- Sub: *"Diagnóstico → protocolo → datos → ajuste. Nos vemos en tu próximo check-in."*
- CTA: **Abrir WhatsApp**

---

## ✦ TRANSVERSAL

### Confianza Vigente.html — 3 pantallas
**Tipo:** app móvil · **Uso:** hace creíble todo lo demás (claim de marca).

**Pantalla 1 — Hub "Por qué creerte"**
- Eyebrow: `Confianza = el producto`
- Título: **"Por qué creerte"**
- Sub: *"En un mercado de frascos anónimos con disclaimer, la confianza es lo que vendemos. Así la construimos."*
- Pilares:
  - **Médico responsable** — *"Cédula real. Toda prescripción la decide y firma un profesional — no un bot, no un anónimo."*
  - **COA por lote** — *"Cada insumo con certificado de análisis. Transparencia, no «confía en mí»."*
  - **Evidencia citada** — *"Cada recomendación con literatura real y su nivel de evidencia. Datos, no marketing."*
  - **Caso #1: el fundador** — *"Documentamos nuestro propio protocolo: labs, energía, recuperación, mapas térmicos."*
- CTA: **Conoce el Caso #1**

**Pantalla 2 — Caso #1**
- Eyebrow: `Caso #1 · El fundador`
- Título: **"Lo que pedimos, lo vivimos"**
- Sub: *"No es un testimonio comprado. Es el protocolo del fundador, documentado con datos — imposible de copiar."*
- Métricas (12 semanas): **hs-CRP −34%** · **Energía AM +41%** · **Recuperación +22%** · **Sueño profundo +28 min**
- Nota: *"12 semanas documentadas: labs antes/después, diario de energía y recuperación, y mapas térmicos. Lo que pedimos, lo vivimos."*
- CTA: **Ver la evidencia**
- Footer: *"Resultados de un caso individual, ilustrativos. No garantizan resultados. No es diagnóstico médico."*

**Pantalla 3 — Evidencia citada**
- Eyebrow: `Evidencia citada`
- Título: **"Cada cosa, con su nivel"**
- Sub: *"Calificamos la fuerza de la evidencia. Donde es emergente, lo decimos — no la inflamos."*
- Sub: *"Calificamos la fuerza de la evidencia en lenguaje plano. Donde es emergente, lo decimos — no la inflamos."*
- Leyenda (lenguaje plano — los códigos E1–E5 quedan internos del RAG):
  - **Fuerte** — RCT o meta-análisis humano
  - **Moderada** — Humano temprano (piloto / cohorte)
  - **Emergente** — Preclínico / mecanístico / animal
- Ingredientes (claim · fuente con PMID · nivel):
  - **Omega-3** · Baja inflamación (hs-CRP) · PMID 28900017 · 30415628 · **Fuerte**
  - **Creatina** · Fuerza y cognición · Kreider et al. 2017 (ISSN position stand) · PMID 28615996 · **Fuerte**
  - **NMN** · Sube NAD+ y energía celular · PMID 33888596 · **Moderada**
  - **Espermidina** · Autofagia / longevidad · PMID 19801973 · **Moderada**
  - **GHK-Cu** · Remodelación de colágeno · PMID 29986520 · **Emergente**
  - **BPC-157** · Reparación de tejido · PMID 21548867 · **Emergente**

---

### Canal Vigente.html — WhatsApp (E) + Estados (F)
**Tipo:** app móvil · **Uso:** el canal concierge y los estados de borde. **Toggle de modo en Tweaks.**

#### E · Guiones de WhatsApp (4 conversaciones)
*Leyenda: 🟫 = concierge (entrante) · ⬜ = usuario (saliente)*

**Hilo 1 — Entrega de lectura** (top of funnel · tras el escaneo)
- 🟫 `¡Listo, Juan! Tu Escaneo Vigente está hecho. 👇`
- 🟫 `Tu Índice de partida: 64/100. Lo que más mueve la aguja para ti: recuperación y energía.`
- 🟫 [tarjeta] **Stack Vigente** · Sin receta · con COA · NMN · Omega-3 · Creatina · +2 más
- 🟫 `¿Quieres activar tu protocolo o ver el detalle primero?`
- ⬜ `Ver el detalle`
- 🟫 [quick-replies] `Activar protocolo` · `Ver mi Índice completo` · `Hablar con el equipo`

**Hilo 2 — Check-in semanal** (recurrencia · cada lunes)
- 🟫 `Buenos días 👋 Toca tu check-in de la semana. Te tomo 3 cosas:`
- 🟫 `1) Una foto de frente (misma luz) / 2) Sync de tu Oura / 3) ¿Cómo viene tu energía?`
- ⬜ `📷 Foto enviada`
- ⬜ `Oura sincronizado ✅`
- 🟫 [quick-replies] `Energía: mejor` · `Igual` · `Peor`
- ⬜ `Energía: mejor`
- 🟫 `Excelente. Tu HRV subió de 48 → 56 ms. Ajusté tu protocolo — te lo muestro en la app. 📈`

**Hilo 3 — Recordatorio de re-test** (trimestral · el loop)
- 🟫 `Han pasado 12 semanas, Juan. Toca tu re-test trimestral. 🔬`
- 🟫 `Repetimos labs + foto + térmico para medir tu avance real y recalibrar el stack.`
- 🟫 [tarjeta] **Re-test trimestral** · Incluido en tu Membresía Plus · Labs · Térmico · Foto CV
- 🟫 [quick-replies] `Agendar mi re-test` · `Recordar en 3 días`

**Hilo 4 — Re-enganche** (retención · inactividad)
- 🟫 `Te extrañamos, Juan. Llevas 2 semanas sin check-in y tu protocolo trabaja mejor con tus datos.`
- 🟫 `Sin presión — ¿retomamos con un check-in rápido o prefieres pausar tu membresía?`
- 🟫 [quick-replies] `Retomar check-in` · `Pausar 1 mes` · `Hablar con alguien`
- ⬜ `Retomar check-in`
- 🟫 `Eso. Aquí seguimos contigo. 🥃`

#### F · Estados y errores (6 pantallas)

| Tipo | Título | Cuerpo | CTA primario | CTA secundario |
|---|---|---|---|---|
| Error | **No pudimos leer tu PDF** | El archivo parece estar protegido o borroso. Súbelo de nuevo o tómale una foto clara a tus resultados. | Volver a subir | Subir una foto |
| Error | **No se conectó tu wearable** | Oura no respondió. Suele ser la sesión. Reintenta o continúa — puedes conectarlo después desde tu perfil. | Reintentar conexión | Continuar sin wearable |
| Error | **Tu pago no se completó** | El banco rechazó la transacción. No se hizo ningún cargo. Prueba otro método — también aceptamos SPEI y OXXO. | Probar otro método | Hablar por WhatsApp |
| Vacío | **Aún no hay datos que mostrar** | Tu primer check-in genera tu gráfica de progreso. Toma 2 minutos y empezamos a ver tu avance real. | Hacer mi primer check-in | — |
| En proceso | **Tu diagnóstico está en proceso** | Nuestro equipo médico revisa tu caso. Te avisamos por WhatsApp en menos de 24 h con tu protocolo. | Entendido | Escribir al equipo |
| Nudge | **Tu re-test trimestral está listo** | Han pasado 12 semanas. Repetir tus mediciones es lo que mantiene tu protocolo afinado a quién eres hoy. | Agendar re-test | Recordar después |

---

## 🗂️ Archivos de soporte (andamiaje — no entregables)

| Archivo | Rol |
|---|---|
| `hv-data.jsx` | Tokens de tema (noir/bronce/vital), todo el contenido/copy, iconos, UI compartida |
| `hv-screens-a.jsx` · `hv-screens-b.jsx` | Pantallas del v1 (ciclo completo) |
| `hv2-screens.jsx` | Onboarding (7 pantallas) |
| `hv3-conversion.jsx` | Conversión Av.1 |
| `hv4-av2.jsx` | Teleconsulta Av.2 |
| `hv5-seguimiento.jsx` | Seguimiento & Membresía |
| `hv6-confianza.jsx` | Confianza |
| `hv7-canal.jsx` | WhatsApp + Estados |
| `tweaks-panel.jsx` | Panel de Tweaks (variantes) |
| `frames/ios-frame.jsx` | Marco de iPhone |
| `Flujo Hombre Vigente.html` | **v1** del ciclo completo (referencia histórica) |

---

## Sistema de marca (resumen)
- **Color:** negro #08080A · acento **bronce #C6A06A** (base monocromática noir; bronce solo en CTA, estados activos, score, ✦/candado)
- **Tipografía:** Montserrat (900/800/700/400) + IBM Plex Mono (etiquetas/datos)
- **Textura:** grano de película + glow ambiental (Tweaks)
- **Voz:** optimización/bienestar · evidencia citada · "el médico firma" · nunca "diagnóstico/cura"
- **Variantes (Tweaks):** acento (noir/bronce/vital) · UX onboarding (guiado/tablero/chat) · modo canal (whatsapp/estados) · grano · glow

---

## Pendientes antes de live (de la revisión)
- **Aviso de Privacidad real (LFPDPPP):** el consentimiento (Onboarding P02) lo enlaza pero aún no existe. Redactarlo antes de live; sin él, el consentimiento es cosmético.
- **Responsable sanitario real:** médico, cédula y contrato reales antes de operar Av.2 (hoy el médico se muestra etiquetado como *ejemplo*).
- **Citas verificadas:** los PMID de Evidencia citada deben validarse contra el SSOT antes de demo pública.
- **Scores 68 (diagnóstico completo) vs 64 (escaneo de 3 datos):** difieren a propósito; el copy ya lo explica ("la lectura a fondo viene en el diagnóstico completo").
- **Caso #1:** métricas marcadas como ilustrativas ("no garantiza resultados") ✓.
