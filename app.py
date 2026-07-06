import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =========================
# RESOURCE VALUES
# =========================
RESOURCE_VALUES = { "oil": 5, "natural_gas": 4, "gold": 6, "diamonds": 7, "iron": 3, "coal": 2, "food": 2 }

# =========================
# CAPITALS (REALISTIC)
# =========================
CAPITALS = { "United States": "Washington, D.C.", "Canada": "Ottawa", "Mexico": "Mexico City", "Brazil": "Brasília", "Argentina": "Buenos Aires", "Venezuela": "Caracas", "United Kingdom": "London", "France": "Paris", "Germany": "Berlin", "Russia": "Moscow", "China": "Beijing", "India": "New Delhi", "Japan": "Tokyo", "Saudi Arabia": "Riyadh", "Iran": "Tehran", "Egypt": "Cairo", "Nigeria": "Abuja", "South Africa": "Pretoria", "Australia": "Canberra" }

# =========================
# WORLD MAP LAYOUT (ABSTRACT)
# =========================
WORLD_MAP_LAYOUT = { "North America": ["United States", "Canada", "Mexico"], "South America": ["Brazil", "Argentina", "Venezuela"], "Europe": ["United Kingdom", "France", "Germany"], "Africa": ["Egypt", "Nigeria", "South Africa"], "Asia": ["Russia", "China", "India", "Japan", "Saudi Arabia", "Iran"], "Oceania": ["Australia"] }

# =========================
# NATION CLASS
# =========================
class Nation: 
    def __init__(self, name, economy, resources): 
        self.name = name 
        self.original_name = name  
        self.economy = economy 
        self.resources = resources 
        self.allies = [] 
        self.war_exhaustion = 0 
        self.at_war = False 
        self.is_eliminated = False
        self.conquered_by = None
        self.has_player_intel = False
        
        # Tech Tree
        self.researched_techs = []
        
        # Nuclear/Space Infrastructure
        self.has_nuclear_program = False
        self.enrichment_level = 1
        self.uranium_stockpile = 0
        self.nukes_ready = 0
        
        self.units = { "infantry": 0, "tanks": 0, "artillery": 0, "anti_air": 0 }

    def military_power(self):
        if self.is_eliminated:
            return 0
        base = (
            self.units["infantry"] +
            self.units["tanks"] * 3 +
            self.units["artillery"] * 2 +
            self.units["anti_air"] * 1.5
        )
        # Precision Engineering Tech Perk
        bonus = 1.2 if "Precision Engineering" in self.researched_techs else 1.0
        penalty = 1 - (self.war_exhaustion * 0.05)
        return max(0, base * penalty * bonus)

    def total_resource_value(self):
        return sum(self.resources.get(r, 0) * RESOURCE_VALUES.get(r, 1) for r in self.resources)

# =========================
# COMBAT & CONQUEST LOGIC
# =========================
def combat(attacker, defender, log, nations): 
    atk = attacker.military_power() + random.randint(0, 10) 
    dfn = defender.military_power() + random.randint(0, 10)

    attacker.war_exhaustion += 2
    defender.war_exhaustion += 2

    if atk > dfn:
        log.append(f"💥 CONQUEST: {attacker.name} completely defeats and annexes {defender.name}!")
        attacker.economy += defender.economy
        for r in defender.resources:
            attacker.resources[r] = attacker.resources.get(r, 0) + defender.resources[r]
        defender.is_eliminated = True
        defender.conquered_by = attacker.name
        defender.at_war = False
        attacker.at_war = False
    else:
        log.append(f"🛡️ DEFENSE: {defender.name} successfully repels the invasion forces of {attacker.name}!")

def apply_upkeep(nation): 
    if nation.is_eliminated:
        return
    upkeep = int(nation.military_power() * 0.1) 
    nation.economy = max(0, nation.economy - upkeep) 
    nation.economy += nation.total_resource_value() // 10
    if nation.has_nuclear_program:
        nation.uranium_stockpile += (5 * nation.enrichment_level)

