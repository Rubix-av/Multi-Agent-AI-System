import os
import re
import sys
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

# Ensure console supports UTF-8 encoding (especially on Windows)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── Theme Toggle Configuration ────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ── CSS Variables and Styling System ──────────────────────────────────────────

# ── Markdown → HTML converter (for rendering inside styled divs) ──────────────
def md_to_html(text):
    """Convert markdown text to HTML so it renders properly inside HTML divs."""
    if not text:
        return ""
    lines = text.split('\n')
    html_lines = []
    in_ul = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines — close any open list first
        if not stripped:
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            continue

        # Headings (check longest prefix first)
        if stripped.startswith('#### '):
            if in_ul:
                html_lines.append('</ul>'); in_ul = False
            html_lines.append(f'<h4>{_inline(stripped[5:])}</h4>')
        elif stripped.startswith('### '):
            if in_ul:
                html_lines.append('</ul>'); in_ul = False
            html_lines.append(f'<h3>{_inline(stripped[4:])}</h3>')
        elif stripped.startswith('## '):
            if in_ul:
                html_lines.append('</ul>'); in_ul = False
            html_lines.append(f'<h2>{_inline(stripped[3:])}</h2>')
        elif stripped.startswith('# '):
            if in_ul:
                html_lines.append('</ul>'); in_ul = False
            html_lines.append(f'<h1>{_inline(stripped[2:])}</h1>')
        # Horizontal rule
        elif stripped == '---' or stripped == '***' or stripped == '___':
            if in_ul:
                html_lines.append('</ul>'); in_ul = False
            html_lines.append('<hr>')
        # Bullet list items (- or *)
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_ul:
                html_lines.append('<ul>')
                in_ul = True
            html_lines.append(f'<li>{_inline(stripped[2:])}</li>')
        # Numbered list items
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ul:
                html_lines.append('<ol>')
                in_ul = True  # reuse flag; close tag handled below
            content = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f'<li>{_inline(content)}</li>')
        # Regular paragraph
        else:
            if in_ul:
                # Detect if the list was <ol> or <ul>
                html_lines.append('</ol>' if any('<ol>' in h for h in html_lines[-10:]) else '</ul>')
                in_ul = False
            html_lines.append(f'<p>{_inline(stripped)}</p>')

    if in_ul:
        html_lines.append('</ol>' if any('<ol>' in h for h in html_lines[-10:]) else '</ul>')

    return '\n'.join(html_lines)

