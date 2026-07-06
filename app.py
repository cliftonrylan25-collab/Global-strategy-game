import random import streamlit as st import matplotlib.pyplot as plt import matplotlib.patches as patches

=========================
RESOURCE VALUES
=========================
RESOURCE_VALUES = { "oil": 5, "natural_gas": 4, "gold": 6, "diamonds": 7, "iron": 3, "coal": 2, "food": 2 }

=========================
CAPITALS (REALISTIC)
=========================
CAPITALS = { "United States": "Washington, D.C.", "Canada": "Ottawa", "Mexico": "Mexico City", "Brazil": "Brasília", "Argentina": "Buenos Aires", "Venezuela": "Caracas", "United Kingdom": "London", "France": "Paris", "Germany": "Berlin", "Russia": "Moscow", "China": "Beijing", "India": "New Delhi", "Japan": "Tokyo", "Saudi Arabia": "Riyadh", "Iran": "Tehran", "Egypt": "Cairo", "Nigeria": "Abuja", "South Africa": "Pretoria", "Australia": "Canberra" }

=========================
WORLD MAP LAYOUT (ABSTRACT)
=========================
WORLD_MAP_LAYOUT = { "North America": ["United States", "Canada", "Mexico"], "South America": ["Brazil", "Argentina", "Venezuela"], "Europe": ["United Kingdom", "France", "Germany"], "Africa": ["Egypt", "Nigeria", "South Africa"], "Asia": ["Russia", "China", "India", "Japan", "Saudi Arabia", "Iran"], "Oceania": ["Australia"] }

=========================
NATION CLASS
=========================
class Nation: def init(self, name, economy, resources): self.name = name self.economy = economy self.resources = resources self.allies = [] self.war_exhaustion = 0 self.at_war = False self.units = { "infantry": 0, "tanks": 0, "artillery": 0, "anti_air": 0 }

def military_power(self):
    base = (
        self.units["infantry"] +
        self.units["tanks"] * 3 +
        self.units["artillery"] * 2 +
        self.units["anti_air"] * 1.5
    )
    penalty = 1 - self.war_exhaustion * 0.05
    return max(0, base * penalty)

def total_resource_value(self):
    return sum(self.resources.get(r, 0) * RESOURCE_VALUES.get(r, 1) for r in self.resources)
=========================
COMBAT & UPKEEP
=========================
def combat(attacker, defender, log): atk = attacker.military_power() + random.randint(0, 10) dfn = defender.military_power() + random.randint(0, 10)

attacker.war_exhaustion += 2
defender.war_exhaustion += 2

