# ⚖️ NyayaAI (न्याय AI)
### AI-Powered Legal Information & Citizen Assistance System for Indian Law

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-128%2F128%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

NyayaAI is an open-source civic technology platform designed to make Indian statutory provisions, constitutional rights, and official redressal pathways more accessible and understandable for citizens.

---

## 📌 Problem Statement

1. **Access to Justice Barrier:** Over 1.4 billion citizens navigate one of the world's most extensive legal frameworks, but legal language remains dense and difficult for non-lawyers to interpret.
2. **Transition to New Criminal Codes:** On July 1, 2024, India implemented modern penal codes:
   - **Bharatiya Nyaya Sanhita (BNS, 2023)** succeeding the Indian Penal Code (IPC)
   - **Bharatiya Nagarik Suraksha Sanhita (BNSS, 2023)** succeeding the Code of Criminal Procedure (CrPC)
   - **Bharatiya Sakshya Adhiniyam (BSA, 2023)** succeeding the Indian Evidence Act (IEA)
   Citizens and researchers frequently need reliable cross-referencing between predecessor sections and successor provisions.
3. **Risks of Unconstrained LLM Generation:** Generic LLMs can invent non-existent section numbers, confuse repealed codes with active ones, or offer speculative legal guidance when not grounded in an explicit statutory corpus.
4. **Administrative Fragmentation:** Identifying the competent dispute forum (e.g., District Consumer Forum vs. State Commission, DLSA vs. Lok Adalat, RERA Bench vs. Appellate Tribunal) is geographically fragmented across districts.

---

## 💡 The NyayaAI Approach

NyayaAI operates on a **corpus-grounded, dual-mode architecture designed to mitigate unconstrained generation**:

- **📖 Information Mode:** Semantic and exact reference retrieval over 50 curated provisions across the Constitution of India, BNS, BNSS, and BSA. Statutory text is **retrieved directly from the project's legal corpus**; plain-language summaries are clearly separated and available in **English, Hindi, Telugu, and Marathi**.
- **⚡ Action Mode:** Deterministic, state-and-district authority routing across 106 official districts in Telangana, Andhra Pradesh, Maharashtra, and Delhi. Relies on structured relational data to identify the designated forum, required documents, statutory fees, filing methods, and escalation bodies.

---

## 🏛️ Core Design Principles

NyayaAI applies four architectural constraints for legal grounding:

1. **Corpus-Grounded Statutory Text:** All legal text (`exact_text`) returned by the retrieval pipeline is stored in the project's curated corpus sourced from official records (India Code, Legislative Department). Statutory provisions are retrieved, not generated dynamically by an LLM.
2. **Strict Separation of Law and Explanation:** The statutory text and the plain-language summary reside in separate data fields and distinct UI cards so users can easily distinguish between statutory wording and AI explanations.
3. **Predecessor Section Mapping:** Queries referencing legacy laws (e.g., "IPC Section 378" or "Section 420") are deterministically mapped to modern provisions (e.g., BNS Section 303 / Section 318) using a cross-reference registry.
4. **Deterministic Authority Routing:** Administrative jurisdictions, filing fees, and escalation hierarchies are resolved from structured relational database tables (`State` → `District` → `Category` → `Authority`), eliminating reliance on LLMs for jurisdictional routing.

---

## 🌟 Key Capabilities

### 1. 🔍 Information Mode (`POST /api/query`)
* **Semantic & Exact Hybrid Retrieval:** ChromaDB vector embeddings combined with exact statutory reference matching (e.g., "Article 21", "BNS Section 303", "BNSS Section 173").
* **Confidence & Relevance Scoring:** 0–100 relevance score calculated from vector cosine distance. Exact reference matches receive 100% score and "High Confidence" signals.
* **Multilingual Plain-Language Explanations:** Explanations available in English (`en`), Hindi (`hi`), Telugu (`te`), and Marathi (`mr`). Statutory text remains in authoritative English.
* **Landmark Case Law References:** Notable Supreme Court judgments (e.g., *Maneka Gandhi v. UOI*, *K.S. Puttaswamy v. UOI*, *D.K. Basu v. State of West Bengal*) linked to relevant provisions.
* **Legal Citation Export:** One-click clipboard copy and formatted `.txt` download for personal reference or documentation.
* **Unresolved Query Guidance:** If a query falls outside the curated corpus, NyayaAI provides search suggestions and official citizen redressal pathways (such as DLSA/NALSA legal aid helpline 15100).

