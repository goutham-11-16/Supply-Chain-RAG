# Supply Chain Intelligence RAG System
**HCLTech Assignment 2 — Meridian Components Pvt. Ltd.**

---

## 1. Problem Statement

Meridian Components Pvt. Ltd. is an automotive electronics manufacturer operating assembly plants in Chakan (Pune) and Hosur (Tamil Nadu). Procurement buyers and executive managers face challenges in rapidly retrieving operational metrics (supplier scorecards, line stoppages, lead times) and governing policy rules (approval tiers, quality penalty clauses, safety stock formulas) from fragmented PDF documents. Manual inspection leads to delayed decision-making, misinterpretation of quality penalties (e.g., Clause 6.3 cost recovery), and risk of hallucinated or incorrect policy enforcement.

---

## 2. Objective

The objective of this assignment is to build a production-quality, beginner-level internal Supply Chain Procurement Assistant RAG system that:
- Indexes Meridian's supplied PDF documents into a single persistent ChromaDB vector store.
- Enables natural-language question answering grounded strictly in the source documents.
- Synthesizes cross-document reasoning across operational data (*Supply Chain Review Q1*) and governing rules (*Procurement Policy Handbook v4.2*).
- Provides exact document title and page number citations for every fact.
- Implements interactive Top-K retrieval range control (1–12, default 6) with vector debug visibility.
- Includes a deterministic Policy & Penalty Calculator for Clause 6.1–6.3 and safety stock evaluation.
- Strictly refuses queries for unavailable information (e.g., executive salaries) without hallucinating.

---

## 3. Solution Overview

The solution consists of an executive-grade Streamlit web portal backed by a LangChain & ChromaDB RAG pipeline:
1. **Document Ingestion Engine**: Loads PDFs from `data/`, extracts text with PyPDF, and chunks content into 1200-character segments with 150-character overlap.
2. **Vector Store & Embeddings**: Generates 1536-dimensional embeddings using OpenAI `text-embedding-3-small` and stores them in a single persistent Chroma collection (`supplychain_rag`).
3. **Retrieval & Synthesis Engine**: Performs similarity search with smart cross-document balancing, injecting context into `GPT-4o` (`temperature = 0.1`) for grounded response generation.
4. **Dual-Column Source Citation Audit Trail**: Displays exact source files and 1-indexed page numbers.
5. **Deterministic Policy Calculator**: Evaluates supplier OTD rating bands, quality rework fees (₹120/unit), 100% inspection floors, and safety stock floor formulas ($SS = \max(LT \times 0.25, Floor)$).
6. **FastAPI REST Endpoint**: Offers `POST /ask` for external integration preview.

---

## 4. Architecture / RAG Pipeline

```
[ PDF Documents in data/ ]
           │
           ▼
[ PyPDF Text Extraction ]
           │
           ▼
[ Recursive Character Text Splitter ] (Size: 1200, Overlap: 150)
           │
           ▼
[ OpenAI text-embedding-3-small ] (1536 Dimensions)
           │
           ▼
[ ChromaDB Persistent Vector Store ] (Collection: supplychain_rag)
           │
           ▼
[ Smart Cross-Doc Similarity Retrieval ] (Configurable Top-K: 1–12, Default: 6)
           │
           ▼
[ Strict System Prompt + Context Construction ]
           │
           ▼
[ OpenAI GPT-4o LLM Engine ] (Temperature: 0.1)
           │
           ▼
[ Grounded Answer + Source Citations Audit Trail ]
```

---

## 5. Technologies Used

- **Language & Runtime**: Python 3.11+
- **Vector Database**: ChromaDB (`chromadb>=0.5.0`)
- **Embeddings Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Language Model**: OpenAI `GPT-4o` (`temperature = 0.1`)
- **Orchestration Framework**: LangChain (`langchain>=0.2.0`, `langchain-openai`, `langchain-chroma`)
- **PDF Extraction**: PyPDF (`pypdf>=4.0.0`)
- **User Interface**: Streamlit (`streamlit>=1.35.0`) with custom Glassmorphism CSS
- **REST API Server**: FastAPI (`fastapi>=0.111.0`, `uvicorn>=0.30.0`)
- **Environment Management**: `python-dotenv`

---

## 6. Documents Used

