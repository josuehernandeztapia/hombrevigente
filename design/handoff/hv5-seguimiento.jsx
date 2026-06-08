// hv5-seguimiento.jsx — Tramo 3: Seguimiento & Membresía (el loop de recurrencia)
const { BASE, THEMES, ThemeCtx, CHECKINS, RESULTS, ADJUSTMENTS, FOOT, MONO, SANS,
        Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Placeholder, Chip } = window.HV;

const MEMBERSHIP = [
  { id:'esencial', name:'Esencial', price:'$899', items:['Seguimiento continuo','Ajustes trimestrales','Descuentos en insumos'] },
  { id:'plus', name:'Plus', price:'$2,499', items:['Todo lo de Esencial','Labs incluidos','Re-test trimestral','Térmico en lounge'], best:true },
];

function Head5({ kicker, title, sub }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div className="hv-rise" style={{ marginBottom:18 }}>
      <Eyebrow accent>{kicker}</Eyebrow>
      <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0', textWrap:'balance' }}>{title}</h1>
      {sub && <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'36ch' }}>{sub}</p>}
    </div>
  );
}
function Pad5({ children }) { return <div style={{ padding:'14px 20px 26px' }}>{children}</div>; }
function Foot5({ children }) {
  const t = React.useContext(ThemeCtx);
  return <p style={{ fontFamily:MONO, fontSize:9.5, lineHeight:1.6, color:t.low, margin:'16px 2px 0' }}>{children || FOOT}</p>;
}

// ═══════════ 1 · DASHBOARD ═══════════
function S1Dashboard({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad5>
      <div className="hv-rise" style={{ display:'flex', alignItems:'center', gap:9, marginBottom:14 }}>
        <span style={{ width:7, height:7, borderRadius:9, background:t.accent, boxShadow:`0 0 10px ${t.accent}` }} />
        <span style={{ fontFamily:MONO, fontSize:11, color:t.mid }}>Protocolo activo · Semana 4</span>
      </div>
      <Head5 kicker="Seguimiento con datos" title="Vas avanzando"
        sub="Computer Vision compara tu progreso real. No promedios — tú." />
      <div className="hv-rise" style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:9, margin:'2px 0 14px' }}>
        {RESULTS.map(r => (
          <div key={r.k} style={{ background:t.surface, border:`1px solid ${t.line}`, borderRadius:13, padding:'12px 8px', textAlign:'center' }}>
            <div style={{ display:'flex', justifyContent:'center', marginBottom:4 }}><Icon name={r.dir} size={15} stroke={t.accent} /></div>
            <div style={{ fontFamily:SANS, fontWeight:900, fontSize:15, color:t.accent }}>{r.v}</div>
            <div style={{ fontFamily:MONO, fontSize:8.5, color:t.low, marginTop:3, lineHeight:1.2 }}>{r.k}</div>
          </div>
        ))}
      </div>
      <div className="hv-rise" style={{ display:'flex', gap:12, marginBottom:6 }}>
        <div style={{ flex:1 }}><Placeholder label="térmico · sem 0" h={104} /></div>
        <div style={{ flex:1 }}><Placeholder label="térmico · sem 4" h={104} /></div>
      </div>
      <p style={{ fontFamily:MONO, fontSize:9.5, color:t.low, margin:'8px 2px 0' }}>ΔT relativo · medición adjunta de bienestar, no diagnóstico.</p>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Hacer mi check-in semanal <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
    </Pad5>
  );
}

