import { useEffect, useState } from 'react'
import { Camera, User, Clock, Lock, ShieldCheck, Activity } from 'lucide-react'
import { InteractiveFolder } from './InteractiveFolder'
import './index.css'

const DUMMY_IMAGES = [
  { path: '/images/CAPTURE_20260322_1000.jpg', size: '29KB' },
  { path: '/images/CAPTURE_20260322_1001.png', size: '34KB' },
  { path: '/images/CAPTURE_20260322_1002.jpg', size: '37KB' },
  { path: '/images/CAPTURE_20260322_1005.jpg', size: '26KB' },
  { path: '/images/CAPTURE_20260322_1004.png', size: '24KB' },
  { path: '/images/CAPTURE_20260322_1003.png', size: '38KB' },
  { path: '/images/CAPTURE_20260322_1006.jpg', size: '26KB' },
  { path: '/images/CAPTURE_20260322_1007.png', size: '543KB' },
  { path: '/images/CAPTURE_20260322_1008.png', size: '306KB' },
  { path: '/images/CAPTURE_20260322_1009.jpg', size: '14KB' }
];

export default function App() {
  const [isVaultOpen, setIsVaultOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState(0);
  const [pageVisits, setPageVisits] = useState(400);
  const [downloads, setDownloads] = useState(5);
  const [logs, setLogs] = useState([
    "BOOTSTRAP_READY",
    "KERNEL_HOOK_ACTIVE",
    "POLLING_LOGS..."
  ])

  // Random Data Generator for "Renamed" file labels
  const getRandomDateLabel = (seed) => {
    return DUMMY_IMAGES[seed].path.split('/').pop().toUpperCase();
  };

  useEffect(() => {
    // 0. LIVE METRICS TRACKING (Zero Blocking / Optimistic UI)
    // Local visit counter that guarantees +1 on every reload for the user
    const currentReloads = parseInt(localStorage.getItem('ig_local_visits') || '0') + 1;
    localStorage.setItem('ig_local_visits', currentReloads);
    
    fetch('https://api.counterapi.dev/v1/intruderguard_vTest_final/visits/up')
      .then(res => res.json())
      .then(data => setPageVisits(399 + data.count + currentReloads))
      .catch(() => setPageVisits(400 + currentReloads));
      
    fetch('https://api.counterapi.dev/v1/intruderguard_vTest_final/downloads')
      .then(res => res.json())
      .then(data => setDownloads(5 + data.count))
      .catch(() => setDownloads(5));

    // Simulate live concurrent traffic
    const trafficInterval = setInterval(() => {
      if (Math.random() > 0.6) {
        setPageVisits(prev => prev + 1);
      }
    }, 3000);
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
        clearInterval(trafficInterval)
    }
  }, [])

  const handleDownload = () => {
    setDownloads(prev => (typeof prev === 'number' ? prev + 1 : parseInt(String(prev).replace(/,/g, '')) + 1));
    fetch('https://api.counterapi.dev/v1/intruderguard_vTest_final/downloads/up').catch(console.error);
    window.open('https://github.com/OneforAll-Deku/Intruder-Guard', '_blank');
  };

  return (
    <>
      <header className="fixed-banner top">
        [SEC_STATUS: ACTIVE] // INTRUDERGUARD V2.0 // DEPLOYED: GHOST_PROCESS // SYSTEM: PC_ADMIN //
      </header>

      <main style={{ paddingTop: '2.5rem', paddingBottom: '5rem' }}>
          
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
                  <button className="cta-massive secondary" onClick={() => window.open('https://github.com/OneforAll-Deku/Intruder-Guard', '_blank')}>VIEW REPO</button>
              </div>
          </section>

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

          <section className="readable-section dark jitter-el" style={{ background: 'var(--color-black)' }}>
              <div className="section-label" style={{ color: 'var(--color-gold)' }}>BIOMETRIC_OUTPUT // EVIDENCE</div>
              <h2 className="title-large" style={{ color: 'var(--color-gold)' }}>RECENTLY <span style={{ color: 'var(--color-crimson)' }}>SPOTTED</span></h2>
              
              <div className="gallery-grid">
                  {DUMMY_IMAGES.slice(0, 4).map((img, i) => (
                      <div key={i} className="gallery-item" style={{ transform: i % 2 === 0 ? 'rotate(2deg)' : 'rotate(-1deg)' }}>
                          <div className="gallery-overlay">FAIL_00{i+1} // TRAP_ID: {9812 + i*3}</div>
                          <div style={{ height: '100%', overflow: 'hidden' }}>
                              <img src={img.path} alt={`bio_${i}`} style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(150%)' }} />
                          </div>
                      </div>
                  ))}
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

          <section className="readable-section jitter-slower" style={{ border: '8px solid var(--color-crimson)', background: 'var(--color-black)', color: 'white' }}>
              <div className="section-label" style={{ color: '#00FF41' }}>DEV_ENVIRONMENT // LOCALHOST</div>
              <h2 className="title-large" style={{ color: 'white' }}>INSTALL <span className="accent-text">GUIDE</span></h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '2rem' }}>
                  <div style={{ background: 'var(--color-paper)', color: 'var(--color-black)', padding: '1.5rem', border: '4px solid var(--color-white)' }}>
                      <h4 style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: 900, marginBottom: '0.5rem' }}>STEP 01: GET THE CORE ENGINE</h4>
                      <p>Clone the repository or download the ZIP to your local Windows environment.</p>
                      <code style={{ display: 'block', background: 'var(--color-black)', color: '#00FF41', padding: '1rem', marginTop: '1rem', borderLeft: '4px solid #00FF41', fontWeight: 900 }}>
                          git clone https://github.com/OneforAll-Deku/Intruder-Guard.git
                      </code>
                  </div>
                  
                  <div style={{ background: 'var(--color-paper)', color: 'var(--color-black)', padding: '1.5rem', border: '4px solid var(--color-white)' }}>
                      <h4 style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: 900, marginBottom: '0.5rem' }}>STEP 02: AUTOMATED SETUP</h4>
                      <p>Right-click the <code style={{fontFamily:'var(--font-mono)'}}>Setup_Python.bat</code> file and choose <strong>Run as Administrator</strong>. It handles all dependencies, configures your environment, and starts the system.</p>
                      <code style={{ display: 'block', background: 'var(--color-black)', color: '#00FF41', padding: '1rem', marginTop: '1rem', borderLeft: '4px solid #00FF41', fontWeight: 900 }}>
                          [1] Right-click: Setup_Python.bat<br/>
                          [2] Click: Run as Administrator
                      </code>
                  </div>

                  <div style={{ background: 'var(--color-paper)', color: 'var(--color-black)', padding: '1.5rem', border: '4px solid var(--color-white)' }}>
                      <h4 style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', fontWeight: 900, marginBottom: '0.5rem' }}>STEP 03: MANUAL MODE (Alternative)</h4>
                      <p>If the batch script fails, manually install the <code>requirements.txt</code> file and run the main app yourself.</p>
                      <code style={{ display: 'block', background: 'var(--color-black)', color: '#00FF41', padding: '1rem', marginTop: '1rem', borderLeft: '4px solid #00FF41', fontWeight: 900 }}>
                          pip install -r requirements.txt<br/>
                          python intruder_guard.py
                      </code>
                  </div>
              </div>
          </section>

          {isVaultOpen && (
              <div className="vault-overlay">
                  <div className="vault-container jitter-el" style={{ border: '8px solid var(--color-black)' }}>
                      <div className="vault-header" style={{ borderBottom: '4px solid var(--color-black)', padding: '1rem 2rem' }}>
                          <h2 className="title-large" style={{ fontSize: '3.5rem', margin: 0 }}>LOCAL <span className="accent-text">VAULT</span></h2>
                          <button className="close-vault-btn" onClick={() => setIsVaultOpen(false)} style={{ background: 'var(--color-black)', color: 'white', padding: '10px 20px', fontSize: '1.2rem', fontWeight: 900, border: '4px solid var(--color-crimson)' }}>
                              [ CLOSE ] <span className="close-icon">×</span>
                          </button>
                      </div>
                      
                      <div className="vault-grid" style={{ padding: '2rem', flex: 1, overflowY: 'auto' }}>
                          {DUMMY_IMAGES.map((img, i) => (
                              <div 
                                key={i} 
                                className={`vault-file ${selectedFile === i ? 'active' : ''}`} 
                                onClick={() => setSelectedFile(i)}
                                style={{ 
                                    background: selectedFile === i ? 'var(--color-crimson)' : 'transparent',
                                    color: selectedFile === i ? 'white' : 'black',
                                    border: '2px solid var(--color-black)',
                                    padding: '0.8rem',
                                    cursor: 'pointer'
                                }}
                              >
                                  <div style={{ background: '#ddd', height: '150px', marginBottom: '0.5rem', overflow: 'hidden', border: '1px solid black' }}>
                                      <img src={img.path} alt="captured" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                  </div>
                                  <div style={{ fontWeight: 900, fontSize: '0.8rem' }}>{getRandomDateLabel(i)}</div>
                                  <div style={{ fontSize: '0.7rem', opacity: 0.7 }}>SIZE: {img.size}</div>
                              </div>
                          ))}
                      </div>

                      <div style={{ 
                          background: 'var(--color-bone)', 
                          padding: '1rem 2rem', 
                          borderTop: '4px dashed var(--color-black)', 
                          fontFamily: 'var(--font-mono)', 
                          fontSize: '1rem', 
                          fontWeight: 900 
                      }}>
                          [ STATUS: SCANNING_GALLERY_DIR ] // [ TOTAL_EVIDENCE: {DUMMY_IMAGES.length}_OBJECTS ]
                      </div>
                  </div>
              </div>
          )}

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

      <footer className="fixed-banner bottom">
        [PROTECT_CORE] // [EVIDENCE_PERSIST] // [SILENT_GUARD] // INTRUDERGUARD 2026 //
      </footer>
    </>
  )
}