### 2. ⚡ Action Mode (`GET /api/route`)
* **4 Supported Jurisdictions (106 Official Districts):**
  * **Telangana (TS)** — 33 districts
  * **Andhra Pradesh (AP)** — 26 districts
  * **Maharashtra (MH)** — 36 districts
  * **National Capital Territory of Delhi (DL)** — 11 districts
* **4 Core Grievance Categories:**
  * 🛒 **Consumer Disputes:** District Consumer Disputes Redressal Commission (DCDRC) → State Commission (SCDRC)
  * 🏢 **Real Estate & Housing:** Real Estate Regulatory Authority (RERA) → RERA Appellate Tribunal
  * ⚖️ **Free Legal Aid:** District Legal Services Authority (DLSA) / Taluk Committees → State Legal Services Authority (SLSA)
  * 🛡️ **Human Rights Violations:** State Human Rights Commission (SHRC) → National Human Rights Commission (NHRC)
* **4-Step Action Roadmap:** Step-by-step procedural roadmap, required documentation checklist, filing fees, and statutory escalation timelines.

---

## 🎨 UI/UX Design Decisions

The frontend is structured to present legal information with clarity, transparency, and accessible hierarchy:

1. **Clear Visual Distinction (AI Summary vs. Statutory Text):**
   - **Section 1 (AI Explanation):** Highlighted with an indigo accent border and an explicit advisory note that it is an AI-generated explanation.
   - **Section 2 (Verified Statutory Provision):** Distinct blue card with a verification badge (`✓ verified`), presenting statutory text in a monospace font block for clarity.
2. **Cognitive Load Reduction:**
   - Visual 4-step progress indicator in Action Mode (**1. Jurisdiction → 2. Grievance Category → 3. Responsible Authority → 4. Action Roadmap**).
   - Categorized sample prompts (Constitution, BNS, BNSS, BSA) for immediate discovery without typing complex queries.
3. **Citizen Confidence Signals:**
   - Color-coded badges: Green for High Confidence (exact/close semantic match), Amber for Moderate Confidence, Muted for Low Confidence.
   - Relevance score percentage displayed alongside confidence tier.
4. **Accessible Design Tokens:**
   - Custom CSS token architecture (`:root` variables) for typography (Inter + JetBrains Mono), spacing, and contrast compliance.
   - Responsive layout optimized for mobile screens (stacked cards, touch-friendly category pills, accessible tap targets).
5. **Contextual Fallback States:**
   - User-friendly network and no-result error cards with contextual retry buttons, search suggestions, and official NALSA/DLSA helplines.

---

## 🏗️ Technical Architecture

