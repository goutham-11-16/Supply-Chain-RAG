# Supply Chain Intelligence RAG System
**HCLTech Assignment 2 — Meridian Components Pvt. Ltd.**

An enterprise-grade internal Supply Chain Procurement & Intelligence Assistant built for **Meridian Components Pvt. Ltd.**, an automotive electronics control unit (ECU) and wiring harness manufacturer operating assembly plants in Chakan (Pune) and Hosur (Tamil Nadu).

The system indexes Meridian's internal procurement policy handbooks and operational performance reviews, allowing procurement buyers and executive managers to ask complex natural-language questions, retrieve document-grounded context, analyze cross-document policy implications, evaluate supplier penalties, calculate safety stock requirements, and inspect full source audit trails.

---

## 📌 Executive Summary & Core Capabilities

- **Document-Grounded Q&A**: Generates answers strictly bound to uploaded internal documents with zero hallucinations.
- **Cross-Document Reasoning**: Seamlessly synthesizes facts across operational data (*Supply Chain Review Q1*) and governing policy rules (*Procurement Handbook v4.2*).
- **Dual-Column Source Citation Audit Trail**: Provides exact document names and page numbers for every cited fact.
- **Top-K Retrieval Range Control**: Interactive control slider (range 1–12, default 6) with real-time vector chunk inspection.
- **Automated Policy & Penalty Calculator**: Interactive rule-based engine evaluating supplier performance against Clause 6.1 (OTD warnings), Clause 6.2 (Rating Bands A–D), Clause 6.3 (Quality Cost Recovery & 100% inspection floor), and Clause 5.1 (Safety Stock math).
- **Honest Refusal & Anti-Hallucination**: Automatically detects queries for unavailable information (e.g., executive salaries or unmentioned historical data) and issues strict, polite refusal notices.

---

## 🏗️ System Architecture

### 1. Vector RAG Pipeline Architecture
```
[ PDF Documents ] ──► [ PyPDF Text Extraction ] ──► [ Recursive Character Chunking ]
                                                                  │ (Size: 1200, Overlap: 150)
                                                                  ▼
[ Grounded Response + Citations ] ◄── [ GPT-4o Synthesis ] ◄── [ ChromaDB Vector Search ]
                                                               (text-embedding-3-small)
```

1. **Document Loading**: PyPDF extracts raw text from PDF files located in `data/`.
2. **Chunking & Preprocessing**: `RecursiveCharacterTextSplitter` segments text into 1200-character chunks with 150-character overlap, appending document metadata (title, filename, 1-indexed page number, document type).
3. **Embedding Generation**: Chunks are embedded into 1536-dimensional vectors using OpenAI's `text-embedding-3-small`.
4. **Vector Storage**: Vectors and metadata are stored in a persistent single-collection ChromaDB database (`supplychain_rag`).
5. **Top-K Similarity Retrieval**: Similarity search retrieves the Top-K nearest vector chunks (configurable 1–12, default 6).
6. **Smart Cross-Doc Balancing**: If a query mentions cross-document concepts (e.g., supplier scorecards and penalty clauses), targeted metadata searches ensure balanced coverage from both PDFs.
7. **Context Construction & Synthesis**: Context is injected into a strict system prompt and passed to `GPT-4o` for grounded answer generation.

### 2. Policy & Penalty Calculator (Deterministic Engine)
Operating alongside the RAG pipeline, the Policy & Penalty Calculator is a deterministic, rule-based execution engine that calculates exact financial penalties, rating bands, and safety stock days using governing formulas from Section 5 & 6 of the Procurement Policy Handbook:
$$\text{Safety Stock (Days)} = \max(\text{Lead Time Days} \times 0.25, \text{Mandatory Floor Days})$$

---

## 🛠️ Technologies Used

- **Language & Runtime**: Python 3.11+
- **Vector Database**: ChromaDB (`chromadb>=0.5.0`)
- **Embeddings Model**: OpenAI `text-embedding-3-small`
- **Language Model**: OpenAI `GPT-4o`
- **Orchestration Framework**: LangChain (`langchain>=0.2.0`, `langchain-openai`, `langchain-chroma`)
- **PDF Extraction**: PyPDF (`pypdf>=4.0.0`)
- **User Interface**: Streamlit (`streamlit>=1.35.0`) with custom Glassmorphism CSS
- **REST API Server**: FastAPI (`fastapi>=0.111.0`, `uvicorn>=0.30.0`)
- **Environment Management**: `python-dotenv`

---

## 📄 Documents Used

The system is pre-loaded with the two Meridian supply chain PDF documents located in `data/`:

1. **`Meridian_Procurement_Policy_Handbook_v4.2.pdf`** *(Procurement Policy Handbook)*:
   - Governing rules for supplier classification (Strategic, Critical, Standard, Tactical), approval authority thresholds, sourcing rules (dual-sourcing, share-of-wallet caps), rating bands (A, B, C, D), quality cost recovery (Clause 6.3), and safety stock formulas.