if atk > dfn:
    log.append(f"{attacker.name} defeats {defender.name}")
    attacker.economy += defender.economy // 4
    defender.economy = max(0, defender.economy - defender.economy // 3)

    for r in defender.resources:
        stolen = defender.resources[r] // 4
        defender.resources[r] -= stolen
        attacker.resources[r] = attacker.resources.get(r, 0) + stolen
else:
    log.append(f"{defender.name} repels the attack")
def apply_upkeep(nation): upkeep = int(nation.military_power() * 0.1) nation.economy = max(0, nation.economy - upkeep) nation.economy += nation.total_resource_value() // 10

=========================
AI TURN
=========================
def ai_turn(nation, player, nations, log): if nation.war_exhaustion >= 10: nation.at_war = False nation.war_exhaustion -= 3 log.append(f"{nation.name} seeks peace") return

if nation.economy < 30:
    nation.economy += random.randint(10, 20)
    return

target = random.choice([n for n in nations if n != nation and n != player])
nation.at_war = target.at_war = True
combat(nation, target, log)
=========================
VISUALS
=========================
def assign_nation_colors(nations): random.seed(42) return {n.name: (random.random(), random.random(), random.random()) for n in nations}

def render_visuals(nations, player): colors = assign_nation_colors(nations) lookup = {n.name: n for n in nations}

fig, ax = plt.subplots(figsize=(14, 7))
ax.set_title("World Map")

y = 0
for region, countries in WORLD_MAP_LAYOUT.items():
    x = 0
    for c in countries:
        nation = lookup.get(c)
        color = colors.get(c, (0.7, 0.7, 0.7))
        edge = "red" if nation and nation.at_war else "black"
        lw = 3 if nation == player else 1

        rect = patches.Rectangle((x, y), 1, 0.8, facecolor=color, edgecolor=edge, linewidth=lw)
        ax.add_patch(rect)

        if nation:
            ax.text(x + 0.5, y + 0.4, c, ha="center", va="center", fontsize=8, color="white")
            ax.plot(x + 0.5, y + 0.6, marker="*", color="gold", markersize=10)

        x += 1.1
    y += 1

ax.axis("off")
ax.set_facecolor((0.75, 0.75, 0.75))
return fig
=========================
GAME SETUP
=========================
def create_nations(): return [ Nation("United States", 80, {"oil": 120, "food": 200, "iron": 90}), Nation("Canada", 60, {"oil": 150, "food": 140}), Nation("Mexico", 55, {"oil": 90, "food": 120}), Nation("Brazil", 70, {"food": 250, "iron": 110, "gold": 60}), Nation("Argentina", 60, {"food": 200}), Nation("Venezuela", 50, {"oil": 300, "gold": 80}), Nation("United Kingdom", 65, {"oil": 70}), Nation("France", 65, {"food": 120}), Nation("Germany", 70, {"iron": 140}), Nation("Russia", 75, {"oil": 220, "iron": 200}), Nation("China", 90, {"coal": 300, "iron": 250}), Nation("India", 85, {"food": 300}), Nation("Japan", 70, {"iron": 80}), Nation("Saudi Arabia", 85, {"oil": 350}), Nation("Iran", 70, {"oil": 200}), Nation("Egypt", 60, {"food": 140}), Nation("Nigeria", 65, {"oil": 180}), Nation("South Africa", 65, {"gold": 120, "diamonds": 90}), Nation("Australia", 70, {"iron": 200, "coal": 180}) ]

=========================
STREAMLIT APP
=========================
st.set_page_config(layout="wide") st.title("Global Strategy Game")

if "game_started" not in st.session_state: st.session_state.game_started = False st.session_state.turn = 1 st.session_state.log = [] st.session_state.nations = create_nations()

nations = st.session_state.nations

if not st.session_state.game_started: choice = st.selectbox("Choose your nation", [n.name for n in nations]) if st.button("Start Game"): st.session_state.player = next(n for n in nations if n.name == choice) st.session_state.game_started = True st.experimental_rerun()

else: player = st.session_state.player

st.subheader(f"Turn {st.session_state.turn}")
st.write(f"**Nation:** {player.name}")
st.write(f"Economy: {player.economy}")
st.write(f"Military Power: {player.military_power():.1f}")
st.write(f"War Exhaustion: {player.war_exhaustion}")

action = st.selectbox(
    "Choose Action",
    ["Invade", "Build Units", "View Nations", "End Turn"]
)

if action == "Invade":
    target_name = st.selectbox("Target", [n.name for n in nations if n != player])
    if st.button("Invade"):
        target = next(n for n in nations if n.name == target_name)
        player.at_war = target.at_war = True
        combat(player, target, st.session_state.log)

if action == "Build Units":
    unit = st.selectbox("Unit Type", ["infantry", "tanks", "artillery", "anti_air"])
    if st.button("Build"):
        cost = {"infantry": 5, "tanks": 15, "artillery": 10, "anti_air": 8}[unit]
        if player.economy >= cost:
            player.economy -= cost
            player.units[unit] += 1
            st.session_state.log.append(f"Built {unit}")
        else:
            st.session_state.log.append("Not enough economy")

if action == "View Nations":
    for n in nations:
        st.write(f"{n.name} | Econ {n.economy} | Mil {n.military_power():.1f}")

if action == "End Turn":
    if st.button("Confirm End Turn"):
        apply_upkeep(player)
        for ai in nations:
            if ai != player:
                ai_turn(ai, player, nations, st.session_state.log)
                apply_upkeep(ai)
        st.session_state.turn += 1
        st.experimental_rerun()

st.subheader("World Map")
st.pyplot(render_visuals(nations, player))

st.subheader("Game Log")
for msg in st.session_state.log[-10:]:
    st.write(msg)# Global-strategy-game-LCMS