```
                                  ┌───────────────────────────┐
                                  │     Citizen / Browser     │
                                  └─────────────┬─────────────┘
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         │   React 19 + Vite Frontend (Port 5173 / 80) │
                         │   • Design Token System (:root variables)   │
                         │   • Visual Step Indicator & Category Pills  │
                         │   • Multilingual Selector (EN/HI/TE/MR)     │
                         │   • Citation Export & Copy Utility          │
                         └──────────────────────┬──────────────────────┘
                                                │ HTTP / REST (JSON)
                         ┌──────────────────────┴──────────────────────┐
                         │      FastAPI Backend Server (Port 8000)     │
                         │   • CORS Middleware & Global Error Handler  │
                         │   • Pydantic v2 Request/Response Schemas    │
                         └──────┬───────────────────────┬──────────────┘
                                │                       │
            ┌───────────────────┴──────────┐   ┌────────┴───────────────────┐
            │   Information Pipeline (RAG) │   │  Action Pipeline (Routing) │
            │                              │   │                            │
            │  • ChromaDB Vector Store     │   │  • SQLite Database         │
            │  • Sentence-Transformers     │   │  • SQLModel ORM            │
            │  • Exact Reference Matcher   │   │  • 106 Districts (TS/AP/   │
            │  • Predecessor Law Mapper    │   │    MH/DL)                  │
            │  • Google Gemini 2.5 SDK     │   │  • Forum & Escalation Logic│
            │    (Curated Fallback Engine) │   │  • Document Checklist DB   │
            └──────────────────────────────┘   └────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite | Responsive single-page application with component-level modularity |
| **Styling** | Vanilla CSS with Design Tokens | Centralized `:root` custom properties, responsive breakpoints, zero heavy UI dependencies |
| **Backend** | FastAPI, Python 3.11–3.13 | Asynchronous REST API framework with native OpenAPI documentation |
| **Data Validation**| Pydantic v2 | Strict request/response contract validation |
| **Vector DB** | ChromaDB | Local vector store for semantic similarity search over curated provisions |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) | Embeddings generated locally without recurring external API cost |
| **Relational DB** | SQLite with SQLModel | Authority routing, district hierarchies, and procedural checklists |
| **LLM Integration** | Google GenAI SDK (`gemini-2.5-flash`) | Multilingual plain-language explanations with curated fallback when offline or unkeyed |

---

## 🚀 Getting Started

### Prerequisites
* **Python:** 3.11 or higher
* **Node.js:** 18.x or higher
* **Git**

### 1. Clone the Repository
```bash
git clone -b development https://github.com/gandladinesh/NyayaAI.git
cd NyayaAI
```

### 2. Configure Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

*(Optional: Copy `.env.example` to `.env` and set `GEMINI_API_KEY` for live AI explanations. If omitted, NyayaAI uses curated plain-language explanations stored in the seed corpus).*

### 3. Run Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
* **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Testing & Verification

NyayaAI maintains an automated test suite of **128 tests** covering statutory integrity, semantic retrieval, multilingual support, confidence scoring, and agent pipelines.

### Run Backend Tests:
```bash
backend/venv/Scripts/python.exe -m pytest backend/tests -q
```

**Results:**
```
128 passed in ~40s
```

### Verify Frontend Production Build:
```bash
cd frontend
npm run build
```

**Results:**
```
✓ 24 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-yEn3B9pg.css   29.37 kB │ gzip:  5.45 kB
dist/assets/index-CxyTj79j.js   230.53 kB │ gzip: 70.33 kB
✓ built in ~500ms
```

---

## 📸 Screenshots & User Flow Guide

*(To capture screenshots for documentation or portfolio presentation, use the guide below)*

| Screen | Description | Suggested View |
| :--- | :--- | :--- |
| **1. Landing & Mode Selection** | Hero banner, mode toggle, and categorized prompt chips | Default home state at [http://localhost:5173](http://localhost:5173) |
| **2. Information Query Input** | Textarea with shortcut hint, language selector (EN/HI/TE/MR), and prompt chips | With sample query entered |
| **3. AI Explanation & Confidence** | Plain-language card with confidence tier pill and percentage match | Results for *"What is the right to life under Article 21?"* |
| **4. Verified Statutory Text** | Statutory text card with `✓ verified` badge retrieved from the legal corpus | Scroll to Section 2 of query results |
| **5. Judicial Precedents & Citation**| Landmark court authorities card and citation copy/download bar | Scroll to Sections 3 & 4 |
| **6. Action Mode Routing Form** | Visual 4-step indicator, State & District dropdowns, category cards | Toggle to "Action Mode" |
| **7. Authority & Procedural Roadmap**| Responsible authority card, filing steps checklist, and escalation alert | Results for TS / Hyderabad / Consumer Dispute |

---

## 🗺️ Engineering Roadmap

- [x] **Phase 1:** Constitution of India Seed Corpus (Articles 12–22, 25–30, 32, 39A, 44, 51A, 226)
- [x] **Phase 1:** State & District Authority Database (TS, AP, MH, DL — 106 official districts)
- [x] **Phase 1:** Action Mode procedural routing & jurisdiction analyzer
- [x] **Phase 2:** Corpus expansion to modern criminal codes (BNS, BNSS, BSA)
- [x] **Phase 2:** Predecessor-to-successor section cross-referencing (IPC/CrPC/IEA → BNS/BNSS/BSA)
- [x] **Phase 3:** 50 verified provisions corpus integration & verification suite
- [x] **Phase 3:** Multilingual plain-language explanations (English, Hindi, Telugu, Marathi)
- [x] **Phase 3:** Citizen confidence scoring (0–100%) and unresolved query redressal pathways
- [x] **Phase 3:** Production hardening (exception handlers, CORS validation, health metrics)
- [x] **Phase 4 (Task 1):** Zero-cost deterministic agent orchestrator pipeline
- [ ] Expansion to all 28 States & 8 UTs (700+ districts)
- [ ] Speech-to-Text audio queries for rural citizen accessibility (Bhashini API integration)
- [ ] Automated court case status tracking via eCourts open API

---

## ⚖️ Legal Disclaimer

> **Important Notice:** NyayaAI is an educational and civic empowerment system designed to assist citizens in understanding Indian legal provisions, landmark case law, and official redressal mechanisms. It **does not constitute formal legal advice** and does not create an advocate-client relationship. Laws, procedural rules, and court fees are subject to government amendments; citizens should verify current requirements on official portals before formal filing.
