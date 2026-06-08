// hv6-confianza.jsx — Tramo G: Confianza (Caso #1 + evidencia citada E1–E4)
const { BASE, THEMES, ThemeCtx, FOOT, MONO, SANS, Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Placeholder, Chip } = window.HV;

const PILLARS = [
  { icon:'lock',  t:'Médico responsable', d:'Cédula real. Toda prescripción la decide y firma un profesional — no un bot, no un anónimo.' },
  { icon:'check', t:'COA por lote',        d:'Cada insumo con certificado de análisis. Transparencia, no “confía en mí”.' },
  { icon:'chart', t:'Evidencia citada',    d:'Cada recomendación con literatura real y su nivel de evidencia. Datos, no marketing.' },
  { icon:'spark', t:'Caso #1: el fundador',d:'Documentamos nuestro propio protocolo: labs, energía, recuperación, mapas térmicos.' },
];
const CASO1 = {
  weeks: 12,
  metrics: [
    { k:'hs-CRP',     v:'−34%', dir:'down' },
    { k:'Energía AM', v:'+41%', dir:'up' },
    { k:'Recuperación', v:'+22%', dir:'up' },
    { k:'Sueño profundo', v:'+28 min', dir:'up' },
  ],
  note:'12 semanas documentadas: labs antes/después, diario de energía y recuperación, y mapas térmicos. Lo que pedimos, lo vivimos.',
};
const EV_LEGEND = [
  { lvl:'Fuerte',    d:'RCT o meta-análisis humano' },
  { lvl:'Moderada',  d:'Humano temprano (piloto / cohorte)' },
  { lvl:'Emergente', d:'Preclínico / mecanístico / animal' },
];
const EVIDENCE = [
  { ing:'Omega-3',     claim:'Baja inflamación (hs-CRP)',        lvl:'Fuerte',    src:'PMID 28900017 · 30415628' },
  { ing:'Creatina',    claim:'Fuerza y cognición',               lvl:'Fuerte',    src:'Kreider 2017 · PMID 28615996' },
  { ing:'NMN',         claim:'Sube NAD+ y energía celular',      lvl:'Moderada',  src:'PMID 33888596' },
  { ing:'Espermidina', claim:'Autofagia / longevidad',           lvl:'Moderada',  src:'PMID 19801973' },
  { ing:'GHK-Cu',      claim:'Remodelación de colágeno',         lvl:'Emergente', src:'PMID 29986520' },
  { ing:'BPC-157',     claim:'Reparación de tejido',             lvl:'Emergente', src:'PMID 21548867' },
];

function Head6({ kicker, title, sub }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div className="hv-rise" style={{ marginBottom:18 }}>
      <Eyebrow accent>{kicker}</Eyebrow>
      <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0', textWrap:'balance' }}>{title}</h1>
      {sub && <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'36ch' }}>{sub}</p>}
    </div>
  );
}
function Pad6({ children }) { return <div style={{ padding:'14px 20px 26px' }}>{children}</div>; }

