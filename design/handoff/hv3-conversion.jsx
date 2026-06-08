// hv3-conversion.jsx — Tramo 1: Resultado del Escaneo → Programa → Checkout Av.1 → Confirmación
const { BASE, THEMES, ThemeCtx, SCAN, STACK_VIGENTE, PROGRAMS, CHECKOUT, CONFIRM_STEPS,
        RAILS, FOOT, MONO, SANS, Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton, Chip } = window.HV;

function Head3({ kicker, title, sub }) {
  const t = React.useContext(ThemeCtx);
  return (
    <div className="hv-rise" style={{ marginBottom:18 }}>
      <Eyebrow accent>{kicker}</Eyebrow>
      <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em',
        color:t.hi, margin:'12px 0 0', textWrap:'balance' }}>{title}</h1>
      {sub && <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'36ch' }}>{sub}</p>}
    </div>
  );
}
function Pad3({ children }) { return <div style={{ padding:'14px 20px 26px' }}>{children}</div>; }
function Foot3({ children }) {
  const t = React.useContext(ThemeCtx);
  return <p style={{ fontFamily:MONO, fontSize:9.5, lineHeight:1.6, color:t.low, margin:'16px 2px 0' }}>{children || FOOT}</p>;
}

// ═══════════ 1 · RESULTADO DEL ESCANEO (gratis) ═══════════
function C1Resultado({ go }) {
  const t = React.useContext(ThemeCtx);
  const R=40, C=2*Math.PI*R;
  return (
    <Pad3>
      <Head3 kicker="Tu lectura inicial · Gratis" title="Tu Escaneo Vigente"
        sub="Esto es tu punto de partida con los 3 datos que diste. La lectura a fondo viene en el diagnóstico completo." />
      <GlassCard className="hv-rise" pad={18} style={{ display:'flex', alignItems:'center', gap:18, marginBottom:14 }}>
        <svg width="96" height="96" viewBox="0 0 96 96" style={{ flexShrink:0 }}>
          <circle cx="48" cy="48" r={R} fill="none" stroke={t.line} strokeWidth="7" />
          <circle cx="48" cy="48" r={R} fill="none" stroke={t.accent} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={C} strokeDashoffset={C*(1-SCAN.score/100)} transform="rotate(-90 48 48)" style={{ transition:'stroke-dashoffset 1s' }} />
          <text x="48" y="50" textAnchor="middle" fontFamily={SANS} fontSize="26" fontWeight="900" fill={t.hi}>{SCAN.score}</text>
          <text x="48" y="65" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={t.low}>/ 100</text>
        </svg>
        <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
          {SCAN.signals.map(s => (
            <div key={s.k} style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ width:5, height:5, borderRadius:9, background:t.accent, flexShrink:0 }} />
              <span style={{ fontFamily:SANS, fontSize:13, fontWeight:700, color:t.hi }}>{s.k}</span>
              <span style={{ fontFamily:MONO, fontSize:10.5, color:t.mid }}>{s.v}</span>
            </div>
          ))}
        </div>
      </GlassCard>
      <GlassCard className="hv-rise" pad={15} active style={{ animationDelay:'.06s' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:9 }}>
          <span style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.12em', textTransform:'uppercase', color:t.low }}>Mini-recomendación</span>
          <Chip>sin receta</Chip>
        </div>
        <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.hi, margin:'0 0 11px' }}>{SCAN.reco}</p>
        <div style={{ fontFamily:SANS, fontWeight:800, fontSize:14, color:t.hi, marginBottom:8 }}>{STACK_VIGENTE.name}</div>
        <div style={{ display:'flex', flexWrap:'wrap', gap:7 }}>
          {STACK_VIGENTE.items.map(it => <Chip key={it}>{it}</Chip>)}
        </div>
      </GlassCard>
      <div className="hv-rise" style={{ marginTop:20, display:'flex', flexDirection:'column', gap:10 }}>
        <PrimaryButton onClick={() => go('+1')}>Activar mi protocolo <Icon name="arrow" size={18} stroke={t.on} /></PrimaryButton>
        <GhostButton onClick={() => go('+1')}><Icon name="chat" size={16} stroke={t.hi} /> Hablar por WhatsApp</GhostButton>
      </div>
      <Foot3>Lectura de optimización con 3 datos. No es diagnóstico médico.</Foot3>
    </Pad3>
  );
}

