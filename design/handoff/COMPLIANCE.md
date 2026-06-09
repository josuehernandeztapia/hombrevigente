# Compliance — estado y pendientes (para el dev)

Barrido de copy/datos sobre `hv-data.jsx` y flujos. Estado al cierre del diseño.

## ✅ Aplicado en la fuente (Claude design)
1. **Stack `wolverine` → `reparacion`.** `id`, `name` ("Protocolo magistral de reparación") y `why` neutralizado (sin "ciática / objetivo #1"). Todas las referencias actualizadas (`hv4-av2.jsx`, v1).
2. **Stacks de péptidos = Av.2 (Rx).** Comentario en `STACKS`: el carril sin receta (Av.1) usa `STACK_VIGENTE` (suplementos), **nunca** estos. Metabolic (Tesamorelin/Khavinson) y Reparación (BPC-157/TB-500) van solo por vía médica.
3. **"Ciática" → genérico ("recuperación").** Limpiado en: check-in del flujo vivo (Seguimiento), cuestionario (INPUTS), chip del Caso #1 (v1). No se nombran condiciones específicas.
4. **GHK-Cu aclarado:** en Glow Stack ahora `GHK-Cu (tópico)` — tópico = cosmético (Av.1); inyectable = Av.2 (Rx). No ofrecer inyectable como suplemento.
5. **Evidencia:** niveles en lenguaje plano (Fuerte/Moderada/Emergente) + PMIDs reales (Omega-3 28900017·30415628, Creatina 28615996, NMN 33888596, Espermidina 19801973, GHK-Cu 29986520, BPC-157 21548867). Sin códigos E1–E5 en UI. Biomarcadores del Índice sin tag de evidencia.
6. **Médico "(ejemplo)"** + nota "pendiente responsable sanitario real" en Teleconsulta.
7. **Ajustes Rx:** copy "el modelo sugiere; tu médico aprueba". Ejemplos del Caso #1 despersonalizados.
8. **TM corregido:** la marca registrada es **Hombre Vigente™** (header/footer landing, brand de posts, h1 del Mapa). Se **quitó el ™ de "Índice Vigente"** en todas las pantallas (onboarding P01/P06, conversión, mapa, reel, storyboard) — el Índice es feature, no marca.
9. **Scores ilustrativos:** el modelo del Índice **no existe aún**. Los scores (68/100 en Onboarding P06, 64/100 en Escaneo) llevan etiqueta **"ilustrativo"/"ejemplo ilustrativo"** para no presentar un número no validado como real. Sustituir por el modelo real (ver KICKOFF M4).

## 🟢 Marcado para producción (no rompe el demo)
- **`{nombre}` (merge field):** los guiones de WhatsApp usan "Juan" como valor de demo. Sustituir por el nombre real del usuario. (Comentario en `hv-data.jsx` sobre `WA_THREADS`.)

## 🔴 Pendientes del mundo real (no de diseño — requieren asesoría)
1. **Aviso de Privacidad (LFPDPPP)** real — el consentimiento (Onboarding P02) lo enlaza. Sin él, el consentimiento es cosmético.
2. **Responsable sanitario real** — médico, cédula y contrato antes de operar Av.2. Hoy "ejemplo".
3. **Validar PMIDs** contra el SSOT/RAG y conectar el motor de evidencia.
4. **Integraciones:** Computer Vision (foto), parsing de labs, API wearables (Oura/Whoop), pagos MX (Conekta/Stripe · SPEI/OXXO/Kueski), WhatsApp Business API, agenda de teleconsulta + farmacia magistral con contrato.

*No es consejo legal — validar 1, 2 y el Aviso de Privacidad con asesoría profesional.*
