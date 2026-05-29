import { useState } from "react";

const sections = [
  {
    id: "overview",
    label: "Overview",
    icon: "◈",
  },
  {
    id: "architecture",
    label: "Architecture",
    icon: "⬡",
  },
  {
    id: "features",
    label: "Core Features",
    icon: "◎",
  },
  {
    id: "platforms",
    label: "Platforms",
    icon: "⬢",
  },
  {
    id: "roadmap",
    label: "Roadmap",
    icon: "→",
  },
];

const features = [
  {
    id: 1,
    category: "COMPLIANCE ENGINE",
    color: "#C8102E",
    title: "Grammarly for Staff Duties",
    subtitle: "Live JSSDM Compliance Checker",
    description:
      "Real-time writing analysis that flags every JSSDM violation as the officer types. Built from parsing the full JSSDM 2022 ruleset.",
    items: [
      {
        name: "Visual Error Highlighting",
        detail:
          "Red underlines for violations (e.g. '26th May' → '26 May 26'), yellow for abbreviation suggestions. Hover to see the JSSDM rule reference.",
      },
      {
        name: "Format Enforcement",
        detail:
          "Detects incorrect date formats, wrong paragraph numbering hierarchy (1. → a. → (1) → (a)), missing security classification headers.",
      },
      {
        name: "Tone & Register Checks",
        detail:
          "Flags informal language, incorrect rank capitalization (e.g. 'lieutenant colonel' must be 'Lieutenant Colonel'), and passive voice violations.",
      },
      {
        name: "JSSDM Rule Citations",
        detail:
          "Every flag links back to the exact JSSDM section — e.g. 'See Section 2, Para 2-6: Date format'. Officers learn as they write.",
      },
    ],
  },
  {
    id: 2,
    category: "SMART EDITOR",
    color: "#00563F",
    title: "Auto-Formatter Engine",
    subtitle: "Live Abbreviation & Structure System",
    items: [
      {
        name: "Live Abbreviation Swapping",
        detail:
          "Toggle ON: typing 'Reference' + spacebar auto-snaps to 'Ref', 'Commanding Officer' → 'CO', 'Operation Order' → 'Op O'. Sourced from JSSDM Chapter VI full abbreviation list.",
      },
      {
        name: "Smart Paragraph Numbering",
        detail:
          "Press Tab to go deeper in the military hierarchy: 1. → a. → (1) → (a) → i → (i). Press Shift+Tab to go up. No manual formatting needed.",
      },
      {
        name: "Margin & Indentation Engine",
        detail:
          "Automatically applies JSSDM-compliant left margins, spacing after headings, and annex indentation rules as defined in Section 2, Annex B.",
      },
      {
        name: "Security Classification Stamper",
        detail:
          "One-click to add RESTRICTED / SECRET / UNCLASSIFIED banners at the top and bottom of every page in the correct position per JSSDM rules.",
      },
    ],
    color2: "#00563F",
  },
  {
    id: 3,
    category: "TEMPLATE LIBRARY",
    color: "#1B3A6B",
    title: "Dynamic Document Templates",
    subtitle: "All 20+ JSSDM Document Types",
    items: [
      {
        name: "Full Template Coverage",
        detail:
          "Commanded Letter, Directed Letter, Routine Letter, Formal Letter, Demi-Official Letter, Memorandum, Loose Minute, Note Sheet, Service Paper, Brief (Info/Decision), Agenda, Minutes of Meeting, Op Order (Army/Navy/Air Force), Admin Order, Warning Order, Signal Message.",
      },
      {
        name: "Pre-Flight Checklist",
        detail:
          "Before exporting, a mandatory checklist appears: ✓ Security classification set? ✓ Distribution list added? ✓ All enclosures numbered? ✓ Signature block complete? Cannot export until all items are checked.",
      },
      {
        name: "Smart Field Detection",
        detail:
          "Templates have intelligent fields. Selecting 'Brigade Op Order' auto-populates the 5-paragraph SMEAC structure. Selecting 'Formal Letter' locks the complimentary ending based on rank relationship selected.",
      },
      {
        name: "Bangla / English Toggle",
        detail:
          "Full support for Bangla-language service writing (Part I of JSSDM 2022) including Bangla abbreviations (e.g. সেকস → সেনা কল্যাণ সংস্থা) and Unicode font handling.",
      },
    ],
  },
  {
    id: 4,
    category: "REFERENCE SYSTEM",
    color: "#7B4B2A",
    title: "Abbreviation Lookup & Symbols",
    subtitle: "Complete JSSDM Annex 16-19 Database",
    items: [
      {
        name: "Instant Search Database",
        detail:
          "Full searchable index of all abbreviations: General (16A), Multiple-meaning (16B), Ranks & Appointments (16C), National Distinguishing Letters (16D), Training Institutions (16E), Army Regiments (16F), Navy Units (16G), Air Force Units (16H).",
      },
      {
        name: "Symbol Reference (Army/Navy/Air Force)",
        detail:
          "Interactive symbol browser for all Army tactical symbols (Chapters 17), Naval chart symbols (Chapter 18), and Air Force operational symbols (Chapter 19). Tap to copy SVG symbol.",
      },
      {
        name: "Disambiguation Tool",
        detail:
          "Abbreviations with multiple meanings (Chapter 16B) show context selector — e.g. 'CO' means 'Commanding Officer' in Army context but 'Commanding Officer / Conscientious Objector' in joint context.",
      },
      {
        name: "Offline-First",
        detail:
          "Full database works offline. No internet required after first install. Critical for field use.",
      },
    ],
  },
  {
    id: 5,
    category: "STAFF PAPER AI",
    color: "#5C2D91",
    title: "Military Appreciation Assistant",
    subtitle: "Guided Decision-Making Tool (JSSDM Ch. 9)",
    items: [
      {
        name: "Step-by-Step Guided Appreciation",
        detail:
          "Walks the officer through all 12 stages: Situation Review → Mission Analysis → Factors → Ground → Enemy Courses → Enemy's Most Probable Course → Own Courses → Selection of Best Course → Plan.",
      },
      {
        name: "IPB-DMP Integration",
        detail:
          "Includes the Intelligence Preparation of the Battlefield – Decision Making Process (IPB-DMP) framework as a guided sub-module (JSSDM Annex 9B).",
      },
      {
        name: "Brief Generator",
        detail:
          "Auto-generates Information Brief (Annex 5A) and Decision Brief (Annex 5B) frameworks from completed Appreciations. Includes PowerPoint presentation guidelines (Annex 5C).",
      },
    ],
  },
];

