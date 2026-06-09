// hv7-canal.jsx — E: Guiones de WhatsApp · F: Estados y errores
const { BASE, THEMES, ThemeCtx, WA_THREADS, STATES, MONO, SANS,
        Icon, Eyebrow, GlassCard, PrimaryButton, GhostButton } = window.HV;

// Verde WhatsApp solo para el canal (es chrome de la plataforma, no la marca)
const WA = { bg:'#0B141A', bar:'#1F2C34', inb:'#1F2C34', out:'#005C4B', tick:'#53BDEB', txt:'#E9EDEF', sub:'#8696A0' };

// ─────────── E · Conversación WhatsApp ───────────
function Bubble({ m, t }) {
  const out = m.s === 'u';
  const base = { maxWidth:'80%', padding:'7px 10px 8px', borderRadius:12, fontFamily:SANS, fontSize:13.5,
    lineHeight:1.4, color:WA.txt, whiteSpace:'pre-wrap', position:'relative', boxShadow:'0 1px 1px rgba(0,0,0,.18)' };
  if (m.kind === 'chips') {
    return (
      <div style={{ alignSelf:'flex-start', display:'flex', flexDirection:'column', gap:6, width:'80%' }}>
        {m.chips.map((c,i) => (
          <div key={i} style={{ background:WA.inb, borderRadius:10, padding:'10px 12px', textAlign:'center',
            fontFamily:SANS, fontWeight:600, fontSize:13, color:t.accent, border:`1px solid rgba(255,255,255,.06)`,
            display:'flex', alignItems:'center', justifyContent:'center', gap:7 }}>
            {i===0 && <Icon name="arrow" size={14} stroke={t.accent} />}{c}
          </div>
        ))}
      </div>
    );
  }
  if (m.kind === 'card') {
    return (
      <div style={{ ...base, alignSelf:'flex-start', background:WA.inb, borderTopLeftRadius:3, padding:0, overflow:'hidden', width:'80%' }}>
        <div style={{ height:96, background:`repeating-linear-gradient(135deg, rgba(255,255,255,.04) 0 8px, transparent 8px 16px)`,
          display:'flex', alignItems:'center', justifyContent:'center', fontFamily:MONO, fontSize:10, color:WA.sub, letterSpacing:'.1em' }}>VIGENTE</div>
        <div style={{ padding:'10px 12px 12px' }}>
          <div style={{ fontFamily:SANS, fontWeight:800, fontSize:14, color:WA.txt }}>{m.card.title}</div>
          <div style={{ fontFamily:MONO, fontSize:10, color:WA.sub, margin:'3px 0 9px' }}>{m.card.sub}</div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:5 }}>
            {m.card.tags.map(x => <span key={x} style={{ fontFamily:MONO, fontSize:10, color:t.accent, background:t.soft, border:`1px solid ${t.ring}`, borderRadius:6, padding:'3px 7px' }}>{x}</span>)}
          </div>
        </div>
      </div>
    );
  }
  return (
    <div style={{ ...base, alignSelf: out?'flex-end':'flex-start', background: out?WA.out:WA.inb,
      borderTopRightRadius: out?3:12, borderTopLeftRadius: out?12:3 }}>
      {m.kind === 'img' && <div style={{ height:70, borderRadius:7, marginBottom:5, background:'rgba(255,255,255,.07)',
        display:'flex', alignItems:'center', justifyContent:'center', fontSize:22 }}>📷</div>}
      {m.t}
      <span style={{ float:'right', fontFamily:MONO, fontSize:9, color: out?WA.tick:WA.sub, margin:'4px 0 -2px 8px' }}>
        9:4{m.s==='u'?'1 ✓✓':'0'}
      </span>
    </div>
  );
}