// ═══════════ 2 · ELEGIR PROGRAMA ═══════════
function C2Programa({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const sel = state.program || 'av1';
  const chosen = PROGRAMS.find(p => p.id === sel) || PROGRAMS[1];
  return (
    <Pad3>
      <Head3 kicker="Programas" title="Elige tu profundidad"
        sub="Empezaste gratis. Subes según tu objetivo. Lo de prescripción, solo por la vía médica." />
      <div style={{ display:'flex', flexDirection:'column', gap:11 }}>
        {PROGRAMS.map((p,i) => {
          const on = sel === p.id, disabled = p.done;
          return (
            <GlassCard key={p.id} active={on && !disabled} onClick={() => !disabled && set(s => ({ ...s, program:p.id }))} pad={15}
              className="hv-rise" style={{ animationDelay:`${i*0.05}s`, opacity:disabled?0.5:1, cursor:disabled?'default':'pointer' }}>
              <div style={{ display:'flex', alignItems:'flex-start', justifyContent:'space-between', gap:10 }}>
                <div style={{ flex:1 }}>
                  <div style={{ display:'flex', alignItems:'center', gap:8, flexWrap:'wrap' }}>
                    <span style={{ fontFamily:MONO, fontSize:9.5, letterSpacing:'0.12em', textTransform:'uppercase', color:t.low }}>{p.tier}</span>
                    {p.best && <Chip accent>recomendado</Chip>}
                    {p.done && <Chip>hecho ✓</Chip>}
                    {p.medico && <Icon name="lock" size={13} stroke={t.mid} />}
                  </div>
                  <div style={{ fontFamily:SANS, fontWeight:800, fontSize:15.5, color:t.hi, marginTop:6 }}>{p.name}</div>
                  <div style={{ fontFamily:SANS, fontSize:12, color:t.mid, marginTop:3, lineHeight:1.4 }}>{p.note}</div>
                </div>
                <div style={{ width:20, height:20, borderRadius:999, flexShrink:0, marginTop:2,
                  border:`2px solid ${on&&!disabled?t.accent:t.lineStrong}`, display:'flex', alignItems:'center', justifyContent:'center' }}>
                  {on && !disabled && <span style={{ width:9, height:9, borderRadius:999, background:t.accent }} />}
                </div>
              </div>
              <div style={{ fontFamily:SANS, fontWeight:800, fontSize:14, color: on&&!disabled?t.accent:t.hi, marginTop:9 }}>{p.price}</div>
            </GlassCard>
          );
        })}
      </div>
      <div style={{ marginTop:18 }}>
        <PrimaryButton onClick={() => go(chosen.medico ? 'wa' : '+1')}>
          {chosen.medico ? <><Icon name="chat" size={16} stroke={t.on} /> Agendar valoración médica</> : <>Continuar con {chosen.name.split(' ')[0]} <Icon name="arrow" size={18} stroke={t.on} /></>}
        </PrimaryButton>
      </div>
      <Foot3>La Avenida 2 (prescripción) requiere valoración y firma de un médico responsable.</Foot3>
    </Pad3>
  );
}

// ═══════════ 3 · CHECKOUT Av.1 ═══════════
function C3Checkout({ state, set, go }) {
  const t = React.useContext(ThemeCtx);
  const rail = state.rail || 'Tarjeta';
  const msi = !!state.msi;
  return (
    <Pad3>
      <Head3 kicker="Activación · Av. 1" title="Tu protocolo"
        sub="Diagnóstico hoy + tu Stack Vigente mensual. Cancela cuando quieras." />
      {/* resumen */}
      <GlassCard className="hv-rise" pad={16} style={{ marginBottom:12 }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', paddingBottom:12, borderBottom:`1px solid ${t.line}` }}>
          <div>
            <div style={{ fontFamily:SANS, fontWeight:700, fontSize:14, color:t.hi }}>{CHECKOUT.diagLabel}</div>
            <div style={{ fontFamily:MONO, fontSize:10.5, color:t.low, marginTop:3 }}>{CHECKOUT.diagSub} · única vez</div>
          </div>
          <span style={{ fontFamily:SANS, fontWeight:800, fontSize:15, color:t.hi }}>${CHECKOUT.diagPrice.toLocaleString('es-MX')}</span>
        </div>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', paddingTop:12 }}>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:SANS, fontWeight:700, fontSize:14, color:t.hi }}>{STACK_VIGENTE.name}</div>
            <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginTop:8 }}>
              {STACK_VIGENTE.items.map(it => <Chip key={it}>{it}</Chip>)}
            </div>
          </div>
          <span style={{ fontFamily:SANS, fontWeight:800, fontSize:15, color:t.hi, whiteSpace:'nowrap', marginLeft:8 }}>${CHECKOUT.stackPrice}<span style={{ fontFamily:MONO, fontSize:10, color:t.low }}>/mes</span></span>
        </div>
      </GlassCard>
      {/* pago MX */}
      <div style={{ fontFamily:MONO, fontSize:10, letterSpacing:'0.1em', textTransform:'uppercase', color:t.low, margin:'2px 2px 9px' }}>Método de pago</div>
      <div style={{ display:'flex', flexWrap:'wrap', gap:8, marginBottom:12 }}>
        {RAILS.map(r => {
          const on = rail === r;
          return <button key={r} onClick={() => set(s => ({ ...s, rail:r }))} style={{ cursor:'pointer', fontFamily:SANS, fontWeight:600, fontSize:12.5,
            padding:'9px 14px', borderRadius:999, color:on?t.accent:t.mid, background:on?t.soft:'transparent', border:`1px solid ${on?t.ring:t.lineStrong}` }}>{r}</button>;
        })}
      </div>
      <button onClick={() => set(s => ({ ...s, msi:!s.msi }))} style={{ cursor:'pointer', display:'flex', alignItems:'center', gap:9,
        fontFamily:SANS, fontWeight:600, fontSize:13, color:msi?t.accent:t.mid, background:'transparent', border:'none', padding:'0 2px', marginBottom:8 }}>
        <span style={{ width:20, height:20, borderRadius:6, background:msi?t.accent:'transparent', border:`1.5px solid ${msi?t.accent:t.lineStrong}`,
          display:'flex', alignItems:'center', justifyContent:'center' }}>{msi && <Icon name="check" size={13} stroke={t.on} />}</span>
        Diferir el diagnóstico a 3 MSI (Kueski)</button>
      <div style={{ marginTop:14 }}>
        <PrimaryButton onClick={() => go('+1')}>
          <Icon name="lock" size={16} stroke={t.on} /> Pagar y activar · {CHECKOUT.todayTotal} hoy
        </PrimaryButton>
      </div>
      <Foot3>Pago seguro. Hoy: diagnóstico + 1er mes de Stack. Luego ${CHECKOUT.stackPrice}/mes hasta que canceles. No es medicamento.</Foot3>
    </Pad3>
  );
}

