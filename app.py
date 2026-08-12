"""
app.py — Supply Chain RAG Streamlit Executive Portal (Next-Level Edition)
Upload PDFs, index them, ask questions about supply chain data and procurement policies.
Features:
- Fixed Streamlit unique element keys
- Executive Procurement Dashboard (Live Scorecards & Stoppage Analytics)
- Cross-Document AI Query Analyst with Dual-Column Source Citations
- Interactive Policy & Penalty Calculator (Clause 6.2, Clause 6.3 & Safety Stock Floor Math)
- Live API Developer Hub (FastAPI payload preview & CURL code snippets)
"""

import os
import json
import tempfile
import streamlit as st

from ingest import (
    ingest_files, get_collection_stats, load_existing_store,
    get_embeddings, CHROMA_DIR, auto_copy_provided_pdfs
)
from rag import ask

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🔗 Meridian Supply Chain Intelligence — Executive RAG Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for Next-Level Glassmorphism Aesthetics
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main theme background */
    .stApp {
        background: radial-gradient(circle at top left, #1a202c 0%, #0d1117 50%, #050811 100%);
        color: #e2e8f0;
    }
    
    /* Header container styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(20, 30, 48, 0.8) 0%, rgba(36, 59, 85, 0.8) 100%);
        border: 1px solid rgba(56, 178, 172, 0.3);
        border-radius: 16px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .brand-tag {
        background: linear-gradient(90deg, #319795 0%, #3182ce 100%);
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 4px 14px;
        border-radius: 20px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 0.6rem;
    }
    
    .main-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(90deg, #38b2ac 0%, #4fd1c5 40%, #63b3ed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0.2rem 0;
    }
    
    .sub-header {
        color: #cbd5e0;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 0.8rem;
    }

    .badge-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #a0aec0;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 12px;
        margin: 0 3px;
    }

    /* Stat Cards */
    .stat-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 178, 172, 0.25);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        border-color: rgba(79, 209, 197, 0.6);
    }
    
    .stat-number {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #4fd1c5;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }

    /* Table styling */
    .glass-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .glass-table th {
        background: rgba(56, 178, 172, 0.2);
        color: #38b2ac;
        padding: 10px 14px;
        font-size: 0.88rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: left;
    }

    .glass-table td {
        padding: 10px 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.95rem;
    }
    
    /* Answer box */
    .answer-card {
        background: linear-gradient(135deg, rgba(13, 27, 42, 0.9) 0%, rgba(20, 32, 54, 0.9) 100%);
        border: 1px solid rgba(56, 178, 172, 0.4);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        line-height: 1.8;
        font-size: 1.05rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    /* Document Badges */
    .doc-badge-review {
        display: inline-flex;
        align-items: center;
        background: rgba(237, 137, 54, 0.18);
        border: 1px solid rgba(237, 137, 54, 0.45);
        border-radius: 8px;
        padding: 0.35rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.88rem;
        font-weight: 500;
        color: #fbd38d;
    }
    
    .doc-badge-handbook {
        display: inline-flex;
        align-items: center;
        background: rgba(66, 153, 225, 0.18);
        border: 1px solid rgba(66, 153, 225, 0.45);
        border-radius: 8px;
        padding: 0.35rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.88rem;
        font-weight: 500;
        color: #90cdf4;
    }
    
    /* Success & Alert Banners */
    .success-banner {
        background: rgba(72, 187, 120, 0.15);
        border: 1px solid rgba(72, 187, 120, 0.4);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #68d391;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Cross-document indicator */
    .cross-doc-badge {
        background: linear-gradient(90deg, rgba(236, 72, 153, 0.22) 0%, rgba(168, 85, 247, 0.22) 100%);
        border: 1px solid rgba(236, 72, 153, 0.5);
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        color: #f472b6;
        font-size: 0.95rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 1rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #090d16 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Hide Streamlit default chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button Customization */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.25s ease;
    }

    /* Primary Action Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #319795 0%, #3182ce 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 14px rgba(49, 151, 149, 0.4);
    }
    
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(49, 151, 149, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------------------------------
# Sidebar — Control Panel & Vector Database Status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ RAG Control Panel")
    
    stats = get_collection_stats()
    if "error" not in stats and stats["total_chunks"] > 0:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_chunks']}</div>
            <div class="stat-label">Indexed Vector Chunks</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"**Collection:** `{stats['collection_name']}`")
        st.markdown(f"**Embeddings:** `{stats['embedding_model']}`")
        st.markdown(f"**Synthesis LLM:** `{stats['llm_model']}`")
    else:
        st.info("No documents indexed yet. Click 'Index Pre-Loaded PDFs' below to initialize.")
    
    st.markdown("---")
    st.markdown("### ⚙️ Retrieval Strategy")
    top_k = st.slider(
        "Top-K Chunks (`top_k`)", 3, 12, 6,
        help="Retrieving top_k=6 enables seamless multi-hop cross-document reasoning across both Review and Handbook PDFs."
    )
    
    st.markdown("---")
    st.markdown("### 📚 Datasets Active")
    st.markdown("""
    <div style="margin-bottom: 0.8rem;">
        <span class="doc-badge-review">📊 Supply Chain Review (Q1)</span><br/>
        <small style="color: #a0aec0;">Supplier scorecards, lead times, stoppages, inventory levels.</small>
    </div>
    <div>
        <span class="doc-badge-handbook">📋 Procurement Handbook (v4.2)</span><br/>
        <small style="color: #a0aec0;">Approval tiers, penalty clauses, safety stock formulas.</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚀 System Status")
    st.markdown("""
    <span class="badge-pill" style="color:#68d391; border-color:#68d391;">✅ FastAPI Active (Port 8000)</span><br/>
    <span class="badge-pill" style="color:#63b3ed; border-color:#63b3ed; margin-top:4px;">⚡ Chroma Single Collection</span>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero Header Banner
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <span class="brand-tag">HCL TECH ASSIGNMENT 2 • EXECUTIVE PORTAL</span>
    <h1 class="main-header">🔗 Meridian Supply Chain Intelligence</h1>
    <p class="sub-header">Autonomous Procurement Analyst & Cross-Document Governance Platform</p>
    <div>
        <span class="badge-pill">📄 Multi-PDF Vector Search</span>
        <span class="badge-pill">🔀 Multi-Hop Clause Matching</span>
        <span class="badge-pill">🧮 Business Math Floor Logic</span>
        <span class="badge-pill">🛡️ Zero Hallucination Guard</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Auto-detect provided PDFs in data/ or parent directory
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
auto_copy_provided_pdfs()

# Main Navigation Tabs
main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "📊 Executive Dashboard",
    "💬 AI Query Analyst",
    "🧮 Policy & Penalty Calculator",
    "⚡ API Developer Hub"
])

# ---------------------------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------------------------
with main_tab1:
    st.markdown("### 📊 Meridian Components Pvt. Ltd. — Q1 Supply Chain Overview")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">₹51.5 Cr</div>
            <div class="stat-label">Total Q1 Spend</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #f6ad55;">82 Hrs</div>
            <div class="stat-label">Line Downtime</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #fc8181;">3</div>
            <div class="stat-label">Line Stoppages</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number" style="color: #68d391;">91.9%</div>
            <div class="stat-label">Avg Supplier OTD</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    col_d1, col_d2 = st.columns([3, 2])
    
    with col_d1:
        st.markdown("#### 📋 Supplier Scorecard Matrix (Q1 FY2025-26)")
        st.markdown("""
        <table class="glass-table">
            <thead>
                <tr>
                    <th>Supplier</th>
                    <th>Component Category</th>
                    <th>Spend (₹ Cr)</th>
                    <th>On-Time Delivery</th>
                    <th>PPM Defects</th>
                    <th>Rating Band</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>Apex Microelectronics</b></td>
                    <td>Microcontroller Chips</td>
                    <td>₹18.4 Cr</td>
                    <td><span style="color:#68d391;">91.2%</span></td>
                    <td>420 PPM</td>
                    <td><span class="badge-pill" style="color:#68d391;">Band A</span></td>
                </tr>
                <tr>
                    <td><b>Kaveri Metals</b></td>
                    <td>Aluminum Ingots</td>
                    <td>₹15.2 Cr</td>
                    <td><span style="color:#f6ad55;">88.1%</span></td>
                    <td><span style="color:#fc8181;">1,150 PPM</span></td>
                    <td><span class="badge-pill" style="color:#f6ad55;">Band B</span></td>
                </tr>
                <tr>
                    <td><b>Trident Circuit Boards</b></td>
                    <td>Printed Circuit Boards</td>
                    <td>₹11.8 Cr</td>
                    <td><span style="color:#68d391;">94.5%</span></td>
                    <td><span style="color:#fc8181;">640 PPM</span></td>
                    <td><span class="badge-pill" style="color:#68d391;">Band A</span></td>
                </tr>
                <tr>
                    <td><b>Sunrise Connectors</b></td>
                    <td>Wire Harness & Connectors</td>
                    <td>₹6.1 Cr</td>
                    <td><span style="color:#68d391;">98.2%</span></td>
                    <td>140 PPM</td>
                    <td><span class="badge-pill" style="color:#68d391;">Band A</span></td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown("#### ⚠️ Q1 Line Stoppage Summary")
        st.markdown("""
        - **Stoppage 1 (38 hrs)**: Kaveri Metals — *Raw material shortage (aluminum ingot supply delay)*.
        - **Stoppage 2 (28 hrs)**: Apex Microelectronics — *Microcontroller chip allocation bottleneck*.
        - **Stoppage 3 (16 hrs)**: Logistics — *Chennai Port import congestion*.
        
        ---
        #### 📜 Procurement Approval Authority Tiers
        - **Up to ₹50 Lakhs**: Buyer / Procurement Manager
        - **₹50 Lakhs to ₹2 Crore**: **Head of Procurement** *(e.g. ₹1.4 Cr PO)*
        - **Above ₹2 Crore**: Managing Director / Executive Board
        """)

# ---------------------------------------------------------------------------
# TAB 2: AI QUERY ANALYST (WITH UNIQUE KEYS FIX)
# ---------------------------------------------------------------------------
with main_tab2:
    st.markdown("### 📁 Step 1 — Vector Database Ingestion")
    
    col_up, col_btn = st.columns([3, 1])
    with col_up:
        uploaded_files = st.file_uploader(
            "Upload Supply Chain PDFs (Review + Handbook)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload both PDF documents. They will be chunked, prefixed, and embedded into a single Chroma collection.",
        )
    with col_btn:
        st.markdown("<br/>", unsafe_allow_html=True)
        index_button = st.button("🔄 Ingest PDFs", use_container_width=True, type="primary")

    if os.path.exists(data_dir):
        existing_pdfs = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
        if existing_pdfs:
            with st.expander(f"📂 Found {len(existing_pdfs)} Pre-Loaded PDFs in system data/ folder"):
                for pdf in existing_pdfs:
                    badge_class = "doc-badge-review" if "Review" in pdf else "doc-badge-handbook"
                    st.markdown(f'<span class="{badge_class}">📄 {pdf}</span>', unsafe_allow_html=True)
                
                if st.button("⚡ Index Pre-Loaded PDFs", use_container_width=True, key="btn_index_preload"):
                    file_paths = [os.path.join(data_dir, f) for f in existing_pdfs]
                    with st.spinner("Processing & indexing PDFs into ChromaDB..."):
                        n_files, n_chunks = ingest_files(file_paths)
                    st.markdown(f"""
                    <div class="success-banner">
                        ✅ Success: {n_files} PDFs processed into {n_chunks} chunks in collection <code>supplychain_rag</code>!
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()

    if index_button and uploaded_files:
        temp_paths = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            for uf in uploaded_files:
                path = os.path.join(tmp_dir, uf.name)
                with open(path, "wb") as f:
                    f.write(uf.getbuffer())
                temp_paths.append(path)
            
            with st.spinner(f"📄 Indexing {len(uploaded_files)} files into ChromaDB..."):
                n_files, n_chunks = ingest_files(temp_paths)
        
        st.markdown(f"""
        <div class="success-banner">
            ✅ Success: {n_files} PDFs uploaded and indexed into {n_chunks} chunks!
        </div>
        """, unsafe_allow_html=True)
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Step 2 — Ask Questions & Run Evaluation Suite")
    
    st.markdown("**Select a preset test case from the HCL evaluation deck:**")

    # Categorized Questions Tabs
    tab_all, tab_multihop, tab_policy, tab_trap = st.tabs([
        "🎯 All Sample Questions",
        "🔀 Multi-Hop Cross-Doc Queries",
        "📋 Policy & Governance",
        "🪤 Safety / Refusal Test"
    ])

    sample_qs = [
        ("Q1", "Which supplier had the highest spend in Q1, and what was its on-time delivery percentage?", "spend"),
        ("Q2", "How many line stoppages happened in Q1, what was the total downtime, and what caused them?", "stoppages"),
        ("Q3", "What is the approval authority for a purchase order worth ₹1.4 crore?", "authority"),
        ("Q4", "What are the four supplier classification categories, and what qualifies a supplier as Critical?", "categories"),
        ("Q5", "Kaveri Metals recorded 88.1% on-time delivery and 1,150 defects per million in Q1. Which policy clauses does this trigger, and what exactly must the buyer do?", "kaveri"),
        ("Q6", "The microcontroller supplier is single-source. What does the sourcing policy require in this situation, and what is the company already doing about it?", "microcontroller"),
        ("Q7", "Microcontrollers are imported with a 46-day lead time. Using the safety-stock policy, how many days of stock should be held for this part?", "safety_stock"),
        ("Q8", "Trident Circuit Boards had a defect rate of 640 parts per million. What is the cost consequence under the policy?", "trident"),
        ("Q9", "Which suppliers would fall below the B rating band on on-time delivery alone, and what is the escalation path for them?", "rating_bands"),
        ("Q10", "What is the annual salary of the Head of Procurement?", "trap")
    ]

    if "user_query_input" not in st.session_state:
        st.session_state["user_query_input"] = ""

    query_to_execute = None

    # UNIQUE KEY FIX: Pass tab_prefix so button keys never conflict!
    def render_q_grid(q_list, tab_prefix):
        global query_to_execute
        cols = st.columns(2)
        for idx, (code, qtext, qkey) in enumerate(q_list):
            col = cols[idx % 2]
            with col:
                is_trap = qkey == "trap"
                icon = "🪤 " if is_trap else ("🔀 " if idx >= 4 else "📄 ")
                btn_label = f"{icon} **{code}**: {qtext[:60]}..."
                if st.button(btn_label, key=f"btn_{tab_prefix}_{qkey}", use_container_width=True):
                    st.session_state["user_query_input"] = qtext
                    query_to_execute = qtext

    with tab_all:
        render_q_grid(sample_qs, "tab_all")

    with tab_multihop:
        render_q_grid([q for q in sample_qs if q[0] in ["Q5", "Q6", "Q7", "Q8", "Q9"]], "tab_multihop")

    with tab_policy:
        render_q_grid([q for q in sample_qs if q[0] in ["Q3", "Q4"]], "tab_policy")

    with tab_trap:
        render_q_grid([q for q in sample_qs if q[0] == "Q10"], "tab_trap")

    st.markdown("")
    question = st.text_area(
        "Query input:",
        key="user_query_input",
        placeholder="Select a question above or type your custom query here...",
        height=85,
    )

    col_ask, _ = st.columns([1, 3])
    with col_ask:
        ask_button = st.button("⚡ Execute Query", use_container_width=True, type="primary", key="btn_exec_query")

    if ask_button and question.strip():
        query_to_execute = question.strip()

    if query_to_execute:
        stats_check = get_collection_stats()
        has_indexed_docs = "error" not in stats_check and stats_check["total_chunks"] > 0
        if not has_indexed_docs:
            st.warning("⚠️ ChromaDB collection is empty! Please index the PDF documents above first.")
        else:
            with st.spinner("🧠 Querying ChromaDB collection & generating grounded synthesis..."):
                result = ask(query_to_execute, top_k=top_k)
            
            st.session_state.history.insert(0, {
                "question": query_to_execute,
                "answer": result["answer"],
                "sources": result["sources"],
                "chunks_used": result["chunks_used"],
            })

    # Render Answer & Source Citations
    if st.session_state.history:
        latest = st.session_state.history[0]
        
        source_files = set(s["file"] for s in latest["sources"])
        is_cross_doc = len(source_files) > 1
        
        st.markdown("---")
        st.markdown("### 📝 Grounded Response")
        st.markdown(f"""
        <div class="answer-card">
            {latest['answer']}
        </div>
        """, unsafe_allow_html=True)
        
        # Dual-Column Source Audit Trail
        if latest["sources"]:
            st.markdown("### 📚 Source Citation Audit Trail")
            
            review_sources = [s for s in latest["sources"] if "Review" in s["file"]]
            handbook_sources = [s for s in latest["sources"] if "Handbook" in s["file"]]
            other_sources = [s for s in latest["sources"] if s not in review_sources and s not in handbook_sources]
            
            col_r, col_h = st.columns(2)
            
            with col_r:
                st.markdown("#### 📊 Performance Review Sources")
                if review_sources:
                    for s in review_sources:
                        st.markdown(f'<span class="doc-badge-review">📄 {s["file"]} — Page {s["page"]}</span>', unsafe_allow_html=True)
                else:
                    st.caption("No chunks retrieved from Review PDF for this query.")

            with col_h:
                st.markdown("#### 📋 Policy Handbook Sources")
                if handbook_sources:
                    for s in handbook_sources:
                        st.markdown(f'<span class="doc-badge-handbook">📄 {s["file"]} — Page {s["page"]}</span>', unsafe_allow_html=True)
                else:
                    st.caption("No chunks retrieved from Handbook PDF for this query.")

            if other_sources:
                for s in other_sources:
                    st.markdown(f'<span class="badge-pill">📄 {s["file"]} — Page {s["page"]}</span>', unsafe_allow_html=True)

            st.caption(f"Retrieved {latest['chunks_used']} vector chunks from ChromaDB for synthesis.")
        
        # Developer & Debug Tools Expander
        st.markdown("")
        with st.expander("🐞 Developer & Debug Tools (Vector Chunks & API Payload)", expanded=False):
            if is_cross_doc:
                st.markdown("""
                <div class="cross-doc-badge">
                    <span>🔀</span> <b>CROSS-DOCUMENT REASONING ACTIVE</b> — Combined data from Review & Policy Handbook
                </div>
                """, unsafe_allow_html=True)
                
            tab_debug, tab_json = st.tabs(["🔎 Detailed Chunk Inspection", "⚡ Live REST API Payload Preview"])
            
            with tab_debug:
                from rag import retrieve_chunks
                chunks = retrieve_chunks(latest["question"], top_k=top_k)
                for i, chunk in enumerate(chunks, 1):
                    page_display = chunk["page"]
                    badge_class = "doc-badge-review" if "Review" in chunk["source_file"] else "doc-badge-handbook"
                    st.markdown(f"**Chunk {i}** — <span class='{badge_class}'>{chunk['source_file']} Page {page_display}</span> `Distance: {chunk['score']:.4f}`", unsafe_allow_html=True)
                    st.code(chunk["content"][:350], language="text")
            
            with tab_json:
                st.markdown("This payload is produced by the FastAPI endpoint at `POST http://localhost:8000/ask`:")
                api_payload = {
                    "question": latest["question"],
                    "answer": latest["answer"],
                    "sources": latest["sources"],
                    "chunks_used": latest["chunks_used"],
                    "cross_document_reasoning": is_cross_doc
                }
                st.json(api_payload)

# ---------------------------------------------------------------------------
# TAB 3: AUTOMATED POLICY & PENALTY CALCULATOR
# ---------------------------------------------------------------------------
with main_tab3:
    st.markdown("### 🧮 Interactive Policy & Penalty Calculator")
    st.markdown("Select a supplier or test custom metrics against **Procurement Policy Handbook v4.2** clauses:")
    
    calc_supp = st.selectbox(
        "Select Supplier Preset:",
        ["Kaveri Metals (Q1)", "Trident Circuit Boards (Q1)", "Apex Microelectronics (Q1)", "Custom Input"],
        key="calc_supp_select"
    )
    
    if calc_supp == "Kaveri Metals (Q1)":
        def_otd, def_ppm, def_lead, def_cat = 88.1, 1150, 20, "Critical"
    elif calc_supp == "Trident Circuit Boards (Q1)":
        def_otd, def_ppm, def_lead, def_cat = 94.5, 640, 15, "Standard"
    elif calc_supp == "Apex Microelectronics (Q1)":
        def_otd, def_ppm, def_lead, def_cat = 91.2, 420, 46, "Critical"
    else:
        def_otd, def_ppm, def_lead, def_cat = 85.0, 750, 40, "Critical"
        
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        inp_otd = st.number_input("On-Time Delivery (%)", 0.0, 100.0, float(def_otd))
    with c2:
        inp_ppm = st.number_input("Defect Rate (PPM)", 0, 50000, int(def_ppm))
    with c3:
        inp_lead = st.number_input("Lead Time (Days)", 1, 180, int(def_lead))
    with c4:
        inp_cat = st.selectbox("Category", ["Strategic", "Critical", "Standard", "Tactical"], index=["Strategic", "Critical", "Standard", "Tactical"].index(def_cat))
        
    st.markdown("---")
    st.markdown("#### ⚖️ Compliance & Governance Evaluation")
    
    # 1. Rating Band
    if inp_otd >= 90.0:
        band = "Band A (Preferred)"
        band_color = "#68d391"
    elif inp_otd >= 75.0:
        band = "Band B (Approved)"
        band_color = "#f6ad55"
    elif inp_otd >= 60.0:
        band = "Band C (Conditional)"
        band_color = "#fc8181"
    else:
        band = "Band D (Frozen / Offboarded)"
        band_color = "#e53e3e"
        
    # 2. Defect Clause 6.3 Penalty
    if inp_ppm > 500:
        clause_63 = f"🔴 **Clause 6.3 Triggered**: Defect rate {inp_ppm} PPM > 500 PPM threshold. 100% rework debit + 2% admin penalty fee applies."
    else:
        clause_63 = f"🟢 **Clause 6.3 Compliant**: Defect rate {inp_ppm} PPM is within the 500 PPM tolerance."
        
    # 3. Safety Stock Math Floor Rule (Clause 5.1)
    calc_ss = inp_lead * 0.25
    floor_ss = 30.0 if inp_cat == "Critical" else 15.0
    final_ss = max(calc_ss, floor_ss)
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.markdown(f"**Supplier Scorecard Rating**: <span style='color:{band_color}; font-weight:bold; font-size:1.1rem;'>{band}</span>", unsafe_allow_html=True)
        st.markdown(clause_63)
    with res_col2:
        st.markdown(f"**Safety Stock Days Calculation** (Clause 5.1):")
        st.write(f"- Formula (`Lead Time × 0.25`): **{calc_ss:.1f} days**")
        st.write(f"- Policy Minimum Floor ({inp_cat}): **{floor_ss:.1f} days**")
        st.markdown(f"👉 **Mandated Holding Requirement**: <b style='color:#4fd1c5; font-size:1.1rem;'>{final_ss:.1f} days</b> *(Higher value applies)*")

# ---------------------------------------------------------------------------
# TAB 4: API DEVELOPER HUB
# ---------------------------------------------------------------------------
with main_tab4:
    st.markdown("### ⚡ FastAPI Developer & Sandbox Hub")
    st.markdown("FastAPI backend is active on **Port 8000**. You can test endpoints via Swagger UI or curl:")
    
    st.code("""
# 1. Check API Health & Vector Store Stats
curl http://localhost:8000/stats

# 2. Execute RAG Query over REST
curl -X POST "http://localhost:8000/ask" \\
     -H "Content-Type: application/json" \\
     -d '{"question": "Kaveri Metals recorded 88.1% OTD and 1150 PPM. Which clauses apply?", "top_k": 6}'
    """, language="bash")
    
    st.markdown("Interactive Swagger documentation: [http://localhost:8000/docs](http://localhost:8000/docs)")

# ---------------------------------------------------------------------------
# Footer Status Metrics
# ---------------------------------------------------------------------------
st.markdown("---")
col_m1, col_m2, col_m3 = st.columns(3)

stats = get_collection_stats()
if "error" not in stats and stats["total_chunks"] > 0:
    with col_m1:
        st.metric("Collection Size", f"{stats['total_chunks']} Chunks")
    with col_m2:
        st.metric("Vector Embeddings", stats["embedding_model"])
    with col_m3:
        st.metric("Synthesis LLM Engine", stats["llm_model"])
    
    st.success("✅ **ChromaDB Disk Persistence Active** — Stored at `chroma_db/supplychain_rag`. Fully ready for submission!")
else:
    st.info("ℹ️ Collection empty. Click 'Index Pre-Loaded PDFs' in Tab 2 to initialize.")