function WhatsAppThread({ thread, t }) {
  const [count, setCount] = React.useState(1);
  React.useEffect(() => {
    setCount(1);
    const id = setInterval(() => setCount(c => c < thread.msgs.length ? c+1 : c), 620);
    return () => clearInterval(id);
  }, [thread.id]);
  const bodyRef = React.useRef(null);
  React.useEffect(() => { if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight; }, [count]);
  return (
    <div style={{ height:'100%', display:'flex', flexDirection:'column', background:WA.bg,
      backgroundImage:'radial-gradient(rgba(255,255,255,.022) 1px, transparent 1px)', backgroundSize:'18px 18px' }}>
      {/* header WA */}
      <div style={{ paddingTop:44, background:WA.bar, flexShrink:0 }}>
        <div style={{ display:'flex', alignItems:'center', gap:11, padding:'9px 14px' }}>
          <Icon name="arrow" size={20} stroke={WA.txt} style={{ transform:'scaleX(-1)' }} />
          <div style={{ width:38, height:38, borderRadius:999, background:t.accent, display:'flex', alignItems:'center', justifyContent:'center',
            fontFamily:SANS, fontWeight:900, fontSize:16, color:t.on, flexShrink:0 }}>V</div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:SANS, fontWeight:700, fontSize:15, color:WA.txt }}>Hombre Vigente</div>
            <div style={{ fontFamily:SANS, fontSize:11, color:WA.sub }}>concierge · en línea</div>
          </div>
          <Icon name="chat" size={19} stroke={WA.sub} />
        </div>
      </div>
      {/* body */}
      <div ref={bodyRef} style={{ flex:1, overflow:'auto', padding:'14px 12px', display:'flex', flexDirection:'column', gap:7 }}>
        <div style={{ alignSelf:'center', background:'rgba(31,44,52,.7)', borderRadius:8, padding:'4px 11px',
          fontFamily:SANS, fontSize:10.5, color:WA.sub, marginBottom:4 }}>🔒 Mensajes cifrados de extremo a extremo</div>
        {thread.msgs.slice(0, count).map((m,i) => <Bubble key={i} m={m} t={t} />)}
        {count < thread.msgs.length && (
          <div style={{ alignSelf: thread.msgs[count].s==='u'?'flex-end':'flex-start', background:WA.inb, borderRadius:12, padding:'10px 13px', display:'flex', gap:4 }}>
            {[0,1,2].map(i => <span key={i} className="hv-typing" style={{ width:6, height:6, borderRadius:9, background:WA.sub, animationDelay:`${i*0.15}s` }} />)}
          </div>
        )}
      </div>
      {/* input fake */}
      <div style={{ flexShrink:0, padding:'8px 12px 12px', background:WA.bar, display:'flex', alignItems:'center', gap:9 }}>
        <div style={{ flex:1, background:WA.bg, borderRadius:999, padding:'10px 15px', fontFamily:SANS, fontSize:13, color:WA.sub }}>Mensaje</div>
        <div style={{ width:40, height:40, borderRadius:999, background:t.accent, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
          <Icon name="arrow" size={18} stroke={t.on} />
        </div>
      </div>
    </div>
  );
}

