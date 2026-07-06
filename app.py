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
        self.units = { "infantry": 0, "tanks": 0 }

    def military_power(self):
        if self.is_eliminated: return 0
        current_power = self.base_military + (self.units["infantry"] * 1) + (self.units["tanks"] * 3)
        penalty = 1 - (self.war_exhaustion * 0.05)
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
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#2d232e')
    ax.set_title("Global Control Status", color='white', pad=20, weight='bold')
    
    x, y = 0, 0
    for i, nation in enumerate(nations):
        if nation.is_eliminated:
            color = "#4a3d4c" if nation.conquered_by != player.name else "#3e734e"
            label = f"{nation.original_name}\n({nation.conquered_by})"
        else:
            color = "#d95763" if nation.name != player.name else "#597dce"
            label = f"{nation.original_name}\nMil: {nation.military_power():.1f}"

        rect = patches.Rectangle((x, y), 1.8, 0.8, facecolor=color, edgecolor="#1a1c2c", linewidth=4)
        ax.add_patch(rect)
        ax.text(x + 0.9, y + 0.4, label, ha="center", va="center", fontsize=8, color="white", weight="bold")
        
        x += 2
        if (i + 1) % 5 == 0: 
            y -= 1
            x = 0

    ax.axis("off")
    return fig

# =========================
# STREAMLIT APP & UI
# =========================
st.set_page_config(layout="wide") 

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

h1, h2, h3 {
    color: #d95763 !important;
    text-shadow: 2px 2px #000000;
}

.stButton>button {
    border: 4px solid #1a1c2c;
    background-color: #d95763;
    color: white;
    border-radius: 0px; 
    box-shadow: 4px 4px 0px #1a1c2c; 
    transition: 0.1s;
    font-size: 12px;
    padding: 10px;
}

.stButton>button:active {
    box-shadow: 0px 0px 0px #1a1c2c;
    transform: translateY(4px) translateX(4px);
    background-color: #ac3232;
}

div[data-baseweb="select"] > div {
    background-color: #4a3d4c;
    border: 4px solid #1a1c2c;
    color: white;
    border-radius: 0px;
}

/* Style the tabs to look retro */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #4a3d4c;
    border: 4px solid #1a1c2c;
    color: white;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #d95763;
}
</style>
"""
st.markdown(pixel_css, unsafe_allow_html=True)

st.title("Global Conquest: Retro Edition")

if "game_started" not in st.session_state: 
    st.session_state.game_started = False 
    st.session_state.turn = 1 
    st.session_state.log = ["System Initialized. Awaiting commands."]
    st.session_state.nations = create_nations()
    st.session_state.action_taken = False 

nations = st.session_state.nations

if not st.session_state.game_started: 
    choice = st.selectbox("Select starting superpower:", [n.name for n in nations]) 
    if st.button("Commence Campaign"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()

else: 
    player = st.session_state.player
    
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    if not remaining_enemies:
        st.success("VICTORY: World Unification Achieved!")
    elif player.is_eliminated:
        st.error(f"DEFEAT: Conquered by {player.conquered_by}.")
    
    else:
        st.subheader(f"Turn {st.session_state.turn}")
        col1, col2 = st.columns(2)
        col1.write(f"Nation: {player.name} | Econ: {player.economy}")
        col2.write(f"Military: {player.military_power():.1f} | Exhaustion: {player.war_exhaustion}")
        
        if st.session_state.action_taken:
            st.warning("Action locked for this turn. End Turn to continue.")
        
        # =========================
        # DASHBOARD TABS
        # =========================
        tab_build, tab_invade, tab_end = st.tabs(["🛠️ Build Units", "⚔️ Launch Invasion", "⏭️ End Turn"])
        
        with tab_build:
            if not st.session_state.action_taken:
                unit = st.selectbox("Select Unit", ["Infantry (Cost: 10)", "Tanks (Cost: 25)"])
                if st.button("Deploy"):
                    cost = 10 if "Infantry" in unit else 25
                    unit_key = "infantry" if "Infantry" in unit else "tanks"
                    
                    if player.economy >= cost:
                        player.economy -= cost
                        player.units[unit_key] += 1
                        st.session_state.action_taken = True
                        st.session_state.log.append(f"Built 1 {unit_key}.")
                        st.rerun()
                    else:
                        st.error("Insufficient Econ.")
            else:
                st.write("Command unavailable. Action already taken this turn.")
                
        with tab_invade:
            if not st.session_state.action_taken:
                targets = [n.name for n in remaining_enemies]
                target_name = st.selectbox("Select Target", targets)
                if st.button("Execute Strike"):
                    target = next(n for n in nations if n.name == target_name)
                    
                    atk_roll = player.military_power() + random.randint(1, 5)
                    def_roll = target.military_power() + random.randint(1, 5)
                    
                    if atk_roll > def_roll:
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        player.economy += target.economy
                        st.session_state.log.append(f"CONQUEST: Defeated {target.name}!")
                    else:
                        player.war_exhaustion += 2
                        st.session_state.log.append(f"DEFEAT: {target.name} repelled invasion!")
                    
                    st.session_state.action_taken = True
                    st.rerun()
            else:
                st.write("Command unavailable. Action already taken this turn.")

        with tab_end:
            st.write("Advance to the next turn and collect Econ.")
            if st.button("Confirm End Turn"):
                player.economy += 15
                for ai in remaining_enemies:
                    ai.economy += 10
                    if ai.economy >= 10 and random.choice([True, False]):
                        ai.economy -= 10
                        ai.units["infantry"] += 1
                        
                st.session_state.turn += 1
                st.session_state.action_taken = False 
                st.rerun()

    # Visuals and Log below the dashboard
    st.pyplot(render_visuals(nations, player))
    
    st.subheader("Event Log")
    for msg in reversed(st.session_state.log[-5:]):
        st.write(f"> {msg}")