2. **`Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf`** *(Operational Performance Review)*:
   - Q1 FY2025-26 scorecard data for Apex Microelectronics, Kaveri Metals, Trident Circuit Boards, Sunrise Logistics, and Shenzhen Rui Electronics; line stoppage logs, inventory cover, and freight lane metrics.

---

## ⚙️ RAG System Configuration

- **Chunk Size**: `1200` characters
- **Chunk Overlap**: `150` characters
- **Embedding Model**: `text-embedding-3-small` (1536 dimensions)
- **LLM Model**: `GPT-4o` (`temperature = 0.0`)
- **Vector Store Collection**: `supplychain_rag`
- **Top-K Retrieval Range**: `1 – 12`
- **Default Top-K**: `6`
- **Persistence Path**: `chroma_db/`

---

## 🚀 Setup & Installation Instructions (Windows)

### Step 1: Clone / Extract Project
Open PowerShell or Command Prompt in the project folder:
```powershell
cd HCLTech_SupplyChain_RAG
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure OpenAI API Key
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in any text editor and paste your HCLTech-provided API key:
```ini
OPENAI_API_KEY=sk-proj-your_actual_hcltech_openai_key_here
```

### Step 5: Ingest PDF Documents into Vector Store
Run the clean ingestion script to build the ChromaDB vector database:
```powershell
python scripts/reset_and_reingest.py
```
*Expected Output:*
```text
[+] Found 2 PDF documents in data/ directory.
[+] Chunking 6 pages (size=1200, overlap=150)...
    Created 22 chunks
[+] Embedding and storing in ChromaDB...
    Stored 22 chunks in chroma_db
✅ [SUCCESS] Vector store re-indexed successfully! (22 Total Chunks)
```

---

## 🖥️ Running the Application

### Option 1: Streamlit Executive Portal (Primary Web UI)
```powershell
python -m streamlit run app.py
```
Open browser at: **`http://localhost:8501`**

### Option 2: FastAPI REST Server
In a separate terminal window:
```powershell
python api/main.py
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Endpoint: `POST http://localhost:8000/ask` with JSON body `{"question": "...", "top_k": 6}`

---

## 🔄 Re-Indexing / Clearing ChromaDB Vector Store

To wipe the vector database and re-ingest the PDFs cleanly at any time, run:
```powershell
python scripts/reset_and_reingest.py
```

---

## 📖 How to Use the Application

1. **RAG Intelligence Analyst (Tab 2)**:
   - Click any of the **10 Sample Question Preset Buttons** (Q1–Q10) to execute instantly.
   - Or type a custom question in the query input box and click **⚡ Execute Query**.
   - Adjust the **Top-K Chunks slider** (1–12) in the sidebar to control context window depth.
   - Expand **🐞 Developer & Debug Tools** at the bottom to inspect retrieved vector text snippets, distance scores, and live REST API JSON payloads.
2. **Policy & Penalty Calculator (Tab 3)**:
   - Select a supplier (e.g., Kaveri Metals or Trident Circuit Boards) or enter custom metrics (OTD %, PPM defect rate, component criticality, lead time).
   - Click **⚡ Calculate Policy Actions & Penalties** to run the deterministic evaluation engine.

---

## 🧪 Verified Assignment Regression Tests

The system has been rigorously tested against all key assignment benchmarks:

| Test ID & Question | Grounded Answer Summary | Source Citation | Status |
| :--- | :--- | :--- | :---: |
| **TEST A**: *"What are the four supplier classification categories?"* | **Critical**, **Strategic**, **Standard**, and **Tail**. | `Policy Handbook Page 1` | ✅ Pass |
| **TEST B**: *"What policy actions are triggered for Trident Circuit Boards based on its Q1 performance?"* | **OTD (84.6%)**: Clause 6.1 warning within 10 days & weekly review calls.<br/>**Defects (640 PPM)**: Clause 6.3 ₹120/unit rework charge & 100% inspection until 3 consecutive lots without defect. | `Review Page 1 & 2`<br/>`Policy Handbook Page 2` | ✅ Pass |
| **TEST C**: *"The microcontroller supplier is single-source. What does sourcing policy require, and what is Meridian doing?"* | **Policy**: Clause 7.1 mandates dual-sourcing within 12 months for Critical parts.<br/>**Meridian Action**: Phase 2 validation of domestic second source & holding 30-day buffer inventory. | `Policy Handbook Page 2`<br/>`Review Page 1 & 3` | ✅ Pass |
| **TEST D**: *"What is the annual salary of the Head of Procurement?"* | *"The information is not available in the uploaded documents."* | N/A (Honest Refusal) | 🛡️ Pass |

---

## 🔐 Security & Confidentiality Notice

> **[IMPORTANT]**: The real OpenAI API key provided by HCLTech is **intentionally excluded** from this submission package for security compliance. `.env` is listed in `.gitignore`. The reviewer must create a local `.env` file using `.env.example` and insert their API key prior to launching the application.
