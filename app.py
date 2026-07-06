import random
import streamlit as st
import plotly.graph_objects as go

# =========================
# GAME ENGINE & CLASSES
# =========================
class Nation: 
    def __init__(self, name, iso_alpha, economy, military_power): 
        self.name = name 
        self.iso_alpha = iso_alpha 
        self.original_name = name  
        self.economy = economy 
        self.base_military = military_power
        self.war_exhaustion = 0 
        self.is_eliminated = False
        self.conquered_by = None
        self.units = { "infantry": 0, "tanks": 0, "jets": 0, "orbital_satellites": 0 }
        
        # 4-Branch Skill Tree Layout
        self.skills = {
            "repairs": False, "off_road": False, "sohc_4_valve": False,
            "situational_awareness": False, "recon": False, "aerospace": False,
            "firefighting": False, "armorer": False, "apex": False,
            "camouflage": False, "quiet_running": False, "loot": False
        }

    def military_power(self):
        if self.is_eliminated: return 0
        
        inf_power = 1
        tank_power = 3
        jet_power = 5
        
        if self.skills["armorer"]: inf_power += 1
        if self.skills["sohc_4_valve"]: tank_power += 2 
        if self.skills["aerospace"]: jet_power += 2
        
        current_power = self.base_military + (self.units["infantry"] * inf_power) + (self.units["tanks"] * tank_power) + (self.units["jets"] * jet_power)
        
        if self.skills["loot"]: current_power *= 1.25 
        
        penalty = max(0.5, 1 - (self.war_exhaustion * 0.05))
        return max(0, current_power * penalty)

def create_nations(): 
    return [ 
        Nation("United States", "USA", 80, 10), Nation("Canada", "CAN", 60, 5), Nation("Mexico", "MEX", 55, 4), 
        Nation("Brazil", "BRA", 70, 7), Nation("United Kingdom", "GBR", 65, 6), Nation("France", "FRA", 65, 6), 
        Nation("Germany", "DEU", 70, 7), Nation("Russia", "RUS", 75, 9), Nation("China", "CHN", 90, 10), 
        Nation("India", "IND", 85, 8), Nation("Japan", "JPN", 70, 6), Nation("Saudi Arabia", "SAU", 85, 5),
        Nation("South Africa", "ZAF", 65, 4), Nation("Australia", "AUS", 70, 5) 
    ]

def apply_casualties(nation, severity=0.3):
    for unit_key in ["infantry", "tanks", "jets"]:
        count = nation.units[unit_key]
        if count > 0:
            lost = random.randint(0, max(1, int(count * severity)))
            if nation.skills["firefighting"]: lost = max(0, lost - 1) 
            nation.units[unit_key] = max(0, count - lost)

# =========================
# INTERACTIVE WORLD MAPPER
# =========================
def render_interactive_map(nations, player):
    locations = []
    z_values = []
    hover_texts = []
    
    # Value keys: 0 = Unoccupied/Defeated AI, 1 = Rival Targets, 2 = Occupied Territories, 3 = Player Core
    colorscale = [[0.0, '#2d232e'], [0.33, '#d95763'], [0.66, '#3e734e'], [1.0, '#597dce']]

    for nation in nations:
        locations.append(nation.iso_alpha)
        if nation.is_eliminated:
            if nation.conquered_by == player.name:
                status_val = 2  
                status_txt = f"Conquered by {player.name.upper()}"
            else:
                status_val = 0  
                status_txt = f"Eliminated by {nation.conquered_by.upper()}"
        else:
            if nation.name == player.name:
                status_val = 3  
                status_txt = "PLAYER EMPIRE HEADQUARTERS"
            else:
                status_val = 1  
                status_txt = f"Active Rival Faction (Mil Power: {nation.military_power():.1f})"
                
        z_values.append(status_val)
        hover_texts.append(f"<b>{nation.name.upper()}</b><br>Status: {status_txt}<br>Economy Portfolio: ${nation.economy}M")

    fig = go.Figure(data=go.Choropleth(
        locations=locations,
        z=z_values,
        text=hover_texts,
        hoverinfo="text",
        colorscale=colorscale,
        showscale=False,
        marker_line_color='#1a1c2c',
        marker_line_width=1.2,
    ))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            backgroundcolor='#1a1c2c',
            bgcolor='#1a1c2c',
            landcolor='#2d232e',
            coastlinecolor='#4a3d4c'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
        paper_bgcolor='#1a1c2c'
    )
    return fig