# =========================
# AI TURN
# =========================
def ai_turn(nation, player, nations, log): 
    if nation.is_eliminated:
        return
    if nation.war_exhaustion >= 10: 
        nation.at_war = False 
        nation.war_exhaustion -= 3 
        log.append(f"🏳️ {nation.name} stabilizes their home front.") 
        return
    if nation.economy < 30:
        nation.economy += random.randint(10, 20)
        return
    active_targets = [n for n in nations if n != nation and not n.is_eliminated]
    if active_targets:
        target = random.choice(active_targets)
        nation.at_war = target.at_war = True
        combat(nation, target, log, nations)

# =========================
# VISUALS
# =========================
def assign_nation_colors(nations): 
    random.seed(42) 
    return {n.name: (random.random(), random.random(), random.random()) for n in nations}

def render_visuals(nations, player): 
    base_colors = assign_nation_colors(nations) 
    lookup = {n.original_name: n for n in nations}
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_title("World Control Status Map")
    y = 0
    for region, countries in WORLD_MAP_LAYOUT.items():
        x = 0
        for c in countries:
            nation = lookup.get(c)
            if nation and nation.is_eliminated:
                if nation.conquered_by == "Radioactive Wasteland":
                    color = (0.0, 0.0, 0.0)
                    label_text = f"{c}\n(WASTELAND)"
                else:
                    color = base_colors.get(nation.conquered_by, (0.5, 0.5, 0.5))
                    label_text = f"{c}\n({nation.conquered_by})"
            else:
                color = base_colors.get(c, (0.7, 0.7, 0.7))
                label_text = c
            edge = "red" if nation and nation.at_war else "black"
            lw = 1
            if nation:
                if nation.name == player.name: lw = 3
                if nation.is_eliminated and nation.conquered_by == player.name: lw = 3
                if nation.conquered_by == "Radioactive Wasteland": lw = 2
            rect = patches.Rectangle((x, y), 1, 0.8, facecolor=color, edgecolor=edge, linewidth=lw)
            ax.add_patch(rect)
            if nation:
                text_color = "red" if nation.conquered_by == "Radioactive Wasteland" else "white"
                ax.text(x + 0.5, y + 0.4, label_text, ha="center", va="center", fontsize=7, color=text_color, weight="bold")
                if not nation.is_eliminated:
                    ax.plot(x + 0.5, y + 0.6, marker="*", color="gold", markersize=8)
            x += 1.2
        y += 1
    ax.axis("off")
    ax.set_facecolor((0.1, 0.1, 0.1))
    return fig

# =========================
# GAME SETUP
# =========================
def create_nations(): 
    return [ 
        Nation("United States", 80, {"oil": 120, "food": 200, "iron": 90}), 
        Nation("Canada", 60, {"oil": 150, "food": 140}), 
        Nation("Mexico", 55, {"oil": 90, "food": 120}), 
        Nation("Brazil", 70, {"food": 250, "iron": 110, "gold": 60}), 
        Nation("Argentina", 60, {"food": 200}), 
        Nation("Venezuela", 50, {"oil": 300, "gold": 80}), 
        Nation("United Kingdom", 65, {"oil": 70}), 
        Nation("France", 65, {"food": 120}), 
        Nation("Germany", 70, {"iron": 140}), 
        Nation("Russia", 75, {"oil": 220, "iron": 200}), 
        Nation("China", 90, {"coal": 300, "iron": 250}), 
        Nation("India", 85, {"food": 300}), 
        Nation("Japan", 70, {"iron": 80}), 
        Nation("Saudi Arabia", 85, {"oil": 350}), 
        Nation("Iran", 70, {"oil": 200}), 
        Nation("Egypt", 60, {"food": 140}), 
        Nation("Nigeria", 65, {"oil": 180}), 
        Nation("South Africa", 65, {"gold": 120, "diamonds": 90}), 
        Nation("Australia", 70, {"iron": 200, "coal": 180}) 
    ]

# =========================
# STREAMLIT APP
# =========================
st.set_page_config(layout="wide") 
st.title("Global Conquest: World Domination")

if "game_started" not in st.session_state: 
    st.session_state.game_started = False 
    st.session_state.turn = 1 
    st.session_state.log = [] 
    st.session_state.nations = create_nations()

nations = st.session_state.nations

if not st.session_state.game_started: 
    choice = st.selectbox("Choose your nation to rule the world:", [n.name for n in nations]) 
    if st.button("Commence Campaign"): 
        st.session_state.player = next(n for n in nations if n.name == choice) 
        st.session_state.game_started = True 
        st.rerun()
