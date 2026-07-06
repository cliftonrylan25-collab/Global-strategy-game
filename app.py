import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =========================
# GAME ENGINE & CLASSES
# =========================
class Nation: 
    def __init__(self, name, economy, military_power): 
        self.name = name 
        self.original_name = name  
        self.economy = economy 
        self.base_military = military_power
        self.war_exhaustion = 0 
        self.is_eliminated = False
        self.conquered_by = None
        self.units = { "infantry": 0, "tanks": 0, "jets": 0 }

    def military_power(self):
        if self.is_eliminated: return 0
        current_power = self.base_military + (self.units["infantry"] * 1) + (self.units["tanks"] * 3) + (self.units["jets"] * 5)
        penalty = max(0.5, 1 - (self.war_exhaustion * 0.05))
        return max(0, current_power * penalty)

def create_nations(): 
    return [ 
        Nation("United States", 80, 10), Nation("Canada", 60, 5), Nation("Mexico", 55, 4), 
        Nation("Brazil", 70, 7), Nation("United Kingdom", 65, 6), Nation("France", 65, 6), 
        Nation("Germany", 70, 7), Nation("Russia", 75, 9), Nation("China", 90, 10), 
        Nation("India", 85, 8), Nation("Japan", 70, 6), Nation("Saudi Arabia", 85, 5),
        Nation("South Africa", 65, 4), Nation("Australia", 70, 5) 
    ]

# =========================
# VISUAL MAP GENERATOR
# =========================
def render_visuals(nations, player): 
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#1a1c2c')
    ax.set_title("TACTICAL OVERVIEW", color='#f4f4f4', pad=20, weight='bold', fontsize=16)
    
    x, y = 0, 0
    for i, nation in enumerate(nations):
        if nation.is_eliminated:
            if nation.conquered_by == player.name:
                color, edge = "#3e734e", "#1a1c2c" 
            else:
                color, edge = "#29366f", "#1a1c2c" 
            label = f"{nation.original_name}\n({nation.conquered_by[:3]})"
        else:
            if nation.name == player.name:
                color, edge = "#597dce", "#f4f4f4" 
            else:
                color, edge = "#d95763", "#1a1c2c" 
            label = f"{nation.original_name}\nMil: {nation.military_power():.1f}"

        rect = patches.Rectangle((x, y), 1.8, 0.8, facecolor=color, edgecolor=edge, linewidth=3)
        ax.add_patch(rect)
        ax.text(x + 0.9, y + 0.4, label, ha="center", va="center", fontsize=9, color="white", weight="bold")
        
        x += 2
        if (i + 1) % 4 == 0: 
            y -= 1
            x = 0

    ax.axis("off")
    return fig

# =========================
# STREAMLIT APP & RETRO UI
# =========================
st.set_page_config(page_title="Global Conquest", layout="wide") 

pixel_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body, [class*="css"], [class*="st-"]  {
    font-family: 'Press Start 2P', cursive !important;
}
.stApp {
    background-color: #2d232e;
    color: #f4f4f4;
}