# =========================
# SKILL NODE COMPONENT
# =========================
def render_skill_node(player, skill_id, display_name, cost, info_html, is_available):
    col_node, col_card = st.columns([1, 4])
    with col_node:
        if player.skills[skill_id]:
            st.markdown("<h3 style='text-align:center; margin:0; padding-top:10px; color:#3bb87c;'>✅</h3>", unsafe_allow_html=True)
        elif is_available and not st.session_state.action_tracking["research"]:
            st.write("")
            if st.button("🟢", key=f"node_{skill_id}"):
                if player.economy >= cost:
                    player.economy -= cost
                    player.skills[skill_id] = True
                    st.session_state.action_tracking["research"] = True
                    st.session_state.log.append(f"🧬 SYSTEM UPGRADE: {display_name.upper()} online.")
                    st.rerun()
                else:
                    st.error("INSUFFICIENT ECONOMY")
        else:
            st.markdown("<h3 style='text-align:center; margin:0; padding-top:10px; color:#4a3d4c;'>🔒</h3>", unsafe_allow_html=True)
            
    with col_card:
        card_border = "#597dce" if player.skills[skill_id] else ("#3bb87c" if is_available else "#4a3d4c")
        st.markdown(f"""
            <div class='skill-card' style='border-color: {card_border}'>
                <b>{display_name}</b> | ${cost}M
                <details class='info-drawer'>
                    <summary>📁 Specs</summary>
                    {info_html}
                </details>
            </div>
        """, unsafe_allow_html=True)

# =========================
# INTERACTIVE CUSTOM UI
# =========================
st.set_page_config(page_title="Global Conquest", layout="wide") 

