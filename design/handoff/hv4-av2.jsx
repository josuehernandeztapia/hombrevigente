// hv4-av2.jsx — Tramo 2: Teleconsulta Av.2 (vía médica) → Receta → Magistral
const { BASE, THEMES, ThemeCtx, MEDICO, ELIGIBILITY, SLOTS, AV2, AV2_CONFIRM, STACKS, FOOT,
        MONO, SANS, Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Chip } = window.HV;
const RX = STACKS.find(s => s.id === 'reparacion'); // péptidos de prescripción (Av.2, vía médica)

function Head4({ kicker, title, sub }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div className="hv-rise" style={{ marginBottom:18 }}>
      <Eyebrow accent>{kicker}</Eyebrow>
      <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0', textWrap:'balance' }}>{title}</h1>
      {sub && <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'36ch' }}>{sub}</p>}
    </div>
  );
}
function Pad4({ children }) { return <div style={{ padding:'14px 20px 26px' }}>{children}</div>; }
function Foot4({ children }) {
  const t = React.useContext(ThemeCtx);
  return <p style={{ fontFamily:MONO, fontSize:9.5, lineHeight:1.6, color:t.low, margin:'16px 2px 0' }}>{children || FOOT}</p>;
}
function MedicoCard() {
  const t = React.useContext(ThemeCtx);
  return (
    <GlassCard pad={14} className="hv-rise">
      <div style={{ display:'flex', alignItems:'center', gap:13 }}>
        <div style={{ width:46, height:46, borderRadius:12, flexShrink:0, background:t.surface2, border:`1px solid ${t.line}`,
          display:'flex', alignItems:'center', justifyContent:'center',
          fontFamily:SANS, fontWeight:800, fontSize:16, color:t.accent }}>AL</div>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:'flex', alignItems:'center', gap:7 }}>
            <div style={{ fontFamily:SANS, fontWeight:800, fontSize:14.5, color:t.hi }}>{MEDICO.name}</div>
            <span style={{ fontFamily:MONO, fontSize:8.5, letterSpacing:'.08em', textTransform:'uppercase', color:t.low, border:`1px solid ${t.line}`, borderRadius:5, padding:'1px 5px' }}>ejemplo</span>
          </div>
          <div style={{ fontFamily:SANS, fontSize:11.5, color:t.mid, marginTop:2 }}>{MEDICO.spec}</div>
          <div style={{ fontFamily:MONO, fontSize:10, color:t.low, marginTop:4 }}>{MEDICO.ced}</div>
        </div>
        <Icon name="check" size={18} stroke={t.accent} />
      </div>
    </GlassCard>
  );
}

// ═══════════ 1 · ELEGIBILIDAD ═══════════
function A1Elegibilidad({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad4>
      <Head4 kicker="Av. 2 · Vía médica" title="Tu caso pasa por médico"
        sub="No todo se resuelve con suplementos. Cuando hay prescripción de por medio, decide y firma un médico responsable — no un bot." />
      <div style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low, margin:'2px 2px 10px' }}>Por qué te rutamos aquí</div>
      <div style={{ display:'flex', flexDirection:'column', gap:10, marginBottom:16 }}>
        {ELIGIBILITY.map((e,i) => (
          <GlassCard key={i} pad={13} className="hv-rise" style={{ animationDelay:`${i*0.06}s` }}>
            <div style={{ display:'flex', alignItems:'center', gap:11 }}>
              <Icon name="lock" size={17} stroke={t.accent} />
              <span style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.4, color:t.hi }}>{e}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <MedicoCard />
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Agendar valoración <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
      </div>
      <Foot4>Ningún insumo de Avenida 2 se entrega sin valoración y firma de un médico.</Foot4>
    </Pad4>
  );
}

// ═══════════ 2 · AGENDAR TELECONSULTA ═══════════
function A2Agenda({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const sel = state.slot ?? 0;
  return (
    <Pad4>
      <Head4 kicker="Teleconsulta" title="Elige tu horario"
        sub="30 min por videollamada. El médico revisa tus datos antes de la cita." />
      <MedicoCard />
      <div style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low, margin:'18px 2px 10px' }}>Horarios disponibles</div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
        {SLOTS.map((s,i) => {
          const on = sel === i;
          return (
            <GlassCard key={i} active={on} onClick={() => set(st => ({ ...st, slot:i }))} pad={14}
              className="hv-rise" style={{ animationDelay:`${i*0.04}s` }}>
              <div style={{ fontFamily:SANS, fontWeight:800, fontSize:15, color: on?t.accent:t.hi }}>{s.d}</div>
              <div style={{ fontFamily:MONO, fontSize:12, color:t.mid, marginTop:4 }}>{s.t}</div>
            </GlassCard>
          );
        })}
      </div>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go('+1')}>Confirmar cita · {AV2.tele}</PrimaryButton>
      </div>
      <Foot4>El costo de la teleconsulta se acredita a tu protocolo si continúas.</Foot4>
    </Pad4>
  );
}