// ═══════════ 1 · HUB ═══════════
function G1Hub({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad6>
      <Head6 kicker="Confianza = el producto" title="Por qué creerte"
        sub="En un mercado de frascos anónimos con disclaimer, la confianza es lo que vendemos. Así la construimos." />
      <div style={{ display:'flex', flexDirection:'column', gap:11 }}>
        {PILLARS.map((p,i) => (
          <GlassCard key={i} pad={15} className="hv-rise" style={{ animationDelay:`${i*0.05}s` }}>
            <div style={{ display:'flex', alignItems:'flex-start', gap:13 }}>
              <div style={{ width:38, height:38, borderRadius:11, flexShrink:0, background:t.soft, border:`1px solid ${t.ring}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
                <Icon name={p.icon} size={18} stroke={t.accent} />
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:SANS, fontWeight:800, fontSize:15, color:t.hi }}>{p.t}</div>
                <div style={{ fontFamily:SANS, fontSize:12.5, color:t.mid, marginTop:3, lineHeight:1.45 }}>{p.d}</div>
              </div>
            </div>
          </GlassCard>
        ))}
      </div>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Conoce el Caso #1 <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
    </Pad6>
  );
}

// ═══════════ 2 · CASO #1 ═══════════
function G2Caso({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad6>
      <Head6 kicker="Caso #1 · El fundador" title="Lo que pedimos, lo vivimos"
        sub="No es un testimonio comprado. Es el protocolo del fundador, documentado con datos — imposible de copiar." />
      <div className="hv-rise" style={{ display:'flex', gap:12, marginBottom:14 }}>
        <div style={{ flex:1 }}><Placeholder label="sem 0" h={110} /></div>
        <div style={{ flex:1 }}><Placeholder label={`sem ${CASO1.weeks}`} h={110} /></div>
      </div>
      <div className="hv-rise" style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:9, marginBottom:14 }}>
        {CASO1.metrics.map(m => (
          <div key={m.k} style={{ background:t.surface, border:`1px solid ${t.line}`, borderRadius:13, padding:'12px 13px', display:'flex', alignItems:'center', gap:10 }}>
            <Icon name={m.dir} size={16} stroke={t.accent} />
            <div>
              <div style={{ fontFamily:SANS, fontWeight:900, fontSize:16, color:t.accent }}>{m.v}</div>
              <div style={{ fontFamily:MONO, fontSize:9, color:t.low, marginTop:2 }}>{m.k}</div>
            </div>
          </div>
        ))}
      </div>
      <p className="hv-rise" style={{ fontFamily:SANS, fontSize:13, lineHeight:1.55, color:t.mid, margin:'0 2px' }}>{CASO1.note}</p>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Ver la evidencia <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <p style={{ fontFamily:MONO, fontSize:9.5, lineHeight:1.6, color:t.low, margin:'14px 2px 0' }}>Resultados de un caso individual, ilustrativos. No garantizan resultados. No es diagnóstico médico.</p>
    </Pad6>
  );
}

// ═══════════ 3 · EVIDENCIA CITADA ═══════════
function G3Evidencia({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad6>
      <Head6 kicker="Evidencia citada" title="Cada cosa, con su nivel"
        sub="Calificamos la fuerza de la evidencia en lenguaje plano. Donde es emergente, lo decimos — no la inflamos." />
      {/* leyenda */}
      <div className="hv-rise" style={{ display:'grid', gridTemplateColumns:'1fr', gap:8, marginBottom:16 }}>
        {EV_LEGEND.map(l => (
          <div key={l.lvl} style={{ display:'flex', alignItems:'center', gap:9, background:t.surface, border:`1px solid ${t.line}`, borderRadius:10, padding:'9px 11px' }}>
            <span style={{ fontFamily:MONO, fontSize:11, fontWeight:700, color:t.hi, background:t.surface2, border:`1px solid ${t.lineStrong}`, borderRadius:6, padding:'2px 7px', flexShrink:0 }}>{l.lvl}</span>
            <span style={{ fontFamily:SANS, fontSize:10.5, color:t.mid, lineHeight:1.25 }}>{l.d}</span>
          </div>
        ))}
      </div>
      {/* items */}
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {EVIDENCE.map((e,i) => (
          <GlassCard key={e.ing} pad={13} className="hv-rise" style={{ animationDelay:`${i*0.04}s` }}>
            <div style={{ display:'flex', alignItems:'center', gap:11 }}>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:SANS, fontWeight:800, fontSize:14, color:t.hi }}>{e.ing}</div>
                <div style={{ fontFamily:SANS, fontSize:12, color:t.mid, marginTop:2 }}>{e.claim}</div>
                <div style={{ fontFamily:MONO, fontSize:9.5, color:t.low, marginTop:4 }}>{e.src}</div>
              </div>
              <span style={{ fontFamily:MONO, fontSize:12, fontWeight:700, color:t.hi, background:t.surface2, border:`1px solid ${t.lineStrong}`, borderRadius:7, padding:'5px 10px', flexShrink:0 }}>{e.lvl}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <div style={{ marginTop:18 }}>
        <button onClick={() => go(1)} style={{ width:'100%', background:'none', border:'none', cursor:'pointer', fontFamily:MONO, fontSize:11, color:t.low, display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
          <Icon name="refresh" size={14} stroke={t.low} /> Reiniciar demo</button>
      </div>
    </Pad6>
  );
}

// ═══════════ SHELL ═══════════
const STEPS6 = [{ key:'hub', Comp:G1Hub }, { key:'caso', Comp:G2Caso }, { key:'evidencia', Comp:G3Evidencia }];
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{ "accent": "bronce", "grain": true, "glow": true }/*EDITMODE-END*/;

function Flow({ t }) {
  const [idx, setIdx] = React.useState(0);
  const scrollRef = React.useRef(null);
  React.useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [idx]);
  const go = (a) => { if (a==='+1') setIdx(c=>Math.min(STEPS6.length-1,c+1)); else if (a===1) setIdx(0); };
  const Comp = STEPS6[idx].Comp;
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
            {STEPS6.map((s,i) => <div key={s.key} style={{ width:i===idx?22:7, height:7, borderRadius:9, background:i<=idx?t.accent:t.line, transition:'all .3s' }} />)}
          </div>
          <span style={{ width:18 }}></span>
        </div>
      </div>
      <div ref={scrollRef} style={{ flex:1, overflow:'auto', position:'relative', zIndex:5, paddingBottom:24 }}>
        <div key={idx} className="hv-screen"><Comp go={go} /></div>
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
