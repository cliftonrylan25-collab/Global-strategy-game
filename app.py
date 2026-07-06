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
        
        inf_power = 1
        tank_power = 3
        jet_power = 5
        
        # Apply Skill Tree Modifiers
        if self.skills["armorer"]: inf_power += 1
        if self.skills["sohc_4_valve"]: tank_power += 2 
        if self.skills["aerospace"]: jet_power += 2
        
        current_power = self.base_military + (self.units["infantry"] * inf_power) + (self.units["tanks"] * tank_power) + (self.units["jets"] * jet_power)
        
        if self.skills["loot"]: current_power *= 1.25 
        
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
            if nation.skills["firefighting"]: lost = max(0, lost - 1) 
            nation.units[unit_key] = max(0, count - lost)

# =========================
# VISUAL MAP GENERATOR
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
div[data-testid="stMetricValue"] { color: #f4f4f4 !important; font-size: 14px !important; }
.stButton>button { border: 4px solid #1a1c2c; background-color: #d95763; color: white; border-radius: 0px; box-shadow: 4px 4px 0px #000000; transition: 0.1s; font-size: 12px; padding: 10px; width: 100%; margin-top: 10px; }
.stButton>button:active { box-shadow: 0px 0px 0px #000000; transform: translateY(4px) translateX(4px); background-color: #ac3232; }
div.row-widget.stRadio > div { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 15px; border-radius: 0px; }
.stRadio label { padding-bottom: 12px; line-height: 1.5; }
.terminal-box { background-color: #000000; border: 2px solid #597dce; padding: 15px; color: #3e734e; font-family: monospace !important; font-size: 12px; height: 180px; overflow-y: auto; }
.skill-card { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 8px; margin-bottom: 8px; text-align: center; font-size: 10px; }
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

        # Action: SKILL TREE (MOBILE RESPONSIVE REWRITE)
        elif action_mode == "🌳 Skill Tree (R&D)":
            st.markdown("### 🧬 EMPIRE TECH TREE STATUS")
            
            # Render a 4-column layout layout that matches your layout image cleanly
            t1, t2, t3, t4 = st.columns(4)
            
            with t1:
                st.markdown("<span style='color:#e4c34a'>⚡ MOBILITY</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['repairs'] else '🔒'} Repairs<br>($15M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['off_road'] else '🔒'} Off-Road<br>($30M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['sohc_4_valve'] else '🔒'} SOHC 4V<br>($60M)</div>", unsafe_allow_html=True)
                
            with t2:
                st.markdown("<span style='color:#9c66d1'>👁️ SPOTTING</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['situational_awareness'] else '🔒'} Sit Aware<br>($15M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['recon'] else '🔒'} Recon<br>($30M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['aerospace'] else '🔒'} Aerospace<br>($100M)</div>", unsafe_allow_html=True)
                
            with t3:
                st.markdown("<span style='color:#d97e41'>🛡️ SURVIVE</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['firefighting'] else '🔒'} Firefight<br>($15M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['armorer'] else '🔒'} Armorer<br>($30M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['apex'] else '🔒'} APEX<br>($200M)</div>", unsafe_allow_html=True)
                
            with t4:
                st.markdown("<span style='color:#3bb87c'>🍃 CONCEAL</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['camouflage'] else '🔒'} Camo<br>($15M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['quiet_running'] else '🔒'} Quiet Run<br>($30M)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-card'>{'✅' if player.skills['loot'] else '🔒'} LOOT Net<br>($75M)</div>", unsafe_allow_html=True)

            st.write("---")

            if not st.session_state.action_taken:
                opts = []
                # Mobility Branch unlocks linearly
                if not player.skills["repairs"]: opts.append(("Repairs (Mobility T1) - $15M", 15, "repairs"))
                elif not player.skills["off_road"]: opts.append(("Off-Road Driving (Mobility T2) - $30M", 30, "off_road"))
                elif not player.skills["sohc_4_valve"]: opts.append(("SOHC 4-Valve Config (Mobility T3) - $60M", 60, "sohc_4_valve"))
                
                # Spotting Branch
                if not player.skills["situational_awareness"]: opts.append(("Situational Awareness (Spotting T1) - $15M", 15, "situational_awareness"))
                elif not player.skills["recon"]: opts.append(("Recon (Spotting T2) - $30M", 30, "recon"))
                elif not player.skills["aerospace"]: opts.append(("Aerospace Command (Spotting T3) - $100M", 100, "aerospace"))

                # Survivability Branch
                if not player.skills["firefighting"]: opts.append(("Firefighting (Survivability T1) - $15M", 15, "firefighting"))
                elif not player.skills["armorer"]: opts.append(("Armorer (Survivability T2) - $30M", 30, "armorer"))
                elif not player.skills["apex"]: opts.append(("APEX Matrix (Survivability T3) - $200M", 200, "apex"))

                # Concealment Branch
                if not player.skills["camouflage"]: opts.append(("Camouflage (Concealment T1) - $15M", 15, "camouflage"))
                elif not player.skills["quiet_running"]: opts.append(("Quiet Running (Concealment T2) - $30M", 30, "quiet_running"))
                elif not player.skills["loot"]: opts.append(("LOOT Network (Concealment T3) - $75M", 75, "loot"))

                if opts:
                    tech_choice = st.selectbox("Direct Research Funding:", [o[0] for o in opts])
                    if st.button("RESEARCH PROJECT"):
                        selected = next(o for o in opts if o[0] == tech_choice)
                        if player.economy >= selected[1]:
                            player.economy -= selected[1]
                            player.skills[selected[2]] = True
                            st.session_state.action_taken = True
                            st.session_state.log.append(f"🧬 SYSTEM UPGRADE: {selected[2].replace('_', ' ').upper()} online.")
                            st.rerun()
                        else:
                            st.error("SYSTEM ERROR: INSUFFICIENT FUNDS.")
                else:
                    st.success("All tech trees fully maximized.")
            else:
                st.caption("🔒 LABORATORY LOCKED: Awaiting next turn cycle.")

        # Action: AEROSPACE COMMAND
        elif action_mode == "🚀 Aerospace Command":
            if not player.skills["aerospace"]:
                st.warning("⚠️ ACCESS DENIED: Requires 'Aerospace Command' research node.")
            elif not st.session_state.action_taken:
                space_action = st.radio("Aerospace Directives", [
                    "Construct Orbital Strike Satellite (Cost: 100)",
                    "Launch Orbital Strike (Consumes 1 Satellite)"
                ])
                if space_action.startswith("Construct"):
                    if st.button("LAUNCH SATELLITE"):
                        if player.economy >= 100:
                            player.economy -= 100
                            player.units["orbital_satellites"] += 1
                            st.session_state.action_taken = True
                            st.session_state.log.append("🛰️ LEO: Strike Satellite deployed.")
                            st.rerun()
                        else:
                            st.error("SYSTEM ERROR: INSUFFICIENT FUNDS.")
                else:
                    target_name = st.radio("Target Coordinates", [n.name for n in remaining_enemies])
                    if st.button("FIRE ORBITAL BEAM"):
                        if player.units["orbital_satellites"] >= 1:
                            target = next(n for n in nations if n.name == target_name)
                            player.units["orbital_satellites"] -= 1
                            target.is_eliminated = True
                            target.conquered_by = player.name
                            player.economy += target.economy
                            st.session_state.action_taken = True
                            st.session_state.log.append(f"💥 ORBITAL STRIKE: {target.name.upper()} vaporized. Recovered ${target.economy}M.")
                            st.rerun()
                        else:
                            st.error("SYSTEM ERROR: NO ASSETS IN ORBIT.")
            else:
                st.caption("🔒 COMMAND LOCKED: Awaiting next turn cycle.")

        # Action: COVERT OPERATIONS
        elif action_mode == "🕵️ Covert Operations":
            if not st.session_state.action_taken:
                op_cost = 10 if player.skills["loot"] else 20
                st.info(f"Infiltrate and sabotage enemy infrastructure. (Cost: ${op_cost}M)")
                target_name = st.radio("Select Target", [n.name for n in remaining_enemies])
                if st.button("EXECUTE OPERATION"):
                    if player.economy >= op_cost:
                        player.economy -= op_cost
                        target = next(n for n in nations if n.name == target_name)
                        target.war_exhaustion += 4
                        target.economy = max(0, target.economy - 15)
                        apply_casualties(target, severity=0.25)
                        st.session_state.action_taken = True
                        st.session_state.log.append(f"🕵️ INTEL: Sabotage successful in {target.name.upper()}.")
                        st.rerun()
                    else:
                        st.error("SYSTEM ERROR: INSUFFICIENT FUNDS.")
            else:
                st.caption("🔒 INTEL LOCKED: Awaiting next turn cycle.")

        # Action: INVADE
        elif action_mode == "⚔️ Execute Strike":
            if not st.session_state.action_taken:
                target_name = st.radio("Designate Invasion Target", [n.name for n in remaining_enemies])
                if st.button("LAUNCH INVASION"):
                    target = next(n for n in nations if n.name == target_name)
                    
                    atk_roll = player.military_power() + random.uniform(1.0, 8.0)
                    def_roll = target.military_power() + random.uniform(1.0, 8.0)
                    
                    if atk_roll > def_roll:
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        player.economy += target.economy
                        apply_casualties(player, severity=0.15) 
                        st.session_state.log.append(f"VICTORY: {target.name.upper()} captured. Gained ${target.economy}M.")
                    else:
                        player.war_exhaustion += 4
                        apply_casualties(player, severity=0.40) 
                        st.session_state.log.append(f"DEFEAT: Invasion of {target.name.upper()} repulsSED.")
                    
                    st.session_state.action_taken = True
                    st.rerun()
            else:
                st.caption("🔒 MILITARY LOCKED: Awaiting next turn cycle.")

        # Action: END TURN
        elif action_mode == "⏭️ End Turn Cycle":
            if st.button("CONFIRM END CYCLE"):
                econ_gain = 50 if player.skills["apex"] else 30
                player.economy += econ_gain
                if player.war_exhaustion > 0: player.war_exhaustion -= 1 
                
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
    log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-5:])])
    st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