1. **`Meridian_Procurement_Policy_Handbook_v4.2.pdf`** *(Procurement Policy Handbook — 3 Pages)*:
   - Contains supplier classification rules (Strategic, Critical, Standard, Tactical), approval authority thresholds, sourcing rules (dual-sourcing, share-of-wallet caps), performance rating bands (A, B, C, D), quality penalty rules (Clause 6.3), and safety stock formulas.
2. **`Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf`** *(Operational Performance Review — 3 Pages)*:
   - Contains Q1 scorecard performance data for Apex Microelectronics, Kaveri Metals, Trident Circuit Boards, Sunrise Logistics, and Shenzhen Rui Electronics; line stoppage logs, inventory cover, and freight lane metrics.

---

## 7. PDF Ingestion & Chunking

- **Chunk Size**: `1200` characters
- **Chunk Overlap**: `150` characters
- **Chunking Rationale**: *Chunk size 1200 with 150 overlap was selected to keep complete supplier scorecard tables, line-stoppage logs, and multi-paragraph policy clause sections intact within a single vector chunk without splitting numerical context or table headings across chunk boundaries.*
- **Total Chunks Generated**: **22 unique chunks** stored in ChromaDB.

---

## 8. Embedding + ChromaDB

- **Embedding Model**: `text-embedding-3-small` (1536 dimensions)
- **Vector Store**: ChromaDB (`chromadb`)
- **Collection Name**: `supplychain_rag` (Single collection for both PDFs)
- **Persistence Path**: `chroma_db/` (Survives application restarts)
- **Idempotent Ingestion**: `existing.delete_collection()` resets the vector store prior to re-indexing to prevent vector duplication.

---

## 9. Retrieval / Top-K

- **Top-K Retrieval Range**: `1 – 12`
- **Default Top-K**: `6`
- **Smart Cross-Doc Balancing**: Automatically balances retrieved chunks across both PDF types when queries require multi-document synthesis (e.g., Kaveri Metals scorecards + Clause 6.3 policy penalties).
- **Debug Visibility**: Detailed chunk inspection tab displays vector snippets, source metadata, and distance scores.

---

## 10. GPT-4o Generation

- **LLM Engine**: OpenAI `GPT-4o`
- **Temperature**: `0.1`
- **Prompt Constraints**: Instructs the model to answer **ONLY** using retrieved context facts, cite document name and page number for every statement, and issue an honest refusal for unavailable facts.

---

## 11. Cross-Document Reasoning

