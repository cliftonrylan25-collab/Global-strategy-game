import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import graphviz

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
        self.units = { "infantry": 0, "tanks": 0, "jets": 0, "orbital_satellites": 0 }
        
        # Skill Tree Unlocks
        self.skills = {
            # Mobility (Yellow)
            "repairs": False, "off_road": False, "sohc_4_valve": False,
            # Spotting (Purple)
            "situational_awareness": False, "recon": False, "aerospace": False,
            # Survivability (Orange)
            "firefighting": False, "armorer": False, "apex": False,
            # Concealment (Green)
            "camouflage": False, "quiet_running": False, "loot": False
        }

    def military_power(self):
        if self.is_eliminated: return 0
        
        # Apply base stats
        inf_power = 1
        tank_power = 3
        jet_power = 5
        
        # Apply Skill Tree Modifiers
        if self.skills["armorer"]: inf_power += 1
        if self.skills["sohc_4_valve"]: tank_power += 2 # Superior engine configuration boosts armor speed
        if self.skills["aerospace"]: jet_power += 2
        
        current_power = self.base_military + (self.units["infantry"] * inf_power) + (self.units["tanks"] * tank_power) + (self.units["jets"] * jet_power)
        
        if self.skills["loot"]: current_power *= 1.25 # 25% tactical boost
        
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

def apply_casualties(nation, severity=0.3):
    for unit_key in ["infantry", "tanks", "jets"]:
        count = nation.units[unit_key]
        if count > 0:
            lost = random.randint(0, max(1, int(count * severity)))
            if nation.skills["firefighting"]: lost = max(0, lost - 1) # Mitigation skill
            nation.units[unit_key] = max(0, count - lost)

# =========================
# VISUAL MAP & TREE GENERATOR
# =========================
def render_map(nations, player): 
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#1a1c2c')
    ax.set_title("TACTICAL OVERVIEW", color='#f4f4f4', pad=20, weight='bold', fontsize=16)
    
    x, y = 0, 0
    for i, nation in enumerate(nations):
        if nation.is_eliminated:
            if nation.conquered_by == player.name: color, edge = "#3e734e", "#1a1c2c" 
            else: color, edge = "#29366f", "#1a1c2c" 
            label = f"{nation.original_name}\n({nation.conquered_by[:3].upper()})"
        else:
            if nation.name == player.name: color, edge = "#597dce", "#f4f4f4" 
            else: color, edge = "#d95763", "#1a1c2c" 
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

def render_skill_tree(player):
    dot = graphviz.Digraph(engine='dot')
    dot.attr(bgcolor='#1a1c2c', color='#f4f4f4', fontcolor='#f4f4f4', rankdir='LR')
    
    # Node Style helper
    def style_node(node_id, label, is_unlocked, bg_color):
        fill = bg_color if is_unlocked else '#2d232e'
        font = '#ffffff' if is_unlocked else '#888888'
        dot.node(node_id, label, style='filled', fillcolor=fill, fontcolor=font, color=bg_color, penwidth='3')

    # Central Core
    dot.node('CORE', 'Global\nCommand', style='filled', fillcolor='#f4f4f4', fontcolor='black', shape='doublecircle')

    # Yellow Branch: Mobility (Driver)
    style_node('Y1', 'Repairs\n($15M)', player.skills['repairs'], '#e4c34a')
    style_node('Y2', 'Off-Road Driving\n($30M)', player.skills['off_road'], '#e4c34a')
    style_node('Y3', 'SOHC 4-Valve Config\n($60M)', player.skills['sohc_4_valve'], '#e4c34a')
    dot.edge('CORE', 'Y1', color='#e4c34a')
    dot.edge('Y1', 'Y2', color='#e4c34a')
    dot.edge('Y2', 'Y3', color='#e4c34a')

    # Purple Branch: Spotting (Radio)
    style_node('P1', 'Situational Awareness\n($15M)', player.skills['situational_awareness'], '#9c66d1')
    style_node('P2', 'Recon\n($30M)', player.skills['recon'], '#9c66d1')
    style_node('P3', 'Aerospace Command\n($100M)', player.skills['aerospace'], '#9c66d1')
    dot.edge('CORE', 'P1', color='#9c66d1')
    dot.edge('P1', 'P2', color='#9c66d1')
    dot.edge('P2', 'P3', color='#9c66d1')

    # Orange Branch: Survivability (Commander)
    style_node('O1', 'Firefighting\n($15M)', player.skills['firefighting'], '#d97e41')
    style_node('O2', 'Armorer\n($30M)', player.skills['armorer'], '#d97e41')
    style_node('O3', 'APEX Matrix\n($200M)', player.skills['apex'], '#d97e41')
    dot.edge('CORE', 'O1', color='#d97e41')
    dot.edge('O1', 'O2', color='#d97e41')
    dot.edge('O2', 'O3', color='#d97e41')

    # Green Branch: Concealment (Gunner)
    style_node('G1', 'Camouflage\n($15M)', player.skills['camouflage'], '#3bb87c')
    style_node('G2', 'Quiet Running\n($30M)', player.skills['quiet_running'], '#3bb87c')
    style_node('G3', 'LOOT Network\n($75M)', player.skills['loot'], '#3bb87c')
    dot.edge('CORE', 'G1', color='#3bb87c')
    dot.edge('G1', 'G2', color='#3bb87c')
    dot.edge('G2', 'G3', color='#3bb87c')

    return dot

