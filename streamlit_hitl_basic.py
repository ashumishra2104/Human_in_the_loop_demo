import streamlit as st
import graphviz
import time
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


# Set page config
st.set_page_config(layout="wide", page_title="HITL Workflow Basic Demo")

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #cce5ff;
        color: #004085;
        border: 1px solid #b8daff;
    }
</style>
""", unsafe_allow_html=True)

# Application State Management
if 'step' not in st.session_state:
    st.session_state.step = 1 # 1: Input, 2: Permission, 4: Answer
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'decision' not in st.session_state:
    st.session_state.decision = None

def reset_app():
    st.session_state.step = 1
    st.session_state.query = ""
    st.session_state.decision = None

# --- Visualization Logic ---
def get_flowchart(current_step, decision=None):
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB')
    graph.attr('node', shape='box', style='filled', fillcolor='white', fontname='Helvetica')
    
    # Node 1: User Input
    c1 = 'lightblue' if current_step == 1 else 'white'
    if current_step > 1: c1 = 'lightgrey'
    graph.node('1', 'Step 1\nSearch Query', fillcolor=c1)
    
    # Node 2: Permission Request
    c2 = 'lightblue' if current_step == 2 else 'white'
    if current_step > 2: c2 = 'lightgrey'
    graph.node('2', 'Step 2\n"Do you want to proceed?"', fillcolor=c2)
    
    # Decisions
    
    # Node 3a: Denied
    c3a = 'white'
    if current_step == 4 and decision == 'no':
        c3a = '#ffcccc' # Red-ish
    graph.node('3a', 'Step 3 (No)\nPermission Denied', fillcolor=c3a)
    
    # Node 3b: Approved -> leads to Step 4
    c3b = 'white'
    if current_step == 4 and decision == 'yes':
        c3b = 'lightgrey' # Passed through
    graph.node('3b', 'Step 3 (Yes)\nPermission Granted', fillcolor=c3b)
    
    # Node 4: Model Answer
    c4 = 'white'
    if current_step == 4 and decision == 'yes':
        c4 = 'lightgreen'
    graph.node('4', 'Step 4\nModel Answer & Action', fillcolor=c4)

    # Edges
    graph.edge('1', '2')
    graph.edge('2', '3a', label=' No')
    graph.edge('2', '3b', label=' Yes')
    graph.edge('3b', '4')
    
    return graph

# --- Main Layout ---
st.title("Human-in-the-Loop Basic Demo")
st.markdown("### A basic tutorial on how HITL interrupts work in AI agents")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Interaction Panel")
    
    # STEP 1: Search Query
    if st.session_state.step == 1:
        st.info("👋 Welcome! Please enter a query to start the demo agent.")
        with st.form("query_form"):
            query_input = st.text_input("Enter your search query:", placeholder="e.g., Run analysis on dataset")
            submitted = st.form_submit_button("Submit Query")
            
            if submitted and query_input:
                st.session_state.query = query_input
                st.session_state.step = 2
                st.rerun()

    # STEP 2: Permission
    elif st.session_state.step == 2:
        st.markdown(f"**User Query:** {st.session_state.query}")
        st.warning("⚠️ **INTERRUPT:** The agent requests permission to execute an action.")
        st.markdown("### Do you want to proceed?")
        
        c_yes, c_no = st.columns(2)
        if c_yes.button("✅ Yes, Proceed"):
            st.session_state.decision = "yes"
            st.session_state.step = 4 # Jump to result
            st.rerun()
            
        if c_no.button("❌ No, Stop"):
            st.session_state.decision = "no"
            st.session_state.step = 4 # Jump to result (denied)
            st.rerun()

    # STEP 4: Result
    elif st.session_state.step == 4:
        st.markdown(f"**User Query:** {st.session_state.query}")
        
        if st.session_state.decision == 'yes':
            st.markdown('<div class="success-box">✅ <strong>Step 3: Permission Granted</strong></div>', unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("🤖 Step 4: Model Answer")
            
            with st.spinner("Generating response from OpenAI..."):
                try:
                    # Initialize LLM
                    llm = ChatOpenAI(temperature=0.7)
                    # Get response
                    response = llm.invoke(st.session_state.query)
                    content = response.content
                except Exception as e:
                    content = f"Error communicating with OpenAI: {e}"
            
            st.markdown(f"""
            **Action Status:** Executed Successfully
            
            **Agent Response:**
            {content}
            
            **Technical Details:**
            - **Timestamp:** {time.strftime("%H:%M:%S")}
            - **Loop Status:** Closed
            """)
            
        else:
            st.markdown('<div class="error-box">🛑 <strong>Step 3: Permission Denied</strong><br>The loop was terminated by the user. NO action was taken.</div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Start Over"):
            reset_app()
            st.rerun()

with col2:
    st.subheader("State Visualization")
    st.caption("Visualizing the current step in the Agent's execution flow.")
    
    # Render the graph
    viz_graph = get_flowchart(st.session_state.step, st.session_state.decision)
    st.graphviz_chart(viz_graph, use_container_width=True) # or width="stretch" if warning persists