def _inline(text):
    """Convert inline markdown (bold, italic, code) to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

bg_color = "#080d14" if IS_DARK else "#fafafa"
bg_subtle = "#0c121e" if IS_DARK else "#f3f4f6"
card_color = "#0e1a2e" if IS_DARK else "#ffffff"
card_hover = "#14253f" if IS_DARK else "#f4f4f5"
border_color = "#1e3a5c" if IS_DARK else "#e5e7eb"
border_subtle = "#12253a" if IS_DARK else "#f0f0f2"
text_color = "#fafafa" if IS_DARK else "#111827"
text_muted = "#7aa8cc" if IS_DARK else "#6b7280"
text_dim = "#4b6c8d" if IS_DARK else "#a1a1aa"
accent_color = "#3a7bd5" if IS_DARK else "#2563eb"
accent_glow = "rgba(58, 123, 213, 0.35)" if IS_DARK else "rgba(37, 99, 235, 0.15)"

# Configure page
st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
    background-color: {bg_color} !important;
    color: {text_color} !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}}

.block-container {{
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
}}

/* Hide standard Streamlit header & footer */
header[data-testid="stHeader"], footer, #MainMenu {{
    visibility: hidden;
    height: 0px !important;
}}

/* ── Custom App Header ── */
.app-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0 1rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid {border_color};
}}
.app-logo {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {text_color};
    display: flex;
    align-items: center;
    gap: 8px;
}}
.app-logo span {{
    background: linear-gradient(135deg, #4ea8f0 0%, #3a7bd5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* ── Hero Card ── */
.hero-wrapper {{
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    height: 220px;
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}}
.hero-bg {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.4);
    position: absolute;
    top: 0; left: 0;
}}
.hero-content {{
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1rem 2rem;
}}
.hero-badge {{
    background: rgba(58,123,213,0.25);
    border: 1px solid rgba(58,123,213,0.5);
    color: #7ab8f5 !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 0.6rem;
    display: inline-block;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.4rem;
    line-height: 1.2;
}}
.hero-sub {{
    color: #cbdcf0;
    font-size: 0.95rem;
    max-width: 650px;
}}

/* ── Card Styles ── */
.custom-card {{
    background-color: {card_color};
    border: 1px solid {border_color};
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}}

/* ── Styled Tabs (pill-style) ── */
button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {text_muted} !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {text_color} !important;
    background: {card_color} !important;
    border-color: {border_color} !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: {bg_subtle} !important;
    border: 1px solid {border_color} !important;
    border-radius: 12px !important;
    padding: 4px !important;
    margin-bottom: 1rem;
}}

/* ── Form Controls override ── */
.stTextArea textarea {{
    background: {bg_subtle} !important;
    border: 1px solid {border_color} !important;
    border-radius: 10px !important;
    color: {text_color} !important;
    font-size: 0.95rem !important;
    resize: none !important;
}}
.stTextArea textarea:focus {{
    border-color: {accent_color} !important;
    box-shadow: 0 0 0 2px {accent_glow} !important;
}}
input[type="text"], .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {{
    background: {bg_subtle} !important;
    border: 1px solid {border_color} !important;
    border-radius: 8px !important;
    color: {text_color} !important;
}}

/* ── Generate button ── */
div[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, #1e70c9 0%, #0d4e94 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 15px {accent_glow} !important;
    transition: all 0.25s ease !important;
}}
div[data-testid="stButton"] > button:hover {{
    box-shadow: 0 6px 22px rgba(58,123,213,0.5) !important;
    transform: translateY(-1.5px) !important;
    background: linear-gradient(135deg, #287fdc 0%, #115dae 100%) !important;
}}

/* ── Metrics Row ── */
.metric-row {{
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}}
.metric-box {{
    flex: 1;
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 0.85rem 1rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}
.metric-val {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {accent_color};
}}
.metric-lbl {{
    font-size: 0.75rem;
    color: {text_muted};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.1rem;
}}

/* ── Plan Content ── */
.plan-container {{
    background: linear-gradient(165deg, {card_color} 0%, {bg_subtle} 100%);
    border: 1px solid {border_color};
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    color: {text_color};
    line-height: 1.7;
    margin-top: 0.5rem;
}}
.plan-container h1 {{
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, {accent_color}, #00d2ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0.2rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid {border_color};
}}
.plan-container h2 {{
    font-size: 1.3rem;
    font-weight: 700;
    color: {accent_color};
    margin: 1.2rem 0 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid {border_color};
}}
.plan-container h3 {{
    font-size: 1.1rem;
    font-weight: 700;
    color: #00d2ff;
    margin: 1rem 0 0.4rem;
}}
.plan-container h4 {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {text_color};
    margin: 0.8rem 0 0.3rem;
}}
.plan-container strong {{
    color: {accent_color};
    font-weight: 600;
}}
.plan-container ul {{
    padding-left: 1.2rem;
    margin: 0.3rem 0;
}}
.plan-container li {{
    margin-bottom: 0.25rem;
    color: {text_color};
}}
.plan-container hr {{
    border: none;
    border-top: 1px solid {border_color};
    margin: 1rem 0;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {bg_subtle} !important;
    border-right: 1px solid {border_color} !important;
}}
.sidebar-chip {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 8px;
    padding: 0.4rem 0.7rem;
    margin-bottom: 0.4rem;
    font-size: 0.8rem;
    color: {text_muted};
    display: flex;
    align-items: center;
    gap: 6px;
}}
.sidebar-title {{
    color: {text_color};
    font-size: 0.95rem;
    font-weight: 700;
    margin: 1.25rem 0 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.save-bar {{
    background: {bg_subtle};
    border: 1px solid {border_color};
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: {text_color};
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.save-bar code {{
    color: {accent_color};
    background: {card_color};
    padding: 2px 6px;
    border-radius: 4px;
}}
</style>
""", unsafe_allow_html=True)

