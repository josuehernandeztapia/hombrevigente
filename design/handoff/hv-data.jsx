// hv-data.jsx — Hombre Vigente · tokens de tema, contenido (de los MDs) y UI compartida
// Exporta todo a window.HV para que los demás scripts babel lo usen.

// ── Base oscura (compartida por las 3 variaciones de acento) ───────────────
const BASE = {
  bg:        '#08080A',
  bg2:       '#0D0D10',
  surface:   'rgba(255,255,255,0.035)',
  surface2:  'rgba(255,255,255,0.06)',
  solid:     '#141417',
  line:      'rgba(255,255,255,0.09)',
  lineStrong:'rgba(255,255,255,0.18)',
  hi:        '#F3F1EC',
  mid:       '#9A9AA0',
  low:       '#5C5C62',
  danger:    '#E0795F',
};

// ── 3 acentos (mismo rol, distinta intención de marca) ─────────────────────
const THEMES = {
  noir:   { key:'noir',   label:'Noir',   accent:'#EDEBE6', glow:'#EDEBE6',
            soft:'rgba(237,235,230,0.10)', ring:'rgba(237,235,230,0.22)', on:'#08080A' },
  bronce: { key:'bronce', label:'Bronce', accent:'#C6A06A', glow:'#C6A06A',
            soft:'rgba(198,160,106,0.13)', ring:'rgba(198,160,106,0.30)', on:'#08080A' },
  vital:  { key:'vital',  label:'Vital',  accent:'#5FE0A2', glow:'#5FE0A2',
            soft:'rgba(95,224,162,0.12)',  ring:'rgba(95,224,162,0.28)',  on:'#08080A' },
};

const ThemeCtx = React.createContext({ ...BASE, ...THEMES.bronce });

// ── Pasos canónicos (00 entrada + los 7 de los MDs) ────────────────────────
const STEPS = [
  { n:'00', key:'entrada',         title:'Entrada',        kicker:'Captación · Caso #1' },
  { n:'01', key:'onboarding',      title:'Tu historial',   kicker:'Onboarding & Data Upload' },
  { n:'02', key:'analisis',        title:'Análisis IA',    kicker:'Análisis multimodal' },
  { n:'03', key:'inconsistencias', title:'Verificación',   kicker:'Detección de inconsistencias' },
  { n:'04', key:'recomendacion',   title:'Tu protocolo',   kicker:'Recomendación personalizada' },
  { n:'05', key:'compra',          title:'Activar',        kicker:'Compra inteligente' },
  { n:'06', key:'seguimiento',     title:'Seguimiento',    kicker:'Acompañamiento continuo' },
  { n:'07', key:'ajuste',          title:'Ajuste & Loop',  kicker:'Mejora continua · Data moat' },
];

// ── Datos de captura del onboarding ────────────────────────────────────────
const INPUTS = [
  { id:'foto',   label:'Foto de rostro y cuerpo', meta:'Computer Vision · glow, daño solar, textura, grasa', icon:'camera' },
  { id:'labs',   label:'PDF de laboratorio',       meta:'hs-CRP · glucosa · IGF-1 · panel hepático',          icon:'lab' },
  { id:'wear',   label:'Conectar wearable',        meta:'Oura · Whoop · HRV, sueño, recuperación',            icon:'watch' },
  { id:'quiz',   label:'Cuestionario de objetivos',meta:'Energía · piel · ciática · composición',             icon:'doc' },
];

// ── Motores de análisis (paso 02) ──────────────────────────────────────────
const ENGINES = [
  { id:'cv',  name:'Computer Vision',  out:'Glow, daño solar, textura y grasa estimada', icon:'eye' },
  { id:'tab', name:'Datos tabulares',  out:'Biomarcadores de sangre y wearable',         icon:'chart' },
  { id:'llm', name:'Razonamiento LLM',  out:'Cruza objetivos + datos → estrategia',       icon:'spark' },
];

// ── Inconsistencias detectadas (paso 03) ───────────────────────────────────
const FLAGS = [
  { id:'f1', a:'Foto', b:'Peso reportado',
    text:'Tu foto sugiere más grasa visceral de la que refleja el peso que reportaste.' },
  { id:'f2', a:'Wearable', b:'Síntomas',
    text:'Tu HRV viene baja pese a que marcaste “duermo bien”. Vale la pena revisarlo.' },
];