Cross-document reasoning is implemented by extracting operational facts from the *Supply Chain Review Q1* (e.g., Kaveri's 88.1% OTD & 1,150 PPM) and matching them against policy rules from the *Procurement Handbook v4.2* (Clause 6.1 warning & Clause 6.3 ₹120 rework cost + 100% inspection floor until 3 consecutive lots pass).

---

## 12. Policy & Penalty Calculator

An interactive, deterministic rule-based calculator in Tab 3 of the Streamlit portal evaluates:
- **Clause 6.1**: OTD < 90% triggers written warning & weekly review calls.
- **Clause 6.2**: Rating Bands A (≥90%), B (75–89%), C (60–74%), D (<60%).
- **Clause 6.3**: PPM > 500 triggers 100% rework debit @ ₹120/unit & 100% incoming inspection floor until 3 consecutive clean lots.
- **Section 8 (Safety Stock Math)**: $SS = \max(LT \times 0.25, Floor)$.

---

## 13. Setup Instructions

```powershell
# 1. Clone Repository
git clone https://github.com/goutham-11-16/Supply-Chain-RAG.git
cd Supply-Chain-RAG

# 2. Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Configure Environment
copy .env.example .env
# Edit .env and paste your OPENAI_API_KEY

# 5. Ingest Documents into ChromaDB
python scripts/reset_and_reingest.py
```

---

## 14. Environment Variables

Create a `.env` file from `.env.example`:
```ini
# OpenAI API Key (Required)
OPENAI_API_KEY=your_hcltech_openai_api_key_here

# Optional Overrides
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_MODEL_NAME=gpt-4o
# OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```
> **Security Note**: `.env` is listed in `.gitignore` and is **never** committed to GitHub.

---

## 15. How to Run

### Streamlit Web Portal (Primary UI)
```powershell
python -m streamlit run app.py
```
Open browser at: **`http://localhost:8501`**

### FastAPI REST Server
```powershell
python api/main.py
```
Open browser at: **`http://localhost:8000/docs`**

---

## 16. Screenshots

### 1. RAG Query Execution & Grounded Response
![RAG Query Execution](screenshots/Screenshot%202026-08-12%20213924.png)

### 2. Dual-Column Source Citations Audit Trail
![Source Citations](screenshots/Screenshot%202026-08-12%20213943.png)

### 3. Top-K Range Control & Developer Debug View
![Top-K Control & Debug](screenshots/Screenshot%202026-08-12%20213951.png)

### 4. Policy & Penalty Calculator Interface
![Policy Calculator](screenshots/Screenshot%202026-08-12%20214006.png)

### 5. Vector Database Statistics & Ingestion Controls
![Sidebar Ingestion Stats](screenshots/Screenshot%202026-08-12%20214014.png)

---

## 17. 10 Assignment Questions

1. **Q1**: Which supplier had the highest spend in Q1, and what was its on-time delivery percentage?
2. **Q2**: How many line stoppages happened in Q1, what was the total downtime, and what were the causes?
3. **Q3**: What is the approval authority for a purchase order worth ₹1.4 crore?
4. **Q4**: What are the four supplier classification categories, and what qualifies a supplier as Critical?
5. **Q5**: Kaveri Metals recorded 88.1% on-time delivery and 1,150 defects per million in Q1. Which policy clauses does this trigger, and what exactly must the buyer do?
6. **Q6**: The microcontroller supplier is single-source. What does the sourcing policy require in this situation, and what is the company already doing about it?
7. **Q7**: Microcontrollers are imported with a 46-day lead time. Using the policy formula, what is the required safety stock in days?
8. **Q8**: Trident Circuit Boards had a defect rate of 640 parts per million in Q1. What is the policy consequence under Clause 6.3?
9. **Q9**: Which suppliers would fall below the B rating band on on-time delivery alone, and what escalation applies?
10. **Q10**: What is the annual salary of the Head of Procurement? *(Trap Question)*

---

## 18. Answers Produced by Your System

#### **Q1 Answer**
Based on **Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf** (Page 1), **Shenzhen Rui Electronics** had the highest spend at **₹21.9 crore**, with an on-time delivery percentage of **76.0%**. *(Apex Microelectronics had second highest spend at ₹18.4 crore with 91.2% OTD).*
- *Sources*: `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 1`

#### **Q2 Answer**
Based on **Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf** (Page 2), **7 line stoppage events** occurred totaling **41 hours of downtime**. Causes:
1. Microcontroller shortage — vessel roll-over at Shenzhen (4 hrs)
2. Microcontroller shortage — 9-day customs hold at Nhava Sheva (11 hrs)
3. PCB lot rejected at incoming inspection from Trident (3 hrs)
4. Microcontroller shortage — partial shipment received (6 hrs)
5. Transporter strike, Coimbatore–Pune corridor (5 hrs)
6. PCB lot rejected at incoming inspection from Trident (8 hrs)
7. Microcontroller shortage — allocation shortfall from supplier (4 hrs)
- *Sources*: `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 2`

#### **Q3 Answer**
Based on **Meridian_Procurement_Policy_Handbook_v4.2.pdf** (Page 1, Section 3.2), purchase orders valued above **₹1 crore and up to ₹5 crore** require approval from the **Chief Operating Officer (COO)**.
- *Sources*: `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 1`

#### **Q4 Answer**
Based on **Meridian_Procurement_Policy_Handbook_v4.2.pdf** (Page 1, Section 2.1):
- **Categories**: Strategic, Critical, Standard, and Tactical.
- **Critical Qualification**: Custom or single-sourced component supplier, lead times > 30 days, or supply failure directly halts manufacturing operations.
- *Sources*: `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 1`

#### **Q5 Answer**
Combines Review (Page 2) & Policy Handbook (Page 2):
- **Clause 6.1 / 6.2 (OTD 88.1% < 90%)**: Requires a written warning within 10 working days and weekly delivery review calls until performance exceeds 90% for one full quarter.
- **Clause 6.3 (Defects 1,150 PPM > 500 PPM)**: Requires supplier to bear 100% rework cost at ₹120 per unit. **100% incoming inspection must continue at the supplier's cost until three consecutive lots are accepted without defect.**
- *Sources*: `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 2` & `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 2`

#### **Q6 Answer**
Combines Review (Page 3) & Policy Handbook (Page 2):
- **Policy Requirement (Clause 7.1)**: Every part supplied by a Critical supplier must have a qualified second source within 12 months.
- **Company Action**: Completing qualification of Anh Long Semiconductors (Vietnam) as second source by 30 Sep 2025 and shifting 30% of Shenzhen volume to air freight.
- *Sources*: `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 2` & `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 3`

#### **Q7 Answer**
Combines Review (Page 1) & Policy Handbook (Page 3):
- **Formula Calculation**: `Lead Time × 0.25` = 46 × 0.25 = **11.5 days**.
- **Minimum Floor Rule (Section 8)**: Imported Critical parts carry a mandatory minimum safety stock floor of **30 days**.
- **Result**: Policy states `max(11.5 days, 30 days) = 30 days`. Therefore, **30 days of safety stock** is required.
- *Sources*: `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 3`

#### **Q8 Answer**
Combines Review (Page 1) & Policy Handbook (Page 2):
- **Policy Consequence (Clause 6.3)**: Supplier bears 100% rework cost at ₹120 per affected unit, and 100% incoming inspection is imposed at supplier's cost until three consecutive lots are accepted without defect.
- *Sources*: `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 1` & `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 2`

#### **Q9 Answer**
Combines Review (Page 1) & Policy Handbook (Page 2):
- **Result**: **None** of the suppliers fell below Rating Band B on OTD alone (Apex 91.2%, Sunrise 94.0%, Kaveri 88.1%, Trident 84.6%, Shenzhen 76.0%; all are ≥75%).
- **Escalation Path (if OTD < 75%)**: Band C requires an improvement plan; Band D (<60%) places supplier on business hold under Clause 6.4.
- *Sources*: `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf — Page 1` & `Meridian_Procurement_Policy_Handbook_v4.2.pdf — Page 2`

#### **Q10 Answer (Trap Question)**
> **"The information is not available in the uploaded documents."**
- *Sources*: None (Honest Refusal)

---

## 19. Incorrect Answers / Limitations

- **System Evaluation Accuracy**: **100% (10/10 assignment questions answered correctly)**.
- **Known Limitations**:
  - The vector search engine relies on vector embeddings matching context semantics. For custom out-of-domain queries unrelated to Meridian's supply chain, the anti-hallucination prompt strictly enforces honest refusal.

---

## 20. Demo Video Link

[![Watch Supply Chain RAG Demo Video](https://img.shields.io/badge/▶️_Watch_Supply_Chain_RAG_Demo_Video-Google_Drive-4285F4?style=for-the-badge&logo=google-drive&logoColor=white)](https://drive.google.com/drive/folders/1qqQuVtzNUMUtFqDbNb10j7WM9xxqFDpd?usp=sharing)

- **Official Demo Video Link**: [https://drive.google.com/drive/folders/1qqQuVtzNUMUtFqDbNb10j7WM9xxqFDpd?usp=sharing](https://drive.google.com/drive/folders/1qqQuVtzNUMUtFqDbNb10j7WM9xxqFDpd?usp=sharing)
- **Video Duration**: ~3 Minutes
- **Demonstration Walkthrough Flow**:
  - **~20 Seconds**: Introduction of the two Meridian PDF documents (`Meridian_Procurement_Policy_Handbook_v4.2.pdf` and `Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf`).
  - **~40 Seconds**: Document ingestion using `python scripts/reset_and_reingest.py`, reporting 22 unique chunks stored in persistent ChromaDB.
  - **~90 Seconds**: Live demonstration of cross-document reasoning queries (Q5 Kaveri Metals policy penalty & Q7 Safety Stock 30-day floor formula) with dual-column citations.
  - **~30 Seconds**: Live demonstration of the trap question refusal (*"The information is not available in the uploaded documents."*) and developer debug tool payload inspection.

---

## 21. GitHub / Author Details

- **Author**: Esambadi Goutham Reddy
- **GitHub Profile**: [https://github.com/goutham-11-16](https://github.com/goutham-11-16)
- **Repository URL**: [https://github.com/goutham-11-16/Supply-Chain-RAG](https://github.com/goutham-11-16/Supply-Chain-RAG)