# ── Application Header ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <div class="app-logo">
        ✈️ <span>AI Travel Planner Portal</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Theme toggle button in header
header_col1, header_col2 = st.columns([11, 1])
with header_col2:
    theme_btn_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_btn_label, on_click=toggle_theme, key="theme_toggle_btn", use_container_width=True)

# ── Sidebar Configuration ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-title'>👤 Session Configuration</div>", unsafe_allow_html=True)
    thread_id = st.text_input("User Thread ID", value="aarohi_user",
                              help="Unique session ID to maintain Postgres conversation memory state.")
    
    st.markdown("<div class='sidebar-title'>⚡ System Architecture</div>", unsafe_allow_html=True)
    tech_stack = [
        ("🔗 LangGraph", "Multi-Agent Orchestrator"),
        ("🧠 Groq LLaMA 3.3", "Inference & Brains"),
        ("🐘 PostgreSQL", "PostgresSaver Memory Checkpointer"),
        ("🔍 Tavily Search", "Web Search Adapter"),
        ("✈️ AviationStack", "Real-time Flight Engine"),
        ("☀️ OpenWeather", "Local Weather API")
    ]
    for tech, desc in tech_stack:
        st.markdown(f"<div class='sidebar-chip'><b>{tech}</b> &nbsp;|&nbsp; <span style='font-size:0.75rem;'>{desc}</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🛰️ Active Agents Status</div>", unsafe_allow_html=True)
    pipeline_placeholder = st.empty()

# Helper function to render status
def update_pipeline_ui(active_node=None, completed_nodes=None):
    if completed_nodes is None:
        completed_nodes = []
    
    steps = [
        ("flight_agent", "✈️ Flight Agent", "Routes & pricing advice"),
        ("hotel_agent", "🏨 Hotel Agent", "Hotel options & booking tips"),
        ("weather_agent", "☀️ Weather Agent", "Local weather & 5-day forecast"),
        ("itinerary_agent", "🗓️ Itinerary Agent", "Combined day-wise trip planner")
    ]
    
    html = ""
    for node, name, desc in steps:
        if node in completed_nodes:
            status_icon = "🟢"
            status_text = "Done"
            color = "#22c55e"
            bg = "rgba(34, 197, 94, 0.08)"
            border = "rgba(34, 197, 94, 0.3)"
        elif node == active_node:
            status_icon = "🔵"
            status_text = "Running"
            color = "#3a7bd5"
            bg = "rgba(58, 123, 213, 0.12)"
            border = "rgba(58, 123, 213, 0.5)"
        else:
            status_icon = "⚪"
            status_text = "Wait"
            color = text_muted
            bg = "transparent"
            border = border_color
            
        html += f"""
        <div style="background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; flex-direction: column;">
                <span style="font-weight:600; font-size:0.82rem; color:{text_color};">{name}</span>
                <span style="font-size:0.7rem; color:{text_muted};">{desc}</span>
            </div>
            <span style="font-size:0.75rem; font-weight:700; color:{color};">{status_icon} {status_text}</span>
        </div>
        """
    pipeline_placeholder.markdown(html, unsafe_allow_html=True)

# Initial pipeline status
update_pipeline_ui()