// ═══════════ 2 · CHECK-IN SEMANAL ═══════════
function S2Checkin({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const done = state.checks || {};
  const n = CHECKINS.filter(c => done[c.id]).length;
  const toggle = (id) => set(s => ({ ...s, checks:{ ...(s.checks||{}), [id]:!(s.checks||{})[id] } }));
  return (
    <Pad5>
      <Head5 kicker="Check-in · por WhatsApp" title="Tu reporte de la semana"
        sub="3 toques. Esto alimenta el modelo y afina tu protocolo." />
      <div style={{ display:'flex', flexDirection:'column', gap:11 }}>
        {CHECKINS.map((c,i) => {
          const on = !!done[c.id];
          return (
            <GlassCard key={c.id} active={on} onClick={() => toggle(c.id)} pad={14} className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
              <div style={{ display:'flex', alignItems:'center', gap:13 }}>
                <div style={{ width:42, height:42, borderRadius:12, flexShrink:0, background:on?t.accent:t.surface2, border:`1px solid ${on?t.accent:t.line}`,
                  display:'flex', alignItems:'center', justifyContent:'center' }}>
                  <Icon name={on?'check':c.icon} size={20} stroke={on?t.on:t.mid} />
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:SANS, fontWeight:700, fontSize:14.5, color:t.hi }}>{c.label}</div>
                  <div style={{ fontFamily:MONO, fontSize:10, color:t.low, marginTop:3, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{c.meta}</div>
                </div>
                <span style={{ fontFamily:MONO, fontSize:11, color:on?t.accent:t.low }}>{on?'listo':'+'}</span>
              </div>
            </GlassCard>
          );
        })}
      </div>
      <div style={{ marginTop:20 }}>
        <PrimaryButton disabled={n<2} onClick={() => go('+1')}>
          {n>=2 ? <>Enviar check-in <Icon name="arrow" size={18} stroke={t.on} /></> : `Registra ${2-n} más`}
        </PrimaryButton>
      </div>
    </Pad5>
  );
}

// ═══════════ 3 · AJUSTE & MEMBRESÍA ═══════════
function S3Ajuste({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const tone = { up:'up', new:'plus', keep:'check' };
  const sel = state.mem || 'plus';
  return (
    <Pad5>
      <Head5 kicker="Mejora continua · Data moat" title="Tu protocolo se ajustó"
        sub="El modelo sugiere; tu médico aprueba cualquier ajuste de prescripción. Cada vuelta, mejor versión." />
      <div style={{ display:'flex', flexDirection:'column', gap:10, marginBottom:16 }}>
        {ADJUSTMENTS.map((a,i) => (
          <GlassCard key={i} pad={13} active={a.tone!=='keep'} className="hv-rise" style={{ animationDelay:`${i*0.06}s` }}>
            <div style={{ display:'flex', alignItems:'center', gap:12 }}>
              <div style={{ width:32, height:32, borderRadius:9, flexShrink:0, background:a.tone==='keep'?t.surface2:t.soft, border:`1px solid ${a.tone==='keep'?t.line:t.ring}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
                <Icon name={tone[a.tone]} size={16} stroke={a.tone==='keep'?t.mid:t.accent} />
              </div>
              <span style={{ fontFamily:SANS, fontSize:13, fontWeight:600, color:t.hi, lineHeight:1.35 }}>{a.text}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <div className="hv-rise" style={{ display:'flex', alignItems:'center', gap:11, background:t.surface, border:`1px solid ${t.line}`, borderRadius:13, padding:'12px 14px', marginBottom:18 }}>
        <Icon name="refresh" size={18} stroke={t.accent} />
        <span style={{ fontFamily:SANS, fontSize:12.5, color:t.mid }}><b style={{ color:t.hi, fontWeight:700 }}>Re-test trimestral</b> · toca en 8 semanas. Re-medimos y volvemos a calibrar.</span>
      </div>
      <div style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low, margin:'2px 2px 10px' }}>Tu membresía</div>
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {MEMBERSHIP.map((m,i) => {
          const on = sel===m.id;
          return (
            <GlassCard key={m.id} active={on} onClick={() => set(s=>({ ...s, mem:m.id }))} pad={15} className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                  <span style={{ fontFamily:SANS, fontWeight:800, fontSize:16, color:t.hi }}>{m.name}</span>
                  {m.best && <Chip accent>recomendado</Chip>}
                </div>
                <div><span style={{ fontFamily:SANS, fontWeight:900, fontSize:17, color:on?t.accent:t.hi }}>{m.price}</span><span style={{ fontFamily:MONO, fontSize:10, color:t.low }}>/mes</span></div>
              </div>
              <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginTop:10 }}>
                {m.items.map(it => <Chip key={it}>{it}</Chip>)}
              </div>
            </GlassCard>
          );
        })}
      </div>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Mantener mi Membresía <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <Foot5>Puedes ajustar o pausar tu protocolo y membresía cuando quieras.</Foot5>
    </Pad5>
  );
}

// ═══════════ 4 · AL DÍA ═══════════
function S4AlDia({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad5>
      <div className="hv-rise" style={{ display:'flex', flexDirection:'column', alignItems:'center', textAlign:'center', paddingTop:18 }}>
        <div style={{ width:72, height:72, borderRadius:999, background:t.soft, border:`1px solid ${t.ring}`, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:18 }}>
          <Icon name="check" size={36} stroke={t.accent} />
        </div>
        <Eyebrow accent>Estás al día</Eyebrow>
        <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0' }}>El loop sigue contigo</h1>
        <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.55, color:t.mid, margin:'12px 0 0', maxWidth:'30ch' }}>
          Diagnóstico → protocolo → datos → ajuste. Nos vemos en tu próximo check-in.
        </p>
      </div>
      <div className="hv-rise" style={{ marginTop:24, display:'flex', flexDirection:'column', gap:10 }}>
        <PrimaryButton onClick={() => {}}><Icon name="chat" size={16} stroke={t.on} /> Abrir WhatsApp</PrimaryButton>
        <button onClick={() => go(1)} style={{ width:'100%', background:'none', border:'none', cursor:'pointer', fontFamily:MONO, fontSize:11, color:t.low, display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
          <Icon name="refresh" size={14} stroke={t.low} /> Reiniciar demo</button>
      </div>
    </Pad5>
  );
}

// ═══════════ SHELL ═══════════
const STEPS5 = [
  { key:'dashboard', Comp:S1Dashboard },
  { key:'checkin',   Comp:S2Checkin },
  { key:'ajuste',    Comp:S3Ajuste },
  { key:'aldia',     Comp:S4AlDia },
];
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{ "accent": "bronce", "grain": true, "glow": true }/*EDITMODE-END*/;

function Flow({ t }) {
  const [idx, setIdx] = React.useState(0);
  const [state, set] = React.useState({ checks:{}, mem:'plus' });
  const scrollRef = React.useRef(null);
  React.useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [idx]);
  const go = (a) => { if (a==='+1') setIdx(c=>Math.min(STEPS5.length-1,c+1)); else if (a===1) { setIdx(0); set({ checks:{}, mem:'plus' }); } };
  const Comp = STEPS5[idx].Comp;
  return (
    <div style={{ height:'100%', display:'flex', flexDirection:'column', background:t.bg, position:'relative' }}>
      {t._glow && <div style={{ position:'absolute', top:-60, left:'50%', transform:'translateX(-50%)', width:340, height:300, borderRadius:'50%', pointerEvents:'none', background:`radial-gradient(circle, ${t.soft} 0%, transparent 68%)` }} />}
      {t._grain && <div style={{ position:'absolute', inset:0, pointerEvents:'none', zIndex:2, opacity:0.5, mixBlendMode:'overlay', backgroundImage:'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'120\' height=\'120\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23n)\' opacity=\'0.5\'/%3E%3C/svg%3E")' }} />}
      <div style={{ paddingTop:52, position:'relative', zIndex:5 }}>
        <div style={{ padding:'8px 18px 12px', display:'flex', alignItems:'center', gap:12 }}>
          <button onClick={() => setIdx(c=>Math.max(0,c-1))} disabled={idx===0} style={{ background:'none', border:'none', padding:4, cursor:idx===0?'default':'pointer', opacity:idx===0?0.25:1, display:'flex' }}>
            <Icon name="arrow" size={18} stroke={t.hi} style={{ transform:'scaleX(-1)' }} />
          </button>
          <div style={{ flex:1, display:'flex', gap:5, justifyContent:'center' }}>
            {STEPS5.map((s,i) => <div key={s.key} style={{ width:i===idx?22:7, height:7, borderRadius:9, background:i<=idx?t.accent:t.line, transition:'all .3s' }} />)}
          </div>
          <span style={{ width:18 }}></span>
        </div>
      </div>
      <div ref={scrollRef} style={{ flex:1, overflow:'auto', position:'relative', zIndex:5, paddingBottom:24 }}>
        <div key={idx} className="hv-screen"><Comp state={state} set={set} go={go} /></div>
      </div>
    </div>
  );
}

function App() {
  const [tw, setTweak] = window.useTweaks(TWEAK_DEFAULTS);
  const theme = THEMES[tw.accent] || THEMES.bronce;
  const t = { ...BASE, ...theme, _grain:tw.grain, _glow:tw.glow };
  return (
    <ThemeCtx.Provider value={t}>
      <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', padding:'30px 16px', background:'#000' }}>
        <div style={{ position:'relative' }}>
          <div style={{ position:'absolute', inset:-40, borderRadius:80, pointerEvents:'none', background:`radial-gradient(circle at 50% 30%, ${t.soft} 0%, transparent 60%)`, filter:'blur(20px)' }} />
          <div style={{ position:'relative', borderRadius:48, boxShadow:`0 50px 110px -30px ${t.soft}, 0 40px 80px rgba(0,0,0,0.5)` }}>
            <window.IOSDevice dark width={390} height={844}><Flow t={t} /></window.IOSDevice>
          </div>
        </div>
      </div>
      <window.TweaksPanel>
        <window.TweakSection label="Acento de marca" />
        <window.TweakRadio label="Acento" value={tw.accent} options={['noir','bronce','vital']} onChange={(v)=>setTweak('accent', v)} />
        <window.TweakSection label="Textura" />
        <window.TweakToggle label="Grano de película" value={tw.grain} onChange={(v)=>setTweak('grain', v)} />
        <window.TweakToggle label="Glow ambiental" value={tw.glow} onChange={(v)=>setTweak('glow', v)} />
      </window.TweaksPanel>
    </ThemeCtx.Provider>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