pixel_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
html, body, [class*="css"], [class*="st-"]  { font-family: 'Press Start 2P', cursive !important; }
.stApp { background-color: #2d232e; color: #f4f4f4; }
h1 { color: #f4f4f4 !important; text-shadow: 4px 4px #d95763; text-align: center; margin-bottom: 20px; font-size: 22px; }
h2, h3 { color: #597dce !important; font-size: 14px; }
div[data-testid="metric-container"] { background-color: #1a1c2c; border: 3px solid #4a3d4c; padding: 8px; box-shadow: 3px 3px 0px #000000; }
div[data-testid="stMetricValue"] { color: #f4f4f4 !important; font-size: 11px !important; }
.stButton>button { border: 4px solid #1a1c2c; background-color: #d95763; color: white; border-radius: 0px; box-shadow: 3px 3px 0px #000000; font-size: 10px; padding: 8px; width: 100%; }
.stButton>button:active { box-shadow: 0px 0px 0px #000000; transform: translateY(3px) translateX(3px); background-color: #ac3232; }
div.row-widget.stRadio > div { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 10px; }
.stRadio label { padding-bottom: 8px; font-size: 10px; }
.terminal-box { background-color: #000000; border: 2px solid #597dce; padding: 12px; color: #3e734e; font-family: monospace !important; font-size: 11px; height: 140px; overflow-y: auto; }
.map-legend { display: flex; justify-content: space-around; background: #1a1c2c; padding: 8px; font-size: 8px; border: 2px solid #4a3d4c; margin-top: -10px; margin-bottom: 15px; }
.legend-item { display: flex; align-items: center; }
.legend-color { width: 12px; height: 12px; margin-right: 6px; border: 1px solid #fff; }

/* Node Cards */
.skill-card { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 8px; margin-bottom: 8px; text-align: center; font-size: 8px; }
.info-drawer { font-size: 7px; margin-top: 4px; text-align: left; background: #2d232e; padding: 4px; border-left: 2px solid #597dce; }
.info-drawer summary { cursor: pointer; color: #597dce; text-align: center; list-style: none; }
.buff-txt { color: #3bb87c; display: block; margin-top: 2px; }
</style>
"""
st.markdown(pixel_css, unsafe_allow_html=True)
st.markdown("<h1>Global Conquest: Retro</h1>", unsafe_allow_html=True)

# =========================
# STATE INITIALIZATION
# =========================
if "game_started" not in st.session_state: 
    st.session_state.game_started = False 
    st.session_state.turn = 1 
    st.session_state.log = ["SYSTEM BOOT SEQUENCE INITIATED...", "AWAITING COMMANDER DIRECTIVE."]
    st.session_state.nations = create_nations()
    st.session_state.action_tracking = {
        "deploy": False, "research": False, "aerospace": False, "covert": False, "strike": False
    }

nations = st.session_state.nations

if not st.session_state.game_started: 
    st.markdown("### INITIALIZE CAMPAIGN")
    choice = st.radio("Select Starting Empire:", [n.name for n in nations]) 
    if st.button("COMMENCE PLANETARY DOMINATION"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()
else: 
    player = st.session_state.player
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    
    if not remaining_enemies:
        st.success("👑 SYSTEM NOTIFICATION: PLANETARY CONQUEST COMPLETE.")
    elif player.is_eliminated:
        st.error(f"💀 EMPIRE CRUSHED BY THE ARMIES OF {player.conquered_by.upper()}.")
    else:
        st.markdown(f"### CYCLE STATUS: TURN {st.session_state.turn}")
        
        # Stats Grid
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 BANK", f"${player.economy}M")
        col2.metric("⚔️ POWER", f"{player.military_power():.1f}")
        col3.metric("🔥 FATIGUE", f"{player.war_exhaustion}")
        
        st.markdown(f"<div style='font-size:8px; text-align:center; padding-bottom:10px;'>Assets: 🎖️ Inf x{player.units['infantry']} | 🚜 Tank x{player.units['tanks']} | ✈️ Jet x{player.units['jets']} | 🛰️ Sat x{player.units['orbital_satellites']}</div>", unsafe_allow_html=True)
        st.write("---")
        
        # Division Status Flags
        d_status = "🔒" if st.session_state.action_tracking['deploy'] else "🟢"
        r_status = "🔒" if st.session_state.action_tracking['research'] else "🟢"
        a_status = "🔒" if st.session_state.action_tracking['aerospace'] else "🟢"
        c_status = "🔒" if st.session_state.action_tracking['covert'] else "🟢"
        s_status = "🔒" if st.session_state.action_tracking['strike'] else "🟢"

        action_mode = st.radio(
            "CHOOSE THE ACTIVE DIVISION:",
            [
                f"🛠️ Requisition & Deploy Assets [{d_status}]", 
                f"🌳 Research Lab Matrix [{r_status}]",
                f"🚀 Stratosphere Flight Command [{a_status}]", 
                f"🕵️ Deep Cover Espionage [{c_status}]",
                f"⚔️ Operational Strike Vector [{s_status}]", 
                "⏭️ Execute End Turn Sequence"
            ]
        )
        st.write("---")
        
        # 1. DEPLOY
        if "🛠️" in action_mode:
            if not st.session_state.action_tracking["deploy"]:
                unit = st.radio("Asset Array Selection:", ["Infantry Battalion ($10M)", "Armored Division ($25M)", "Interceptor Squadron ($40M)"])
                if st.button("DEPLOY REQUISITIONS"):
                    if "Infantry" in unit: cost, key = 10, "infantry"
                    elif "Armored" in unit: cost, key = 25, "tanks"
                    else: cost, key = 40, "jets"
                    
                    if player.economy >= cost:
                        player.economy -= cost
                        player.units[key] += 1
                        st.session_state.action_tracking["deploy"] = True
                        st.session_state.log.append(f"PRODUCTION: {key.upper()} deployed to operational status.")
                        st.rerun()
                    else:
                        st.error("LOGISTICS FAILURE: FUNDS DEFICT.")
            else:
                st.warning("🔒 Logistics deployment locks reset at the turn change.")

        # 2. SKILL TREE (Based on image layout)
        elif "🌳" in action_mode:
            st.markdown("### 🧬 SYSTEM R&D TECHNOLOGY NETWORK")
            if st.session_state.action_tracking["research"]:
                st.warning("🔒 Research vectors filled for current tactical turn loop.")
            
            t1, t2, t3, t4 = st.columns(4)
            
            with t1:
                st.markdown("<span style='color:#e4c34a; font-size:9px;'>⚡ MOBILITY</span>", unsafe_allow_html=True)
                m1 = not player.skills["repairs"]
                render_skill_node(player, "repairs", "Repairs", 15, "Speed up logistics assemblies.<br><span class='buff-txt'>+ Fast tracking production loops.</span>", m1)
                m2 = player.skills["repairs"] and not player.skills["off_road"]
                render_skill_node(player, "off_road", "Off-Road", 30, "All-terrain modular frames.<br><span class='buff-txt'>+ Cuts geographical delay costs.</span>", m2)
                m3 = player.skills["off_road"] and not player.skills["sohc_4_valve"]
                render_skill_node(player, "sohc_4_valve", "SOHC 4V Engine", 60, "High-rev valvetrain updates.<br><span class='buff-txt'>+ Armored Tank Power +2.</span>", m3)
                
            with t2:
                st.markdown("<span style='color:#9c66d1; font-size:9px;'>👁️ SPOTTING</span>", unsafe_allow_html=True)
                s1 = not player.skills["situational_awareness"]
                render_skill_node(player, "situational_awareness", "Sit-Aware", 15, "Automated alert infrastructure.<br><span class='buff-txt'>+ Protects economic networks.</span>", s1)
                s2 = player.skills["situational_awareness"] and not player.skills["recon"]
                render_skill_node(player, "recon", "Recon", 30, "Deep-territory scouts map roots.<br><span class='buff-txt'>+ Softens fail modifiers.</span>", s2)
                s3 = player.skills["recon"] and not player.skills["aerospace"]
                render_skill_node(player, "aerospace", "Aerospace", 100, "Low-Earth tracking satellite grids.<br><span class='buff-txt'>+ Unlocks Orbital Strike matrix.</span>", s3)
                
            with t3:
                st.markdown("<span style='color:#d97e41; font-size:9px;'>🛡️ SURVIVAL</span>", unsafe_allow_html=True)
                v1 = not player.skills["firefighting"]
                render_skill_node(player, "firefighting", "Firefight", 15, "Automated compartment blocks.<br><span class='buff-txt'>+ Limits surprise casualties.</span>", v1)
                v2 = player.skills["firefighting"] and not player.skills["armorer"]
                render_skill_node(player, "armorer", "Armorer", 30, "Reinforced infantry chassis weaves.<br><span class='buff-txt'>+ Infantry Power +1.</span>", v2)
                v3 = player.skills["armorer"] and not player.skills["apex"]
                render_skill_node(player, "apex", "APEX Matrix", 200, "Advanced Predictive Executive Nexus.<br><span class='buff-txt'>+ Step Up turn yield to $50M.</span>", v3)
                
            with t4:
                st.markdown("<span style='color:#3bb87c; font-size:9px;'>🍃 CONCEAL</span>", unsafe_allow_html=True)
                c1 = not player.skills["camouflage"]
                render_skill_node(player, "camouflage", "Camo", 15, "Multi-spectral refractive layers.<br><span class='buff-txt'>+ Lowers defensive threat profile.</span>", c1)
                c2 = player.skills["camouflage"] and not player.skills["quiet_running"]
                render_skill_node(player, "quiet_running", "Quiet Run", 30, "Acoustic vehicle deadeners.<br><span class='buff-txt'>+ Cuts operational exhaustion.</span>", c2)
                c3 = player.skills["quiet_running"] and not player.skills["loot"]
                render_skill_node(player, "loot", "LOOT Net", 75, "Subversive logistics engine.<br><span class='buff-txt'>+ Military Power +25% & cuts Sabotage costs.</span>", c3)

            st.write("---")

        # 3. AEROSPACE COMMAND
        elif "🚀" in action_mode:
            if not player.skills["aerospace"]:
                st.warning("⚠️ SECURITY EXCEPTION: Requires 'Aerospace' integration unlocked in the Science Matrix.")
            elif not st.session_state.action_tracking["aerospace"]:
                space_action = st.radio("Satellite Grid Control Array:", ["Deploy Heavy Strike Uplink ($100M)", "Execute Orbital Ion Beam Fire Loop"])
                if "Deploy" in space_action:
                    if st.button("LAUNCH PLATFORM"):
                        if player.economy >= 100:
                            player.economy -= 100
                            player.units["orbital_satellites"] += 1
                            st.session_state.action_tracking["aerospace"] = True
                            st.session_state.log.append("🛰️ COMMAND: Kinetic strike platform deployed into high orbit.")
                            st.rerun()
                        else:
                            st.error("RESOURCE SHORTAGE.")
                else:
                    target_name = st.radio("Select Uplink Coordinates:", [n.name for n in remaining_enemies])
                    if st.button("INITIATE ION INVERSION BURST"):
                        if player.units["orbital_satellites"] >= 1:
                            target = next(n for n in nations if n.name == target_name)
                            player.units["orbital_satellites"] -= 1
                            target.is_eliminated = True
                            target.conquered_by = player.name
                            player.economy += target.economy
                            st.session_state.action_tracking["aerospace"] = True
                            st.session_state.log.append(f"💥 ION STRIKE: {target.name.upper()} wiped from arrays. Captured ${target.economy}M.")
                            st.rerun()
                        else:
                            st.error("SATELLITE MATRIX OFFLINE: REQUISITION REQUIRED.")
            else:
                st.warning("🔒 Uplink arrays running standard safety cooldown sequences.")

        # 4. COVERT OPS
        elif "🕵️" in action_mode:
            if not st.session_state.action_tracking["covert"]:
                op_cost = 10 if player.skills["loot"] else 20
                st.info(f"Target enemy asset reserves. Operation Cost Matrix: ${op_cost}M")
                target_name = st.radio("Designate Sabotage Infiltration:", [n.name for n in remaining_enemies])
                if st.button("EXECUTE STRIKE CONTRACT"):
                    if player.economy >= op_cost:
                        player.economy -= op_cost
                        target = next(n for n in nations if n.name == target_name)
                        target.war_exhaustion += 4
                        target.economy = max(0, target.economy - 15)
                        apply_casualties(target, severity=0.25)
                        st.session_state.action_tracking["covert"] = True
                        st.session_state.log.append(f"🕵️ NETWORK INTEL: Disrupted production networks in {target.name.upper()}.")
                        st.rerun()
                    else:
                        st.error("TRANSACTION EXCEPTION: SYSTEM FUNDS EMPTY.")
            else:
                st.warning("🔒 Espionage operators hiding tracking trails. Locked until turn reset.")

        # 5. INVADE
        elif "⚔️" in action_mode:
            if not st.session_state.action_tracking["strike"]:
                target_name = st.radio("Select Territorial Target Vector:", [n.name for n in remaining_enemies])
                if st.button("LAUNCH LAND ASSAULT"):
                    target = next(n for n in nations if n.name == target_name)
                    atk_roll = player.military_power() + random.uniform(1.0, 8.0)
                    def_roll = target.military_power() + random.uniform(1.0, 8.0)
                    
                    if atk_roll > def_roll:
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        player.economy += target.economy
                        apply_casualties(player, severity=0.15) 
                        st.session_state.log.append(f"VICTORY: Overran frontlines in {target.name.upper()}. Secured ${target.economy}M.")
                    else:
                        player.war_exhaustion += 4
                        apply_casualties(player, severity=0.40) 
                        st.session_state.log.append(f"TACTICAL BREAK: Assasult vector on {target.name.upper()} collapsed.")
                    
                    st.session_state.action_tracking["strike"] = True
                    st.rerun()
            else:
                st.warning("🔒 Tactical lines organizing replenishment procedures.")

        # 6. END TURN CYCLE
        elif "⏭️" in action_mode:
            if st.button("COMMIT AND FLUSH TURNS"):
                econ_gain = 50 if player.skills["apex"] else 30
                player.economy += econ_gain
                if player.war_exhaustion > 0: player.war_exhaustion -= 1 
                
                for ai in remaining_enemies:
                    ai.economy += 20
                    if ai.economy >= 40:
                        ai.economy -= 40
                        ai.units["tanks"] += 1
                        
                st.session_state.turn += 1
                for key in st.session_state.action_tracking:
                    st.session_state.action_tracking[key] = False
                    
                st.session_state.log.append(f"CYCLE COMPLETE: Beginning Tactical Cycle {st.session_state.turn}.")
                st.rerun()

    # RENDER PLOTLY CHOROPLETH GRAPH INTERACTIVE MAP
    st.plotly_chart(render_interactive_map(nations, player), use_container_width=True, config={'displayModeBar': False})
    
    # Custom Mobile Map Legend
    st.markdown("""
    <div class='map-legend'>
        <div class='legend-item'><div class='legend-color' style='background:#597dce;'></div>Player</div>
        <div class='legend-item'><div class='legend-color' style='background:#d95763;'></div>Rival</div>
        <div class='legend-item'><div class='legend-color' style='background:#3e734e;'></div>Conquered</div>
        <div class='legend-item'><div class='legend-color' style='background:#2d232e;'></div>Defeated/Out</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### STRATEGIC EVENT FEED")
    log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-4:])])
    st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