else: 
    player = st.session_state.player
    if player.is_eliminated:
        st.error(f"❌ GAME OVER: Your empire has been conquered by {player.conquered_by}!")
        if st.button("Restart Campaign"):
            st.session_state.clear()
            st.rerun()
    else:
        remaining_enemies = [n for n in nations if n != player and not n.is_eliminated]
        if not remaining_enemies:
            st.balloons()
            st.success("👑 VICTORY: World Unification Achieved!")
            if st.button("Play Again"):
                st.session_state.clear()
                st.rerun()
        
        st.subheader(f"Turn {st.session_state.turn}")
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Nation:** {player.name}\n\n**Economy:** {player.economy}")
        col2.write(f"**Military Power:** {player.military_power():.1f}")
        col3.write(f"**Uranium:** {player.uranium_stockpile} | **ICBMs:** {player.nukes_ready}")

        action = st.selectbox(
            "Choose Action",
            ["Invade Enemy", "Build Units", "Covert Ops", "Nuclear/Space", "Tech Tree", "View Intel Board", "End Turn"]
        )

        if action == "Invade Enemy":
            alive_targets = [n.name for n in nations if n != player and not n.is_eliminated]
            if alive_targets:
                target_name = st.selectbox("Target Nation", alive_targets)
                if st.button("Launch Invasion"):
                    target = next(n for n in nations if n.name == target_name)
                    player.at_war = target.at_war = True
                    combat(player, target, st.session_state.log, nations)
                    st.rerun()
        elif action == "Build Units":
            unit = st.selectbox("Unit Type", ["infantry", "tanks", "artillery", "anti_air"])
            if st.button("Deploy Forces"):
                cost = {"infantry": 5, "tanks": 15, "artillery": 10, "anti_air": 8}[unit]
                if player.economy >= cost:
                    player.economy -= cost
                    player.units[unit] += 1
                    st.rerun()
                else: st.error("Insufficient funding.")
        elif action == "Covert Ops":
            alive_targets = [n.name for n in nations if n != player and not n.is_eliminated]
            if alive_targets:
                target_name = st.selectbox("Target Nation", alive_targets)
                op_type = st.selectbox("Operation Type", ["Gather Intel (Cost: 10)", "Sabotage Military (Cost: 25)"])
                if st.button("Execute"):
                    target = next(n for n in nations if n.name == target_name)
                    if "Intel" in op_type and player.economy >= 10:
                        player.economy -= 10
                        target.has_player_intel = True
                        st.rerun()
                    elif "Sabotage" in op_type and player.economy >= 25:
                        player.economy -= 25
                        target.units["tanks"] = max(0, target.units["tanks"] - 2)
                        st.rerun()
        elif action == "Nuclear/Space":
            if not player.has_nuclear_program:
                if st.button("Establish Enrichment Facility (Cost: 50)"):
                    if player.economy >= 50:
                        player.economy -= 50
                        player.has_nuclear_program = True
                        st.rerun()
            else:
                st.write(f"Level: {player.enrichment_level} | Uranium: {player.uranium_stockpile}")
                if st.button("Assemble ICBM (Cost: 100 Uranium)"):
                    if player.uranium_stockpile >= 100:
                        player.uranium_stockpile -= 100
                        player.nukes_ready += 1
                        st.rerun()
        elif action == "Tech Tree":
            techs = {"Basic Rocketry": 50, "Precision Engineering": 100, "Satellite Network": 150}
            for tech, cost in techs.items():
                if tech not in player.researched_techs:
                    if st.button(f"Research {tech} (Cost: {cost})"):
                        if player.economy >= cost:
                            player.economy -= cost
                            player.researched_techs.append(tech)
                            st.rerun()
                else: st.write(f"✅ {tech}")
        elif action == "End Turn":
            if st.button("Confirm"):
                apply_upkeep(player)
                for ai in nations:
                    if ai != player and not ai.is_eliminated:
                        ai_turn(ai, player, nations, st.session_state.log)
                        apply_upkeep(ai)
                st.session_state.turn += 1
                st.rerun()

    st.subheader("Global Control Map")
    st.pyplot(render_visuals(nations, player))
