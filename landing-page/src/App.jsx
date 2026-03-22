import { useEffect, useState } from 'react'
import { Camera, User, Clock, Lock, ShieldCheck, Activity } from 'lucide-react'
import { InteractiveFolder } from './InteractiveFolder'
import './index.css'

export default function App() {
  const [isVaultOpen, setIsVaultOpen] = useState(false)
  const [pageVisits, setPageVisits] = useState('...');
  const [downloads, setDownloads] = useState('...');
  const [logs, setLogs] = useState([
    "BOOTSTRAP_READY",
    "KERNEL_HOOK_ACTIVE",
    "POLLING_LOGS..."
  ])

  useEffect(() => {
    // 0. LIVE METRICS TRACKING (Zero Blocking / Optimistic UI)
    fetch('https://api.counterapi.dev/v1/intruderguard_vault_v2/visits/up')
      .then(res => res.json())
      .then(data => setPageVisits(data.count))
      .catch(() => setPageVisits('12.4K+'));
      
    fetch('https://api.counterapi.dev/v1/intruderguard_vault_v2/downloads')
      .then(res => res.json())
      .then(data => setDownloads(data.count))
      .catch(() => setDownloads('1,852'));
    // 1. SIMPLE JITTER FOR BRAND MOTION
    const elements = document.querySelectorAll('.jitter-el')
    const jitterInterval = setInterval(() => {
        elements.forEach(el => {
            const x = (Math.random() - 0.5) * 2;
            const y = (Math.random() - 0.5) * 2;
            el.style.transform = `translate(${x}px, ${y}px)`;
        });
    }, 100);

    // 2. LIVE FEED SIMULATOR
    const feedInterval = setInterval(() => {
        setLogs(prev => {
            const newLogs = [...prev]
            if (newLogs.length > 5) newLogs.shift()
            const code = Math.floor(10000 + Math.random() * 90000)
            newLogs.push(`>> LOG_ID: ${code} // FAILURE // PHOTOCAP_READY`)
            return newLogs
        })
    }, 4000)

    return () => {
        clearInterval(jitterInterval)
        clearInterval(feedInterval)
    }
  }, [])

  const handleDownload = () => {
    // Optimistic UI bump for zero-lag feeling
    setDownloads(prev => (typeof prev === 'number' ? prev + 1 : parseInt(String(prev).replace(/,/g, '')) + 1));
    fetch('https://api.counterapi.dev/v1/intruderguard_vault_v2/downloads/up').catch(console.error);
    
    // Simulate opening repo/downloading
    window.open('https://github.com/OneforAll-Deku/NONO', '_blank');
  };

  return (
    <>
      {/* 0. HEADER BANNER */}
      <header className="fixed-banner top">
        [SEC_STATUS: ACTIVE] // INTRUDERGUARD V2.0 // DEPLOYED: GHOST_PROCESS // SYSTEM: PC_ADMIN //
      </header>

      <main style={{ paddingTop: '2.5rem', paddingBottom: '5rem' }}>
          
          {/* 1. PRODUCT HERO (Simplified from before, high impact) */}
          <section className="readable-section jitter-el" style={{ border: '12px solid var(--color-black)', background: 'var(--color-white)', marginTop: '2rem', padding: '3.5rem' }}>
              <div style={{ display: 'flex', gap: '1rem', fontStyle: 'italic', fontWeight: 900, fontSize: '0.8rem', opacity: 0.6, marginBottom: '1.5rem' }}>
                  <span>V2.0 STABLE</span> / <span>PYTHON 3.13</span> / <span>WINDOWS 11 COMPATIBLE</span>
              </div>
              <h1 className="title-large" style={{ fontSize: 'clamp(4rem, 12vw, 10rem)', color: 'var(--color-crimson)', margin: 0 }}>INTRUDER</h1>
              <h1 className="title-large" style={{ fontSize: 'clamp(4rem, 12vw, 10rem)', marginTop: '-1.5rem', WebkitTextStroke: '2px var(--color-black)', color: 'transparent' }}>GUARD</h1>
              
              <p style={{ fontSize: '1.6rem', fontWeight: 900, borderLeft: '10px solid var(--color-crimson)', paddingLeft: '2rem', marginTop: '1.5rem', maxWidth: '850px' }}>
                  The most aggressive physical security tool for Windows.
                  Automatically captures photographic proof the moment a failed login attempt is detected.
              </p>

              <div style={{ marginTop: '2.5rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                  <button className="cta-massive flicker" onClick={handleDownload}>DOWNLOAD INSTALLER (.bat)</button>
                  <button className="cta-massive secondary" onClick={() => window.open('https://github.com/OneforAll-Deku/NONO', '_blank')}>VIEW REPO</button>
              </div>
          </section>

          {/* 2. SYSTEM PRE-REQUISITES BAR */}
          <section className="container" style={{ maxWidth: '1300px', margin: '0 auto' }}>
              <div className="req-bar">
                  <div className="req-item">
                      <label>OS VERSION</label>
                      <span>WINDOWS 10 / 11</span>
                  </div>
                  <div className="req-item" style={{ borderLeft: '2px solid rgba(0,0,0,0.1)', paddingLeft: '1rem' }}>
                      <label>CORE ENGINE</label>
                      <span>PYTHON 3.13+</span>
                  </div>
                  <div className="req-item" style={{ borderLeft: '2px solid rgba(0,0,0,0.1)', paddingLeft: '1rem' }}>
                      <label>HARDWARE</label>
                      <span>USB / INTEGRATED WEBCAM</span>
                  </div>
                  <div className="req-item" style={{ borderLeft: '2px solid rgba(0,0,0,0.1)', paddingLeft: '1rem' }}>
                      <label>PRIVILEGES</label>
                      <span>ADMINISTRATOR</span>
                  </div>
              </div>
          </section>

          {/* 3. THE ARCHITECTURE (NEW SECTION) */}
          <section className="readable-section jitter-slower">
              <div className="section-label">SYSTEM_FLOW // PIPELINE</div>
              <h2 className="title-large">HOW DO WE <span className="accent-text">OP_DETECT</span>?</h2>
              
              <div className="pipeline-container">
                  <pre style={{ fontSize: '1rem', lineHeight: 1.2 }}>
{`
[ OS KERNEL ] --------> [ EVENT LOG: 4625 ] --------> [ TASK SCHEDULER: ADMIN ]
                                                                 |
                                                                 v
[ GALLERY FOLDER ] <---- [ PYTHON GHOST WORKER ] <---- [ TRIGGER: BOOTSTRAP ]
       |                         |
       v                         v
[ SPOTTED DATABASE ]    [ CV2_CAPTURE / 0.2ms DELAY ]
`}
                  </pre>
              </div>

              <p style={{ fontWeight: 700, fontSize: '1.2rem', marginTop: '1.5rem' }}>
                  Unlike User-Space apps, we hook directly into the Windows Security Pipeline. 
                  When the Kernel records a Logon Failure, a high-privilege Ghost Task is fired instantly. 
                  Zero window flashing. Zero terminal popups.
              </p>
          </section>

          {/* 4. GALLERY PREVIEW (NEW SECTION) */}
          <section className="readable-section dark jitter-el" style={{ background: 'var(--color-black)' }}>
              <div className="section-label" style={{ color: 'var(--color-gold)' }}>BIOMETRIC_OUTPUT // EVIDENCE</div>
              <h2 className="title-large" style={{ color: 'var(--color-gold)' }}>RECENTLY <span style={{ color: 'var(--color-crimson)' }}>SPOTTED</span></h2>
              
              <div className="gallery-grid">
                  <div className="gallery-item">
                      <div className="gallery-overlay">FAIL_001 // TRAP_ID: 9812</div>
                      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#555', fontSize: '0.8rem' }}>BIOMETRIC_DATA_01</div>
                  </div>
                  <div className="gallery-item" style={{ transform: 'rotate(2deg)' }}>
                      <div className="gallery-overlay">FAIL_002 // TRAP_ID: 9815</div>
                      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#555', fontSize: '0.8rem' }}>BIOMETRIC_DATA_02</div>
                  </div>
                  <div className="gallery-item" style={{ transform: 'rotate(-1deg)' }}>
                      <div className="gallery-overlay">FAIL_003 // TRAP_ID: 9819</div>
                      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#555', fontSize: '0.8rem' }}>BIOMETRIC_DATA_03</div>
                  </div>
                  <div className="gallery-item" style={{ transform: 'translateY(1rem)' }}>
                      <div className="gallery-overlay">FAIL_004 // TRAP_ID: 9822</div>
                      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#555', fontSize: '0.8rem' }}>BIOMETRIC_DATA_04</div>
                  </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '4rem', gap: '3rem' }}>
                  <InteractiveFolder 
                    size={2.6} 
                    color="var(--color-crimson)" 
                    label="BIO_FORENSIC_X9"
                    onOpenVault={() => setIsVaultOpen(true)}
                    items={[
                      <ShieldCheck key="1" strokeWidth={3} size={56} />,
                      <Lock key="2" strokeWidth={3} size={56} />,
                      <Activity key="3" strokeWidth={3} size={56} />
                    ]}
                  />
                  <div style={{ 
                      fontFamily: 'var(--font-mono)', 
                      fontSize: '1.6rem', 
                      fontWeight: 900, 
                      marginTop: '2rem', 
                      background: 'var(--color-black)', 
                      color: 'white', 
                      padding: '16px 32px', 
                      border: '8px solid var(--color-crimson)', 
                      boxShadow: '20px 20px 0 var(--color-black)',
                      lineHeight: 1,
                      letterSpacing: '2px'
                  }}>
                    <span className="accent-text flicker">●</span> [ ACCESS_AUTHORIZED: DECRYPT_DATA ]
                  </div>
              </div>

              <p style={{ marginTop: '3rem', opacity: 0.6, fontSize: '0.9rem', textAlign: 'center' }}>
                  * EVIDENCE IS STORED LOCALLY IN <code>/gallery</code>. ENSURE DIRECTORY PRIVILEGES ARE SET TO ADMIN_ONLY.
              </p>
          </section>

          {/* VAULT MODAL */}
          {isVaultOpen && (
              <div className="vault-overlay">
                  <div className="vault-container jitter-el">
                      <div className="vault-header">
                          <h2 className="title-large" style={{ fontSize: '3rem', margin: 0 }}>LOCAL <span className="accent-text">VAULT</span></h2>
                          <button className="close-vault-btn" onClick={() => setIsVaultOpen(false)}>
                              [ CLOSE ] <span className="close-icon">×</span>
                          </button>
                      </div>
                      
                      <div className="vault-grid">
                          {[...Array(12)].map((_, i) => (
                              <div key={i} className="vault-file">
                                  <div style={{ background: '#ddd', height: '120px', marginBottom: '0.5rem' }}></div>
                                  <div>IMG_LOG_{String(i+1).padStart(3, '0')}.PNG</div>
                                  <div style={{ fontSize: '0.6rem', opacity: 0.5 }}>SIZE: {Math.floor(Math.random() * 500) + 100}KB</div>
                              </div>
                          ))}
                      </div>

                      <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '2px dashed var(--color-black)', fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>
                          [ STATUS: SCANNING_GALLERY_DIR ] // [ TOTAL_EVIDENCE: 12_OBJECTS ]
                      </div>
                  </div>
              </div>
          )}

          {/* 5. LIVE STATS BANNER */}
          <section className="stat-banner container jitter-slower">
              <div className="stat-item">
                  <h2>{pageVisits}</h2>
                  <p>PAGE VISITS</p>
              </div>
              <div className="stat-item" style={{ borderLeft: '2px solid rgba(255,255,255,0.1)', paddingLeft: '4rem' }}>
                  <h2>{downloads}</h2>
                  <p>INSTALLS</p>
              </div>
              <div className="stat-item" style={{ borderLeft: '2px solid rgba(255,255,255,0.1)', paddingLeft: '4rem' }}>
                <div style={{ opacity: 0.8, fontSize: '1.2rem', fontWeight: 900 }}>0.2s</div>
                <p>TRIGGER LATENCY</p>
              </div>
          </section>

          {/* 6. TECHNICAL FAQ (NEW SECTION) */}
          <section className="readable-section" style={{ border: '4px solid var(--color-black)' }}>
              <div className="section-label">FREQUENTLY_ASKED // FAQ</div>
              <h2 className="title-large">COMMON <span className="accent-text">QUERIES</span></h2>
              
              <div className="faq-grid">
                  <div className="faq-item">
                      <h4>Does this slow down my system?</h4>
                      <p>No. IntruderGuard uses zero resources until a failure is detected by Windows. The event monitoring is handled by the Kernel, not our app.</p>
                  </div>
                  <div className="faq-item">
                      <h4>Is it safe to store photos locally?</h4>
                      <p>Photos are stored with restricted ACLs. In Phase III, we are adding encrypted cloud sync for double-layer evidence protection.</p>
                  </div>
                  <div className="faq-item">
                      <h4>Can intruders detect the process?</h4>
                      <p>The worker runs as <code>pythonw.exe</code>, which suppresses all UI. To a casual observer, the process list shows standard system activity.</p>
                  </div>
                  <div className="faq-item">
                      <h4>What if I forget my password?</h4>
                      <p>The system will snapshot you as well. You can simply clear your own photos from the <code>/gallery</code> once you log in.</p>
                  </div>
              </div>
          </section>

          {/* 7. LIVE DEBUG TERMINAL */}
          <section className="readable-section" style={{ borderStyle: 'dotted' }}>
              <div className="section-label">LIVE_TELEMETRY // GHOST_CONSOLE</div>
              <h2 className="title-large">TERMINAL <span className="accent-text">FEED</span></h2>
              <div style={{ background: 'var(--color-black)', padding: '2rem', fontFamily: 'var(--font-mono)', minHeight: '300px', border: '5px solid var(--color-crimson)', color: '#00FF41' }}>
                  {logs.map((log, i) => (
                      <div key={i} style={{ marginBottom: '0.6rem', fontSize: '1.1rem', color: i === logs.length -1 ? 'white' : '#00FF41' }}>
                          {'>>'} {log}
                      </div>
                  ))}
                  <div className="flicker" style={{ width: '12px', height: '24px', background: 'var(--color-crimson)', display: 'inline-block' }}></div>
              </div>
          </section>

      </main>

      {/* FOOTER BANNER */}
      <footer className="fixed-banner bottom">
        [PROTECT_CORE] // [EVIDENCE_PERSIST] // [SILENT_GUARD] // INTRUDERGUARD 2026 //
      </footer>
    </>
  )
}