# ── Hero Banner ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="flight sky background"/>
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent Orchestrator</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">Enter your destination details and four specialized agents will collaborate to check flights, hotels, and local weather to build your personalized travel itinerary.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Destintation Quick Cards ──────────────────────────────────────────────────
st.markdown("<div style='font-size:0.85rem; font-weight:700; color:var(--text); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.6rem;'>🔥 Recommended Destinations</div>", unsafe_allow_html=True)
DESTINATIONS = [
    ("Tokyo, Japan", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("Paris, France", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("Bangkok, Thailand", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("Rome, Italy", "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("Dubai, UAE", "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
selected_quick_dest = None
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div style="border-radius:10px; overflow:hidden; position:relative; height:85px; margin-bottom:8px;">
            <img src="{img_url}" style="width:100%; height:100%; object-fit:cover; filter:brightness(0.55);" />
            <div style="position:absolute; bottom:6px; left:0; right:0; text-align:center; color:#ffffff; font-size:0.78rem; font-weight:700;">{name}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Configure", key=f"btn_{name}", use_container_width=True):
            selected_quick_dest = name

# Initialize session state value for custom input
if "builder_destination" not in st.session_state:
    st.session_state.builder_destination = ""

if selected_quick_dest:
    st.session_state.builder_destination = selected_quick_dest

# ── Trip Builder Interface ────────────────────────────────────────────────────
st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
input_tab1, input_tab2 = st.tabs(["✍️ Custom Trip Builder", "💬 Quick Prompt Input"])

with input_tab1:
    col_dest, col_days = st.columns([3, 1])
    with col_dest:
        dest_val = st.text_input("Target Destination", value=st.session_state.builder_destination, placeholder="e.g. Kyoto, Japan or Mumbai, India")
        # Sync state if edited manually
        st.session_state.builder_destination = dest_val
    with col_days:
        trip_days = st.number_input("Duration (Days)", min_value=1, max_value=30, value=7)
    
    col_budget, col_currency, col_style = st.columns([2, 1, 2])
    with col_budget:
        trip_budget = st.number_input("Total Budget", min_value=1000, value=150000, step=5000)
    with col_currency:
        currency = st.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)", "AED (AED)"])
    with col_style:
        travel_style = st.selectbox("Travel Style", ["Balanced", "Backpacker/Budget", "Luxury & Leisure", "Adventure & Active", "Culture & History", "Family Friendly"])
    
    special_notes = st.text_area("Special Notes & Preferences (Optional)", placeholder="e.g. Prefer direct flights, vegetarian dining, staying close to metro stations", height=68)
    
    # Construct combined query
    compiled_query = f"Plan a complete {trip_days}-day trip to {dest_val} with a budget of {currency} {trip_budget}. Travel style: {travel_style}."
    if special_notes.strip():
        compiled_query += f" Special preferences: {special_notes.strip()}."

with input_tab2:
    quick_query = st.text_area(
        "Enter Travel Prompt",
        value=f"Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs" if not st.session_state.builder_destination else compiled_query,
        placeholder="Type here...",
        height=130
    )

user_query = compiled_query if dest_val else quick_query
generate = st.button("🚀  Generate Travel Plan", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Dynamic Outputs and Visualization ─────────────────────────────────────────
tab_plan, tab_flights, tab_hotels, tab_weather = st.tabs([
    "🗓️ Full Travel Itinerary", 
    "✈️ Flight Suggestions", 
    "🏨 Hotel Options", 
    "☀️ Weather & Forecast"
])

with tab_plan:
    itinerary_placeholder = st.empty()
    itinerary_placeholder.info("Click 'Generate Travel Plan' above to build your day-wise itinerary.")

with tab_flights:
    flights_placeholder = st.empty()
    flights_placeholder.info("Flight routing, airlines, and estimate options will display here.")

with tab_hotels:
    hotels_placeholder = st.empty()
    hotels_placeholder.info("Hotel recommendations and stays will display here.")

with tab_weather:
    weather_placeholder = st.empty()
    weather_placeholder.info("Current destination weather and 5-day forecast will display here.")

# ── Execution Logic ───────────────────────────────────────────────────────────
if generate:
    if not user_query.strip():
        st.warning("Please specify a destination or write a prompt first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        
        # Dictionary to store outputs from stream updates
        collected = {
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "itinerary": "",
            "final_response": "",
            "llm_calls": 0
        }

        # Clear placeholders and show loaders
        itinerary_placeholder.markdown("<div style='text-align:center; padding: 2rem;'><div class='stSpinner'></div><p style='color:var(--text-muted); margin-top:10px;'>Building travel plan...</p></div>", unsafe_allow_html=True)
        flights_placeholder.info("Flight agent is preparing to search routes...")
        hotels_placeholder.info("Hotel agent is waiting to discover stays...")
        weather_placeholder.info("Weather agent is waiting to pull regional forecasts...")

        completed_agents = []
        
        # Run stream
        try:
            for chunk in app.stream(
                {
                    "messages": [HumanMessage(content=user_query)],
                    "user_query": user_query,
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "itinerary": "",
                    "llm_calls": 0,
                },
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    # Update status timeline UI to Running
                    update_pipeline_ui(active_node=node_name, completed_nodes=completed_agents)
                    
                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text
                        flights_placeholder.markdown(f"<div class='plan-container'>{md_to_html(text)}</div>", unsafe_allow_html=True)
                        completed_agents.append(node_name)
                        
                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text
                        hotels_placeholder.markdown(f"<div class='plan-container'>{md_to_html(text)}</div>", unsafe_allow_html=True)
                        completed_agents.append(node_name)
                        
                    elif node_name == "weather_agent":
                        text = state_update.get("weather_results", "")
                        collected["weather_results"] = text
                        weather_placeholder.markdown(f"<div class='plan-container'>{md_to_html(text)}</div>", unsafe_allow_html=True)
                        completed_agents.append(node_name)
                        
                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        collected["final_response"] = text
                        itinerary_placeholder.markdown(f"<div class='plan-container'>{md_to_html(text)}</div>", unsafe_allow_html=True)
                        completed_agents.append(node_name)
                        
                    collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])
            
            # Execution finished successfully
            update_pipeline_ui(completed_nodes=completed_agents)
            
            # Display overall run metrics
            st.markdown(f"""
            <div class="metric-row" style="margin-top: 1.5rem;">
                <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents Executed</div></div>
                <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Operations</div></div>
                <div class="metric-box"><div class="metric-val">🟢 Active</div><div class="metric-lbl">Session Memory</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Auto-save Markdown Artifact
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"travel_plan_{timestamp}.md"
            save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
            os.makedirs(save_dir, exist_ok=True)
            
            file_content = f"""# Travel Plan - {dest_val or 'Custom Request'}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Query:** {user_query}
**Session Thread ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'Information not available.'}

---

## 🏨 Hotel Accommodations
{collected['hotel_results'] or 'Information not available.'}

---

## ☀️ Weather & Forecast
{collected['weather_results'] or 'Information not available.'}

---

## 🗓️ Final Travel Itinerary
{collected['itinerary'] or 'Itinerary build failed.'}

---
*Generated via LangGraph multi-agent systems orchestration.*
"""
            with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
                f.write(file_content)
            
            # Save feedback bar & download button
            col_dl, col_sav = st.columns([1, 3])
            with col_dl:
                st.download_button("⬇️ Download Plan", data=file_content,
                                   file_name=filename, mime="text/markdown",
                                   use_container_width=True)
            with col_sav:
                st.markdown(f"<div class='save-bar'>💾 Auto-saved successfully &nbsp;|&nbsp; <code>travel_plans/{filename}</code></div>",
                            unsafe_allow_html=True)
                
        except Exception as e:
            update_pipeline_ui()
            st.error(f"An error occurred during agent pipeline execution: {str(e)}")
            itinerary_placeholder.error(f"Pipeline failed: {str(e)}")