# =========================
# STREAMLIT APP & UI
# =========================
st.set_page_config(page_title="Global Conquest", layout="wide") 

pixel_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
html, body, [class*="css"], [class*="st-"]  { font-family: 'Press Start 2P', cursive !important; }
.stApp { background-color: #2d232e; color: #f4f4f4; }
h1 { color: #f4f4f4 !important; text-shadow: 4px 4px #d95763; text-align: center; margin-bottom: 20px; }
h2, h3 { color: #597dce !important; }
div[data-testid="metric-container"] { background-color: #1a1c2c; border: 3px solid #4a3d4c; padding: 10px; border-radius: 0px; box-shadow: 3px 3px 0px #000000; }
div[data-testid="stMetricValue"] { color: #f4f4f4 !important; font-size: 16px !important; }
.stButton>button { border: 4px solid #1a1c2c; background-color: #d95763; color: white; border-radius: 0px; box-shadow: 4px 4px 0px #000000; transition: 0.1s; font-size: 14px; padding: 15px; width: 100%; margin-top: 10px; }
.stButton>button:active { box-shadow: 0px 0px 0px #000000; transform: translateY(4px) translateX(4px); background-color: #ac3232; }
div.row-widget.stRadio > div { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 15px; border-radius: 0px; }
.stRadio label { padding-bottom: 12px; line-height: 1.5; }
.terminal-box { background-color: #000000; border: 2px solid #597dce; padding: 15px; color: #3e734e; font-family: monospace !important; font-size: 12px; height: 180px; overflow-y: auto; }
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

if not st.session_state.game_started: 
    st.markdown("### INITIALIZE CAMPAIGN")
    choice = st.radio("Select Superpower Faction:", [n.name for n in nations]) 
    if st.button("COMMENCE DOMINATION"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()
else: 
    player = st.session_state.player
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    
    if not remaining_enemies:
        st.success("👑 TOTAL PLANETARY UNIFICATION ACHIEVED.")
    elif player.is_eliminated:
        st.error(f"💀 YOUR EMPIRE HAS FALLEN. CONQUERED BY {player.conquered_by.upper()}.")
    else:
        st.markdown(f"### TURN: {st.session_state.turn}")
        
        # Dashboard
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 ECON", f"${player.economy}M")
        col2.metric("⚔️ MILITARY", f"{player.military_power():.1f}")
        col3.metric("🔥 EXHAUSTION", f"{player.war_exhaustion}")
        
        st.markdown(f"**GARRISON:** 🎖️ Inf: {player.units['infantry']} | 🚜 Tanks: {player.units['tanks']} | ✈️ Jets: {player.units['jets']} | 🛰️ Sats: {player.units['orbital_satellites']}")
        st.write("---")
        
        # Command Menu
        action_mode = st.radio(
            "COMMAND TERMINAL:",
            [
                "🛠️ Deploy Forces", 
                "🌳 Skill Tree (R&D)",
                "🚀 Aerospace Command", 
                "🕵️ Covert Operations",
                "⚔️ Execute Strike", 
                "⏭️ End Turn Cycle"
            ]
        )
        st.write("---")
        
        # Action: DEPLOY FORCES
        if action_mode == "🛠️ Deploy Forces":
            if not st.session_state.action_taken:
                unit = st.radio("Requisition Assets", [
                    "Infantry Battalion (Cost: 10)", 
                    "Armored Tanks (Cost: 25)",
                    "Fighter Squadron (Cost: 40)"
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

        # Action: SKILL TREE
        elif action_mode == "🌳 Skill Tree (R&D)":
            st.graphviz_chart(render_skill_tree(player), use_container_width=True)
            
            if not st.session_state.action_taken:
                # Compile available upgrades based on prerequisites
                opts = []
                # Mobility
                if not player.skills["repairs"]: opts.append(("Repairs (Tier 1 Mobility) - $15M", 15, "repairs"))
                elif not player.skills["off_road"]: opts.append(("Off-Road Driving (Tier 2 Mobility) - $30M", 30, "off_road"))
                elif not player.skills["sohc_4_valve"]: opts.append(("SOHC 4-Valve Config (Tier 3 Mobility) - $60M", 60, "sohc_4_valve"))
                
                # Spotting
                if not player.skills["situational_awareness"]: opts.append(("Situational Awareness (Tier 1 Spotting) - $15M", 15, "situational_awareness"))
                elif not player.skills["recon"]: opts.append(("Recon (Tier 2 Spotting) - $30M", 30, "recon"))
                elif not player.skills["aerospace"]: opts.append(("Aerospace Command (Tier 3 Spotting) - $100M", 100, "aerospace"))

                # Survivability
                if not player.skills["firefighting"]: opts.append(("Firefighting (Tier 1 Survivability) - $15M", 15, "firefighting"))
                elif not player.skills["armorer"]: opts.append(("Armorer (Tier 2 Survivability) - $30M", 30, "armorer"))
                elif not player.skills["apex"]: opts.append(("Advanced Predictive Executive Matrix (Tier 3 Survivability) - $200M", 200, "apex"))

                # Concealment
                if not player.skills["camouflage"]: opts.append(("Camouflage (Tier 1 Concealment) - $15M", 15, "camouflage"))
                elif not player.skills["quiet_running"]: opts.append(("Quiet Running (Tier 2 Concealment) - $30M", 30, "quiet_running"))
                elif not player.skills["loot"]: opts.append(("LOOT Network (Tier 3 Concealment) - $75M", 75, "loot"))

                if opts:
                    tech_choice = st.selectbox("Select Branch Node to Unlock:", [o[0] for o in opts])
                    if st.button("UNLOCK NODE"):
                        selected = next(o for o in opts if o[0] == tech_choice)
                        if player.economy >= selected[1]:
                            player.economy -= selected[1]
                            player.skills[selected[2]] = True
                            st.session_state.action_taken = True
                            st.session_state.log.append(f"🧬 SKILL UNLOCKED: {selected[2].replace('_', ' ').upper()}")
                            st.rerun()
                        else:
                            st.error("SYSTEM ERROR: INSUFFICIENT FUNDS.")
                else:
                    st.success("All nodes acquired. Tech tree mastered.")
            else:
                st.caption("🔒 R&D LOCKED: Awaiting next turn cycle.")

        # Action: END TURN (Simplified for brevity, same combat logic applies)
        elif action_mode == "⏭️ End Turn Cycle":
            if st.button("CONFIRM CYCLE END"):
                # APEX Matrix grants massive economy if unlocked
                econ_gain = 50 if player.skills["apex"] else 30
                player.economy += econ_gain
                if player.war_exhaustion > 0: player.war_exhaustion -= 1 
                
                # AI Turn Logic
                for ai in remaining_enemies:
                    ai.economy += 20
                    if ai.economy >= 40:
                        ai.economy -= 40
                        ai.units["tanks"] += 1
                        
                st.session_state.turn += 1
                st.session_state.action_taken = False 
                st.session_state.log.append(f"CYCLE COMPLETE. Turn {st.session_state.turn} begins.")
                st.rerun()

    st.pyplot(render_map(nations, player))
    st.markdown("### SYSTEM LOG")
    log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-7:])])
    st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)