const platforms = [
  {
    name: "Flutter Mobile & Desktop",
    icon: "📱",
    description:
      "Single codebase for Android, iOS, Windows, macOS, Linux. Officers use it on phones in the field, desktop at HQ. Offline-first with local SQLite database.",
    tech: ["Flutter 3.x", "Dart", "SQLite (drift)", "Riverpod state mgmt", "flutter_quill editor"],
    priority: "PRIMARY",
    color: "#0175C2",
  },
  {
    name: "Google Chrome Extension",
    icon: "🌐",
    description:
      "Sidebar assistant that activates on any webpage or Google Docs. Paste or type staff writing directly — the compliance checker runs live. Drag-in templates. Works on JFB intranet portals.",
    tech: ["Manifest V3", "Vanilla JS / TypeScript", "Chrome Side Panel API", "Content Scripts"],
    priority: "HIGH",
    color: "#4285F4",
  },
  {
    name: "Microsoft Word Add-in",
    icon: "📄",
    description:
      "The most critical extension. Adds a JSSDM panel to Word's ribbon. Live compliance highlighting inside the Word document. One-click template insertion. Pre-flight checklist before Save/Print.",
    tech: ["Office.js (Office Add-ins API)", "React task pane", "Word JavaScript API", "Node.js backend"],
    priority: "HIGH",
    color: "#2B579A",
  },
  {
    name: "Flutter Web App",
    icon: "💻",
    description:
      "Deployable on armed forces intranet. Same Flutter codebase compiled to web. No installation required for HQ users. Progressive Web App (PWA) for offline capability.",
    tech: ["Flutter Web", "PWA", "Firebase Auth", "Cloud Firestore (optional sync)"],
    priority: "MEDIUM",
    color: "#00897B",
  },
];

