import streamlit as st
import time
import sys
import io
import os
from dotenv import load_dotenv

# Set page config FIRST, before any other streamlit commands
st.set_page_config(
    page_title="⚽ Pitch-Side Intel: Tactical Rules & News AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Import the compiled LangGraph app instance
try:
    from graph.graph import app
except Exception as e:
    st.error(f"Failed to import LangGraph application: {e}")
    st.stop()

# -------------------------------------------------------------
# CUSTOM CSS STYLE INJECTION (Modern Light Football Analytics)
# -------------------------------------------------------------
st.markdown("""
<style>
    /* Main body background */
    .stApp {
        background: linear-gradient(135deg, #FFFFFF 0%, #F4F6F4 100%) !important;
        color: #111111 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
        font-weight: 700 !important;
    }
    
    /* Custom section header with green accent */
    .section-header {
        border-bottom: 2px solid #2E7D32;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.4rem;
        font-weight: 600;
        color: #111111;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Green badges or status indicators */
    .neon-badge {
        background-color: rgba(46, 125, 50, 0.08);
        border: 1px solid #2E7D32;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
    }
    
    /* Chat message container custom borders and backgrounds */
    [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        background-color: #FFFFFF !important;
        border: 1px solid #DEE2E6 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: #111111 !important;
    }
    
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div, [data-testid="stChatMessage"] span {
        color: #111111 !important;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08) !important;
    }
    
    /* Style Chat Input Box */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    
    [data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #CED4DA !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stChatInput"] textarea:focus {
        border-color: #2E7D32 !important;
        box-shadow: 0 0 10px rgba(46, 125, 50, 0.15) !important;
    }
    
    /* Logs panel styling */
    .logs-container {
        background: #FFFFFF;
        border: 1px solid #DEE2E6;
        border-radius: 12px;
        padding: 16px 20px;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 0.8rem;
        line-height: 1.7;
    }
    
    .log-line {
        padding: 2px 0;
    }
    
    .log-separator {
        color: #CED4DA;
        font-weight: 600;
        padding: 6px 0 2px 0;
    }
    
    .log-prompt {
        color: #111111;
        font-weight: 700;
        padding: 0 0 6px 0;
    }
    
    .log-node {
        background: rgba(46, 125, 50, 0.08);
        color: #2E7D32;
        font-weight: 700;
        padding: 6px 10px;
        margin: 6px 0 2px 0;
        border-left: 3px solid #2E7D32;
        border-radius: 0 6px 6px 0;
    }
    
    .log-route {
        color: #1565C0;
        font-weight: 600;
        padding: 2px 0 2px 12px;
    }
    
    .log-pass {
        color: #2E7D32;
        font-weight: 600;
        padding: 2px 0 2px 12px;
    }
    
    .log-fail {
        color: #C62828;
        font-weight: 600;
        padding: 2px 0 2px 12px;
    }
    
    .log-detail {
        color: #555555;
        padding: 2px 0 2px 12px;
    }
    
    .log-sql {
        background: #F5F5F5;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0 4px 12px;
        color: #37474F;
        font-size: 0.75rem;
        word-break: break-all;
    }
    
    .log-finished {
        color: #6C757D;
        font-style: italic;
        padding: 2px 0 2px 0;
        border-bottom: 1px solid #F0F0F0;
        margin-bottom: 4px;
    }
    
    .log-error {
        color: #C62828;
        font-weight: 700;
        background: rgba(198, 40, 40, 0.06);
        padding: 6px 10px;
        border-left: 3px solid #C62828;
        border-radius: 0 6px 6px 0;
        margin: 4px 0;
    }
    
    .log-cooldown {
        color: #9E9E9E;
        font-size: 0.72rem;
        padding: 1px 0 1px 20px;
    }
    
    .logs-container::-webkit-scrollbar {
        width: 6px;
    }
    .logs-container::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.03);
    }
    .logs-container::-webkit-scrollbar-thumb {
        background: #CED4DA;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "log_output" not in st.session_state:
    st.session_state.log_output = ""

# -------------------------------------------------------------
# APPLICATION HEADER
# -------------------------------------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding: 15px 20px; background: #FFFFFF; border: 1px solid #DEE2E6; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
    <div>
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #111111 0%, #2E7D32 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 10px;">
            ⚽ PITCH-SIDE INTEL
        </h1>
        <p style="margin: 5px 0 0 0; color: #495057; font-size: 0.95rem; font-weight: 500;">
            Advanced Tactical Rules Analyst & News AI • LangGraph Adaptive RAG Engine
        </p>
    </div>
    <div style="text-align: right;">
        <span class="neon-badge">Tactical Analytics Mode</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# DUAL-COLUMN LAYOUT
# -------------------------------------------------------------
col1, col2 = st.columns([3, 2])

# Helper: capture stdout from graph nodes into a string
class StreamCapture(io.StringIO):
    """Tee that writes to both StringIO buffer and original stdout."""
    def __init__(self, original_stdout):
        super().__init__()
        self._original = original_stdout
    def write(self, s):
        self._original.write(s)
        super().write(s)
    def flush(self):
        self._original.flush()
        super().flush()

# Helper: render the log text into the diagnostics placeholder with styling
def render_logs(placeholder, log_text: str):
    if not log_text.strip():
        placeholder.markdown(
            '<div class="logs-container" style="text-align: center; padding: 40px 20px; color: #9E9E9E;">'
            '🔄 Waiting for query submission to trace execution path...'
            '</div>',
            unsafe_allow_html=True
        )
        return
    
    import html as html_module
    lines = log_text.split('\n')
    html_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        safe = html_module.escape(stripped)
        
        # Classify each line by its content pattern
        if stripped.startswith('====='):
            html_lines.append(f'<div class="log-separator">{safe}</div>')
        elif stripped.startswith('USER PROMPT:'):
            html_lines.append(f'<div class="log-prompt">{safe}</div>')
        elif stripped.startswith('---NODE:'):
            html_lines.append(f'<div class="log-node">{safe}</div>')
        elif stripped.startswith('--- ROUTING') or stripped.startswith('--- ASSESSING') or stripped.startswith('--- CRITIC:'):
            html_lines.append(f'<div class="log-node">{safe}</div>')
        elif '-> ROUTE DECISION:' in stripped:
            html_lines.append(f'<div class="log-route">→ {html_module.escape(stripped.split("ROUTE DECISION:")[1].strip())}</div>')
        elif '-> DECISION:' in stripped:
            html_lines.append(f'<div class="log-route">→ {html_module.escape(stripped.split("DECISION:")[1].strip())}</div>')
        elif 'CRITIC PASS:' in stripped:
            html_lines.append(f'<div class="log-pass">✓ {html_module.escape(stripped.split("CRITIC PASS:")[1].strip())}</div>')
        elif 'CRITIC FAIL:' in stripped:
            html_lines.append(f'<div class="log-fail">✗ {html_module.escape(stripped.split("CRITIC FAIL:")[1].strip())}</div>')
        elif '-> Generated SQL Command:' in stripped:
            sql = html_module.escape(stripped.split('Generated SQL Command:')[1].strip())
            html_lines.append(f'<div class="log-detail">→ Generated SQL Command:</div>')
            html_lines.append(f'<div class="log-sql">{sql}</div>')
        elif 'DOCUMENT RELEVANT' in stripped or 'DOCUMENT NOT RELEVANT' in stripped:
            if 'NOT RELEVANT' in stripped:
                html_lines.append(f'<div class="log-fail">✗ DOCUMENT NOT RELEVANT</div>')
            else:
                html_lines.append(f'<div class="log-pass">✓ DOCUMENT RELEVANT</div>')
        elif 'Finished running Node:' in stripped:
            html_lines.append(f'<div class="log-finished">{safe}</div>')
        elif 'ERROR' in stripped or '⚠️' in stripped:
            html_lines.append(f'<div class="log-error">{safe}</div>')
        elif 'Cooling down' in stripped or '...Cool' in stripped:
            html_lines.append(f'<div class="log-cooldown">{safe}</div>')
        elif stripped.startswith('-> Retrieved') or stripped.startswith('-> Doc') or stripped.startswith('Preview:') or stripped.startswith('-> Saved'):
            html_lines.append(f'<div class="log-detail">{safe}</div>')
        else:
            html_lines.append(f'<div class="log-detail">{safe}</div>')
    
    content = '\n'.join(html_lines)
    placeholder.markdown(
        f'<div class="logs-container">{content}</div>',
        unsafe_allow_html=True
    )

# -------------------------------------------------------------
# COLUMN 1: CONVERSATIONAL INTERFACE
# -------------------------------------------------------------
with col1:
    st.markdown('<div class="section-header">💬 Match-Day Chat Feed</div>', unsafe_allow_html=True)
    
    # Render all message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# -------------------------------------------------------------
# COLUMN 2: EXECUTION LOGS
# -------------------------------------------------------------
with col2:
    st.markdown('<div class="section-header">📊 Execution Logs</div>', unsafe_allow_html=True)
    diagnostics_placeholder = st.empty()
    render_logs(diagnostics_placeholder, st.session_state.log_output)

# -------------------------------------------------------------
# CHAT INPUT & EXECUTION LOOP
# -------------------------------------------------------------
if prompt := st.chat_input("Ask about game rules, yellow/red cards, tactical updates, or news..."):
    # 1. Append and render user query in chat column
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col1:
        with st.chat_message("user"):
            st.markdown(prompt)
            
    # 2. Reset log output and show the separator header
    st.session_state.log_output = f"=================================================="
    st.session_state.log_output += f"\nUSER PROMPT: {prompt}"
    st.session_state.log_output += f"\n==================================================\n"
    with col2:
        render_logs(diagnostics_placeholder, st.session_state.log_output)
        
    # Variables to collect execution results
    final_answer = None
    execution_success = False
    
    # 3. Stream graph execution, capturing all print() output from nodes
    capturer = StreamCapture(sys.stdout)
    sys.stdout = capturer
    
    try:
        inputs = {"question": prompt}
        config = {"recursion_limit": 15}
        
        for event in app.stream(inputs, config=config, stream_mode="updates"):
            for node_name, state_update in event.items():
                # Grab the generation for the final answer
                if node_name == "generate":
                    final_answer = state_update.get("generation", "")
                
                # Append the "Finished running Node" line
                print(f"\nFinished running Node: [{node_name}]")
                
                # Update the logs panel live
                st.session_state.log_output = capturer.getvalue()
                with col2:
                    render_logs(diagnostics_placeholder, st.session_state.log_output)
                
                time.sleep(0.3)
        
        execution_success = True
        
    except Exception as e:
        error_msg = str(e)
        is_429 = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "rate limit" in error_msg.lower()
        print(f"\n⚠️ ERROR: {error_msg}")
        
        # Update logs with the error
        st.session_state.log_output = capturer.getvalue()
        with col2:
            render_logs(diagnostics_placeholder, st.session_state.log_output)
            
        with col1:
            if is_429:
                st.error("""
                ⚠️ **Gemini API Quota Exceeded (429 Resource Exhausted)**
                
                The free-tier Gemini API is limited to 5 requests per minute.
                Please wait roughly **15 to 30 seconds** for the rate-limiting window to clear, then try again.
                """)
            else:
                st.error(f"⚠️ **Adaptive RAG Error**: {error_msg}")
    finally:
        # Always restore stdout
        sys.stdout = capturer._original
        st.session_state.log_output = capturer.getvalue()
        with col2:
            render_logs(diagnostics_placeholder, st.session_state.log_output)
                
    # 4. Stream response chunk-by-chunk using st.write_stream
    if execution_success:
        with col1:
            with st.chat_message("assistant"):
                def typewriter_streamer(text: str):
                    words = text.split(" ")
                    for i, word in enumerate(words):
                        yield word + (" " if i < len(words) - 1 else "")
                        time.sleep(0.02)
                
                if final_answer:
                    response_content = st.write_stream(typewriter_streamer(final_answer))
                else:
                    response_content = st.write_stream(typewriter_streamer("The query execution completed, but no final answer could be generated."))
                
        st.session_state.messages.append({"role": "assistant", "content": response_content})
