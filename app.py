import random
import streamlit as st
import plotly.graph_objects as go

# =========================
# GAME ENGINE & CLASSES
# =========================
class Nation: 
    def __init__(self, name, iso_codes, economy, military_power, perk_desc, is_cluster=False): 
        self.name = name 
        self.iso_codes = iso_codes # Now accepts a list of ISO alpha-3 codes
        self.economy = economy 
        self.base_military = military_power
        self.base_income = 0  
        self.war_exhaustion = 0 
        self.is_eliminated = False
        self.conquered_by = None
        self.is_cluster = is_cluster
        self.district = "None"  
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
        
        inf_power = 2 if self.name == "Canada" else 1
        tank_power = 3
        jet_power = 5
        
        if self.skills["armorer"]: inf_power += 1
        if self.skills["sohc_4_valve"]: 
            tank_power += 4 if self.name == "Germany" else 2 
        if self.skills["aerospace"]: jet_power += 2
        
        current_power = self.base_military + (self.units["infantry"] * inf_power) + (self.units["tanks"] * tank_power) + (self.units["jets"] * jet_power)
        
        if self.district == "Garrison": current_power += 6
        if self.district == "Factory": current_power += 10
        if self.skills["loot"]: current_power *= 1.25 
        
        penalty = max(0.4, 1 - (self.war_exhaustion * 0.05))
        return max(0, current_power * penalty)

def create_nations(): 
    nations = [ 
        # MAJOR POWERS
        Nation("United States", ["USA"], 85, 12, "Air Superiority: Starts with Aerospace tech"), 
        Nation("Canada", ["CAN"], 60, 6, "Northern Guard: Infantry possess +1 Power"), 
        Nation("Mexico", ["MEX"], 55, 5, "Border Tolls: Permanently yields +$3M income"), 
        Nation("Brazil", ["BRA"], 70, 8, "Jungle Canopy: Starts with Off-Road tech"), 
        Nation("United Kingdom", ["GBR"], 70, 7, "Maritime Finance: Commences with +$3M income"), 
        Nation("France", ["FRA"], 65, 7, "Foreign Legion: Infantry deployment optimized to $7M"), 
        Nation("Germany", ["DEU"], 75, 9, "Advanced Engineering: SOHC 4V upgrade gives Tanks +4 Power"), 
        Nation("Russia", ["RUS"], 80, 11, "Winter Attrition: Failed attacks against RUS inflict +2 Exhaustion"), 
        Nation("China", ["CHN"], 95, 12, "Mass Production Engine: Infantry deployments cost $5M"), 
        Nation("India", ["IND"], 85, 9, "Tech Infrastructure Hub: Research Nodes discounted 25%"), 
        Nation("Japan", ["JPN"], 75, 7, "Industrial Conglomerate: Interceptors discounted to $30M"), 
        Nation("Saudi Arabia", ["SAU"], 90, 6, "Sovereign Wealth: Starts with an extra $60M reserves"),
        Nation("South Africa", ["ZAF"], 65, 5, "Mineral Reserves: Permanently yields +$3M income"), 
        Nation("Australia", ["AUS"], 70, 6, "Deep Isolation: Highly secure geographic profile"),
        
        # REGIONAL CLUSTERS
        Nation("European Union", ['ITA', 'ESP', 'POL', 'SWE', 'NOR', 'FIN', 'ROU', 'NLD', 'BEL', 'GRC', 'PRT', 'CZE', 'HUN', 'AUT', 'CHE', 'BGR', 'DNK', 'SVK', 'IRL', 'HRV', 'LTU', 'SVN', 'LVA', 'EST'], 140, 15, "Continental Coalition: High combined military and economic yield", True),
        Nation("South American Coalition", ['ARG', 'COL', 'PER', 'VEN', 'CHL', 'ECU', 'BOL', 'PRY', 'URY', 'GUY', 'SUR'], 110, 10, "Resource Cartels: Extensive natural reserves", True),
        Nation("African Continental Bloc", ['NGA', 'ETH', 'EGY', 'COD', 'TZA', 'KEN', 'UGA', 'DZA', 'SDN', 'MAR', 'AGO', 'GHA', 'MOZ', 'MDG', 'CIV', 'CMR', 'NER', 'BFA', 'MLI', 'MWI', 'ZMB', 'SEN', 'TCD', 'SOM', 'ZWE', 'GIN', 'RWA', 'BEN', 'BDI', 'SSD', 'ERI', 'SLE', 'TGO', 'LBY', 'CAF', 'MRT', 'COG', 'LBR', 'NAM', 'BWA', 'GMB', 'GAB', 'LSO', 'GNB', 'GNQ', 'MUS', 'SWZ', 'DJI'], 130, 11, "Emerging Markets: Massive population defense lines", True),
        Nation("Middle East Pact", ['IRN', 'TUR', 'IRQ', 'YEM', 'SYR', 'JOR', 'ARE', 'ISR', 'LBN', 'OMN', 'KWT', 'QAT'], 120, 14, "Petro-State Defense: Hardened military fronts", True),
        Nation("Southeast Asian Alliance", ['IDN', 'PHL', 'VNM', 'THA', 'MMR', 'MYS', 'KHM', 'LAO', 'SGP', 'BRN', 'TLS'], 115, 10, "Archipelago Network: Distributed economy", True),
        Nation("Central Asian Federation", ['PAK', 'BGD', 'AFG', 'UZB', 'NPL', 'KAZ', 'LKA', 'TJK', 'KGZ', 'TKM', 'BTN', 'MNG'], 105, 9, "Steppe Vanguard: Difficult terrain defense", True),
        Nation("Caribbean League", ['GTM', 'CUB', 'HTI', 'DOM', 'HND', 'NIC', 'SLV', 'CRI', 'PAN', 'JAM', 'TTO', 'BHS'], 80, 5, "Trade Gateways: Canal and shipping logistics", True),
        Nation("Oceania Syndicate", ['NZL', 'PNG', 'FJI', 'SLB', 'VUT', 'WSM'], 60, 4, "Pacific Reach: Isolated island chains", True)
    ]
    
    for n in nations:
        if n.name == "United States": n.skills["aerospace"] = True
        elif n.name == "Brazil": n.skills["off_road"] = True
        elif n.name in ["Mexico", "United Kingdom", "South Africa"]: n.base_income += 3
        elif n.name == "Saudi Arabia": n.economy += 60
            
    return nations

