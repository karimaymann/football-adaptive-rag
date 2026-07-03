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
        padding: 16px;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .logs-container pre {
        color: #111111 !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        margin: 0 !important;
        background: transparent !important;
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

# Helper: render the log text into the diagnostics placeholder
def render_logs(placeholder, log_text: str):
    if not log_text.strip():
        placeholder.markdown(
            '<div class="logs-container"><pre style="color: #6c757d;">'
            '🔄 Waiting for query submission to trace execution path...'
            '</pre></div>',
            unsafe_allow_html=True
        )
    else:
        import html as html_module
        safe_text = html_module.escape(log_text)
        placeholder.markdown(
            f'<div class="logs-container"><pre>{safe_text}</pre></div>',
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