// ═══════════ 3 · RECETA + MAGISTRAL ═══════════
function A3Receta({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const ok = !!state.consent;
  return (
    <Pad4>
      <Head4 kicker="Receta · Magistral" title="Tu protocolo Pro"
        sub="Tras tu valoración, el médico definió y firmó este protocolo. Se prepara bajo receta, no se importa gris." />
      {/* receta firmada */}
      <GlassCard className="hv-rise" pad={16} style={{ marginBottom:12 }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:11 }}>
          <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.12em', textTransform:'uppercase', color:t.low }}>Receta · firmada</span>
          <Chip accent>{MEDICO.ced}</Chip>
        </div>
        <div style={{ fontFamily:SANS, fontWeight:800, fontSize:16, color:t.hi }}>Protocolo magistral de reparación</div>
        <div style={{ fontFamily:SANS, fontSize:12, color:t.mid, marginTop:3 }}>Péptidos · reparación estructural y nerviosa</div>
        <div style={{ display:'flex', flexWrap:'wrap', gap:7, margin:'11px 0 12px' }}>
          {RX.items.map(it => <Chip key={it} accent>{it}</Chip>)}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:9, paddingTop:12, borderTop:`1px solid ${t.line}` }}>
          <Icon name="check" size={16} stroke={t.accent} />
          <span style={{ fontFamily:SANS, fontSize:12.5, color:t.mid }}>Farmacia magistral · preparado con <b style={{ color:t.hi, fontWeight:700 }}>COA por lote</b></span>
        </div>
      </GlassCard>
      {/* consentimiento */}
      <button onClick={() => set(s => ({ ...s, consent:!s.consent }))} style={{ width:'100%', textAlign:'left', cursor:'pointer',
        background:t.surface, border:`1px solid ${ok?t.ring:t.line}`, borderRadius:14, padding:'13px 14px', display:'flex', alignItems:'flex-start', gap:12 }}>
        <span style={{ width:22, height:22, borderRadius:6, flexShrink:0, marginTop:1, background:ok?t.accent:'transparent', border:`1.5px solid ${ok?t.accent:t.lineStrong}`,
          display:'flex', alignItems:'center', justifyContent:'center' }}>{ok && <Icon name="check" size={14} stroke={t.on} />}</span>
        <span style={{ fontFamily:SANS, fontSize:12.5, lineHeight:1.45, color:ok?t.hi:t.mid }}>Acepto la receta y el consentimiento informado de optimización con péptidos bajo supervisión médica.</span>
      </button>
      <div style={{ marginTop:16 }}>
        <PrimaryButton disabled={!ok} onClick={() => go('+1')}>
          {ok ? <><Icon name="lock" size={16} stroke={t.on} /> Activar protocolo Pro · {AV2.protocolo}{AV2.protoUnit}</> : 'Acepta el consentimiento para continuar'}
        </PrimaryButton>
      </div>
      <Foot4>Optimización bajo prescripción y supervisión médica. No sustituye atención médica integral. Médico y cédula mostrados son un ejemplo — pendiente responsable sanitario real.</Foot4>
    </Pad4>
  );
}

// ═══════════ 4 · CONFIRMACIÓN ═══════════
function A4Confirma({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad4>
      <div className="hv-rise" style={{ display:'flex', flexDirection:'column', alignItems:'center', textAlign:'center', paddingTop:14 }}>
        <div style={{ width:72, height:72, borderRadius:999, background:t.soft, border:`1px solid ${t.ring}`, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:18 }}>
          <Icon name="check" size={36} stroke={t.accent} />
        </div>
        <Eyebrow accent>Protocolo Pro activo</Eyebrow>
        <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0' }}>El médico ya está contigo</h1>
        <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'32ch' }}>Tu caso quedó bajo seguimiento clínico. Esto es lo que sigue:</p>
      </div>
      <div style={{ display:'flex', flexDirection:'column', gap:10, marginTop:22 }}>
        {AV2_CONFIRM.map((s,i) => (
          <GlassCard key={i} pad={14} className="hv-rise" style={{ animationDelay:`${i*0.07}s` }}>
            <div style={{ display:'flex', alignItems:'center', gap:12 }}>
              <span style={{ fontFamily:MONO, fontSize:13, fontWeight:700, color:t.accent, width:18, flexShrink:0 }}>{i+1}</span>
              <span style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.4, color:t.hi }}>{s}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <div style={{ marginTop:20, display:'flex', flexDirection:'column', gap:10 }}>
        <PrimaryButton onClick={() => window.location.href='Seguimiento%20Vigente.html'}><Icon name="chart" size={16} stroke={t.on} /> Ver mi seguimiento</PrimaryButton>
        <button onClick={() => go(1)} style={{ width:'100%', background:'none', border:'none', cursor:'pointer', fontFamily:MONO, fontSize:11, color:t.low, display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
          <Icon name="refresh" size={14} stroke={t.low} /> Reiniciar demo</button>
      </div>
    </Pad4>
  );
}

// ═══════════ SHELL ═══════════
const STEPS4 = [
  { key:'elegibilidad', Comp:A1Elegibilidad },
  { key:'agenda',       Comp:A2Agenda },
  { key:'receta',       Comp:A3Receta },
  { key:'confirma',     Comp:A4Confirma },
];
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{ "accent": "bronce", "grain": true, "glow": true }/*EDITMODE-END*/;

function Flow({ t }) {
  const [idx, setIdx] = React.useState(0);
  const [state, set] = React.useState({ slot:0, consent:false });
  const scrollRef = React.useRef(null);
  React.useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [idx]);
  const go = (a) => { if (a==='+1') setIdx(c=>Math.min(STEPS4.length-1,c+1)); else if (a===1) { setIdx(0); set({ slot:0, consent:false }); } };
  const Comp = STEPS4[idx].Comp;
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
            {STEPS4.map((s,i) => <div key={s.key} style={{ width:i===idx?22:7, height:7, borderRadius:9, background:i<=idx?t.accent:t.line, transition:'all .3s' }} />)}
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