def apply_casualties(nation, severity=0.3):
    for unit_key in ["infantry", "tanks", "jets"]:
        count = nation.units[unit_key]
        if count > 0:
            lost = random.randint(0, max(1, int(count * severity)))
            if nation.skills["firefighting"]: lost = max(0, lost - 1) 
            nation.units[unit_key] = max(0, count - lost)

# =========================
# COMBAT ENGINE WITH RPS
# =========================
def resolve_combat(attacker, defender):
    rps_bonus = 0
    if attacker.units["tanks"] > defender.units["infantry"] and defender.units["infantry"] > 0: rps_bonus += 4
    if attacker.units["jets"] > defender.units["tanks"] and defender.units["tanks"] > 0: rps_bonus += 5
    if attacker.units["infantry"] > defender.units["jets"] and defender.units["jets"] > 0: rps_bonus += 3
    
    def_district_bonus = 8 if defender.district == "Garrison" else 0
    
    atk_roll = attacker.military_power() + rps_bonus + random.uniform(1.0, 10.0)
    def_roll = defender.military_power() + def_district_bonus + random.uniform(1.0, 10.0)
    
    return atk_roll > def_roll

# =========================
# GEOGRAPHIC CHOROPLETH MAP
# =========================
def render_interactive_map(nations, player):
    locations, z_values, hover_texts = [], [], []
    colorscale = [[0.0, '#2d232e'], [0.33, '#d95763'], [0.66, '#3e734e'], [1.0, '#597dce']]

    for nation in nations:
        # Determine status text and values once per nation
        if nation.is_eliminated:
            val = 2 if nation.conquered_by == player.name else 0
            status_txt = f"Annexed by {player.name.upper()}" if nation.conquered_by == player.name else f"Held by {nation.conquered_by.upper()}"
            hover_text = f"<b>{nation.name.upper()}</b><br>Status: {status_txt}<br>Sector Specialization: {nation.district}"
        else:
            if nation.name == player.name:
                val = 3
                hover_text = f"<b>{nation.name.upper()}</b><br>EMPIRE CENTRAL COMMAND<br>Infrastructure Specialization: {nation.district}<br>Dividends: +${player.base_income}M/Turn"
            else:
                val = 1
                loot = int(nation.economy * 0.5)
                type_desc = "Regional Faction Cluster" if nation.is_cluster else "Active Sovereign Rival"
                hover_text = f"<b>{nation.name.upper()}</b><br>Status: {type_desc}<br>Combat Rating: {nation.military_power():.1f}<br>Perk: {nation.perk_desc}<br>💰 Loot Yield: ${loot}M"

        # Apply to all ISO codes associated with this Nation/Cluster
        for iso_code in nation.iso_codes:
            locations.append(iso_code)
            z_values.append(val)
            hover_texts.append(hover_text)

    fig = go.Figure(
        data=go.Choropleth(
            locations=locations, z=z_values, text=hover_texts, hoverinfo="text",
            colorscale=colorscale, showscale=False, marker_line_color='#1a1c2c', marker_line_width=1.2,
        ),
        layout=dict(
            margin={"r":0,"t":0,"l":0,"b":0}, height=340, paper_bgcolor='#1a1c2c', plot_bgcolor='#1a1c2c',
            geo=dict( showframe=False, showcoastlines=True, projection_type='equirectangular', showland=True,
                landcolor='#2d232e', coastlinecolor='#4a3d4c', showocean=False, showcountries=True, countrycolor='#4a3d4c' )
        )
    )
    return fig