// ── Stacks reales (de Plan Maestro §2) ─────────────────────────────────────
const STACKS = [
  { id:'glow', name:'Glow Stack', focus:'Piel',
    tag:'Piel · Colágeno · Antiinflamatorio',
    items:['GHK-Cu','NMN','Resveratrol'],
    why:'Luminosidad, firmeza y baja de inflamación cutánea.' },
  { id:'wolverine', name:'Wolverine Stack', focus:'Recuperación',
    tag:'Reparación estructural y nerviosa',
    items:['BPC-157','TB-500','Goralatide'],
    why:'Reparación de tejido y nervio — tu ciática es el objetivo #1.' },
  { id:'metabolic', name:'Metabolic Longevity Stack', focus:'Longevidad',
    tag:'Grasa visceral · NAD+ · Epigenética',
    items:['Tesamorelin','NMN','Spermidine','Fisetin','Khavinson'],
    why:'Grasa visceral, energía celular y relojes epigenéticos.' },
];

// proyección a 8 semanas (índices relativos 0–100, ilustrativos)
const PROJECTION = {
  inflamacion: [62, 58, 51, 47, 44, 40, 36, 34],
  energia:     [40, 44, 49, 55, 60, 66, 70, 74],
};

// ── Pricing ladder en MXN (de Market Research, Exhibit M) ───────────────────
const PRICING = [
  { id:'entrada', name:'Membresía Vigente', price:'$990', unit:'MXN / mes',
    blurb:'Diagnóstico + acompañamiento digital', tier:'Entrada' },
  { id:'core', name:'Protocolo Gestionado', price:'$2,990', unit:'MXN / mes',
    blurb:'Protocolo + insumo magistral con receta + seguimiento', tier:'Core', best:true },
  { id:'lounge', name:'Lounge Querétaro', price:'Fase 2', unit:'próximamente',
    blurb:'Diagnóstico profundo presencial + aplicación', tier:'Premium', soon:true },
];

const RAILS = ['Tarjeta','SPEI','OXXO','Kueski · MSI'];

// ── Seguimiento (paso 06) ──────────────────────────────────────────────────
const CHECKINS = [
  { id:'c1', label:'Foto semanal',       meta:'Computer Vision compara tu progreso', icon:'camera' },
  { id:'c2', label:'Sync wearable',      meta:'HRV y sueño de los últimos 7 días',   icon:'watch' },
  { id:'c3', label:'Check-in de síntomas',meta:'Energía, ciática, ánimo, descanso',   icon:'doc' },
];
const RESULTS = [
  { k:'Inflamación', v:'−28%', dir:'down', good:true },
  { k:'Energía',     v:'+15%', dir:'up',   good:true },
  { k:'Sueño profundo', v:'+22 min', dir:'up', good:true },
];

// ── Ajustes del loop (paso 07) — el modelo sugiere, el médico aprueba ───────
const ADJUSTMENTS = [
  { text:'Tu médico aprobó subir tu dosis del péptido de reparación', tone:'up' },
  { text:'Sumamos un senólitico los fines de semana (sin receta)', tone:'new' },
  { text:'Mantenemos tu base — tus marcadores responden bien', tone:'keep' },
];

const DISCLAIMER = 'Optimización y bienestar — no es un medicamento ni sustituye atención médica. El análisis de imagen es un adjunto, no un diagnóstico. Insumo preparado en farmacia magistral bajo receta.';

// ═══════════ Onboarding v2 — copy deck de 7 pantallas ══════════════════════
const FOOT = 'Optimización y bienestar. No sustituye atención médica.';

// 01 bienvenida
const BIENVENIDA_BULLETS = [
  'Tus datos, no promedios',
  'Evidencia citada, no marketing',
  'Un médico responsable detrás',
];

// 02 consentimiento
const CONSENT = [
  'Acepto que mis datos se usen para generar mi protocolo de optimización.',
  'Entiendo que un médico responsable revisa mi caso cuando aplica.',
  'He leído el Aviso de Privacidad: cifrado, almacenamiento y cómo borrar mis datos cuando quiera.',
];

// 03 historial — fuentes con su acción (arregla el estado “listo”)
const SOURCES = [
  { id:'foto', label:'Foto de rostro', meta:'Computer Vision · glow, textura, daño solar', icon:'camera', action:'Subir' },
  { id:'labs', label:'PDF de laboratorio', meta:'hs-CRP · glucosa · IGF-1 · panel', icon:'lab', action:'Subir' },
  { id:'wear', label:'Conectar wearable', meta:'Oura · Whoop · HRV, sueño, recuperación', icon:'watch', action:'Conectar' },
];

