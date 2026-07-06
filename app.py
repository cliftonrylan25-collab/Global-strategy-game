import random
import streamlit as st
import plotly.graph_objects as go

# =========================
# GAME ENGINE & CLASSES
# =========================
class Nation: 
    def __init__(self, name, iso_alpha, economy, military_power, perk_desc): 
        self.name = name 
        self.iso_alpha = iso_alpha 
        self.original_name = name  
        self.economy = economy 
        self.base_military = military_power
        self.base_income = 0  
        self.war_exhaustion = 0 
        self.is_eliminated = False
        self.conquered_by = None
        self.units = { "infantry": 0, "tanks": 0, "jets": 0, "orbital_satellites": 0 }
        self.perk_desc = perk_desc
        
        self.skills = {
            "repairs": False, "off_road": False, "sohc_4_valve": False,
            "situational_awareness": False, "recon": False, "aerospace": False,
            "firefighting": False, "armorer": False, "apex": False,
            "camouflage": False, "quiet_running": False, "loot": False
        }

    def military_power(self):
        if self.is_eliminated: return 0
        
        # Base unit power
        inf_power = 2 if self.name == "Canada" else 1
        tank_power = 3
        jet_power = 5
        
        # Skill Tree Buffs
        if self.skills["armorer"]: inf_power += 1
        if self.skills["sohc_4_valve"]: 
            tank_power += 4 if self.name == "Germany" else 2 # GERMANY PERK
        if self.skills["aerospace"]: jet_power += 2
        
        current_power = self.base_military + (self.units["infantry"] * inf_power) + (self.units["tanks"] * tank_power) + (self.units["jets"] * jet_power)
        
        if self.skills["loot"]: current_power *= 1.25 
        
        penalty = max(0.5, 1 - (self.war_exhaustion * 0.05))
        return max(0, current_power * penalty)

def create_nations(): 
    nations = [ 
        Nation("United States", "USA", 80, 10, "Air Superiority: Starts with Aerospace Unlocked"), 
        Nation("Canada", "CAN", 60, 5, "Northern Guard: Base Infantry Power +1"), 
        Nation("Mexico", "MEX", 55, 4, "Cartel Bounties: Starts with +$2M Base Income"), 
        Nation("Brazil", "BRA", 70, 7, "Jungle Tactics: Starts with Off-Road Unlocked"), 
        Nation("United Kingdom", "GBR", 65, 6, "Naval Heritage: Starts with +$2M Base Income"), 
        Nation("France", "FRA", 65, 6, "Foreign Legion: Infantry Deployments cost $8M"), 
        Nation("Germany", "DEU", 70, 7, "Advanced Engineering: SOHC 4V upgrade gives Tanks +4 Power"), 
        Nation("Russia", "RUS", 75, 9, "Winter Attrition: Failed attacks against RUS yield +2 Exhaustion"), 
        Nation("China", "CHN", 90, 10, "Mass Production: Infantry Deployments cost $5M"), 
        Nation("India", "IND", 85, 8, "Tech Hub: Research Nodes cost 20% less"), 
        Nation("Japan", "JPN", 70, 6, "Keiretsu: Jet Deployments cost $30M (Normally $40M)"), 
        Nation("Saudi Arabia", "SAU", 85, 5, "Oil Baron: Starts with an extra $50M in the bank"),
        Nation("South Africa", "ZAF", 65, 4, "Diamond Mines: Starts with +$2M Base Income"), 
        Nation("Australia", "AUS", 70, 5, "Isolationist: Highly unlikely to be targeted by AI") 
    ]
    
    # Apply initial perks
    for n in nations:
        if n.name == "United States": n.skills["aerospace"] = True
        elif n.name == "Brazil": n.skills["off_road"] = True
        elif n.name in ["Mexico", "United Kingdom", "South Africa"]: n.base_income += 2
        elif n.name == "Saudi Arabia": n.economy += 50
            
    return nations

def apply_casualties(nation, severity=0.3):
    for unit_key in ["infantry", "tanks", "jets"]:
        count = nation.units[unit_key]
        if count > 0:
            lost = random.randint(0, max(1, int(count * severity)))
            if nation.skills["firefighting"]: lost = max(0, lost - 1) 
            nation.units[unit_key] = max(0, count - lost)