h1 {
    color: #f4f4f4 !important;
    text-shadow: 4px 4px #d95763;
    text-align: center;
    margin-bottom: 20px;
}
h2, h3 { color: #597dce !important; }

div[data-testid="metric-container"] {
    background-color: #1a1c2c;
    border: 3px solid #4a3d4c;
    padding: 10px;
    border-radius: 0px;
    box-shadow: 3px 3px 0px #000000;
}
div[data-testid="stMetricValue"] {
    color: #f4f4f4 !important;
    font-size: 16px !important;
}

.stButton>button {
    border: 4px solid #1a1c2c;
    background-color: #d95763;
    color: white;
    border-radius: 0px; 
    box-shadow: 4px 4px 0px #000000; 
    transition: 0.1s;
    font-size: 14px;
    padding: 15px;
    width: 100%;
    margin-top: 10px;
}
.stButton>button:active {
    box-shadow: 0px 0px 0px #000000;
    transform: translateY(4px) translateX(4px);
    background-color: #ac3232;
}

div.row-widget.stRadio > div {
    background-color: #1a1c2c;
    border: 2px solid #4a3d4c;
    padding: 15px;
    border-radius: 0px;
}
.stRadio label {
    padding-bottom: 12px;
    line-height: 1.5;
}

.terminal-box {
    background-color: #000000;
    border: 2px solid #597dce;
    padding: 15px;
    color: #3e734e;
    font-family: monospace !important;
    font-size: 12px;
    height: 150px;
    overflow-y: auto;
}
</style>
"""
st.markdown(pixel_css, unsafe_allow_html=True)

st.markdown("<h1>Global Conquest</h1>", unsafe_allow_html=True)

# =========================
# GAME INITIALIZATION
# =========================
if "game_started" not in st.session_state: 
    st.session_state.game_started = False 
    st.session_state.turn = 1 
    st.session_state.log = ["SYSTEM BOOT SEQUENCE INITIATED...", "AWAITING COMMANDER DIRECTIVE."]
    st.session_state.nations = create_nations()
    st.session_state.action_taken = False 

nations = st.session_state.nations

# =========================
# PRE-GAME LOBBY
# =========================
if not st.session_state.game_started: 
    st.markdown("### INITIALIZE CAMPAIGN")
    choice = st.radio("Select Superpower Faction:", [n.name for n in nations]) 
    if st.button("COMMENCE DOMINATION"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()

# =========================
# MAIN GAME LOOP
# =========================
else: 
    player = st.session_state.player
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    
    if not remaining_enemies:
        st.success("👑 TOTAL PLANETARY UNIFICATION ACHIEVED. YOU ARE SUPREME COMMANDER.")
        st.balloons()
    elif player.is_eliminated:
        st.error(f"💀 YOUR EMPIRE HAS FALLEN. CONQUERED BY {player.conquered_by.upper()}.")
    
    else:
        st.markdown(f"### TURN: {st.session_state.turn}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 ECON", f"${player.economy}M")
        col2.metric("⚔️ MILITARY", f"{player.military_power():.1f}")
        col3.metric("🔥 EXHAUSTION", f"{player.war_exhaustion}")
        
        st.write("War Exhaustion Level:")
        st.progress(min(player.war_exhaustion / 15, 1.0))
        
        st.write("---")
        
        action_mode = st.radio(
            "COMMAND TERMINAL:",
            ["🛠️ Deploy Forces", "⚔️ Execute Strike", "⏭️ End Turn Cycle"]
        )
        
        st.write("---")
        
        # Action: BUILD
        if action_mode == "🛠️ Deploy Forces":
            if not st.session_state.action_taken:
                unit = st.radio("Requisition Assets", [
                    "Infantry Battalion (Cost: 10 | Pow: 1)", 
                    "Armored Tanks (Cost: 25 | Pow: 3)",
                    "Fighter Squadron (Cost: 40 | Pow: 5)"
                ])
                if st.button("CONFIRM DEPLOYMENT"):
                    if "Infantry" in unit: cost, key = 10, "infantry"
                    elif "Tanks" in unit: cost, key = 25, "tanks"
                    else: cost, key = 40, "jets"
                    
                    if player.economy >= cost:
                        player.economy -= cost
                        player.units[key] += 1
                        st.session_state.action_taken = True
                        st.session_state.log.append(f"PRODUCTION: {key.upper()} deployed.")
                        st.rerun()
                    else:
                        st.error("SYSTEM ERROR: INSUFFICIENT FUNDS.")
            else:
                st.caption("🔒 LOGISTICS LOCKED: Awaiting next turn cycle.")
                
        # Action: INVADE
        elif action_mode == "⚔️ Execute Strike":
            if not st.session_state.action_taken:
                targets = [n.name for n in remaining_enemies]
                target_name = st.radio("Designate Target Coordinates", targets)
                if st.button("LAUNCH INVASION"):
                    target = next(n for n in nations if n.name == target_name)
                    
                    atk_roll = player.military_power() + random.uniform(1.0, 5.0)
                    def_roll = target.military_power() + random.uniform(1.0, 5.0)
                    
                    if atk_roll > def_roll:
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        player.economy += target.economy
                        st.session_state.log.append(f"VICTORY: {target.name.upper()} SECURED. Looted ${target.economy}M.")
                    else:
                        player.war_exhaustion += 3
                        st.session_state.log.append(f"DEFEAT: STRIKE ON {target.name.upper()} REPULSED. Exhaustion increased.")
                    
                    st.session_state.action_taken = True
                    st.rerun()
            else:
                st.caption("🔒 MILITARY LOCKED: Awaiting next turn cycle.")

        # Action: END TURN
        elif action_mode == "⏭️ End Turn Cycle":
            if st.button("CONFIRM CYCLE END"):
                player.economy += 20
                if player.war_exhaustion > 0:
                    player.war_exhaustion -= 1 
                
                for ai in remaining_enemies:
                    ai.economy += 15
                    if ai.economy >= 40 and random.choice([True, False]):
                        ai.economy -= 40
                        ai.units["jets"] += 1
                    elif ai.economy >= 25 and random.choice([True, False]):
                        ai.economy -= 25
                        ai.units["tanks"] += 1
                    elif ai.economy >= 10:
                        ai.economy -= 10
                        ai.units["infantry"] += 1
                        
                st.session_state.turn += 1
                st.session_state.action_taken = False 
                st.session_state.log.append(f"CYCLE COMPLETE. Turn {st.session_state.turn} begins.")
                st.rerun()

    st.pyplot(render_visuals(nations, player))
    
    st.markdown("### SYSTEM LOG")
    log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-6:])])
    st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
