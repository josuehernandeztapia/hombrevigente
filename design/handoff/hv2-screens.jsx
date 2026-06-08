// hv2-screens.jsx — Onboarding v2 (copy deck de 7 pantallas)
const { ThemeCtx, FOOT, BIENVENIDA_BULLETS, CONSENT, SOURCES, GOALS, HABITS, HABIT_SCALE,
        ANALYSIS_LINES, INDEX_SCORE, INDEX_SIGNALS, ROUTES, MONO, SANS,
        Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Placeholder, Chip } = window.HV;

function Head2({ kicker, title, sub }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div className="hv-rise" style={{ marginBottom:18 }}>
      <Eyebrow accent>{kicker}</Eyebrow>
      <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07,
        letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0', textWrap:'balance' }}>{title}</h1>
      {sub && <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid,
        margin:'10px 0 0', maxWidth:'36ch' }}>{sub}</p>}
    </div>
  );
}
function Pad2({ children }) { return <div style={{ padding:'14px 20px 26px' }}>{children}</div>; }
function Foot({ children }) {
  const t = React.useContext(ThemeCtx);
  return <p style={{ fontFamily:MONO, fontSize:9.5, lineHeight:1.6, color:t.low, margin:'16px 2px 0', letterSpacing:'0.02em' }}>{children || FOOT}</p>;
}

