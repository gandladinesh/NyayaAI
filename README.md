# ⚖️ NyayaAI (न्याय AI)
### AI-Powered Legal Assistant & Official Authority Router for Indian Law

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-81%2F81%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

NyayaAI is an open-source civic technology platform designed to make Indian law and legal remedies accessible, understandable, and actionable for every citizen.

---

## 🏛️ Core Architectural Invariants

NyayaAI operates under strict architectural principles to guarantee legal authenticity and prevent AI hallucinations:

1. **Exact Legal Text is Verbatim & Official:** Statutory and constitutional text (`exact_text`) is sourced strictly from official Government of India sources (India Code, Ministry of Law & Justice, Legislative Department) or court repositories (eCourts). It is **NEVER AI-generated, paraphrased, or reconstructed from model weights**.
2. **Strict Separation of Text and Explanation:** The verbatim legal text and the AI-generated plain-language summary (`ai_explanation`) reside in completely separate fields. They are never conflated or presented interchangeably.
3. **Truth in Source Labeling:** Only verified government and court sources carry the `official` or `court` badge. Third-party portals such as IndianKanoon are strictly designated as `supplementary`.
4. **Deterministic Authority Routing:** Administrative jurisdictions and complaint procedures are computed deterministically from structured database relationships (`State` → `District` → `Problem Category` → `Authority`), never hallucinated by an LLM.

---

## 🌟 Key Features

### 1. 🔍 Information Mode (`POST /api/query`)
* **Semantic Legal RAG:** Retrieves relevant constitutional articles and statutes using semantic search over ChromaDB vector embeddings.
* **Plain-Language Explanations:** Employs the official Google Gemini SDK (`google-genai`) with strict system prompts to explain complex legal text in simple terms without altering legal meaning.
* **Landmark Case Law Integration:** Automatically links seminal Supreme Court precedents (e.g., *Maneka Gandhi v. UOI*, *K.S. Puttaswamy v. UOI*, *Indira Sawhney v. UOI*) establishing foundational principles.
* **Legal Citation Export:** One-click download of clean, structured legal citation documents (`.txt`) or clipboard copying formatted for advocacy or personal reference.
* **Quick-Prompt Discovery:** Interactive chips to explore core Fundamental Rights (Right to Life, Equality Before Law, Freedom of Speech, Free Legal Aid, Protection Against Arrest).

### 2. ⚡ Action Mode (`GET /api/route`)
* **Citizen-First Routing Pipeline:** Guides citizens through State and District selection to identify the exact competent forum for their grievance.
* **Four Supported Jurisdictions (Phase 1):**
  * **Telangana (TS)** — 33 districts
  * **Andhra Pradesh (AP)** — 26 districts
  * **Maharashtra (MH)** — 36 districts
  * **National Capital Territory of Delhi (DL)** — 11 districts
* **Four Core Grievance Categories:**
  * 🛒 **Consumer Disputes:** District Consumer Disputes Redressal Commission (DCDRC) → State Commission (SCDRC)
  * 🏢 **Real Estate & Housing:** Real Estate Regulatory Authority (RERA) → RERA Appellate Tribunal
  * ⚖️ **Free Legal Aid:** District Legal Services Authority (DLSA) / Taluk Committees → State Legal Services Authority (SLSA)
  * 🛡️ **Human Rights Violations:** State Human Rights Commission (SHRC) → National Human Rights Commission (NHRC)
* **4-Step Action Roadmap:** Provides step-by-step guidance including required documents, fee structures, filing modes (online portal vs. physical registry), and statutory escalation timelines.

---

## 🏗️ System Architecture