// ═══════════ 4 · CONFIRMACIÓN ═══════════
function C4Confirma({ go }) {
  const t = React.useContext(ThemeCtx);
  return (
    <Pad3>
      <div className="hv-rise" style={{ display:'flex', flexDirection:'column', alignItems:'center', textAlign:'center', paddingTop:14 }}>
        <div style={{ width:72, height:72, borderRadius:999, background:t.soft, border:`1px solid ${t.ring}`,
          display:'flex', alignItems:'center', justifyContent:'center', marginBottom:18 }}>
          <Icon name="check" size={36} stroke={t.accent} />
        </div>
        <Eyebrow accent>Protocolo activo</Eyebrow>
        <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:28, lineHeight:1.07, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0' }}>Ya eres Vigente</h1>
        <p style={{ fontFamily:SANS, fontSize:13.5, lineHeight:1.5, color:t.mid, margin:'10px 0 0', maxWidth:'32ch' }}>
          Tu diagnóstico está en proceso y tu Stack Vigente en camino. Esto es lo que sigue:
        </p>
      </div>
      <div style={{ display:'flex', flexDirection:'column', gap:10, marginTop:22 }}>
        {CONFIRM_STEPS.map((s,i) => (
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
        <button onClick={() => go(1)} style={{ width:'100%', background:'none', border:'none', cursor:'pointer',
          fontFamily:MONO, fontSize:11, color:t.low, display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
          <Icon name="refresh" size={14} stroke={t.low} /> Reiniciar demo</button>
      </div>
    </Pad3>
  );
}

// ═══════════ SHELL ═══════════
const STEPS3 = [
  { key:'resultado', Comp:C1Resultado },
  { key:'programa',  Comp:C2Programa },
  { key:'checkout',  Comp:C3Checkout },
  { key:'confirma',  Comp:C4Confirma },
];
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{ "accent": "bronce", "grain": true, "glow": true }/*EDITMODE-END*/;

function Flow({ t }) {
  const [idx, setIdx] = React.useState(() => {
    const h = (window.location.hash || '').replace('#','');
    return h === 'checkout' ? 2 : h === 'programa' ? 1 : 0;
  });
  const [state, set] = React.useState({ program:'av1', rail:'Tarjeta', msi:false });
  const [wa, setWa] = React.useState(false);
  const scrollRef = React.useRef(null);
  React.useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [idx]);
  const go = (a) => { if (a==='+1') setIdx(c=>Math.min(STEPS3.length-1,c+1)); else if (a===1) { setIdx(0); set({ program:'av1', rail:'Tarjeta', msi:false }); } else if (a==='wa') window.location.href='Teleconsulta%20Vigente.html'; };
  const Comp = STEPS3[idx].Comp;
  return (
    <div style={{ height:'100%', display:'flex', flexDirection:'column', background:t.bg, position:'relative' }}>
      {t._glow && <div style={{ position:'absolute', top:-60, left:'50%', transform:'translateX(-50%)', width:340, height:300, borderRadius:'50%', pointerEvents:'none', background:`radial-gradient(circle, ${t.soft} 0%, transparent 68%)` }} />}
      {t._grain && <div style={{ position:'absolute', inset:0, pointerEvents:'none', zIndex:2, opacity:0.5, mixBlendMode:'overlay', backgroundImage:'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'120\' height=\'120\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23n)\' opacity=\'0.5\'/%3E%3C/svg%3E")' }} />}
      {/* barra superior: back + dots */}
      <div style={{ paddingTop:52, position:'relative', zIndex:5 }}>
        <div style={{ padding:'8px 18px 12px', display:'flex', alignItems:'center', gap:12 }}>
          <button onClick={() => setIdx(c=>Math.max(0,c-1))} disabled={idx===0} style={{ background:'none', border:'none', padding:4, cursor:idx===0?'default':'pointer', opacity:idx===0?0.25:1, display:'flex' }}>
            <Icon name="arrow" size={18} stroke={t.hi} style={{ transform:'scaleX(-1)' }} />
          </button>
          <div style={{ flex:1, display:'flex', gap:5, justifyContent:'center' }}>
            {STEPS3.map((s,i) => <div key={s.key} style={{ width:i===idx?22:7, height:7, borderRadius:9, background:i<=idx?t.accent:t.line, transition:'all .3s' }} />)}
          </div>
          <span style={{ fontFamily:MONO, fontSize:11, color:t.low, width:18 }}></span>
        </div>
      </div>
      <div ref={scrollRef} style={{ flex:1, overflow:'auto', position:'relative', zIndex:5, paddingBottom:24 }}>
        <div key={idx} className="hv-screen"><Comp state={state} set={set} go={go} /></div>
      </div>
      {wa && (
        <div onClick={() => setWa(false)} style={{ position:'absolute', inset:0, zIndex:80, background:'rgba(0,0,0,0.62)', backdropFilter:'blur(6px)', display:'flex', alignItems:'center', justifyContent:'center', padding:24 }}>
          <div onClick={e=>e.stopPropagation()} className="hv-rise" style={{ background:t.bg2, border:`1px solid ${t.line}`, borderRadius:20, padding:22, textAlign:'center', maxWidth:300 }}>
            <Icon name="chat" size={32} stroke={t.accent} style={{ margin:'0 auto 12px' }} />
            <div style={{ fontFamily:SANS, fontWeight:800, fontSize:16, color:t.hi }}>Vía médica</div>
            <p style={{ fontFamily:SANS, fontSize:13, lineHeight:1.5, color:t.mid, margin:'8px 0 16px' }}>Te conectamos por WhatsApp con el equipo para agendar tu teleconsulta. (Flujo Av.2 — siguiente tramo.)</p>
            <GhostButton onClick={() => setWa(false)}>Entendido</GhostButton>
          </div>
        </div>
      )}
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