// 04 cuestionario
const GOALS = ['Energía','Recomposición','Recuperación','Piel','Longevidad general'];
const HABITS = ['Sueño','Ejercicio','Alcohol','Estrés'];
const HABIT_SCALE = ['Bajo','Medio','Alto'];

// 05 análisis — líneas rotativas
const ANALYSIS_LINES = [
  'Leyendo tus biomarcadores…',
  'Cruzando con tus señales de wearable…',
  'Buscando la evidencia que aplica a ti…',
];

// 06 índice vigente — informe de optimización
const INDEX_SCORE = 68;
const INDEX_SIGNALS = [
  { k:'hs-CRP', read:'Rango superior', note:'Inflamación a vigilar',
    why:'Marca inflamación sistémica de bajo grado. Baja con sueño, omega-3 y movimiento constante.' },
  { k:'HRV', read:'48 ms · baja', note:'Recuperación a mejorar',
    why:'Señal de estrés autonómico. Responde a higiene de sueño y a dosificar la carga de entrenamiento.' },
  { k:'Glow facial', read:'62 / 100', note:'Textura y daño solar moderados',
    why:'Optimizable con rutina de piel, fotoprotección y antioxidantes tópicos.' },
  { k:'Glucosa', read:'En rango', note:'Base metabólica estable',
    why:'Buen punto de partida metabólico. El objetivo aquí es mantener.' },
];

// 07 tu siguiente paso — routing Av.1 / Av.2
const ROUTES = [
  { id:'a', tag:'Ruta A · la mayoría', title:'Optimización', icon:'spark',
    body:'Hábitos + Stack Vigente (suplementos, sin receta).',
    items:['Hábitos guiados','Stack Vigente','Re-medición 8 sem'], cta:'Empezar mi protocolo' },
  { id:'b', tag:'Ruta B · si calificas', title:'Valoración médica', icon:'lock',
    body:'Tu caso amerita la revisión de un médico responsable antes de cualquier insumo de prescripción (vía magistral).',
    items:['Teleconsulta','Receta','Magistral'], cta:'Agendar teleconsulta' },
];

// ───────────────────────────────────────────────────────────────────────────
//  ICONOS (line icons simples — primitivas de UI)
// ───────────────────────────────────────────────────────────────────────────
function Icon({ name, size = 22, stroke, sw = 1.6, style }) {
  const c = stroke || 'currentColor';
  const P = (d, extra) => <path d={d} fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" {...extra} />;
  const paths = {
    camera: <>{P('M3 8.5A1.5 1.5 0 0 1 4.5 7H7l1.3-1.8a1 1 0 0 1 .8-.4h5.8a1 1 0 0 1 .8.4L17 7h2.5A1.5 1.5 0 0 1 21 8.5v9A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z')}<circle cx="12" cy="12.5" r="3.2" fill="none" stroke={c} strokeWidth={sw}/></>,
    lab: <>{P('M9 3h6M10 3v6.2L5.6 17a2 2 0 0 0 1.8 3h9.2a2 2 0 0 0 1.8-3L14 9.2V3')}{P('M7.4 14h9.2')}</>,
    watch: <>{P('M9 6.5 9.4 4h5.2L15 6.5M9 17.5l.4 2.5h5.2l.4-2.5')}<rect x="7" y="6.5" width="10" height="11" rx="2.6" fill="none" stroke={c} strokeWidth={sw}/></>,
    doc: <>{P('M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z')}{P('M14 3v4h4M9 12h6M9 16h6')}</>,
    eye: <>{P('M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z')}<circle cx="12" cy="12" r="2.6" fill="none" stroke={c} strokeWidth={sw}/></>,
    chart: <>{P('M4 4v16h16')}{P('M8 15l3.2-3.6 2.6 2 3.8-5')}</>,
    spark: <>{P('M12 3l1.9 5.3L19 10l-5.1 1.7L12 17l-1.9-5.3L5 10l5.1-1.7z')}</>,
    check: P('M5 12.5l4.2 4.2L19 7'),
    alert: <>{P('M12 4.5 21 19.5H3z')}{P('M12 10v4')}<circle cx="12" cy="17" r="0.9" fill={c} stroke="none"/></>,
    arrow: P('M5 12h14M13 6l6 6-6 6'),
    chat: <>{P('M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H9l-4 3.5V16H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z')}</>,
    lock: <>{P('M7 10V8a5 5 0 0 1 10 0v2')}<rect x="5" y="10" width="14" height="10" rx="2.4" fill="none" stroke={c} strokeWidth={sw}/></>,
    refresh: <>{P('M4 11a8 8 0 0 1 13.4-4.5L20 9M20 4v5h-5')}{P('M20 13a8 8 0 0 1-13.4 4.5L4 15M4 20v-5h5')}</>,
    up: P('M12 19V5M6 11l6-6 6 6'),
    down: P('M12 5v14M18 13l-6 6-6-6'),
    plus: P('M12 5v14M5 12h14'),
    dot: <circle cx="12" cy="12" r="3.2" fill={c} stroke="none"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" style={{ display:'block', flexShrink:0, ...style }}>{paths[name] || null}</svg>;
}

// ───────────────────────────────────────────────────────────────────────────
//  UI COMPARTIDA
// ───────────────────────────────────────────────────────────────────────────
const MONO = '"IBM Plex Mono", ui-monospace, monospace';
const SANS = '"Montserrat", system-ui, sans-serif';

function Eyebrow({ children, accent }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, fontFamily:MONO,
      fontSize:10.5, letterSpacing:'0.22em', textTransform:'uppercase',
      color: t.mid }}>
      <span style={{ width:5, height:5, borderRadius:9, background:t.accent, boxShadow:`0 0 8px ${t.accent}` }} />
      {children}
    </div>
  );
}