// ═══════════════ 01 · BIENVENIDA ═══════════════
function S1Bienvenida({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad2>
      <div className="hv-rise" style={{ display:'flex', alignItems:'center', gap:8, marginBottom:20 }}>
        <Icon name="chat" size={15} stroke={t.mid} />
        <span style={{ fontFamily:MONO, fontSize:11, color:t.mid }}>Continúas tu conversación de WhatsApp</span>
      </div>
      <Head2 kicker="Onboarding · Guiado" title={<>Empecemos por los datos,<br/>no por opiniones</>}
        sub={<>En 7 pasos construimos tu <em style={{ fontStyle:'normal', color:t.hi, fontWeight:700 }}>Índice Vigente™</em>: una lectura objetiva de tu punto de partida. Con eso, un protocolo personalizado y, si tu caso lo amerita, la valoración de un médico.</>} />
      <div className="hv-rise" style={{ display:'flex', flexDirection:'column', gap:10, marginTop:22, animationDelay:'.08s' }}>
        {BIENVENIDA_BULLETS.map((b,i) => (
          <div key={i} style={{ display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ width:30, height:30, borderRadius:9, flexShrink:0, background:t.soft,
              border:`1px solid ${t.ring}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Icon name="check" size={16} stroke={t.accent} />
            </div>
            <span style={{ fontFamily:SANS, fontSize:14.5, fontWeight:600, color:t.hi }}>{b}</span>
          </div>
        ))}
      </div>
      <div className="hv-rise" style={{ marginTop:26, animationDelay:'.16s' }}>
        <PrimaryButton onClick={() => go('+1')}>Comenzar <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <Foot>Información de optimización y bienestar. No es diagnóstico ni tratamiento médico.</Foot>
    </Pad2>
  );
}

// ═══════════════ 02 · CONSENTIMIENTO ═══════════════
function S2Consentimiento({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const c = state.consent || [false,false,false];
  const toggle = (i) => set(s => { const n=[...(s.consent||[false,false,false])]; n[i]=!n[i]; return { ...s, consent:n }; });
  const all = c.every(Boolean);
  return (
    <Pad2>
      <Head2 kicker="Tus datos · Tu control" title="Antes de empezar, lo importante"
        sub="Vas a compartir datos de salud (labs, foto, wearable). Son sensibles y los tratamos como tal." />
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {CONSENT.map((txt,i) => {
          const on = c[i];
          return (
            <GlassCard key={i} active={on} onClick={() => toggle(i)} pad={14}
              className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
              <div style={{ display:'flex', alignItems:'flex-start', gap:12 }}>
                <div style={{ width:24, height:24, borderRadius:7, flexShrink:0, marginTop:1,
                  background: on ? t.accent : 'transparent', border:`1.5px solid ${on?t.accent:t.lineStrong}`,
                  display:'flex', alignItems:'center', justifyContent:'center' }}>
                  {on && <Icon name="check" size={15} stroke={t.on} />}
                </div>
                <span style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.45, color: on?t.hi:t.mid }}>{txt}</span>
              </div>
            </GlassCard>
          );
        })}
      </div>
      <p style={{ fontFamily:SANS, fontSize:12.5, lineHeight:1.5, color:t.mid, margin:'14px 2px 0' }}>
        Nunca vendemos tus datos. Puedes revocar tu consentimiento y eliminarlos en cualquier momento.
      </p>
      <div style={{ marginTop:18 }}>
        <PrimaryButton disabled={!all} onClick={() => go('+1')}>
          {all ? <>Acepto y continúo <Icon name="arrow" size={18} stroke={t.on} /></> : `Marca los ${3 - c.filter(Boolean).length} restantes`}
        </PrimaryButton>
      </div>
    </Pad2>
  );
}

// ═══════════════ 03 · TU HISTORIAL (3 variantes) ═══════════════
function S3Historial({ state, set, go, variant }) {
  const t = React.useContext(ThemeCtx);
  const ups = state.uploads || {};
  const done = SOURCES.filter(i => ups[i.id]).length;
  const toggle = (id) => set(s => ({ ...s, uploads:{ ...(s.uploads||{}), [id]: !(s.uploads||{})[id] } }));
  const ready = done >= 2;
  return (
    <Pad2>
      <Head2 kicker="Tus fuentes · Mínimo 2" title="Tu historial"
        sub="Sube tus datos objetivos. Mientras más fuentes, mejor tu protocolo. Con 2 empezamos." />
      {variant === 'tablero' ? <HistTablero ups={ups} done={done} toggle={toggle} />
        : variant === 'chat' ? <HistChat ups={ups} toggle={toggle} />
        : <HistGuiado ups={ups} toggle={toggle} />}
      <div style={{ marginTop:20 }}>
        <PrimaryButton disabled={!ready} onClick={() => go('+1')}>
          {ready ? <>Continuar <Icon name="arrow" size={18} stroke={t.on} /></> : `Sube ${2 - done} fuente${2-done===1?'':'s'} más`}
        </PrimaryButton>
      </div>
      <Foot>Foto de cuerpo, opcional. La foto se analiza para piel y optimización, no para diagnóstico.</Foot>
    </Pad2>
  );
}
function HistGuiado({ ups, toggle }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:11 }}>
      {SOURCES.map((s,i) => {
        const on = !!ups[s.id];
        return (
          <GlassCard key={s.id} active={on} onClick={() => toggle(s.id)} pad={14}
            className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
            <div style={{ display:'flex', alignItems:'center', gap:13 }}>
              <div style={{ width:42, height:42, borderRadius:12, flexShrink:0,
                display:'flex', alignItems:'center', justifyContent:'center',
                background: on?t.accent:t.surface2, border:`1px solid ${on?t.accent:t.line}` }}>
                <Icon name={on?'check':s.icon} size={20} stroke={on?t.on:t.mid} />
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:SANS, fontWeight:700, fontSize:14.5, color:t.hi }}>{s.label}</div>
                <div style={{ fontFamily:MONO, fontSize:10.5, color:t.low, marginTop:3,
                  whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{s.meta}</div>
              </div>
              <span style={{ fontFamily:MONO, fontSize:11, fontWeight:600, padding:'5px 11px', borderRadius:999,
                whiteSpace:'nowrap', color: on?t.accent:t.on,
                background: on?'transparent':t.accent, border: on?`1px solid ${t.ring}`:'none' }}>
                {on ? '✓ Listo' : s.action}
              </span>
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
function HistTablero({ ups, done, toggle }) {
  const t = React.useContext(ThemeCtx);
  const pct = done/SOURCES.length, R=34, C=2*Math.PI*R;
  return (
    <div>
      <GlassCard className="hv-rise" pad={18} style={{ display:'flex', alignItems:'center', gap:18, marginBottom:14 }}>
        <svg width="84" height="84" viewBox="0 0 84 84" style={{ flexShrink:0 }}>
          <circle cx="42" cy="42" r={R} fill="none" stroke={t.line} strokeWidth="6" />
          <circle cx="42" cy="42" r={R} fill="none" stroke={t.accent} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={C} strokeDashoffset={C*(1-pct)} transform="rotate(-90 42 42)" style={{ transition:'stroke-dashoffset .5s' }} />
          <text x="42" y="46" textAnchor="middle" fontFamily={MONO} fontSize="18" fontWeight="700" fill={t.hi}>{done}/{SOURCES.length}</text>
        </svg>
        <div>
          <div style={{ fontFamily:SANS, fontWeight:800, fontSize:16, color:t.hi }}>Perfil base</div>
          <div style={{ fontFamily:MONO, fontSize:11, color:t.mid, marginTop:4 }}>
            {done===0?'Toca una fuente para empezar':done<2?'Una fuente más para analizar':'Listo para analizar'}</div>
        </div>
      </GlassCard>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:11 }}>
        {SOURCES.map((s,i) => {
          const on = !!ups[s.id];
          return (
            <GlassCard key={s.id} active={on} onClick={() => toggle(s.id)} pad={14}
              className="hv-rise" style={{ animationDelay:`${i*0.05}s`, minHeight:118, display:'flex', flexDirection:'column', justifyContent:'space-between' }}>
              <div style={{ width:38, height:38, borderRadius:11, display:'flex', alignItems:'center', justifyContent:'center',
                background:on?t.accent:t.surface2, border:`1px solid ${on?t.accent:t.line}` }}>
                <Icon name={on?'check':s.icon} size={19} stroke={on?t.on:t.mid} />
              </div>
              <div>
                <div style={{ fontFamily:SANS, fontWeight:700, fontSize:13, color:t.hi, lineHeight:1.2 }}>{s.label}</div>
                <div style={{ fontFamily:MONO, fontSize:10, color:on?t.accent:t.low, marginTop:5 }}>{on?'✓ Listo':s.action}</div>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
}
function HistChat({ ups, toggle }) {
  const t = React.useContext(ThemeCtx);
  const ask = SOURCES.find(s => !ups[s.id]);
  const bot = { background:t.surface2, border:`1px solid ${t.line}`, color:t.hi, alignSelf:'flex-start', borderRadius:'4px 16px 16px 16px' };
  const usr = { background:t.accent, color:t.on, alignSelf:'flex-end', borderRadius:'16px 4px 16px 16px' };
  const bub = { maxWidth:'82%', padding:'11px 14px', fontFamily:SANS, fontSize:13.5, lineHeight:1.45 };
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
      <div style={{ ...bub, ...bot }}>Hola. Soy tu asistente Vigente. Empecemos por tus datos. 👇</div>
      {SOURCES.map(s => ups[s.id] && (
        <React.Fragment key={s.id}>
          <div style={{ ...bub, ...bot, display:'flex', alignItems:'center', gap:9 }}>
            <Icon name={s.icon} size={16} stroke={t.mid} /> ¿Me compartes tu {s.label.toLowerCase()}?</div>
          <div style={{ ...bub, ...usr, display:'flex', alignItems:'center', gap:8 }}>
            <Icon name="check" size={15} stroke={t.on} /> Enviado</div>
        </React.Fragment>
      ))}
      {ask && (
        <>
          <div style={{ ...bub, ...bot, display:'flex', alignItems:'center', gap:9 }}>
            <Icon name={ask.icon} size={16} stroke={t.mid} /> ¿Me compartes tu {ask.label.toLowerCase()}?</div>
          <button onClick={() => toggle(ask.id)} style={{ alignSelf:'flex-end', cursor:'pointer',
            fontFamily:SANS, fontWeight:700, fontSize:13, color:t.accent, background:t.soft,
            border:`1px solid ${t.ring}`, borderRadius:999, padding:'10px 16px', display:'flex', alignItems:'center', gap:7 }}>
            <Icon name="plus" size={15} stroke={t.accent} /> {ask.action}</button>
        </>
      )}
    </div>
  );
}

// ═══════════════ 04 · CUESTIONARIO ═══════════════
function S4Cuestionario({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const goals = state.goals || [];
  const habits = state.habits || {};
  const hablar = !!state.hablar;
  const toggleGoal = (g) => set(s => { const a=s.goals||[]; return { ...s, goals: a.includes(g)?a.filter(x=>x!==g):[...a,g] }; });
  const setHabit = (h,v) => set(s => ({ ...s, habits:{ ...(s.habits||{}), [h]:v } }));
  const QL = ({ children }) => <div style={{ fontFamily:MONO, fontSize:10.5, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low, margin:'2px 2px 10px' }}>{children}</div>;
  return (
    <Pad2>
      <Head2 kicker="2 min · Tu contexto" title="¿Qué quieres mover?"
        sub="Esto afina la prioridad de tu protocolo. Sé honesto, nadie más lo ve." />

      <QL>Objetivo principal</QL>
      <div style={{ display:'flex', flexWrap:'wrap', gap:8, marginBottom:20 }}>
        {GOALS.map(g => {
          const on = goals.includes(g);
          return (
            <button key={g} onClick={() => toggleGoal(g)} style={{ cursor:'pointer', fontFamily:SANS, fontWeight:600,
              fontSize:13, padding:'9px 14px', borderRadius:999, color: on?t.accent:t.mid,
              background: on?t.soft:'transparent', border:`1px solid ${on?t.ring:t.lineStrong}` }}>{g}</button>
          );
        })}
      </div>

      <QL>Medicamentos o antecedentes a considerar</QL>
      <div style={{ background:t.surface, border:`1px solid ${t.line}`, borderRadius:14, padding:'12px 14px', marginBottom:10,
        fontFamily:SANS, fontSize:13, color:t.low }}>Escribe aquí…</div>
      <button onClick={() => set(s => ({ ...s, hablar:!s.hablar }))} style={{ cursor:'pointer', display:'flex', alignItems:'center', gap:9,
        fontFamily:SANS, fontWeight:600, fontSize:13, color: hablar?t.accent:t.mid, background:'transparent', border:'none', padding:'0 2px', marginBottom:20 }}>
        <span style={{ width:20, height:20, borderRadius:6, background:hablar?t.accent:'transparent', border:`1.5px solid ${hablar?t.accent:t.lineStrong}`,
          display:'flex', alignItems:'center', justifyContent:'center' }}>{hablar && <Icon name="check" size={13} stroke={t.on} />}</span>
        Prefiero hablarlo con el médico</button>

      <QL>Hábitos hoy</QL>
      <div style={{ display:'flex', flexDirection:'column', gap:9 }}>
        {HABITS.map(h => (
          <div key={h} style={{ display:'flex', alignItems:'center', gap:10 }}>
            <span style={{ fontFamily:SANS, fontSize:13, color:t.hi, width:74, flexShrink:0 }}>{h}</span>
            <div style={{ display:'flex', gap:5, flex:1 }}>
              {HABIT_SCALE.map(v => {
                const on = habits[h]===v;
                return <button key={v} onClick={() => setHabit(h,v)} style={{ flex:1, cursor:'pointer', fontFamily:MONO, fontSize:11,
                  padding:'8px 4px', borderRadius:8, color:on?t.accent:t.low, background:on?t.soft:'transparent',
                  border:`1px solid ${on?t.ring:t.line}` }}>{v}</button>;
              })}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop:20 }}>
        <PrimaryButton onClick={() => go('+1')}>Guardar y seguir <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <Foot>Si marcas medicamentos o antecedentes, tu caso pasa a revisión médica antes de cualquier recomendación de prescripción.</Foot>
    </Pad2>
  );
}

// ═══════════════ 05 · ANÁLISIS ═══════════════
function S5Analisis({ go }) {
  const t = React.useContext(ThemeCtx);
  const [line, setLine] = React.useState(0);
  React.useEffect(() => {
    const iv = setInterval(() => setLine(l => (l+1) % ANALYSIS_LINES.length), 1100);
    const to = setTimeout(() => go('+1'), 4200);
    return () => { clearInterval(iv); clearTimeout(to); };
  }, []);
  return (
    <Pad2>
      <Head2 kicker="Procesando · Con evidencia" title="Analizando tu Índice Vigente" />
      <div className="hv-rise" style={{ position:'relative', margin:'8px 0 18px' }}>
        <Placeholder label="cruzando tus señales" h={150} />
        <div className="hv-scan" style={{ background:`linear-gradient(90deg,transparent, ${t.accent}, transparent)` }} />
      </div>
      <div style={{ minHeight:26, display:'flex', alignItems:'center', gap:11 }}>
        <span className="hv-spin" style={{ width:15, height:15, borderRadius:9, border:`2px solid ${t.line}`, borderTopColor:t.accent, flexShrink:0 }} />
        <span key={line} className="hv-rise" style={{ fontFamily:SANS, fontSize:15, fontWeight:600, color:t.hi }}>{ANALYSIS_LINES[line]}</span>
      </div>
      <div style={{ marginTop:18, height:4, borderRadius:9, background:t.surface2, overflow:'hidden' }}>
        <div style={{ height:'100%', background:t.accent, borderRadius:9, animation:'hvBar 4.2s linear forwards' }} />
      </div>
      <Foot>Cada recomendación se justifica con literatura real. Donde no hay evidencia suficiente, te lo decimos.</Foot>
    </Pad2>
  );
}

// ═══════════════ 06 · TU ÍNDICE VIGENTE ═══════════════
function S6Indice({ go }) {
  const t = React.useContext(ThemeCtx);
  const [open, setOpen] = React.useState(0);
  const R=40, C=2*Math.PI*R;
  return (
    <Pad2>
      <Head2 kicker="Tu lectura · Informe de optimización" title="Tu Índice Vigente™"
        sub="Tu lectura de partida — un punto de referencia para optimizar y volver a medir. No es un diagnóstico médico." />
      <GlassCard className="hv-rise" pad={18} style={{ display:'flex', alignItems:'center', gap:18, marginBottom:14 }}>
        <svg width="96" height="96" viewBox="0 0 96 96" style={{ flexShrink:0 }}>
          <circle cx="48" cy="48" r={R} fill="none" stroke={t.line} strokeWidth="7" />
          <circle cx="48" cy="48" r={R} fill="none" stroke={t.accent} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={C} strokeDashoffset={C*(1-INDEX_SCORE/100)} transform="rotate(-90 48 48)" style={{ transition:'stroke-dashoffset 1s' }} />
          <text x="48" y="50" textAnchor="middle" fontFamily={SANS} fontSize="26" fontWeight="900" fill={t.hi}>{INDEX_SCORE}</text>
          <text x="48" y="65" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={t.low}>/ 100</text>
        </svg>
        <div>
          <div style={{ fontFamily:SANS, fontWeight:800, fontSize:16, color:t.hi }}>Punto de partida</div>
          <div style={{ fontFamily:SANS, fontSize:12.5, color:t.mid, marginTop:5, lineHeight:1.45 }}>4 señales clave para optimizar. Volvemos a medir en 8 semanas.</div>
        </div>
      </GlassCard>
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {INDEX_SIGNALS.map((s,i) => {
          const isOpen = open===i;
          return (
            <GlassCard key={s.k} pad={14} onClick={() => setOpen(isOpen?-1:i)} className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
              <div style={{ display:'flex', alignItems:'center', gap:11 }}>
                <div style={{ flex:1, minWidth:0 }}>
                  <span style={{ fontFamily:SANS, fontWeight:800, fontSize:14.5, color:t.hi }}>{s.k}</span>
                  <div style={{ fontFamily:SANS, fontSize:12.5, color:t.mid, marginTop:4 }}>
                    <span style={{ fontFamily:MONO, fontSize:11, color:t.hi }}>{s.read}</span>
                    <span style={{ color:t.low }}> · </span>{s.note}
                  </div>
                </div>
                <span style={{ fontFamily:MONO, fontSize:10.5, color: isOpen?t.accent:t.low, whiteSpace:'nowrap', display:'flex', alignItems:'center', gap:5 }}>
                  {isOpen?'ocultar':'ver por qué'}
                  <Icon name="arrow" size={13} stroke={isOpen?t.accent:t.low} style={{ transform: isOpen?'rotate(-90deg)':'rotate(90deg)' }} />
                </span>
              </div>
              {isOpen && <p className="hv-rise" style={{ fontFamily:SANS, fontSize:12.5, lineHeight:1.5, color:t.mid,
                margin:'11px 0 0', paddingTop:11, borderTop:`1px solid ${t.line}` }}><strong style={{ color:t.hi, fontWeight:700 }}>Por qué importa. </strong>{s.why}</p>}
            </GlassCard>
          );
        })}
      </div>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Ver mi plan <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <Foot>Las áreas marcadas no significan enfermedad; son oportunidades de optimización.</Foot>
    </Pad2>
  );
}

// ═══════════════ 07 · TU SIGUIENTE PASO ═══════════════
function S7Siguiente({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const sel = state.route;
  return (
    <Pad2>
      <Head2 kicker="Tu protocolo · Personalizado" title="Tu camino Vigente"
        sub="Según tus datos, este es el siguiente paso." />
      <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
        {ROUTES.map((r,i) => {
          const on = sel===r.id, primary = r.id==='a';
          return (
            <GlassCard key={r.id} active={on} onClick={() => set(s => ({ ...s, route:r.id }))} pad={16}
              className="hv-rise" style={{ animationDelay:`${i*0.07}s` }}>
              <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:9 }}>
                <div style={{ width:34, height:34, borderRadius:10, flexShrink:0, background:t.soft, border:`1px solid ${t.ring}`,
                  display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <Icon name={r.icon} size={18} stroke={t.accent} />
                </div>
                <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low }}>{r.tag}</span>
              </div>
              <div style={{ fontFamily:SANS, fontWeight:800, fontSize:18, color:t.hi }}>{r.title}</div>
              <p style={{ fontFamily:SANS, fontSize:13, lineHeight:1.5, color:t.mid, margin:'7px 0 12px' }}>{r.body}</p>
              <div style={{ display:'flex', flexWrap:'wrap', gap:7, marginBottom:14 }}>
                {r.items.map(it => <Chip key={it}>{it}</Chip>)}
              </div>
              {primary
                ? <PrimaryButton onClick={(e)=>{ e.stopPropagation(); set(s=>({ ...s, route:r.id })); window.location.href='Conversion%20Vigente.html#programa'; }}>{r.cta}</PrimaryButton>
                : <GhostButton onClick={(e)=>{ e.stopPropagation(); set(s=>({ ...s, route:r.id })); window.location.href='Teleconsulta%20Vigente.html'; }}><Icon name="chat" size={16} stroke={t.hi} /> {r.cta}</GhostButton>}
            </GlassCard>
          );
        })}
      </div>
      <Foot>Ningún insumo de Avenida 2 se entrega sin valoración y firma de un médico. Puedes ajustar o pausar tu protocolo cuando quieras.</Foot>
      <div style={{ marginTop:14 }}>
        <button onClick={() => go(1)} style={{ width:'100%', background:'none', border:'none', cursor:'pointer',
          fontFamily:MONO, fontSize:11, color:t.low, display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
          <Icon name="refresh" size={14} stroke={t.low} /> Reiniciar recorrido</button>
      </div>
    </Pad2>
  );
}

Object.assign(window, { S1Bienvenida, S2Consentimiento, S3Historial, S4Cuestionario, S5Analisis, S6Indice, S7Siguiente });