const roadmapPhases = [
  {
    phase: "Phase 1",
    duration: "Months 1–3",
    title: "Foundation",
    color: "#C8102E",
    deliverables: [
      "Parse full JSSDM 2022 into structured JSON database (all rules, abbreviations, templates)",
      "Flutter mobile app — core editor with paragraph numbering engine",
      "Abbreviation lookup & symbol browser (Chapters 16–19)",
      "All 20+ document templates with Pre-Flight Checklist",
      "Bangla + English dual language support",
    ],
  },
  {
    phase: "Phase 2",
    duration: "Months 4–6",
    title: "Intelligence Layer",
    color: "#1B3A6B",
    deliverables: [
      "Live compliance checker with rule-referenced error highlights",
      "Auto-abbreviation swapping engine (toggle ON/OFF)",
      "Security classification stamper",
      "Military Appreciation guided module (JSSDM Ch. 9 + IPB-DMP)",
      "Flutter desktop app (Windows / macOS)",
    ],
  },
  {
    phase: "Phase 3",
    duration: "Months 7–9",
    title: "Ecosystem Expansion",
    color: "#00563F",
    deliverables: [
      "Google Chrome Extension (side panel with live checker)",
      "Microsoft Word Add-in (ribbon integration + live highlights in Word)",
      "Flutter Web / PWA for intranet deployment",
      "Export to JSSDM-compliant .docx format",
      "Signal message composer (Chapter 15)",
    ],
  },
  {
    phase: "Phase 4",
    duration: "Months 10–12",
    title: "Advanced Features",
    color: "#5C2D91",
    deliverables: [
      "AI-powered brief generator from Appreciation input",
      "Collaborative document editing with role-based access",
      "Amendment tracking (Amendment Record Sheet automation)",
      "Admin dashboard for unit commanders",
      "Bangla full Part I coverage expansion",
    ],
  },
];