function GlassCard({ children, style, pad = 18, active, onClick }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div onClick={onClick} style={{
      background: active ? t.soft : t.surface,
      border: `1px solid ${active ? t.ring : t.line}`,
      borderRadius: 18, padding: pad, boxSizing:'border-box',
      transition:'border-color .25s, background .25s, transform .15s',
      cursor: onClick ? 'pointer' : 'default', ...style }}>
      {children}
    </div>
  );
}

function PrimaryButton({ children, onClick, disabled, style }) {
  const t = React.useContext(ThemeCtx);
  return (
    <button onClick={onClick} disabled={disabled} style={{
      width:'100%', border:'none', borderRadius:999, cursor: disabled?'default':'pointer',
      background: disabled ? 'rgba(255,255,255,0.08)' : t.accent,
      color: disabled ? t.low : t.on, fontFamily:SANS, fontWeight:800,
      fontSize:15, letterSpacing:'0.01em', padding:'16px 20px',
      display:'flex', alignItems:'center', justifyContent:'center', gap:9,
      transition:'opacity .2s, transform .12s', opacity: disabled?0.6:1,
      boxShadow: disabled ? 'none' : `0 8px 30px -10px ${t.accent}`, ...style }}>
      {children}
    </button>
  );
}

function GhostButton({ children, onClick, style }) {
  const t = React.useContext(ThemeCtx);
  return (
    <button onClick={onClick} style={{
      width:'100%', borderRadius:999, cursor:'pointer', background:'transparent',
      border:`1px solid ${t.lineStrong}`, color:t.hi, fontFamily:SANS, fontWeight:700,
      fontSize:14, padding:'14px 18px', display:'flex', alignItems:'center',
      justifyContent:'center', gap:8, ...style }}>
      {children}
    </button>
  );
}

// placeholder de imagen rayado con etiqueta mono
function Placeholder({ label, h = 120, style }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div style={{ height:h, borderRadius:14, position:'relative', overflow:'hidden',
      border:`1px solid ${t.line}`,
      background:`repeating-linear-gradient(135deg, rgba(255,255,255,0.035) 0 8px, transparent 8px 16px)`,
      display:'flex', alignItems:'center', justifyContent:'center', ...style }}>
      <span style={{ fontFamily:MONO, fontSize:10.5, letterSpacing:'0.14em',
        textTransform:'uppercase', color:t.low }}>{label}</span>
    </div>
  );
}

// chip mono
function Chip({ children, accent }) {
  const t = React.useContext(ThemeCtx);
  return (
    <span style={{ fontFamily:MONO, fontSize:10.5, letterSpacing:'0.04em',
      padding:'4px 9px', borderRadius:7, whiteSpace:'nowrap',
      color: accent ? t.hi : t.mid,
      background: accent ? t.surface2 : 'rgba(255,255,255,0.04)',
      border:`1px solid ${accent ? t.lineStrong : t.line}` }}>{children}</span>
  );
}

