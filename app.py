import streamlit as st
import graphviz
import time
import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command

# Import the graphs
# We use try/except to avoid errors if dependencies are missing during initial setup, 
# ensuring the app shell still loads.
try:
    from chatbot_without_hitl import chatbot as chatbot_no_hitl
    from chatbot_with_hitl import chatbot as chatbot_hitl
except ImportError as e:
    st.error(f"Failed to import chatbots: {e}")

load_dotenv()

# --- Configurations ---
st.set_page_config(
    layout="wide", 
    page_title="Human-in-the-Loop AI Dashboard",
    page_icon="🤖"
)

# Custom CSS for the Dashboard
st.markdown("""
<style>
    /* Card Styles for Home Page */
    .card {
        background-color: #f9f9f9;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #007bff;
    }
    .card h3 {
        margin-bottom: 1rem;
        color: #333;
    }
    .card p {
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Button Styles */
    div.stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Chat Message Styling Enhancements */
    /* (Streamlit's default is usually fine, but we can tweak if needed) */
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'

# --- Navigation Helpers ---
def navigate_to(view_name):
    st.session_state.current_view = view_name
    st.rerun()

# ==============================================================================
# VIEW: HOME
# ==============================================================================
def render_home():
    st.title("Human-in-the-Loop (HITL) Basic Demo")
    st.markdown("### Explore different levels of AI Agent autonomy and control.")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>Demo 1: The Concept</h3>
            <p>A basic, visual tutorial identifying the step-by-step flow of how HITL interrupts work in AI agents.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Demo 1"):
            navigate_to('demo1')

    with col2:
        st.markdown("""
        <div class="card">
            <h3>Demo 2: Fully Autonomous</h3>
            <p>A Stock Chatbot that executes tools immediately without asking for permission. <br>(Fast but Risky)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Demo 2"):
            navigate_to('demo2')

    with col3:
        st.markdown("""
        <div class="card">
            <h3>Demo 3: Human-in-the-Loop</h3>
            <p>A Stock Chatbot that pauses and asks for approval before executing sensitive actions. <br>(Safe & Controlled)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Demo 3"):
            navigate_to('demo3')


# ==============================================================================
# VIEW: DEMO 1 (Basic Logic Flow)
# ==============================================================================
def render_demo1():
    st.button("← Back to Home", on_click=lambda: navigate_to('home'))
    st.title("Demo 1: HITL Workflow Concept")
    
    # --- Local State for Demo 1 ---
    if 'd1_step' not in st.session_state:
        st.session_state.d1_step = 1
    if 'd1_query' not in st.session_state:
        st.session_state.d1_query = ""
    if 'd1_decision' not in st.session_state:
        st.session_state.d1_decision = None
        
    def reset_d1():
        st.session_state.d1_step = 1
        st.session_state.d1_query = ""
        st.session_state.d1_decision = None

    # Visualization Helpers
    def get_flowchart(current_step, decision=None):
        graph = graphviz.Digraph()
        graph.attr(rankdir='TB')
        graph.attr('node', shape='box', style='filled', fillcolor='white', fontname='Helvetica')
        
        c1 = 'lightblue' if current_step == 1 else 'lightgrey' if current_step > 1 else 'white'
        graph.node('1', 'Step 1\nSearch Query', fillcolor=c1)
        
        c2 = 'lightblue' if current_step == 2 else 'lightgrey' if current_step > 2 else 'white'
        graph.node('2', 'Step 2\n"Do you want to proceed?"', fillcolor=c2)
        
        c3a = '#ffcccc' if current_step == 4 and decision == 'no' else 'white'
        graph.node('3a', 'Step 3 (No)\nPermission Denied', fillcolor=c3a)
        
        c3b = 'lightgrey' if current_step == 4 and decision == 'yes' else 'white'
        graph.node('3b', 'Step 3 (Yes)\nPermission Granted', fillcolor=c3b)
        
        c4 = 'lightgreen' if current_step == 4 and decision == 'yes' else 'white'
        graph.node('4', 'Step 4\nModel Answer & Action', fillcolor=c4)

        graph.edge('1', '2')
        graph.edge('2', '3a', label=' No')
        graph.edge('2', '3b', label=' Yes')
        graph.edge('3b', '4')
        return graph

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Interaction Panel")
        if st.session_state.d1_step == 1:
            st.info("👋 Welcome! Please enter a query to start the demo agent.")
            with st.form("d1_form"):
                q = st.text_input("Enter your search query:", placeholder="e.g., Run analysis")
                if st.form_submit_button("Submit"):
                    st.session_state.d1_query = q
                    st.session_state.d1_step = 2
                    st.rerun()

        elif st.session_state.d1_step == 2:
            st.markdown(f"**User Query:** {st.session_state.d1_query}")
            st.warning("⚠️ **INTERRUPT:** Agent requests permission.")
            c_yes, c_no = st.columns(2)
            if c_yes.button("✅ Yes, Proceed"):
                st.session_state.d1_decision = 'yes'
                st.session_state.d1_step = 4
                st.rerun()
            if c_no.button("❌ No, Stop"):
                st.session_state.d1_decision = 'no'
                st.session_state.d1_step = 4
                st.rerun()

        elif st.session_state.d1_step == 4:
            if st.session_state.d1_decision == 'yes':
                st.success("Permission Granted.")
                st.subheader("bot response:")
                with st.spinner("Generating..."):
                    try:
                        llm = ChatOpenAI(temperature=0.7)
                        res = llm.invoke(st.session_state.d1_query)
                        content = res.content
                    except Exception as e:
                        content = f"Error: {e}"
                st.write(content)
            else:
                st.error("Permission Denied. No Action Taken.")
            
            if st.button("Start Over"):
                reset_d1()
                st.rerun()

    with col2:
        st.subheader("Flow Visualization")
        st.graphviz_chart(get_flowchart(st.session_state.d1_step, st.session_state.d1_decision), use_container_width=True)


# ==============================================================================
# VIEW: DEMO 2 (NO HITL CHATBOT)
# ==============================================================================
def render_demo2():
    st.button("← Back to Home", on_click=lambda: navigate_to('home'))
    st.title("Demo 2: Fully Autonomous Agent")
    st.caption("This agent has tools to 'get_stock_price' and 'purchase_stock'. It will execute purchases IMMEDIATELY without asking.")
    st.markdown("---")

    if 'd2_messages' not in st.session_state:
        st.session_state.d2_messages = []
    if 'd2_thread_id' not in st.session_state:
        st.session_state.d2_thread_id = str(uuid.uuid4())

    # Display Chat History
    for msg in st.session_state.d2_messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # Input
    if prompt := st.chat_input("Ask me to buy a stock..."):
        # Add user message
        user_msg = HumanMessage(content=prompt)
        st.session_state.d2_messages.append(user_msg)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Run Graph
        with st.chat_message("assistant"):
            with st.spinner("Thinking & Acting..."):
                config = {"configurable": {"thread_id": st.session_state.d2_thread_id}}
                # We need to construct the state correctly
                # LangGraph expects a dict with 'messages'
                response = chatbot_no_hitl.invoke({"messages": [user_msg]}, config=config)
                
                # The response 'messages' contains the full history or updates. 
                # We usually want the LAST message.
                # However, since we are managing history locally in 'd2_messages' for display,
                # we should update our local history with the NEW messages returned by the graph.
                
                # Actually, the graph returns the *state*. `messages` in state might be the full list or diff depending on reducer.
                # standard ChatState usually accumulates.
                
                new_messages = response['messages']
                # Determine which ones are new.
                # Simple logic: assume we just get the new ones if we passed only the user msg? 
                # No, MemorySaver persists. The result['messages'] is usually the FULL history if add_messages is used.
                
                # Let's just grab the last message content to display, 
                # BUT for proper chat UI, we should probably just sync our view with the full graph state.
                
                # Syncing:
                st.session_state.d2_messages = new_messages
                
                # Display the last response
                last_msg = new_messages[-1]
                st.markdown(last_msg.content)


# ==============================================================================
# VIEW: DEMO 3 (WITH HITL CHATBOT)
# ==============================================================================
def render_demo3():
    st.button("← Back to Home", on_click=lambda: navigate_to('home'))
    st.title("Demo 3: Human-in-the-Loop Agent")
    st.caption("This agent INTERRUPTS before 'purchase_stock'. You must approve or reject.")
    st.markdown("---")

    if 'd3_messages' not in st.session_state:
        st.session_state.d3_messages = []
    if 'd3_thread_id' not in st.session_state:
        st.session_state.d3_thread_id = str(uuid.uuid4())

    # --- RENDER HISTORY ---
    # We always render the full history stored in session state
    for msg in st.session_state.d3_messages:
        # We process Human, AI.
        # ToolMessages usually shouldn't be main chat bubbles, but for debugging/demo it's fine.
        if isinstance(msg, HumanMessage):
             with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
             with st.chat_message("assistant"):
                st.markdown(msg.content)
        # elif isinstance(msg, ToolMessage):
        #      # Optional: Show tool outputs in expando
        #      with st.expander(f"Tool: {msg.name}"):
        #          st.code(msg.content)

    # --- CHECK FOR INTERRUPTS (Pending Action) ---
    config = {"configurable": {"thread_id": st.session_state.d3_thread_id}}
    
    # We inspect the CURRENT state of the graph to see if it is interrupted.
    current_state = chatbot_hitl.get_state(config)
    
    if current_state.next:
        # If there is a 'next' step, check if it's an interrupt
        # In LangGraph, tasks are interrupted if we are paused.
        # We can look at the 'tasks' text or interrupt info.
        # The easiest way with `interrupt()` tool usage is checking the `tasks` tuple or `tasks[0].interrupts`
        if current_state.tasks and current_state.tasks[0].interrupts:
            interrupt_value = current_state.tasks[0].interrupts[0].value
            
            with st.chat_message("assistant"):
                st.warning(f"🛑 **APPROVAL REQUIRED:** {interrupt_value}")
                col_y, col_n = st.columns(2)
                
                if col_y.button("👍 Approve"):
                    # Resume with logic
                    with st.spinner("Resuming..."):
                        res = chatbot_hitl.invoke(Command(resume="yes"), config=config)
                        st.session_state.d3_messages = res['messages']
                        st.rerun()

                if col_n.button("👎 Reject"):
                    # Resume with logic
                    with st.spinner("Resuming..."):
                        res = chatbot_hitl.invoke(Command(resume="no"), config=config)
                        st.session_state.d3_messages = res['messages']
                        st.rerun()
            return # Stop rendering input if we are waiting for user
            

    # --- NORMAL CHAT INPUT ---
    # Only show if NOT interrupted
    if prompt := st.chat_input("Ask to buy AAPL..."):
        # Add to local view temporarily
        st.session_state.d3_messages.append(HumanMessage(content=prompt))
        st.rerun() # Force rerun to render message then process

    # PROCESSING LOGIC (After rerun)
    # If the last message is Human and we are NOT in an interrupt state, we invoke.
    if st.session_state.d3_messages and isinstance(st.session_state.d3_messages[-1], HumanMessage):
        # We need to verify if this message has already been processed by the graph.
        # Compare length or IDs. 
        # A simpler way: The graph state IS the source of truth.
        # If `current_state` messages count < session_state messages count, we need to push.
        
        # Let's simplify:
        # 1. User inputs -> set `d3_input_pending` = prompt
        # 2. Rerun
        # 3. Detect pending input -> invoke graph
        
        # Actually, let's use the standard pattern:
        pass


# Re-implementing Demo 3 logic to be more robust with Streamlit's loop
# We'll use a specific key for 'processing'
if 'd3_pending_input' not in st.session_state:
    st.session_state.d3_pending_input = None

def demo3_process_logic():
    # If we have a pending input, send it to graph
    if st.session_state.d3_pending_input:
        user_text = st.session_state.d3_pending_input
        st.session_state.d3_pending_input = None # clear it
        
        config = {"configurable": {"thread_id": st.session_state.d3_thread_id}}
        
        with st.spinner("Agent processing..."):
             # Invoke with new message
             res = chatbot_hitl.invoke({"messages": [HumanMessage(content=user_text)]}, config=config)
             # Update history
             st.session_state.d3_messages = res['messages']
             st.rerun()

# Hook into Render Demo 3 for the input
# We override the input block in render_demo3 to just set pending_input
def render_demo3_fixed():
    st.button("← Back to Home", on_click=lambda: navigate_to('home'))
    st.title("Demo 3: Human-in-the-Loop Agent")
    st.markdown("---")

    if 'd3_messages' not in st.session_state:
        st.session_state.d3_messages = []
    if 'd3_thread_id' not in st.session_state:
        st.session_state.d3_thread_id = str(uuid.uuid4())

    # 1. Show History
    for msg in st.session_state.d3_messages:
        if isinstance(msg, HumanMessage):
             with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
             with st.chat_message("assistant"):
                st.markdown(msg.content)

    # 2. Check Interrupts
    config = {"configurable": {"thread_id": st.session_state.d3_thread_id}}
    state = chatbot_hitl.get_state(config)
    
    is_interrupted = False
    if state.next:
        # Check for interrupt
        if state.tasks and state.tasks[0].interrupts:
            is_interrupted = True
            intr = state.tasks[0].interrupts[0].value
            with st.chat_message("assistant"):
                st.warning(f"🛑 **APPROVAL NEEDED:** {intr}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve"):
                    with st.spinner("Resuming..."):
                        res = chatbot_hitl.invoke(Command(resume="yes"), config=config)
                        st.session_state.d3_messages = res['messages']
                        st.rerun()
                if c2.button("❌ Reject"):
                    with st.spinner("Resuming..."):
                        res = chatbot_hitl.invoke(Command(resume="no"), config=config)
                        st.session_state.d3_messages = res['messages']
                        st.rerun()

    # 3. Chat Input (Only if not interrupted)
    if not is_interrupted:
        if prompt := st.chat_input("Ask to buy stock..."):
            # Optimistic update
            # st.session_state.d3_messages.append(HumanMessage(content=prompt))
            # Actually, let's just RUN it immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = chatbot_hitl.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
                    st.session_state.d3_messages = res['messages']
                    st.rerun()


# ==============================================================================
# ROUTER
# ==============================================================================
if st.session_state.current_view == 'home':
    render_home()
elif st.session_state.current_view == 'demo1':
    render_demo1()
elif st.session_state.current_view == 'demo2':
    render_demo2()
elif st.session_state.current_view == 'demo3':
    render_demo3_fixed()