# =========================
# RESEARCH NETWORK NODE
# =========================
def render_skill_node(player, skill_id, display_name, base_cost, info_html, is_available, current_event):
    cost = int(base_cost * 0.5) if current_event == "Tech Boom" else base_cost
    if player.name == "India": cost = int(cost * 0.75)
    
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
                    st.session_state.log.append(f"🧬 MATRIX LINKED: {display_name.upper()} integration successful.")
                    st.rerun()
                else: st.error("CREDIT DEFICIT")
        else: st.markdown("<h3 style='text-align:center; margin:0; padding-top:10px; color:#4a3d4c;'>🔒</h3>", unsafe_allow_html=True)
            
    with col_card:
        card_border = "#597dce" if player.skills[skill_id] else ("#3bb87c" if is_available else "#4a3d4c")
        st.markdown(f"""
            <div class='skill-card' style='border-color: {card_border}'>
                <b>{display_name}</b> | ${cost}M
                <details class='info-drawer'>
                    <summary>📁 Specifications</summary>{info_html}
                </details>
            </div>
        """, unsafe_allow_html=True)

# =========================
# CUSTOM GRAPHICS COMPONENT
# =========================
st.set_page_config(page_title="Global Conquest: BETA", layout="wide") 

pixel_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
html, body, [class*="css"], [class*="st-"]  { font-family: 'Press Start 2P', cursive !important; }
.stApp { background-color: #2d232e; color: #f4f4f4; }
h1 { color: #f4f4f4 !important; text-shadow: 4px 4px #d95763; text-align: center; margin-bottom: 20px; font-size: 24px; }
h2, h3 { color: #597dce !important; font-size: 13px; }
div[data-testid="metric-container"] { background-color: #1a1c2c; border: 3px solid #4a3d4c; padding: 10px; box-shadow: 4px 4px 0px #000000; }
div[data-testid="stMetricValue"] { color: #f4f4f4 !important; font-size: 12px !important; }
.stButton>button { border: 4px solid #1a1c2c; background-color: #d95763; color: white; border-radius: 0px; box-shadow: 3px 3px 0px #000000; font-size: 10px; padding: 10px; width: 100%; }
.stButton>button:active { box-shadow: 0px 0px 0px #000000; transform: translateY(3px) translateX(3px); background-color: #ac3232; }
div.row-widget.stRadio > div { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 12px; }
.stRadio label { padding-bottom: 8px; font-size: 10px; }
.terminal-box { background-color: #000000; border: 3px solid #597dce; padding: 14px; color: #3bb87c; font-family: monospace !important; font-size: 11px; height: 160px; overflow-y: auto; margin-bottom: 20px;}
.map-legend { display: flex; justify-content: space-around; background: #1a1c2c; padding: 8px; font-size: 8px; border: 2px solid #4a3d4c; margin-top: -10px; margin-bottom: 15px; }
.legend-item { display: flex; align-items: center; }
.legend-color { width: 12px; height: 12px; margin-right: 6px; border: 1px solid #fff; }
.skill-card { background-color: #1a1c2c; border: 2px solid #4a3d4c; padding: 8px; margin-bottom: 8px; text-align: center; font-size: 8px; }
.info-drawer { font-size: 7px; margin-top: 4px; text-align: left; background: #2d232e; padding: 6px; border-left: 2px solid #597dce; }
.info-drawer summary { cursor: pointer; color: #597dce; text-align: center; list-style: none; }
.buff-txt { color: #3bb87c; display: block; margin-top: 2px; }
.dilemma-box { background-color: #1a1c2c; border: 4px dashed #d95763; padding: 15px; margin-bottom: 20px; }
</style>
"""
st.markdown(pixel_css, unsafe_allow_html=True)
st.markdown("<h1>Global Conquest: Regional Expansion</h1>", unsafe_allow_html=True)

# =========================
# STATE SEEDING
# =========================
if "game_started" not in st.session_state: 
    st.session_state.game_started = False 
    st.session_state.turn = 1 
    st.session_state.current_event = None
    st.session_state.active_dilemma = None
    st.session_state.log = ["TACTICAL MATRIX DEPLOYED...", "AWAITING PERK PROFILES REQUISITION."]
    st.session_state.nations = create_nations()
    st.session_state.action_tracking = { "deploy": False, "research": False, "aerospace": False, "covert": False, "strike": False, "infrastructure": False }

nations = st.session_state.nations

if not st.session_state.game_started: 
    st.markdown("### 🖥️ CAMPAIGN CHARACTER ALLOCATION")
    st.info("Select your starting faction. Global AI entities and Regional Clusters will adopt remaining territory.")
    
    choice_options = [f"{n.name} | {n.perk_desc}" for n in nations if not n.is_cluster]
    selected_str = st.radio("Select Starting Empire:", choice_options)
    choice = selected_str.split(" | ")[0]
    
    if st.button("LAUNCH STRATEGIC ENGINE"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()
else: 
    player = st.session_state.player
    remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
    conquered_territories = [n for n in nations if n.conquered_by == player.name]
    
    if not remaining_enemies:
        st.success("👑 CAMPAIGN COMPLETE: GLOBAL SYSTEM CONQUERED.")
        st.balloons()
    elif player.is_eliminated:
        st.error(f"💀 CRITICAL DEFEAT: EMPIRE DISMANTLED BY {player.conquered_by.upper()}.")
    else:
        st.markdown(f"### 📊 GLOBAL CYCLE TACTICAL DATAFEED: TURN {st.session_state.turn}")
        
        if st.session_state.current_event:
            st.error(f"🚨 ACTIVE WORLD MATRIX MUTATOR: {st.session_state.current_event.upper()}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 BANK BALANCE", f"${player.economy}M")
        m2.metric("⚔️ NET POWER", f"{player.military_power():.1f}")
        m3.metric("🔥 OPERATIONAL EXHAUSTION", f"{player.war_exhaustion}")
        st.markdown(f"<div style='font-size:8px; text-align:center; padding-bottom:12px;'>Force Deployment: Infantry x{player.units['infantry']} | Tanks x{player.units['tanks']} | Interceptors x{player.units['jets']} | Strike Platforms x{player.units['orbital_satellites']}</div>", unsafe_allow_html=True)
        
        # =========================
        # CRITICAL RE-ORDERED EVENT FEED
        # =========================
        st.markdown("### 📡 COMBAT BROADCAST FEED & INTEL LOG")
        log_content = "<br>".join([f"> {msg}" for msg in reversed(st.session_state.log[-5:])])
        st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
        st.write("---")
        
        # =========================
        # COMMAND DILEMMA SYSTEM
        # =========================
        if st.session_state.active_dilemma:
            d = st.session_state.active_dilemma
            st.markdown(f"""
            <div class='dilemma-box'>
                <span style='color:#d95763; font-size:12px;'>⚠️ HIGH EXECUTIVE ACTION MANDATE:</span><br>
                <p style='font-size:10px; margin-top:8px;'>{d['text']}</p>
            </div>
            """, unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            if dc1.button(d['opt1_text']):
                d['opt1_action'](player)
                st.session_state.log.append(f"⚖️ EXECUTIVE CHOICE: {d['opt1_log']}")
                st.session_state.active_dilemma = None
                st.rerun()
            if dc2.button(d['opt2_text']):
                d['opt2_action'](player)
                st.session_state.log.append(f"⚖️ EXECUTIVE CHOICE: {d['opt2_log']}")
                st.session_state.active_dilemma = None
                st.rerun()
            st.write("---")

        d_status = "🔒" if st.session_state.action_tracking['deploy'] else "🟢"
        r_status = "🔒" if st.session_state.action_tracking['research'] else "🟢"
        i_status = "🔒" if st.session_state.action_tracking['infrastructure'] else "🟢"
        a_status = "🔒" if st.session_state.action_tracking['aerospace'] else "🟢"
        c_status = "🔒" if st.session_state.action_tracking['covert'] else "🟢"
        s_status = "🔒" if st.session_state.action_tracking['strike'] else "🟢"

        action_mode = st.radio(
            "CHOOSE THE ACTIVE DIVISION:",
            [
                f"🛠️ Requisition & Deploy Assets [{d_status}]", 
                f"🌳 Research Lab Matrix [{r_status}]",
                f"🏢 Territorial District Infrastructure [{i_status}]",
                f"🚀 Stratosphere Flight Command [{a_status}]", 
                f"🕵️ Deep Cover Espionage [{c_status}]",
                f"⚔️ Operational Strike Vector [{s_status}]", 
                "⏭️ Execute End Turn Sequence"
            ]
        )
        st.write("---")
        
        # 1. DEPLOY ASSETS
        if "🛠️" in action_mode:
            if not st.session_state.action_tracking["deploy"]:
                inf_cost = 5 if player.name == "China" else (7 if player.name == "France" else 10)
                jet_cost = 30 if player.name == "Japan" else 40
                
                unit = st.radio("Asset Array Selection:", [f"Infantry Battalion (${inf_cost}M)", "Armored Division ($25M)", f"Interceptor Squadron (${jet_cost}M)"])
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
                    else: st.error("LOGISTICS FAILURE: DEFICIT RESERVES.")
            else: st.warning("🔒 Production pipelines locked until the next operational cycle.")

        # 2. SCIENCE MATRIX
        elif "🌳" in action_mode:
            st.markdown("### 🧬 SYSTEM R&D TECHNOLOGY NETWORK")
            if st.session_state.action_tracking["research"]: st.warning("🔒 Computing nodes running simulation updates. Locked.")
            
            t1, t2, t3, t4 = st.columns(4)
            evt = st.session_state.current_event
            
            with t1:
                st.markdown("<span style='color:#e4c34a; font-size:9px;'>⚡ MOBILITY</span>", unsafe_allow_html=True)
                render_skill_node(player, "repairs", "Repairs", 15, "Automated logistical recycling.<br><span class='buff-txt'>+ Fast tracks assembly vectors.</span>", not player.skills["repairs"], evt)
                render_skill_node(player, "off_road", "Off-Road", 30, "All-terrain modular powerframes.<br><span class='buff-txt'>+ Minimizes regional mobility delays.</span>", player.skills["repairs"] and not player.skills["off_road"], evt)
                render_skill_node(player, "sohc_4_valve", "SOHC 4V Engine", 60, "High-rev valvetrain updates.<br><span class='buff-txt'>+ Armored Tank Power +2.</span>", player.skills["off_road"] and not player.skills["sohc_4_valve"], evt)
                
            with t2:
                st.markdown("<span style='color:#9c66d1; font-size:9px;'>👁️ SPOTTING</span>", unsafe_allow_html=True)
                render_skill_node(player, "situational_awareness", "Sit-Aware", 15, "Perimeter security updates.", not player.skills["situational_awareness"], evt)
                render_skill_node(player, "recon", "Recon Shuttles", 30, "Deep-territory scoping arrays.<br><span class='buff-txt'>+ Limits tactical ambush chance.</span>", player.skills["situational_awareness"] and not player.skills["recon"], evt)
                render_skill_node(player, "aerospace", "Aerospace Engineering", 100, "Low-Earth tracking satellite grids.<br><span class='buff-txt'>+ Unlocks Orbital Strike matrix.</span>", player.skills["recon"] and not player.skills["aerospace"], evt)
                
            with t3:
                st.markdown("<span style='color:#d97e41; font-size:9px;'>🛡️ SURVIVAL</span>", unsafe_allow_html=True)
                render_skill_node(player, "firefighting", "Suppression", 15, "Compartmentalized fire networks.", not player.skills["firefighting"], evt)
                render_skill_node(player, "armorer", "Armorer Weave", 30, "Reinforcing composite body frameworks.<br><span class='buff-txt'>+ Infantry Power +1.</span>", player.skills["firefighting"] and not player.skills["armorer"], evt)
                render_skill_node(player, "apex", "APEX Matrix", 200, "Advanced Predictive Executive Matrix.<br><span class='buff-txt'>+ Core cycle economic yield sets to $50M.</span>", player.skills["armorer"] and not player.skills["apex"], evt)
                
            with t4:
                st.markdown("<span style='color:#3bb87c; font-size:9px;'>🍃 CONCEAL</span>", unsafe_allow_html=True)
                render_skill_node(player, "camouflage", "Camo Plating", 15, "Multi-spectral thermal masks.", not player.skills["camouflage"], evt)
                render_skill_node(player, "quiet_running", "Quiet Running", 30, "Acoustic motor acoustic absorption.", player.skills["camouflage"] and not player.skills["quiet_running"], evt)
                render_skill_node(player, "loot", "LOOT Net", 75, "Subversive asset recovery engines.<br><span class='buff-txt'>+ Military Power +25%.</span>", player.skills["quiet_running"] and not player.skills["loot"], evt)

        # 3. CONQUERED DISTRICT PRODUCTION
        elif "🏢" in action_mode:
            st.markdown("### 🏢 SECTOR DISTRICT INFRASTRUCTURE MANAGEMENT")
            if not conquered_territories:
                st.info("Annex foreign sovereign targets or regional clusters to unlock internal district specialization.")
            elif st.session_state.action_tracking["infrastructure"]:
                st.warning("🔒 Logistics teams deployed to construction zones. Locked.")
            else:
                target_map = {n.name: n for n in conquered_territories}
                selected_t = st.selectbox("Designate Regional Sector Core:", list(target_map.keys()))
                active_zone = target_map[selected_t]
                
                st.write(f"Current Structure: **{active_zone.district}**")
                dist_choice = st.radio("Construct Structural Specialty ($30M):", [
                    "Garrison [Defensive Fortification: Sector Power +6]",
                    "Industrial Factory [Weapon Assembly: Sector Power +10]",
                    "Research Lab [Science Network: Subsequent Turn Yield +$5M]",
                    "Trade Port [Commercial Hub: Subsequent Turn Yield +$12M]"
                ])
                
                if st.button("AUTHORIZE REGIONAL CONSTRUCTION"):
                    if player.economy >= 30:
                        player.economy -= 30
                        active_zone.district = dist_choice.split(" ")[0]
                        st.session_state.action_tracking["infrastructure"] = True
                        st.session_state.log.append(f"🏢 CONSTRUCTION: Built {active_zone.district} in {active_zone.name.upper()}.")
                        st.rerun()
                    else: st.error("INSUFFICIENT INFRASTRUCTURE CAPITAL.")

        # 4. AEROSPACE DIVISION
        elif "🚀" in action_mode:
            if st.session_state.current_event == "Orbital Debris":
                st.error("⚠️ MATRIX BREACH: Satellite tracking modules offline due to debris fields.")
            elif not player.skills["aerospace"]:
                st.warning("⚠️ ACCESS DENIED: Uncouple 'Aerospace Engineering' in the Science Matrix.")
            elif not st.session_state.action_tracking["aerospace"]:
                space_action = st.radio("Satellite Grid Control Array:", ["Deploy Kinetic Strike Platform ($100M)", "Execute Ion Beam Decimation Field"])
                if "Deploy" in space_action:
                    if st.button("LAUNCH SATELLITE"):
                        if player.economy >= 100:
                            player.economy -= 100
                            player.units["orbital_satellites"] += 1
                            st.session_state.action_tracking["aerospace"] = True
                            st.session_state.log.append("🛰️ TELEMETRY: Kinetic strike platform linked in orbit.")
                            st.rerun()
                        else: st.error("FUNDS UNFAVORABLE.")
                else:
                    target_name = st.selectbox("Input Vector Coordinates:", [n.name for n in remaining_enemies])
                    if st.button("ENGAGE ORBITAL STRIKE"):
                        if player.units["orbital_satellites"] >= 1:
                            target = next(n for n in nations if n.name == target_name)
                            player.units["orbital_satellites"] -= 1
                            target.is_eliminated = True
                            target.conquered_by = player.name
                            loot = int(target.economy * 0.5)
                            player.economy += loot
                            player.base_income += 6
                            st.session_state.action_tracking["aerospace"] = True
                            st.session_state.log.append(f"💥 IONIZED IMPACT: {target.name.upper()} neutral. Claimed ${loot}M & +$6M dividend.")
                            st.rerun()
                        else: st.error("PLATFORMS VACANT: REQUISITION REQUIRED.")

        # 5. ESPIONAGE OPERATIONS
        elif "🕵️" in action_mode:
            if not st.session_state.action_tracking["covert"]:
                op_cost = 12 if player.skills["loot"] else 25
                st.info(f"Infiltrate backend bank networks. Cost Matrix: ${op_cost}M")
                target_name = st.selectbox("Select Network Target Vector:", [n.name for n in remaining_enemies])
                if st.button("ENGAGE SABOTAGE PROTOCOL"):
                    if player.economy >= op_cost:
                        player.economy -= op_cost
                        target = next(n for n in nations if n.name == target_name)
                        target.war_exhaustion += 5
                        target.economy = max(0, target.economy - 20)
                        apply_casualties(target, severity=0.30)
                        st.session_state.action_tracking["covert"] = True
                        st.session_state.log.append(f"🕵️ EXPLOIT: Disabled network nodes inside {target.name.upper()}.")
                        st.rerun()
                    else: st.error("BLACK RESOURCE FUNDS INSUFFICIENT.")
            else: st.warning("🔒 Operatives extraction in progress. Re-engaging next loop.")

        # 6. INVASION VECTOR
        elif "⚔️" in action_mode:
            if not st.session_state.action_tracking["strike"]:
                st.info("🎯 INTEL: Tanks break Infantry | Jets vaporize Tanks | Infantry traps Air elements.")
                target_name = st.selectbox("Designate Conquest Frontline:", [n.name for n in remaining_enemies])
                if st.button("LAUNCH REGIMENTAL STRIKE"):
                    target = next(n for n in nations if n.name == target_name)
                    
                    if resolve_combat(player, target):
                        target.is_eliminated = True
                        target.conquered_by = player.name
                        loot = int(target.economy * 0.5)
                        player.economy += loot
                        player.base_income += 6
                        apply_casualties(player, severity=0.15) 
                        st.session_state.log.append(f"⚔️ DOMINANCE: Conquered {target.name.upper()}! Looted ${loot}M & +$6M/Turn.")
                    else:
                        penalty = 6 if target.name == "Russia" else 4
                        player.war_exhaustion += penalty
                        apply_casualties(player, severity=0.35) 
                        st.session_state.log.append(f"❌ COMPROMISED: Assault on {target.name.upper()} broke. Exhaustion +{penalty}.")
                        
                        if random.random() < 0.40:
                            st.session_state.log.append(f"🚨 RETALIATION: {target.name.upper()} drove a column directly into our line!")
                            apply_casualties(player, severity=0.25)
                    
                    st.session_state.action_tracking["strike"] = True
                    st.rerun()
            else: st.warning("🔒 Frontline tactical positions processing replenishment loops.")

        # 7. SYSTEM REFRESH ROLLOVER
        elif "⏭️" in action_mode:
            if st.button("FLUSH ACTIVE TURNS"):
                
                e_roll = random.random()
                if e_roll < 0.12: st.session_state.current_event = "Market Crash"
                elif e_roll < 0.24: st.session_state.current_event = "Tech Boom"
                elif e_roll < 0.36: st.session_state.current_event = "Orbital Debris"
                elif e_roll < 0.48: st.session_state.current_event = "Economic Boom"
                else: st.session_state.current_event = None

                if random.random() < 0.35:
                    st.session_state.active_dilemma = {
                        "text": "A specialized corporate technology syndicate offers to lease out experimental logistics code systems to enhance weapon production speed.",
                        "opt1_text": "Accept Lease (Gain $40M instantly, increase Exhaustion +2)",
                        "opt2_text": "Reject Offer (Lower global Exhaustion by 3)",
                        "opt1_action": lambda p: setattr(p, 'economy', p.economy + 40) or setattr(p, 'war_exhaustion', p.war_exhaustion + 2),
                        "opt2_action": lambda p: setattr(p, 'war_exhaustion', max(0, p.war_exhaustion - 3)),
                        "opt1_log": "Leased out network interfaces. Cash reserves increased.",
                        "opt2_log": "Secure operations maintained. System core stabilized."
                    }

                base_yield = 50 if player.skills["apex"] else 30
                
                district_dividends = sum(12 for n in conquered_territories if n.district == "Port")
                district_dividends += sum(5 for n in conquered_territories if n.district == "Lab")
                
                econ_gain = base_yield + player.base_income + district_dividends
                if st.session_state.current_event == "Market Crash": econ_gain = int(econ_gain * 0.5)
                if st.session_state.current_event == "Economic Boom": econ_gain += 35
                
                player.economy += econ_gain
                if player.war_exhaustion > 0: player.war_exhaustion -= 1 
                
                for ai in remaining_enemies:
                    if ai.is_eliminated: continue
                    
                    ai_gain = 20 + ai.base_income
                    if ai.district == "Port": ai_gain += 12
                    if st.session_state.current_event == "Market Crash": ai_gain = max(5, ai_gain - 12)
                    ai.economy += ai_gain
                    
                    if ai.economy >= 40:
                        ai.economy -= 40
                        ai.units[random.choice(["infantry", "tanks", "jets"])] += 1
                        
                    if random.random() < 0.18 and ai.military_power() > 12:
                        potential_targets = [n for n in nations if n != ai and not n.is_eliminated]
                        potential_targets = [n for n in potential_targets if not (n.name == "Australia" and random.random() < 0.75)]
                        
                        if potential_targets:
                            target = random.choice(potential_targets)
                            if resolve_combat(ai, target):
                                target.is_eliminated = True
                                target.conquered_by = ai.name
                                ai.economy += int(target.economy * 0.4)
                                ai.base_income += 6
                                
                                if target.name == player.name:
                                    st.session_state.log.append(f"🚨 ALERT: {ai.name.upper()} systematically bypassed your frontier assets!")
                                else:
                                    st.session_state.log.append(f"🌍 THEATRE WIDE NEWS: {ai.name.upper()} annexed {target.name.upper()}.")
                            else:
                                ai.war_exhaustion += 2

                st.session_state.turn += 1
                for key in st.session_state.action_tracking: st.session_state.action_tracking[key] = False
                st.session_state.log.append(f"CYCLE COMPLETE: Rotated to Turn {st.session_state.turn} | Network Yield: +${econ_gain}M.")
                st.rerun()

    st.plotly_chart(render_interactive_map(nations, player), use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("""
    <div class='map-legend'>
        <div class='legend-item'><div class='legend-color' style='background:#597dce;'></div>User Empire</div>
        <div class='legend-item'><div class='legend-color' style='background:#d95763;'></div>Sovereign Competitor / Cluster</div>
        <div class='legend-item'><div class='legend-color' style='background:#3e734e;'></div>Annexed Sector</div>
        <div class='legend-item'><div class='legend-color' style='background:#2d232e;'></div>Defeated Sector</div>
    </div>
    """, unsafe_allow_html=True)