// ═══════════ Conversión — Tramo 1 (resultado del Escaneo + checkout Av.1) ═══════════
// Lectura inicial del Escaneo gratis (top of funnel)
const SCAN = {
  score: 64,
  signals: [
    { k:'Inflamación', v:'a vigilar' },
    { k:'Recuperación', v:'baja · HRV' },
    { k:'Energía',      v:'optimizable' },
  ],
  reco: 'Tu prioridad es recuperación y energía. Empezamos sin receta, con tu Stack Vigente.',
};

// Stack Vigente = suplementos de optimización (Av.1, SIN receta — no péptidos)
const STACK_VIGENTE = {
  name: 'Stack Vigente',
  focus: 'Optimización · sin receta',
  items: ['NMN','Omega-3','Creatina','Vitamina D3 + K2','Magnesio glicinato'],
};

// Programas (precios MXN ilustrativos, de la landing)
const PROGRAMS = [
  { id:'scan', tier:'Gancho',            name:'Escaneo Vigente',           price:'Gratis',            note:'Ya lo completaste', done:true },
  { id:'av1',  tier:'Av. 1 · sin receta', name:'Diagnóstico + Stack Vigente', price:'$1,490 + $899/mes', note:'Labs interpretados + protocolo + suplementos con COA', best:true },
  { id:'mem',  tier:'Recurrencia',        name:'Membresía Vigente',         price:'$899–2,499/mes',    note:'Seguimiento, ajustes trimestrales, labs incluidos (Plus)' },
  { id:'av2',  tier:'Av. 2 · médico',     name:'Protocolo Vigente Pro',     price:'Bajo prescripción', note:'Teleconsulta + receta + magistral. Solo si calificas.', medico:true },
];

// Checkout Av.1
const CHECKOUT = { diagLabel:'Diagnóstico Vigente', diagSub:'Labs interpretados + tu Índice', diagPrice:1490, stackPrice:899, todayTotal:'$2,389' };

const CONFIRM_STEPS = [
  'Te escribimos por WhatsApp con tu protocolo en detalle.',
  'Tu Stack Vigente se prepara con COA y llega en 3–5 días.',
  'A las 4 semanas: tu primer check-in y ajuste con datos reales.',
];

// ═══════════ Av. 2 — Vía médica (teleconsulta + receta + magistral) ═══════════
const MEDICO = { name:'Dr. Andrés Lemus', ced:'Céd. Prof. 7 482 119', spec:'Medicina de longevidad · Responsable sanitario' };
const ELIGIBILITY = [
  'Marcaste antecedentes a considerar en tu cuestionario.',
  'Tu objetivo requiere insumo de prescripción (vía magistral).',
  'hs-CRP fuera de rango — conviene criterio clínico.',
];
const SLOTS = [
  { d:'Hoy',     t:'7:30 PM' }, { d:'Mañana', t:'9:00 AM' },
  { d:'Mañana',  t:'6:00 PM' }, { d:'Jue 11',  t:'8:00 AM' },
];
const AV2 = { tele:'$890', protocolo:'$3,900', protoUnit:'/mes' };
const AV2_CONFIRM = [
  'Recibes el enlace de tu teleconsulta por WhatsApp.',
  'Tras la valoración, el médico evalúa y firma tu receta.',
  'La farmacia magistral prepara tu protocolo con COA y lo envía.',
];