```
                                 ┌────────────────────────┐
                                 │   Citizen / Browser    │
                                 └───────────┬────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │ React 19 + Vite Frontend (Port 5173 / 80) │
                       └─────────────────────┬─────────────────────┘
                                             │ HTTP / REST
                       ┌─────────────────────┴─────────────────────┐
                       │   FastAPI Backend Server (Port 8000)      │
                       └─────┬───────────────────┬───────────┬─────┘
                             │                   │           │
           ┌─────────────────┴────────┐  ┌───────┴──────┐  ┌─┴────────────────────────┐
           │     RAG / Retrieval      │  │  SQL Database│  │   AI Explanation Engine  │
           │                          │  │              │  │                          │
           │  • ChromaDB Vector Store │  │  • SQLite    │  │  • Google Gemini 2.5     │
           │  • LegalProvisionService │  │  • SQLModel  │  │  • Strict Grounding Rules│
           │  • Verified Bare Acts    │  │  • TS/AP/MH/ │  │  • Case Law Enrichment   │
           │    (Constitution, BNS)   │  │    DL forums │  │                          │
           └──────────────────────────┘  └──────────────┘  └──────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
* **Python:** 3.11 or higher
* **Node.js:** 18.x or higher
* **Git**

### Option A: Local Development

#### 1. Clone the Repository
```bash
git clone -b development https://github.com/gandladinesh/NyayaAI.git
cd NyayaAI
```

#### 2. Configure Backend Environment
```bash
cd backend
cp .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY` in `backend/.env` for live LLM explanations. Without an API key, NyayaAI uses curated authoritative explanations stored in the verified seed corpus.)*

#### 3. Setup Backend Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Run Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
* Interactive Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

#### 5. Setup & Run Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B: Docker Compose (One-Command Deployment)

```bash
# Build and launch both frontend and backend
docker compose up --build
```
* Frontend: [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173))
* Backend API: [http://localhost:8000](http://localhost:8000)

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status, database type, and version info |
| `POST` | `/api/query` | Information Mode: RAG semantic search with AI explanation |
| `GET` | `/api/route` | Action Mode: Authority and procedural routing by State & District |
| `GET` | `/api/states` | List all supported States and Union Territories |
| `GET` | `/api/states/{id}/districts` | List all official districts for a given state |
| `GET` | `/api/authorities` | Search authorities filtered by jurisdiction and problem category |
| `GET` | `/api/authorities/{id}` | Comprehensive authority profile with contacts & procedures |
| `GET` | `/api/provisions` | Browse verified statutory provisions (optional `?search=` keyword filter) |
| `GET` | `/api/provisions/{id}` | Retrieve specific verified provision by ID |
| `GET` | `/api/provisions/reference/{ref}`| Retrieve provision by Article/Section reference |

---

## 🧪 Testing & Verification

NyayaAI includes a comprehensive test suite of **81 automated backend tests** validating:
* Exact legal text verification and integrity
* Semantic retrieval threshold enforcement
* Authority jurisdiction boundaries and hierarchy
* Edge cases (empty inputs, out-of-scope queries, special characters, max lengths)
* Pydantic v2 schemas and REST contracts

Run the test suite:
```bash
# From the project root
backend/venv/Scripts/python.exe -m pytest backend/tests -v
```

Output:
```
============================== 81 passed in ~25s ==============================
```

Frontend production build verification:
```bash
cd frontend
npm run build
```

---

## 🗺️ Roadmap

- [x] Phase 1 Seed Corpus: Constitution of India (Articles 12–22, 25–30, 32, 39A, 44, 51A, 226)
- [x] Phase 1 State & District Database: TS, AP, MH, DL (106 official districts)
- [x] Phase 1 Information Mode with Semantic RAG & Gemini AI Explainer
- [x] Phase 1 Action Mode with Jurisdiction Analysis & Step-by-Step Action Plan
- [x] Legal Citation Export (Download & Clipboard Copy)
- [x] Dockerization & Production Environment Templates
- [ ] Phase 2 Legal Corpus Expansion: Bharatiya Nyaya Sanhita (BNS), BNSS, BSA
- [ ] Multilingual Support (Hindi, Telugu, Marathi)
- [ ] PostgreSQL + `pgvector` migration for enterprise deployments

---

## ⚖️ Legal Disclaimer

> **Important Notice:** NyayaAI is an educational and civic empowerment tool designed to assist citizens in understanding legal concepts and official redressal mechanisms. It **does not constitute formal legal advice** and cannot substitute for representation by a qualified advocate. Citizens are encouraged to verify current fees and timings on official government portals before filing complaints.