# =========================
# COMBAT & TACTICAL RPS
# =========================
def resolve_combat(attacker, defender):
    # Rock Paper Scissors Tactical Modifiers
    rps_bonus = 0
    # Tanks crush Infantry
    if attacker.units["tanks"] > 0 and defender.units["infantry"] > 0: rps_bonus += 3
    # Jets crush Tanks
    if attacker.units["jets"] > 0 and defender.units["tanks"] > 0: rps_bonus += 4
    # Infantry (AA) shoots down Jets
    if attacker.units["infantry"] > 0 and defender.units["jets"] > 0: rps_bonus += 2
    
    atk_roll = attacker.military_power() + rps_bonus + random.uniform(1.0, 8.0)
    def_roll = defender.military_power() + random.uniform(1.0, 8.0)
    
    return atk_roll > def_roll

# =========================
# STABLE INTERACTIVE MAP
# =========================
def render_interactive_map(nations, player):
    locations, z_values, hover_texts = [], [], []
    colorscale = [[0.0, '#2d232e'], [0.33, '#d95763'], [0.66, '#3e734e'], [1.0, '#597dce']]

    for nation in nations:
        locations.append(nation.iso_alpha)
        if nation.is_eliminated:
            val = 2 if nation.conquered_by == player.name else 0
            status_txt = f"Conquered by {player.name.upper()}" if nation.conquered_by == player.name else f"Eliminated by {nation.conquered_by.upper()}"
            hover_text = f"<b>{nation.name.upper()}</b><br>Status: {status_txt}"
        else:
            if nation.name == player.name:
                val = 3
                hover_text = f"<b>{nation.name.upper()}</b><br>PLAYER HEADQUARTERS<br>Bonus Income: +${player.base_income}M/Turn"
            else:
                val = 1
                loot = int(nation.economy * 0.5)
                hover_text = f"<b>{nation.name.upper()}</b><br>Power: {nation.military_power():.1f}<br>Perk: {nation.perk_desc}<br>💰 Conquest Loot: ${loot}M"
        z_values.append(val)
        hover_texts.append(hover_text)

    fig = go.Figure(
        data=go.Choropleth(
            locations=locations, z=z_values, text=hover_texts, hoverinfo="text",
            colorscale=colorscale, showscale=False, marker_line_color='#1a1c2c', marker_line_width=1.2,
        ),
        layout=dict(
            margin={"r":0,"t":0,"l":0,"b":0}, height=320, paper_bgcolor='#1a1c2c', plot_bgcolor='#1a1c2c',
            geo=dict( showframe=False, showcoastlines=True, projection_type='equirectangular', showland=True,
                landcolor='#2d232e', coastlinecolor='#4a3d4c', showocean=False, showcountries=True, countrycolor='#4a3d4c' )
        )
    )
    return fig