// ═══════════ E — Guiones de WhatsApp (el canal concierge) ═══════════
// b = bot/concierge (entrante), u = usuario (saliente). chip = botón/quick-reply.
const WA_THREADS = [
  { id:'lectura', title:'Entrega de lectura', sub:'Top of funnel · tras el escaneo',
    msgs:[
      { s:'b', t:'¡Listo, Juan! Tu Escaneo Vigente está hecho. 👇' },
      { s:'b', t:'Tu Índice de partida: 64/100 (ilustrativo). Lo que más mueve la aguja para ti: recuperación y energía.' },
      { s:'b', kind:'card', card:{ title:'Stack Vigente', sub:'Sin receta · con COA', tags:['NMN','Omega-3','Creatina','+2 más'] } },
      { s:'b', t:'¿Quieres activar tu protocolo o ver el detalle primero?' },
      { s:'u', t:'Ver el detalle' },
      { s:'b', kind:'chips', chips:['Activar protocolo','Ver mi Índice completo','Hablar con el equipo'] },
    ] },
  { id:'checkin', title:'Check-in semanal', sub:'Recurrencia · cada lunes',
    msgs:[
      { s:'b', t:'Buenos días 👋 Toca tu check-in de la semana. Te tomo 3 cosas:' },
      { s:'b', t:'1) Una foto de frente (misma luz)\n2) Sync de tu Oura\n3) ¿Cómo viene tu energía?' },
      { s:'u', kind:'img', t:'📷 Foto enviada' },
      { s:'u', t:'Oura sincronizado ✅' },
      { s:'b', kind:'chips', chips:['Energía: mejor','Igual','Peor'] },
      { s:'u', t:'Energía: mejor' },
      { s:'b', t:'Excelente. Tu HRV subió de 48 → 56 ms. Ajusté tu protocolo — te lo muestro en la app. 📈' },
    ] },
  { id:'retest', title:'Recordatorio de re-test', sub:'Trimestral · el loop',
    msgs:[
      { s:'b', t:'Han pasado 12 semanas, Juan. Toca tu re-test trimestral. 🔬' },
      { s:'b', t:'Repetimos labs + foto + térmico para medir tu avance real y recalibrar el stack.' },
      { s:'b', kind:'card', card:{ title:'Re-test trimestral', sub:'Incluido en tu Membresía Plus', tags:['Labs','Térmico','Foto CV'] } },
      { s:'b', kind:'chips', chips:['Agendar mi re-test','Recordar en 3 días'] },
    ] },
  { id:'reenganche', title:'Re-enganche', sub:'Retención · inactividad',
    msgs:[
      { s:'b', t:'Te extrañamos, Juan. Llevas 2 semanas sin check-in y tu protocolo trabaja mejor con tus datos.' },
      { s:'b', t:'Sin presión — ¿retomamos con un check-in rápido o prefieres pausar tu membresía?' },
      { s:'b', kind:'chips', chips:['Retomar check-in','Pausar 1 mes','Hablar con alguien'] },
      { s:'u', t:'Retomar check-in' },
      { s:'b', t:'Eso. Aquí seguimos contigo. 🥃' },
    ] },
];

// ═══════════ F — Estados y errores ═══════════
const STATES = [
  { id:'upload_err', kind:'error', icon:'alert', title:'No pudimos leer tu PDF',
    body:'El archivo parece estar protegido o borroso. Súbelo de nuevo o tómale una foto clara a tus resultados.',
    primary:'Volver a subir', ghost:'Subir una foto' },
  { id:'wear_fail', kind:'error', icon:'watch', title:'No se conectó tu wearable',
    body:'Oura no respondió. Suele ser la sesión. Reintenta o continúa — puedes conectarlo después desde tu perfil.',
    primary:'Reintentar conexión', ghost:'Continuar sin wearable' },
  { id:'pay_fail', kind:'error', icon:'lock', title:'Tu pago no se completó',
    body:'El banco rechazó la transacción. No se hizo ningún cargo. Prueba otro método — también aceptamos SPEI y OXXO.',
    primary:'Probar otro método', ghost:'Hablar por WhatsApp' },
  { id:'empty_results', kind:'empty', icon:'chart', title:'Aún no hay datos que mostrar',
    body:'Tu primer check-in genera tu gráfica de progreso. Toma 2 minutos y empezamos a ver tu avance real.',
    primary:'Hacer mi primer check-in', ghost:null },
  { id:'pending', kind:'wait', icon:'refresh', title:'Tu diagnóstico está en proceso',
    body:'Nuestro equipo médico revisa tu caso. Te avisamos por WhatsApp en menos de 24 h con tu protocolo.',
    primary:'Entendido', ghost:'Escribir al equipo' },
  { id:'retest_due', kind:'nudge', icon:'spark', title:'Tu re-test trimestral está listo',
    body:'Han pasado 12 semanas. Repetir tus mediciones es lo que mantiene tu protocolo afinado a quién eres hoy.',
    primary:'Agendar re-test', ghost:'Recordar después' },
];

window.HV = {
  BASE, THEMES, ThemeCtx, STEPS, INPUTS, ENGINES, FLAGS, STACKS, PROJECTION,
  PRICING, RAILS, CHECKINS, RESULTS, ADJUSTMENTS, DISCLAIMER,
  FOOT, BIENVENIDA_BULLETS, CONSENT, SOURCES, GOALS, HABITS, HABIT_SCALE,
  ANALYSIS_LINES, INDEX_SCORE, INDEX_SIGNALS, ROUTES,
  SCAN, STACK_VIGENTE, PROGRAMS, CHECKOUT, CONFIRM_STEPS,
  MEDICO, ELIGIBILITY, SLOTS, AV2, AV2_CONFIRM, WA_THREADS, STATES,
  MONO, SANS, Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Placeholder, Chip,
};