export default function JSSDMPlan() {
  const [activeSection, setActiveSection] = useState("overview");
  const [expandedFeature, setExpandedFeature] = useState(null);

  return (
    <div style={{
      fontFamily: "'Georgia', 'Times New Roman', serif",
      background: "#0A0F1E",
      minHeight: "100vh",
      color: "#E8E0D0",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Background texture */}
      <div style={{
        position: "fixed",
        inset: 0,
        backgroundImage: `
          repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(200,16,46,0.03) 40px, rgba(200,16,46,0.03) 41px),
          repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(200,16,46,0.03) 40px, rgba(200,16,46,0.03) 41px)
        `,
        pointerEvents: "none",
        zIndex: 0,
      }} />

      {/* Header */}
      <header style={{
        position: "relative",
        zIndex: 10,
        borderBottom: "1px solid rgba(200,16,46,0.3)",
        padding: "0 32px",
        background: "rgba(10,15,30,0.95)",
        backdropFilter: "blur(10px)",
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "20px 0 12px" }}>
            <div style={{
              width: 48, height: 48,
              background: "linear-gradient(135deg, #C8102E, #8B0015)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 22, fontWeight: "bold", color: "white",
              clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
            }}>★</div>
            <div>
              <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 2 }}>
                BANGLADESH ARMED FORCES — JSP-001
              </div>
              <h1 style={{ margin: 0, fontSize: 22, fontWeight: "bold", letterSpacing: 1, color: "#F0E8D8" }}>
                JSSDM Staff Suite
              </h1>
            </div>
            <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
              {["RESTRICTED", "DRAFT", "2025"].map(tag => (
                <span key={tag} style={{
                  fontSize: 10, letterSpacing: 2, padding: "3px 8px",
                  border: "1px solid rgba(200,16,46,0.4)",
                  color: "#C8102E", fontFamily: "'Courier New', monospace",
                }}>{tag}</span>
              ))}
            </div>
          </div>

          {/* Nav */}
          <nav style={{ display: "flex", gap: 0 }}>
            {sections.map(s => (
              <button key={s.id} onClick={() => setActiveSection(s.id)} style={{
                background: "none", border: "none",
                borderBottom: activeSection === s.id ? "2px solid #C8102E" : "2px solid transparent",
                color: activeSection === s.id ? "#F0E8D8" : "rgba(232,224,208,0.4)",
                padding: "10px 20px",
                cursor: "pointer",
                fontSize: 12, letterSpacing: 2,
                fontFamily: "'Courier New', monospace",
                textTransform: "uppercase",
                transition: "all 0.2s",
              }}>
                <span style={{ marginRight: 6 }}>{s.icon}</span>{s.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main style={{ position: "relative", zIndex: 5, maxWidth: 1200, margin: "0 auto", padding: "40px 32px" }}>

        {/* OVERVIEW */}
        {activeSection === "overview" && (
          <div>
            <div style={{ marginBottom: 48 }}>
              <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 12 }}>
                PRODUCT CONCEPT / EXECUTIVE SUMMARY
              </div>
              <h2 style={{ fontSize: 36, margin: "0 0 16px", fontWeight: "normal", lineHeight: 1.2 }}>
                One Unified App for<br />
                <em style={{ color: "#C8102E" }}>All Staff Duties</em>
              </h2>
              <p style={{ fontSize: 16, lineHeight: 1.8, color: "rgba(232,224,208,0.7)", maxWidth: 680, margin: 0 }}>
                A cross-platform suite built directly on the JSSDM 2022 (JSP-001) — the official
                Bangladesh Armed Forces service writing manual. Every rule, template, abbreviation,
                and format standard from the manual is encoded into an intelligent, real-time
                writing assistant available on mobile, desktop, browser, and Microsoft Word.
              </p>
            </div>

            {/* Core pillars */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 48 }}>
              {[
                { icon: "◈", title: "Write Correctly", desc: "Live compliance checker flags every JSSDM violation in real-time — dates, abbreviations, paragraph numbering, classification headers.", color: "#C8102E" },
                { icon: "⬡", title: "Write Faster", desc: "Auto-formatting, live abbreviation swapping, and 20+ pre-built templates eliminate repetitive formatting work for junior staff officers.", color: "#1B3A6B" },
                { icon: "◎", title: "Write Anywhere", desc: "Flutter mobile & desktop, Chrome extension, and Word Add-in. One account, one database, all devices — online or offline.", color: "#00563F" },
              ].map(p => (
                <div key={p.title} style={{
                  background: "rgba(255,255,255,0.03)",
                  border: `1px solid rgba(255,255,255,0.08)`,
                  borderTop: `3px solid ${p.color}`,
                  padding: 28,
                }}>
                  <div style={{ fontSize: 28, color: p.color, marginBottom: 12 }}>{p.icon}</div>
                  <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>{p.title}</h3>
                  <p style={{ margin: 0, fontSize: 14, lineHeight: 1.7, color: "rgba(232,224,208,0.6)" }}>{p.desc}</p>
                </div>
              ))}
            </div>

            {/* What's in JSSDM */}
            <div style={{
              background: "rgba(200,16,46,0.06)",
              border: "1px solid rgba(200,16,46,0.2)",
              padding: 32,
              marginBottom: 48,
            }}>
              <div style={{ fontSize: 11, letterSpacing: 3, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 20 }}>
                SOURCE DOCUMENT — JSSDM 2022 (JSP-001) ANALYSIS
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
                {[
                  { ch: "I", title: "General Rules", items: ["Superscription", "Security Classifications (4 levels)", "Precedence system", "Paragraph numbering", "Signature & subscription rules", "Date & reference formats"] },
                  { ch: "II", title: "Correspondence", items: ["Commanded Letters", "Directed Letters", "Routine Letters", "Formal & Demi-Official Letters", "Memoranda", "Loose Minute / Note Sheet"] },
                  { ch: "III", title: "Staff Papers", items: ["Service Papers", "Information & Decision Briefs", "PowerPoint Brief Guidelines", "Agenda & Minutes", "Précis & Summaries", "Military Appreciations (12-step)"] },
                  { ch: "IV", title: "Operational Writing", items: ["Op Orders (Army/Navy/AF)", "Admin Orders", "Directives & Instructions", "Warning Orders", "Confirmatory Notes", "Fragmentary Orders"] },
                  { ch: "V", title: "Signal Communication", items: ["Message writing rules", "Precedence levels (FLASH→ROUTINE)", "Crypto message handling", "Signal message format", "Security classification in signals"] },
                  { ch: "VI", title: "Abbreviations & Symbols", items: ["600+ general abbreviations", "Multiple-meaning list", "All ranks & appointments", "Army tactical symbols", "Naval chart symbols", "Air Force operational symbols"] },
                ].map(ch => (
                  <div key={ch.ch}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                      <span style={{
                        width: 28, height: 28, background: "rgba(200,16,46,0.3)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 12, fontFamily: "'Courier New', monospace", color: "#C8102E",
                      }}>Ch.{ch.ch}</span>
                      <span style={{ fontSize: 14, fontWeight: "bold" }}>{ch.title}</span>
                    </div>
                    <ul style={{ margin: 0, padding: "0 0 0 16px", listStyle: "none" }}>
                      {ch.items.map(i => (
                        <li key={i} style={{
                          fontSize: 12, color: "rgba(232,224,208,0.55)", lineHeight: 2,
                          borderLeft: "2px solid rgba(200,16,46,0.2)", paddingLeft: 8, marginBottom: 2,
                        }}>→ {i}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ARCHITECTURE */}
        {activeSection === "architecture" && (
          <div>
            <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 24 }}>
              TECHNICAL ARCHITECTURE
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>
              {/* Flutter Core */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(1,117,194,0.3)", padding: 28, borderTop: "3px solid #0175C2" }}>
                <div style={{ fontSize: 11, letterSpacing: 3, color: "#0175C2", fontFamily: "'Courier New', monospace", marginBottom: 12 }}>
                  CORE PLATFORM
                </div>
                <h3 style={{ margin: "0 0 16px", fontSize: 20 }}>Flutter (Dart)</h3>
                <p style={{ fontSize: 13, lineHeight: 1.7, color: "rgba(232,224,208,0.6)", marginBottom: 16 }}>
                  Single codebase targeting Android, iOS, Windows, macOS, Linux, and Web. Chosen for
                  its native performance on all platforms and strong offline support.
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {[
                    ["State Management", "Riverpod"],
                    ["Local DB", "SQLite / drift"],
                    ["Editor", "flutter_quill"],
                    ["PDF Export", "pdf package"],
                    ["Word Export", "docx_template"],
                    ["Sync (optional)", "Firebase / Supabase"],
                  ].map(([k, v]) => (
                    <div key={k} style={{ fontSize: 11, borderLeft: "2px solid #0175C2", paddingLeft: 8 }}>
                      <div style={{ color: "rgba(232,224,208,0.4)", marginBottom: 2 }}>{k}</div>
                      <div style={{ color: "#E8E0D0", fontFamily: "'Courier New', monospace" }}>{v}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* JSSDM Database */}
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(200,16,46,0.3)", padding: 28, borderTop: "3px solid #C8102E" }}>
                <div style={{ fontSize: 11, letterSpacing: 3, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 12 }}>
                  KNOWLEDGE BASE
                </div>
                <h3 style={{ margin: "0 0 16px", fontSize: 20 }}>JSSDM Rules Engine</h3>
                <p style={{ fontSize: 13, lineHeight: 1.7, color: "rgba(232,224,208,0.6)", marginBottom: 16 }}>
                  The entire JSSDM 2022 is parsed into a structured JSON/SQLite database. All rules,
                  abbreviations, templates, and symbols are versioned and updatable via patch files.
                </p>
                <div style={{ fontFamily: "'Courier New', monospace", fontSize: 11, background: "rgba(0,0,0,0.3)", padding: 16, color: "#90EE90", lineHeight: 1.8 }}>
                  <div style={{ color: "rgba(144,238,144,0.5)" }}>// Database schema (simplified)</div>
                  <div>rules: [id, chapter, ref, text, severity]</div>
                  <div>abbreviations: [abbr, meaning, context, lang]</div>
                  <div>templates: [id, type, structure, fields]</div>
                  <div>symbols: [id, service, svg_path, name]</div>
                  <div>vocab: [english, bangla, category]</div>
                </div>
              </div>
            </div>

            {/* Extensions */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(66,133,244,0.3)", padding: 28, borderTop: "3px solid #4285F4" }}>
                <div style={{ fontSize: 11, letterSpacing: 3, color: "#4285F4", fontFamily: "'Courier New', monospace", marginBottom: 12 }}>
                  CHROME EXTENSION
                </div>
                <h3 style={{ margin: "0 0 12px", fontSize: 18 }}>Manifest V3 Architecture</h3>
                <div style={{ fontFamily: "'Courier New', monospace", fontSize: 11, background: "rgba(0,0,0,0.3)", padding: 16, color: "#87CEEB", lineHeight: 1.8 }}>
                  <div>background.js (Service Worker)</div>
                  <div>  └─ Rule engine (shared JSSDM DB)</div>
                  <div>content.js (injected in every page)</div>
                  <div>  └─ Text selection listener</div>
                  <div>  └─ Live compliance overlay</div>
                  <div>sidepanel.html (Chrome Side Panel API)</div>
                  <div>  └─ Full editor + template browser</div>
                  <div>  └─ Abbreviation lookup</div>
                </div>
              </div>

              <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(43,87,154,0.4)", padding: 28, borderTop: "3px solid #2B579A" }}>
                <div style={{ fontSize: 11, letterSpacing: 3, color: "#2B579A", fontFamily: "'Courier New', monospace", marginBottom: 12 }}>
                  WORD ADD-IN
                </div>
                <h3 style={{ margin: "0 0 12px", fontSize: 18 }}>Office.js Task Pane</h3>
                <div style={{ fontFamily: "'Courier New', monospace", fontSize: 11, background: "rgba(0,0,0,0.3)", padding: 16, color: "#87CEEB", lineHeight: 1.8 }}>
                  <div>manifest.xml (Add-in registration)</div>
                  <div>taskpane/ (React SPA)</div>
                  <div>  └─ JSSDM compliance panel</div>
                  <div>  └─ Template inserter</div>
                  <div>  └─ Pre-flight checklist</div>
                  <div>Word JS API hooks:</div>
                  <div>  └─ onContentChanged → live scan</div>
                  <div>  └─ insertContentControl → highlights</div>
                  <div>  └─ insertParagraph → auto-format</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FEATURES */}
        {activeSection === "features" && (
          <div>
            <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 24 }}>
              CORE FEATURE MODULES
            </div>
            {features.map(f => (
              <div key={f.id} style={{
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderLeft: `4px solid ${f.color}`,
                marginBottom: 16,
                overflow: "hidden",
              }}>
                <div
                  onClick={() => setExpandedFeature(expandedFeature === f.id ? null : f.id)}
                  style={{ padding: "20px 28px", cursor: "pointer", display: "flex", alignItems: "center", gap: 16 }}
                >
                  <div style={{
                    width: 36, height: 36, background: f.color, display: "flex",
                    alignItems: "center", justifyContent: "center", fontSize: 16, color: "white", flexShrink: 0,
                  }}>{f.id}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 10, letterSpacing: 3, color: f.color, fontFamily: "'Courier New', monospace", marginBottom: 4 }}>
                      MODULE {f.id.toString().padStart(2,"0")} — {f.category}
                    </div>
                    <div style={{ fontSize: 18, fontWeight: "bold" }}>{f.title}</div>
                    <div style={{ fontSize: 13, color: "rgba(232,224,208,0.5)", marginTop: 2 }}>{f.subtitle}</div>
                  </div>
                  <div style={{ color: f.color, fontSize: 18 }}>
                    {expandedFeature === f.id ? "▲" : "▼"}
                  </div>
                </div>
                {expandedFeature === f.id && (
                  <div style={{ padding: "0 28px 28px", borderTop: `1px solid rgba(255,255,255,0.05)` }}>
                    {f.description && (
                      <p style={{ fontSize: 14, lineHeight: 1.7, color: "rgba(232,224,208,0.6)", marginTop: 16, marginBottom: 24 }}>
                        {f.description}
                      </p>
                    )}
                    <div style={{ display: "grid", gridTemplateColumns: f.items.length > 3 ? "1fr 1fr" : "1fr", gap: 16 }}>
                      {f.items.map((item, idx) => (
                        <div key={idx} style={{
                          background: "rgba(255,255,255,0.03)",
                          border: `1px solid rgba(255,255,255,0.06)`,
                          borderLeft: `3px solid ${f.color}40`,
                          padding: 16,
                        }}>
                          <div style={{ fontSize: 13, fontWeight: "bold", color: "#F0E8D8", marginBottom: 8 }}>
                            {item.name}
                          </div>
                          <div style={{ fontSize: 12, lineHeight: 1.7, color: "rgba(232,224,208,0.55)" }}>
                            {item.detail}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* PLATFORMS */}
        {activeSection === "platforms" && (
          <div>
            <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 24 }}>
              PLATFORM TARGETS
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              {platforms.map(p => (
                <div key={p.name} style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.07)",
                  borderTop: `3px solid ${p.color}`,
                  padding: 28,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                    <div style={{ fontSize: 28 }}>{p.icon}</div>
                    <span style={{
                      fontSize: 10, letterSpacing: 2,
                      padding: "3px 10px",
                      background: p.priority === "PRIMARY" ? p.color : "transparent",
                      border: `1px solid ${p.color}`,
                      color: p.priority === "PRIMARY" ? "white" : p.color,
                      fontFamily: "'Courier New', monospace",
                    }}>{p.priority}</span>
                  </div>
                  <h3 style={{ margin: "0 0 12px", fontSize: 20 }}>{p.name}</h3>
                  <p style={{ margin: "0 0 20px", fontSize: 13, lineHeight: 1.7, color: "rgba(232,224,208,0.6)" }}>
                    {p.description}
                  </p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {p.tech.map(t => (
                      <span key={t} style={{
                        fontSize: 11, padding: "3px 8px",
                        background: `${p.color}20`,
                        border: `1px solid ${p.color}40`,
                        color: "rgba(232,224,208,0.7)",
                        fontFamily: "'Courier New', monospace",
                      }}>{t}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Shared core note */}
            <div style={{
              marginTop: 28,
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              padding: 24,
              display: "flex", gap: 24, alignItems: "center",
            }}>
              <div style={{ fontSize: 32, color: "#C8102E" }}>◈</div>
              <div>
                <div style={{ fontSize: 14, fontWeight: "bold", marginBottom: 6 }}>Shared JSSDM Knowledge Core</div>
                <div style={{ fontSize: 13, color: "rgba(232,224,208,0.55)", lineHeight: 1.7 }}>
                  All four platforms share the same JSSDM rules database, abbreviation list, and template library.
                  Updates to the manual (e.g. a future JSSDM 2025 edition) require only one database patch —
                  all platforms automatically reflect the changes. The Flutter app uses SQLite locally;
                  extensions load a compressed JSON version of the same dataset.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ROADMAP */}
        {activeSection === "roadmap" && (
          <div>
            <div style={{ fontSize: 11, letterSpacing: 4, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 24 }}>
              DEVELOPMENT ROADMAP — 12 MONTHS
            </div>
            <div style={{ position: "relative" }}>
              {/* Timeline line */}
              <div style={{
                position: "absolute",
                left: 28, top: 0, bottom: 0,
                width: 2,
                background: "linear-gradient(to bottom, #C8102E, #5C2D91)",
                zIndex: 0,
              }} />

              {roadmapPhases.map((phase, idx) => (
                <div key={phase.phase} style={{ display: "flex", gap: 32, marginBottom: 40, position: "relative", zIndex: 1 }}>
                  {/* Timeline node */}
                  <div style={{ flexShrink: 0, width: 56, display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <div style={{
                      width: 56, height: 56,
                      background: phase.color,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 12, fontWeight: "bold", color: "white",
                      fontFamily: "'Courier New', monospace",
                      clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
                    }}>P{idx + 1}</div>
                  </div>

                  <div style={{
                    flex: 1,
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid rgba(255,255,255,0.07)",
                    borderLeft: `3px solid ${phase.color}`,
                    padding: "24px 28px",
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                      <div>
                        <div style={{ fontSize: 11, letterSpacing: 3, color: phase.color, fontFamily: "'Courier New', monospace", marginBottom: 4 }}>
                          {phase.phase} — {phase.duration}
                        </div>
                        <h3 style={{ margin: 0, fontSize: 22 }}>{phase.title}</h3>
                      </div>
                      <div style={{ fontSize: 10, color: "rgba(232,224,208,0.3)", fontFamily: "'Courier New', monospace" }}>
                        {phase.deliverables.length} DELIVERABLES
                      </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                      {phase.deliverables.map((d, di) => (
                        <div key={di} style={{
                          display: "flex", gap: 10, alignItems: "flex-start",
                          fontSize: 13, color: "rgba(232,224,208,0.65)", lineHeight: 1.5,
                        }}>
                          <span style={{ color: phase.color, flexShrink: 0, marginTop: 2 }}>→</span>
                          <span>{d}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom note */}
            <div style={{
              background: "rgba(200,16,46,0.07)",
              border: "1px solid rgba(200,16,46,0.2)",
              padding: 24,
              marginTop: 8,
            }}>
              <div style={{ fontSize: 11, letterSpacing: 3, color: "#C8102E", fontFamily: "'Courier New', monospace", marginBottom: 8 }}>
                NEXT STEP
              </div>
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.7, color: "rgba(232,224,208,0.65)" }}>
                Phase 1 begins with converting the JSSDM 2022 document into a structured rules database —
                this is the foundation that all features depend on. The Flutter mobile app with templates
                and abbreviation lookup can be delivered in Month 3 as the first testable product.
                Ready to begin building?
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