# =========================
# SKILL NODE COMPONENT
# =========================
def render_skill_node(player, skill_id, display_name, base_cost, info_html, is_available, event_active):
    # Apply Tech Boom event & India Perk
    cost = int(base_cost * 0.5) if event_active == "Tech Boom" else base_cost
    if player.name == "India": cost = int(cost * 0.8)
    
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
                    <summary>📁 Specs</summary>{info_html}
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
div[data-testid="metric-container"] { background-color: #1a1c2c; border: 3px solid #4a3d4c; padding: 8px; box-shadow: 3px 3px 0px #000000; }
div[data-testid="stMetricValue"] { color: #f4f4f4 !important; font-size: 11px !important; }
.stButton>button { border: 4px solid #1a1c2c; background-color: #d95763; color: white; border-radius: 0px; box-shadow: 3px 3px 0px #000000; font-size: 10px; padding: 8px; width: 100%; }
.stButton>button:active { box-shadow: 0px 0px 0px #000000; transform: translateY(3px) translateX(3px); background-color: #ac3232; }
div.row-widget.stRadio > div { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 10px; }
.stRadio label { padding-bottom: 8px; font-size: 10px; }
.terminal-box { background-color: #000000; border: 2px solid #597dce; padding: 12px; color: #3e734e; font-family: monospace !important; font-size: 11px; height: 140px; overflow-y: auto; margin-bottom: 15px;}
.map-legend { display: flex; justify-content: space-around; background: #1a1c2c; padding: 8px; font-size: 8px; border: 2px solid #4a3d4c; margin-top: -10px; margin-bottom: 15px; }
.legend-item { display: flex; align-items: center; }
.legend-color { width: 12px; height: 12px; margin-right: 6px; border: 1px solid #fff; }
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
    st.session_state.current_event = None
    st.session_state.log = ["SYSTEM BOOT SEQUENCE INITIATED...", "AWAITING COMMANDER DIRECTIVE."]
    st.session_state.nations = create_nations()
    st.session_state.action_tracking = { "deploy": False, "research": False, "aerospace": False, "covert": False, "strike": False }

nations = st.session_state.nations

if not st.session_state.game_started: 
    st.markdown("### INITIALIZE CAMPAIGN")
    st.info("Pick your empire. Each nation has unique strategic perks.")
    
    choice_options = [f"{n.name} | {n.perk_desc}" for n in nations]
    selected_str = st.radio("Select Starting Empire:", choice_options)
    choice = selected_str.split(" | ")[0]
    
    if st.button("COMMENCE PLANETARY DOMINATION"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()
else: 
    player = st.session_state.player
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    
    if not remaining_enemies:
        st.success("👑 SYSTEM NOTIFICATION: PLANETARY CONQUEST COMPLETE.")
        st.balloons()
    elif player.is_eliminated:
        st.error(f"💀 GAME OVER: YOUR EMPIRE WAS CRUSHED BY {player.conquered_by.upper()}.")
    else:
        st.markdown(f"### CYCLE STATUS: TURN {st.session_state.turn}")
        
        if st.session_state.current_event:
            st.warning(f"🚨 GLOBAL EVENT ACTIVE: {st.session_state.current_event}")
        
        # Stats Grid
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 BANK", f"${player.economy}M")
        col2.metric("⚔️ POWER", f"{player.military_power():.1f}")
        col3.metric("🔥 FATIGUE", f"{player.war_exhaustion}")
        st.markdown(f"<div style='font-size:8px; text-align:center; padding-bottom:10px;'>Assets: 🎖️ Inf x{player.units['infantry']} | 🚜 Tank x{player.units['tanks']} | ✈️ Jet x{player.units['jets']} | 🛰️ Sat x{player.units['orbital_satellites']}</div>", unsafe_allow_html=True)
        
        # NEW: MOVED LOG TO TOP
        log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-5:])])
        st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
        st.write("---")
        
        d_status = "🔒" if st.session_state.action_tracking['deploy'] else "🟢"
        r_status = "🔒" if st.session_state.action_tracking['research'] else "🟢"
        a_status = "🔒" if st.session_state.action_tracking['aerospace'] else "🟢"
        c_status = "🔒" if st.session_state.action_tracking['covert'] else "🟢"
        s_status = "🔒" if st.session_state.action_tracking['strike'] else "🟢"

        action_mode = st.radio(
            "CHOOSE THE ACTIVE DIVISION:",
            [
                f"🛠️ Requisition & Deploy Assets [{d_status}]", f"🌳 Research Lab Matrix [{r_status}]",
                f"🚀 Stratosphere Flight Command [{a_status}]", f"🕵️ Deep Cover Espionage [{c_status}]",
                f"⚔️ Operational Strike Vector [{s_status}]", "⏭️ Execute End Turn Sequence"
            ]
        )
        st.write("---")
        
        # 1. DEPLOY
        if "🛠️" in action_mode:
            if not st.session_state.action_tracking["deploy"]:
                # Perks affecting costs
                inf_cost = 5 if player.name == "China" else (8 if player.name == "France" else 10)
                jet_cost = 30 if player.name == "Japan" else 40
                
                unit = st.radio("Asset Array Selection:", [f"Infantry Battalion (${inf_cost}M)", f"Armored Division ($25M)", f"Interceptor Squadron (${jet_cost}M)"])
                if st.button("DEPLOY REQUISITIONS"):
                    if "Infantry" in unit: cost, key = inf_cost, "infantry"
                    elif "Armored" in unit: cost, key = 25, "tanks"
                    else: cost, key = jet_cost, "jets"
                    
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

        # 2. SKILL TREE
        elif "🌳" in action_mode:
            st.markdown("### 🧬 SYSTEM R&D TECHNOLOGY NETWORK")
            if st.session_state.action_tracking["research"]: st.warning("🔒 Research vectors filled for current tactical turn loop.")
            
            t1, t2, t3, t4 = st.columns(4)
            evt = st.session_state.current_event
            
            with t1:
                st.markdown("<span style='color:#e4c34a; font-size:9px;'>⚡ MOBILITY</span>", unsafe_allow_html=True)
                render_skill_node(player, "repairs", "Repairs", 15, "Speed up logistics.<br><span class='buff-txt'>+ Fast tracking.</span>", not player.skills["repairs"], evt)
                render_skill_node(player, "off_road", "Off-Road", 30, "All-terrain modular frames.<br><span class='buff-txt'>+ Cuts delay.</span>", player.skills["repairs"] and not player.skills["off_road"], evt)
                render_skill_node(player, "sohc_4_valve", "SOHC 4V", 60, "High-rev valvetrain updates.<br><span class='buff-txt'>+ Armored Tank Power +2.</span>", player.skills["off_road"] and not player.skills["sohc_4_valve"], evt)
                
            with t2:
                st.markdown("<span style='color:#9c66d1; font-size:9px;'>👁️ SPOTTING</span>", unsafe_allow_html=True)
                render_skill_node(player, "situational_awareness", "Sit-Aware", 15, "Automated alert infrastructure.", not player.skills["situational_awareness"], evt)
                render_skill_node(player, "recon", "Recon", 30, "Deep-territory scouts.<br><span class='buff-txt'>+ Softens fail modifiers.</span>", player.skills["situational_awareness"] and not player.skills["recon"], evt)
                render_skill_node(player, "aerospace", "Aerospace", 100, "Low-Earth tracking grids.<br><span class='buff-txt'>+ Unlocks Orbital Strikes.</span>", player.skills["recon"] and not player.skills["aerospace"], evt)
                
            with t3:
                st.markdown("<span style='color:#d97e41; font-size:9px;'>🛡️ SURVIVAL</span>", unsafe_allow_html=True)
                render_skill_node(player, "firefighting", "Firefight", 15, "Automated compartment blocks.", not player.skills["firefighting"], evt)
                render_skill_node(player, "armorer", "Armorer", 30, "Reinforced infantry chassis.<br><span class='buff-txt'>+ Inf Power +1.</span>", player.skills["firefighting"] and not player.skills["armorer"], evt)
                render_skill_node(player, "apex", "APEX Matrix", 200, "Advanced Predictive Executive Matrix.<br><span class='buff-txt'>+ Turn yield to $50M.</span>", player.skills["armorer"] and not player.skills["apex"], evt)
                
            with t4:
                st.markdown("<span style='color:#3bb87c; font-size:9px;'>🍃 CONCEAL</span>", unsafe_allow_html=True)
                render_skill_node(player, "camouflage", "Camo", 15, "Refractive layers.", not player.skills["camouflage"], evt)
                render_skill_node(player, "quiet_running", "Quiet Run", 30, "Acoustic vehicle deadeners.", player.skills["camouflage"] and not player.skills["quiet_running"], evt)
                render_skill_node(player, "loot", "LOOT Net", 75, "Subversive logistics engine.<br><span class='buff-txt'>+ Military Power +25%.</span>", player.skills["quiet_running"] and not player.skills["loot"], evt)

            st.write("---")

        # 3. AEROSPACE COMMAND
        elif "🚀" in action_mode:
            if st.session_state.current_event == "Orbital Debris":
                st.error("⚠️ HIGH ORBIT DEBRIS FIELD: Satellite systems offline this turn.")
            elif not player.skills["aerospace"]:
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
                        else: st.error("RESOURCE SHORTAGE.")
                else:
                    target_name = st.radio("Select Uplink Coordinates:", [n.name for n in remaining_enemies])
                    if st.button("INITIATE ION INVERSION BURST"):
                        if player.units["orbital_satellites"] >= 1:
                            target = next(n for n in nations if n.name == target_name)
                            player.units["orbital_satellites"] -= 1
                            target.is_eliminated = True
                            target.conquered_by = player.name
                            loot = int(target.economy * 0.5)
                            player.economy += loot
                            player.base_income += 5
                            st.session_state.action_tracking["aerospace"] = True
                            st.session_state.log.append(f"💥 ION STRIKE: {target.name.upper()} wiped. Looted ${loot}M & +$5M/Turn.")
                            st.rerun()
                        else: st.error("SATELLITE MATRIX OFFLINE: REQUISITION REQUIRED.")
            else: st.warning("🔒 Uplink arrays running standard safety cooldown sequences.")

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
                    else: st.error("TRANSACTION EXCEPTION: SYSTEM FUNDS EMPTY.")
            else: st.warning("🔒 Espionage operators hiding tracking trails. Locked until turn reset.")

        # 5. INVADE
        elif "⚔️" in action_mode:
            if not st.session_state.action_tracking["strike"]:
                st.info("💡 TACTICAL INTEL: Tanks beat Infantry, Jets beat Tanks, Infantry (AA) beat Jets.")
                target_name = st.radio("Select Territorial Target Vector:", [n.name for n in remaining_enemies])
                if st.button("LAUNCH LAND ASSAULT"):
                    target = next(n for n in nations if n.name == target_name)
                    
                    if resolve_combat(player, target):
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        loot = int(target.economy * 0.5)
                        player.economy += loot
                        player.base_income += 5
                        apply_casualties(player, severity=0.15) 
                        st.session_state.log.append(f"VICTORY: Annexed {target.name.upper()}! Secured ${loot}M & +$5M/Turn.")
                    else:
                        penalty = 6 if target.name == "Russia" else 4 # RUSSIA PERK
                        player.war_exhaustion += penalty
                        apply_casualties(player, severity=0.40) 
                        st.session_state.log.append(f"TACTICAL BREAK: Assault on {target.name.upper()} collapsed. Exhaustion +{penalty}.")
                        
                        # COUNTER-ATTACK LOGIC
                        if random.random() < 0.3:
                            st.session_state.log.append(f"⚠️ AMBUSH: {target.name.upper()} launched a rapid counter-offensive!")
                            apply_casualties(player, severity=0.20)
                    
                    st.session_state.action_tracking["strike"] = True
                    st.rerun()
            else: st.warning("🔒 Tactical lines organizing replenishment procedures.")

        # 6. END TURN CYCLE (WITH AI & EVENTS)
        elif "⏭️" in action_mode:
            if st.button("COMMIT AND FLUSH TURNS"):
                
                # Dynamic Events Generation
                event_roll = random.random()
                if event_roll < 0.10: st.session_state.current_event = "Market Crash" # Income halved
                elif event_roll < 0.20: st.session_state.current_event = "Tech Boom" # Research halved
                elif event_roll < 0.30: st.session_state.current_event = "Orbital Debris" # No space
                elif event_roll < 0.40: st.session_state.current_event = "Economic Boom" # Extra cash
                else: st.session_state.current_event = None

                # Player Income
                base_yield = 50 if player.skills["apex"] else 30
                econ_gain = base_yield + player.base_income 
                if st.session_state.current_event == "Market Crash": econ_gain = int(econ_gain * 0.5)
                if st.session_state.current_event == "Economic Boom": econ_gain += 30
                
                player.economy += econ_gain
                if player.war_exhaustion > 0: player.war_exhaustion -= 1 
                
                # Aggressive AI Loop
                for ai in remaining_enemies:
                    if ai.is_eliminated: continue
                    
                    ai.economy += 20 + ai.base_income
                    if st.session_state.current_event == "Market Crash": ai.economy -= 10
                    
                    # AI Purchasing
                    if ai.economy >= 40:
                        ai.economy -= 40
                        ai.units[random.choice(["infantry", "tanks", "jets"])] += 1
                        
                    # AI War Declarations (15% chance to attack per turn)
                    if random.random() < 0.15 and ai.military_power() > 10:
                        potential_targets = [n for n in nations if n != ai and not n.is_eliminated]
                        # Australia Perk (Harder for AI to target)
                        potential_targets = [n for n in potential_targets if not (n.name == "Australia" and random.random() < 0.7)]
                        
                        if potential_targets:
                            target = random.choice(potential_targets)
                            
                            # AI resolves combat
                            if resolve_combat(ai, target):
                                target.is_eliminated = True
                                target.conquered_by = ai.name
                                ai.economy += int(target.economy * 0.5)
                                ai.base_income += 5
                                
                                if target.name == player.name:
                                    st.session_state.log.append(f"🚨 FATAL BREACH: {ai.name.upper()} successfully invaded our headquarters!")
                                else:
                                    st.session_state.log.append(f"🌍 GLOBAL NEWS: {ai.name.upper()} conquered {target.name.upper()}.")
                            else:
                                ai.war_exhaustion += 2

                st.session_state.turn += 1
                for key in st.session_state.action_tracking: st.session_state.action_tracking[key] = False
                st.session_state.log.append(f"CYCLE COMPLETE: Turn {st.session_state.turn} | Tax Yield: ${econ_gain}M.")
                st.rerun()

    # RENDER PLOTLY MAP
    st.plotly_chart(render_interactive_map(nations, player), use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("""
    <div class='map-legend'>
        <div class='legend-item'><div class='legend-color' style='background:#597dce;'></div>Player</div>
        <div class='legend-item'><div class='legend-color' style='background:#d95763;'></div>Rival</div>
        <div class='legend-item'><div class='legend-color' style='background:#3e734e;'></div>Conquered</div>
        <div class='legend-item'><div class='legend-color' style='background:#2d232e;'></div>Defeated</div>
    </div>
    """, unsafe_allow_html=True)