// ─────────── F · Estado/Error ───────────
function StateScreen({ st, t }) {
  const toneRing = st.kind==='error' ? 'rgba(224,121,95,.4)' : t.ring;
  const toneIcon = st.kind==='error' ? t.danger : t.accent;
  return (
    <div style={{ height:'100%', display:'flex', flexDirection:'column', background:t.bg, position:'relative' }}>
      {t._grain && <div style={{ position:'absolute', inset:0, pointerEvents:'none', zIndex:2, opacity:0.45, mixBlendMode:'overlay', backgroundImage:'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'120\' height=\'120\'%3E%3Cfilter id=\'n\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23n)\' opacity=\'0.5\'/%3E%3C/svg%3E")' }} />}
      <div style={{ paddingTop:56, flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', textAlign:'center', padding:'56px 30px 30px', position:'relative', zIndex:5 }}>
        <div style={{ width:84, height:84, borderRadius:999, background: st.kind==='error'?'rgba(224,121,95,.1)':t.soft,
          border:`1px solid ${toneRing}`, display:'flex', alignItems:'center', justifyContent:'center', marginBottom:24 }}>
          <Icon name={st.icon} size={38} stroke={toneIcon} />
        </div>
        <div>
          <Eyebrow>{st.kind==='error'?'Algo salió mal':st.kind==='empty'?'Sin datos aún':st.kind==='wait'?'En proceso':'Tu siguiente paso'}</Eyebrow>
        </div>
        <h1 style={{ fontFamily:SANS, fontWeight:900, fontSize:26, lineHeight:1.1, letterSpacing:'-0.02em', color:t.hi, margin:'12px 0 0' }}>{st.title}</h1>
        <p style={{ fontFamily:SANS, fontSize:14, lineHeight:1.55, color:t.mid, margin:'12px 0 0', maxWidth:'32ch' }}>{st.body}</p>
      </div>
      <div style={{ padding:'0 24px 30px', display:'flex', flexDirection:'column', gap:10, position:'relative', zIndex:5 }}>
        <PrimaryButton onClick={() => {}}>{st.primary}</PrimaryButton>
        {st.ghost && <GhostButton onClick={() => {}}>{st.ghost}</GhostButton>}
      </div>
    </div>
  );
}

// ─────────── SHELL ───────────
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{ "accent": "bronce", "mode": "whatsapp", "grain": true, "glow": true }/*EDITMODE-END*/;

function Selector({ items, sel, onPick, t, getLabel, getSub }) {
  return (
    <div style={{ position:'fixed', top:0, left:0, right:0, zIndex:50, background:'rgba(8,8,10,.82)', backdropFilter:'blur(10px)', borderBottom:`1px solid ${t.line}` }}>
      <div style={{ display:'flex', gap:8, overflowX:'auto', padding:'12px 16px' }}>
        {items.map((it,i) => {
          const on = sel === i;
          return (
            <button key={i} onClick={() => onPick(i)} style={{ flexShrink:0, cursor:'pointer', textAlign:'left',
              background: on?t.soft:'transparent', border:`1px solid ${on?t.ring:t.line}`, borderRadius:11, padding:'8px 13px' }}>
              <div style={{ fontFamily:SANS, fontWeight:700, fontSize:12.5, color: on?t.accent:t.hi, whiteSpace:'nowrap' }}>{getLabel(it)}</div>
              <div style={{ fontFamily:MONO, fontSize:9, color:t.low, marginTop:2, whiteSpace:'nowrap' }}>{getSub(it)}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function App() {
  const [tw, setTweak] = window.useTweaks(TWEAK_DEFAULTS);
  const theme = THEMES[tw.accent] || THEMES.bronce;
  const t = { ...BASE, ...theme, _grain:tw.grain, _glow:tw.glow };
  const mode = tw.mode || 'whatsapp';
  const [waSel, setWaSel] = React.useState(0);
  const [stSel, setStSel] = React.useState(0);

  return (
    <ThemeCtx.Provider value={t}>
      {mode === 'whatsapp'
        ? <Selector items={WA_THREADS} sel={waSel} onPick={setWaSel} t={t} getLabel={x=>x.title} getSub={x=>x.sub} />
        : <Selector items={STATES} sel={stSel} onPick={setStSel} t={t} getLabel={x=>x.title} getSub={x=>x.kind} />}

      <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', padding:'90px 16px 30px', background:'#000' }}>
        <div style={{ position:'relative' }}>
          <div style={{ position:'absolute', inset:-40, borderRadius:80, pointerEvents:'none', background:`radial-gradient(circle at 50% 30%, ${t.soft} 0%, transparent 60%)`, filter:'blur(20px)' }} />
          <div style={{ position:'relative', borderRadius:48, boxShadow:`0 50px 110px -30px ${t.soft}, 0 40px 80px rgba(0,0,0,0.5)` }}>
            <window.IOSDevice dark width={390} height={844}>
              {mode === 'whatsapp'
                ? <WhatsAppThread thread={WA_THREADS[waSel]} t={t} />
                : <StateScreen st={STATES[stSel]} t={t} />}
            </window.IOSDevice>
          </div>
        </div>
      </div>

      <window.TweaksPanel>
        <window.TweakSection label="Qué ver" />
        <window.TweakRadio label="Modo" value={mode} options={['whatsapp','estados']} onChange={(v)=>setTweak('mode', v)} />
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
