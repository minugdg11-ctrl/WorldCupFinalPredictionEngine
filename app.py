import streamlit as st
from scipy.stats import poisson
import math
import random

st.set_page_config(
    page_title="World Cup Prediction Engine",
    page_icon="⚽",
    layout="wide"
)

# ⬇️ PASTE THE TEAM_DATA HERE

TEAM_DATA = {
    "Argentina": {
        "elo": 2177,
        "goals_per_game": 2.7,
        "xg_per_game": 1.9,
        "goals_against_per_game": 1.0,
        "shots_per_game": 15.6,
        "possession": 66.0,
        "chances_created_per_game": 9.3
    },

    "Spain": {
        "elo": 2232,
        "goals_per_game": 1.9,
        "xg_per_game": 1.7,
        "goals_against_per_game": 0.1,
        "shots_per_game": 16.3,
        "possession": 71.0,
        "chances_created_per_game": 10.9
    }
}
# --------------------------------------------------
# VERIFIED PLAYER AND HISTORICAL EVENT DATA
# --------------------------------------------------

PLAYER_REAL_DATA = {
    "Messi": {
        "appearances": 7,
        "starts": 6,
        "minutes": 621,
        "goals": 8,
        "xg": 5.09,
        "assists": 4,
        "shots": 33,
        "shots_on_target": 16,
        "penalty_goals": 0,
        "takes_penalties": True
    },

    "Yamal": {
        "appearances": 7,
        "starts": 6,
        "minutes": 496,
        "goals": 1,
        "xg": 1.59,
        "assists": 0,
        "shots": 23,
        "shots_on_target": 10,
        "penalty_goals": 0,
        "takes_penalties": False
    }
}

# --------------------------------------------------
# VERIFIED TEAM AND HISTORICAL EVENT DATA
# --------------------------------------------------

TEAM_EVENT_DATA = {
    "Argentina": {
        "matches": 7,
        "corners": 37,
        "fouls_committed": 81,
        "yellow_cards": 9
    },

    "Spain": {
        "matches": 7,
        "corners": 45,
        "fouls_committed": 80,
        "yellow_cards": 6
    }
}


HISTORICAL_EVENT_PRIORS = {
    # Combined 2018 and 2022 World Cups:
    # 52 penalties awarded across 128 matches.
    "penalty_probability": 52 / 128,

    # Combined conversion estimate from those tournaments.
    "penalty_conversion_probability": 39 / 52
}

def calculate_team_rating(team):
    data = TEAM_DATA[team]

    # Convert each raw statistic onto a similar 0–100 scale

    elo_score = max(
        0,
        min(100, (data["elo"] - 1400) / 9)
    )

    goals_score = max(
        0,
        min(100, data["goals_per_game"] / 3.0 * 100)
    )

    xg_score = max(
        0,
        min(100, data["xg_per_game"] / 2.5 * 100)
    )

    defence_score = max(
        0,
        min(100, 100 - data["goals_against_per_game"] * 45)
    )

    shots_score = max(
        0,
        min(100, data["shots_per_game"] / 20 * 100)
    )

    possession_score = max(
        0,
        min(100, data["possession"])
    )

    chances_score = max(
        0,
        min(100, data["chances_created_per_game"] / 13 * 100)
    )

    rating = (
        elo_score * 0.25
        + goals_score * 0.15
        + xg_score * 0.20
        + defence_score * 0.20
        + shots_score * 0.05
        + possession_score * 0.05
        + chances_score * 0.10
    )

    return round(rating, 2)


    # --------------------------------------------------
# STATISTICAL HELPER FUNCTIONS
# --------------------------------------------------

def probability_at_least_one(event_rate):
    event_rate = max(0.0, event_rate)
    return 1 - math.exp(-event_rate)


def smoothed_event_rate(
    events,
    matches,
    prior_events=1.0,
    prior_matches=4.0
):
    return (
        events + prior_events
    ) / (
        matches + prior_matches
    )


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))

st.title("⚽ World Cup Prediction Engine")

st.subheader("Version 0.1")

st.write("Welcome! This software will predict the 2026 FIFA World Cup Final.")


argentina_rating = calculate_team_rating("Argentina")
spain_rating = calculate_team_rating("Spain")
st.write("### Team Ratings")

st.write(f"🇦🇷 Argentina: {argentina_rating}")

st.write(f"🇪🇸 Spain: {spain_rating}")


rating_difference = argentina_rating - spain_rating

# --------------------------------------------------
# SCENARIO CONTROLS
# --------------------------------------------------

def reset_scenarios():
    st.session_state.messi_status = "Fully fit"
    st.session_state.messi_event = "No forced event"
    st.session_state.yamal_status = "Fully fit"
    st.session_state.yamal_event = "No forced event"
    st.session_state.first_goal = "No forced event"
    st.session_state.argentina_red_card = False
    st.session_state.spain_red_card = False


st.sidebar.title("Match Scenario Simulator")

st.sidebar.button(
    "Reset scenarios",
    on_click=reset_scenarios,
    use_container_width=True
)

st.sidebar.divider()

st.sidebar.subheader("Lionel Messi")

messi_status = st.sidebar.selectbox(
    "Messi availability",
    [
        "Fully fit",
        "Limited fitness",
        "Unavailable"
    ],
    key="messi_status"
)

messi_event = st.sidebar.selectbox(
    "Messi match event",
    [
        "No forced event",
        "Scores",
        "Assists",
        "Scores and assists"
    ],
    key="messi_event",
    disabled=(messi_status == "Unavailable")
)

st.sidebar.divider()

st.sidebar.subheader("Lamine Yamal")

yamal_status = st.sidebar.selectbox(
    "Yamal availability",
    [
        "Fully fit",
        "Limited fitness",
        "Unavailable"
    ],
    key="yamal_status"
)

yamal_event = st.sidebar.selectbox(
    "Yamal match event",
    [
        "No forced event",
        "Scores",
        "Assists",
        "Scores and assists"
    ],
    key="yamal_event",
    disabled=(yamal_status == "Unavailable")
)

st.sidebar.divider()

st.sidebar.subheader("Match Events")

first_goal = st.sidebar.selectbox(
    "Team scoring first",
    [
        "No forced event",
        "Argentina",
        "Spain"
    ],
    key="first_goal"
)

argentina_red_card = st.sidebar.checkbox(
    "Argentina receive a red card",
    key="argentina_red_card"
)

spain_red_card = st.sidebar.checkbox(
    "Spain receive a red card",
    key="spain_red_card"
)

# --------------------------------------------------
# BASELINE EXPECTED GOALS
# --------------------------------------------------

baseline_argentina_xg = 1.35 + rating_difference * 0.025
baseline_spain_xg = 1.35 - rating_difference * 0.025

argentina_xg = baseline_argentina_xg
spain_xg = baseline_spain_xg

scenario_notes = []

# --------------------------------------------------
# MESSI EFFECTS
# --------------------------------------------------

if messi_status == "Limited fitness":
    argentina_xg *= 0.92
    scenario_notes.append(
        "Messi's limited fitness reduces Argentina's attacking estimate by 8%."
    )

elif messi_status == "Unavailable":
    argentina_xg *= 0.82
    scenario_notes.append(
        "Messi's absence reduces Argentina's attacking estimate by 18%."
    )

if messi_status != "Unavailable":

    if messi_event == "Scores":
        argentina_xg += 0.45
        scenario_notes.append(
            "A forced Messi goal adds 0.45 to Argentina's expected-goals estimate."
        )

    elif messi_event == "Assists":
        argentina_xg += 0.30
        scenario_notes.append(
            "A forced Messi assist adds 0.30 to Argentina's expected-goals estimate."
        )

    elif messi_event == "Scores and assists":
        argentina_xg += 0.65
        scenario_notes.append(
            "A Messi goal and assist add 0.65 to Argentina's expected-goals estimate."
        )

# --------------------------------------------------
# YAMAL EFFECTS
# --------------------------------------------------

if yamal_status == "Limited fitness":
    spain_xg *= 0.93
    scenario_notes.append(
        "Yamal's limited fitness reduces Spain's attacking estimate by 7%."
    )

elif yamal_status == "Unavailable":
    spain_xg *= 0.84
    scenario_notes.append(
        "Yamal's absence reduces Spain's attacking estimate by 16%."
    )

if yamal_status != "Unavailable":

    if yamal_event == "Scores":
        spain_xg += 0.40
        scenario_notes.append(
            "A forced Yamal goal adds 0.40 to Spain's expected-goals estimate."
        )

    elif yamal_event == "Assists":
        spain_xg += 0.28
        scenario_notes.append(
            "A forced Yamal assist adds 0.28 to Spain's expected-goals estimate."
        )

    elif yamal_event == "Scores and assists":
        spain_xg += 0.60
        scenario_notes.append(
            "A Yamal goal and assist add 0.60 to Spain's expected-goals estimate."
        )

# --------------------------------------------------
# MATCH-EVENT EFFECTS
# --------------------------------------------------

if first_goal == "Argentina":
    argentina_xg += 0.35
    spain_xg *= 0.92

    scenario_notes.append(
        "Argentina scoring first increases their game-state advantage."
    )

elif first_goal == "Spain":
    spain_xg += 0.35
    argentina_xg *= 0.92

    scenario_notes.append(
        "Spain scoring first increases their game-state advantage."
    )

if argentina_red_card:
    argentina_xg *= 0.68
    spain_xg *= 1.30

    scenario_notes.append(
        "An Argentina red card reduces their attacking estimate and increases Spain's."
    )

if spain_red_card:
    spain_xg *= 0.68
    argentina_xg *= 1.30

    scenario_notes.append(
        "A Spain red card reduces their attacking estimate and increases Argentina's."
    )

argentina_xg = max(0.10, min(4.50, argentina_xg))
spain_xg = max(0.10, min(4.50, spain_xg))

# --------------------------------------------------
# POISSON MATCH MODEL
# --------------------------------------------------

argentina_win_probability = 0
draw_probability = 0
spain_win_probability = 0

most_likely_score = (0, 0)
highest_score_probability = 0

score_probabilities = []

for argentina_goals in range(8):
    for spain_goals in range(8):

        score_probability = (
            poisson.pmf(argentina_goals, argentina_xg)
            * poisson.pmf(spain_goals, spain_xg)
        )

        score_probabilities.append(
            (
                argentina_goals,
                spain_goals,
                score_probability
            )
        )

        if argentina_goals > spain_goals:
            argentina_win_probability += score_probability

        elif argentina_goals == spain_goals:
            draw_probability += score_probability

        else:
            spain_win_probability += score_probability

        if score_probability > highest_score_probability:
            highest_score_probability = score_probability
            most_likely_score = (
                argentina_goals,
                spain_goals
            )

total_probability = (
    argentina_win_probability
    + draw_probability
    + spain_win_probability
)

argentina_win_probability = (
    argentina_win_probability
    / total_probability
    * 100
)

draw_probability = (
    draw_probability
    / total_probability
    * 100
)

spain_win_probability = (
    spain_win_probability
    / total_probability
    * 100
)

if argentina_win_probability > spain_win_probability:
    predicted_winner = "Argentina"
else:
    predicted_winner = "Spain"

# --------------------------------------------------
# DATA-DRIVEN PLAYER EVENT ESTIMATES
# --------------------------------------------------

# Compare the current scenario attack level with the baseline.
argentina_attack_scale = (
    argentina_xg
    / max(0.10, baseline_argentina_xg)
)

spain_attack_scale = (
    spain_xg
    / max(0.10, baseline_spain_xg)
)


# Calculate smoothed tournament scoring and assisting rates.
# Tournament playing-time rates
messi_90s = PLAYER_REAL_DATA["Messi"]["minutes"] / 90
yamal_90s = PLAYER_REAL_DATA["Yamal"]["minutes"] / 90

# Expected-goal production per 90
messi_xg_per_90 = (
    PLAYER_REAL_DATA["Messi"]["xg"]
    / messi_90s
)

yamal_xg_per_90 = (
    PLAYER_REAL_DATA["Yamal"]["xg"]
    / yamal_90s
)

# Actual assist production per 90
messi_assists_per_90 = (
    PLAYER_REAL_DATA["Messi"]["assists"]
    / messi_90s
)

yamal_assists_per_90 = (
    PLAYER_REAL_DATA["Yamal"]["assists"]
    / yamal_90s
)

# Shooting-volume information
messi_shots_per_90 = (
    PLAYER_REAL_DATA["Messi"]["shots"]
    / messi_90s
)

yamal_shots_per_90 = (
    PLAYER_REAL_DATA["Yamal"]["shots"]
    / yamal_90s
)

messi_sot_rate = (
    PLAYER_REAL_DATA["Messi"]["shots_on_target"]
    / PLAYER_REAL_DATA["Messi"]["shots"]
)

yamal_sot_rate = (
    PLAYER_REAL_DATA["Yamal"]["shots_on_target"]
    / PLAYER_REAL_DATA["Yamal"]["shots"]
)

# Blend xG production with shooting accuracy.
# xG carries most of the weight because it represents chance quality.
messi_goal_rate = (
    messi_xg_per_90 * 0.80
    + messi_shots_per_90 * messi_sot_rate * 0.05
)

yamal_goal_rate = (
    yamal_xg_per_90 * 0.80
    + yamal_shots_per_90 * yamal_sot_rate * 0.05
)

# Assist estimates use actual tournament assists.
# Simple smoothing prevents a zero-assist sample from becoming a certain 0%.
messi_assist_rate = smoothed_event_rate(
    PLAYER_REAL_DATA["Messi"]["assists"],
    PLAYER_REAL_DATA["Messi"]["appearances"],
    prior_events=0.6,
    prior_matches=5.0
)

yamal_assist_rate = smoothed_event_rate(
    PLAYER_REAL_DATA["Yamal"]["assists"],
    PLAYER_REAL_DATA["Yamal"]["appearances"],
    prior_events=0.6,
    prior_matches=5.0
)

availability_multiplier = {
    "Fully fit": 1.00,
    "Limited fitness": 0.72,
    "Unavailable": 0.00
}


# Adjust each player's event rate using:
# 1. Their tournament record
# 2. Their team's scenario-adjusted attacking level
# 3. Their availability
messi_goal_lambda = (
    messi_goal_rate
    * argentina_attack_scale
    * availability_multiplier[messi_status]
)

messi_assist_lambda = (
    messi_assist_rate
    * argentina_attack_scale
    * availability_multiplier[messi_status]
)

yamal_goal_lambda = (
    yamal_goal_rate
    * spain_attack_scale
    * availability_multiplier[yamal_status]
)

yamal_assist_lambda = (
    yamal_assist_rate
    * spain_attack_scale
    * availability_multiplier[yamal_status]
)


# Convert expected event rates into probabilities
# of at least one goal or assist.
messi_goal_probability = (
    probability_at_least_one(messi_goal_lambda)
    * 100
)

messi_assist_probability = (
    probability_at_least_one(messi_assist_lambda)
    * 100
)

yamal_goal_probability = (
    probability_at_least_one(yamal_goal_lambda)
    * 100
)

yamal_assist_probability = (
    probability_at_least_one(yamal_assist_lambda)
    * 100
)


# If the user forces an event in the simulator,
# that selected event becomes certain in that scenario.
if messi_event == "Scores":
    messi_goal_probability = 100.0

elif messi_event == "Assists":
    messi_assist_probability = 100.0

elif messi_event == "Scores and assists":
    messi_goal_probability = 100.0
    messi_assist_probability = 100.0


if yamal_event == "Scores":
    yamal_goal_probability = 100.0

elif yamal_event == "Assists":
    yamal_assist_probability = 100.0

elif yamal_event == "Scores and assists":
    yamal_goal_probability = 100.0
    yamal_assist_probability = 100.0


# Probability of recording at least one goal OR one assist.
messi_goal_contribution_probability = (
    1
    - (
        1 - messi_goal_probability / 100
    ) * (
        1 - messi_assist_probability / 100
    )
) * 100

yamal_goal_contribution_probability = (
    1
    - (
        1 - yamal_goal_probability / 100
    ) * (
        1 - yamal_assist_probability / 100
    )
) * 100


# Keep all displayed percentages within valid limits.
messi_goal_probability = clamp(
    messi_goal_probability,
    0,
    100
)

messi_assist_probability = clamp(
    messi_assist_probability,
    0,
    100
)

messi_goal_contribution_probability = clamp(
    messi_goal_contribution_probability,
    0,
    100
)

yamal_goal_probability = clamp(
    yamal_goal_probability,
    0,
    100
)

yamal_assist_probability = clamp(
    yamal_assist_probability,
    0,
    100
)

yamal_goal_contribution_probability = clamp(
    yamal_goal_contribution_probability,
    0,
    100
)

# --------------------------------------------------
# DYNAMIC, DATA-DRIVEN MATCH EVENT ESTIMATES
# --------------------------------------------------

argentina_matches = TEAM_EVENT_DATA["Argentina"]["matches"]
spain_matches = TEAM_EVENT_DATA["Spain"]["matches"]


# --------------------------------------------------
# BASELINE TOURNAMENT AVERAGES
# --------------------------------------------------

baseline_argentina_corners = (
    TEAM_EVENT_DATA["Argentina"]["corners"]
    / argentina_matches
)

baseline_spain_corners = (
    TEAM_EVENT_DATA["Spain"]["corners"]
    / spain_matches
)

baseline_argentina_fouls = (
    TEAM_EVENT_DATA["Argentina"]["fouls_committed"]
    / argentina_matches
)

baseline_spain_fouls = (
    TEAM_EVENT_DATA["Spain"]["fouls_committed"]
    / spain_matches
)

baseline_argentina_yellows = (
    TEAM_EVENT_DATA["Argentina"]["yellow_cards"]
    / argentina_matches
)

baseline_spain_yellows = (
    TEAM_EVENT_DATA["Spain"]["yellow_cards"]
    / spain_matches
)


# Start every scenario from the real tournament averages.
expected_argentina_corners = baseline_argentina_corners
expected_spain_corners = baseline_spain_corners

expected_argentina_fouls = baseline_argentina_fouls
expected_spain_fouls = baseline_spain_fouls

expected_argentina_yellows = baseline_argentina_yellows
expected_spain_yellows = baseline_spain_yellows

penalty_awarded_probability = (
    HISTORICAL_EVENT_PRIORS["penalty_probability"]
)


event_scenario_notes = []


# --------------------------------------------------
# ATTACK-LEVEL EFFECTS
# --------------------------------------------------

# Compare scenario xG with baseline xG.
argentina_attack_ratio = (
    argentina_xg
    / max(0.10, baseline_argentina_xg)
)

spain_attack_ratio = (
    spain_xg
    / max(0.10, baseline_spain_xg)
)


# More attacking pressure generally means more corners.
expected_argentina_corners *= (
    0.55 + 0.45 * argentina_attack_ratio
)

expected_spain_corners *= (
    0.55 + 0.45 * spain_attack_ratio
)


# --------------------------------------------------
# PLAYER AVAILABILITY EFFECTS
# --------------------------------------------------

if messi_status == "Limited fitness":
    expected_argentina_corners *= 0.96

    event_scenario_notes.append(
        "Messi's limited fitness slightly lowers Argentina's "
        "expected attacking pressure and corner total."
    )

elif messi_status == "Unavailable":
    expected_argentina_corners *= 0.90
    expected_argentina_fouls *= 1.04

    event_scenario_notes.append(
        "Messi's absence lowers Argentina's expected corner output "
        "and slightly increases their expected fouls."
    )


if yamal_status == "Limited fitness":
    expected_spain_corners *= 0.96

    event_scenario_notes.append(
        "Yamal's limited fitness slightly lowers Spain's expected "
        "attacking pressure and corner total."
    )

elif yamal_status == "Unavailable":
    expected_spain_corners *= 0.90
    expected_spain_fouls *= 1.04

    event_scenario_notes.append(
        "Yamal's absence lowers Spain's expected corner output "
        "and slightly increases their expected fouls."
    )


# --------------------------------------------------
# FIRST-GOAL GAME-STATE EFFECTS
# --------------------------------------------------

if first_goal == "Argentina":
    # Spain are expected to chase the match.
    expected_spain_corners *= 1.18
    expected_argentina_corners *= 0.94

    expected_argentina_fouls *= 1.08
    expected_argentina_yellows *= 1.08

    event_scenario_notes.append(
        "Argentina scoring first causes Spain to attack more, "
        "raising Spain's projected corners."
    )

elif first_goal == "Spain":
    # Argentina are expected to chase the match.
    expected_argentina_corners *= 1.18
    expected_spain_corners *= 0.94

    expected_spain_fouls *= 1.08
    expected_spain_yellows *= 1.08

    event_scenario_notes.append(
        "Spain scoring first causes Argentina to attack more, "
        "raising Argentina's projected corners."
    )


# --------------------------------------------------
# RED-CARD EFFECTS
# --------------------------------------------------

if argentina_red_card:
    expected_argentina_corners *= 0.68
    expected_spain_corners *= 1.28

    expected_argentina_fouls *= 1.14
    expected_argentina_yellows += 0.65
    expected_spain_yellows *= 1.05

    penalty_awarded_probability *= 1.12

    event_scenario_notes.append(
        "An Argentina red card lowers their attacking output, "
        "raises Spain's corner expectation and increases discipline risk."
    )


if spain_red_card:
    expected_spain_corners *= 0.68
    expected_argentina_corners *= 1.28

    expected_spain_fouls *= 1.14
    expected_spain_yellows += 0.65
    expected_argentina_yellows *= 1.05

    penalty_awarded_probability *= 1.12

    event_scenario_notes.append(
        "A Spain red card lowers their attacking output, "
        "raises Argentina's corner expectation and increases discipline risk."
    )


# --------------------------------------------------
# FORCED PLAYER-EVENT EFFECTS
# --------------------------------------------------

if messi_event in ["Scores", "Scores and assists"]:
    expected_spain_fouls *= 1.05
    expected_spain_yellows *= 1.05

    event_scenario_notes.append(
        "A forced Messi goal slightly increases Spain's projected "
        "fouls and cards as they chase the match."
    )


if yamal_event in ["Scores", "Scores and assists"]:
    expected_argentina_fouls *= 1.05
    expected_argentina_yellows *= 1.05

    event_scenario_notes.append(
        "A forced Yamal goal slightly increases Argentina's projected "
        "fouls and cards as they chase the match."
    )


# --------------------------------------------------
# SAFETY LIMITS
# --------------------------------------------------

expected_argentina_corners = clamp(
    expected_argentina_corners,
    1.0,
    12.0
)

expected_spain_corners = clamp(
    expected_spain_corners,
    1.0,
    12.0
)

expected_argentina_fouls = clamp(
    expected_argentina_fouls,
    5.0,
    22.0
)

expected_spain_fouls = clamp(
    expected_spain_fouls,
    5.0,
    22.0
)

expected_argentina_yellows = clamp(
    expected_argentina_yellows,
    0.2,
    6.0
)

expected_spain_yellows = clamp(
    expected_spain_yellows,
    0.2,
    6.0
)

penalty_awarded_probability = clamp(
    penalty_awarded_probability,
    0.10,
    0.65
)


# --------------------------------------------------
# FINAL EVENT TOTALS
# --------------------------------------------------

expected_total_corners = (
    expected_argentina_corners
    + expected_spain_corners
)

expected_total_fouls = (
    expected_argentina_fouls
    + expected_spain_fouls
)

expected_total_yellow_cards = (
    expected_argentina_yellows
    + expected_spain_yellows
)


# A team's foul-derived free kicks are estimated from
# the opponent's projected fouls.
expected_argentina_free_kicks = expected_spain_fouls
expected_spain_free_kicks = expected_argentina_fouls

expected_total_foul_free_kicks = (
    expected_argentina_free_kicks
    + expected_spain_free_kicks
)


penalty_conversion_probability = (
    HISTORICAL_EVENT_PRIORS[
        "penalty_conversion_probability"
    ]
)

penalty_goal_probability = (
    penalty_awarded_probability
    * penalty_conversion_probability
)

# --------------------------------------------------
# PAGE LAYOUT
# --------------------------------------------------

active_scenario_count = len(scenario_notes)

st.title("2026 World Cup Final Prediction Model")

st.caption(
    "Argentina vs Spain | Statistical prediction and interactive scenario analysis"
)

# --------------------------------------------------
# GLOBAL SCENARIO STATUS
# --------------------------------------------------

if active_scenario_count == 0:
    st.info(
        "Baseline model active. No What-If adjustments are currently applied. "
        "Use the sidebar to test alternative match scenarios."
    )
else:
    st.warning(
        f"Scenario model active: {active_scenario_count} adjustment(s) applied. "
        "All match probabilities, expected goals, score predictions and player "
        "probabilities on every tab have been recalculated."
    )

with st.container(border=True):
    st.subheader("Current scenario")

    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)

    with scenario_col1:
        st.write("Messi")
        st.write(f"Availability: **{messi_status}**")
        st.write(f"Event: **{messi_event}**")

    with scenario_col2:
        st.write("Lamine Yamal")
        st.write(f"Availability: **{yamal_status}**")
        st.write(f"Event: **{yamal_event}**")

    with scenario_col3:
        st.write("Match events")
        st.write(f"First goal: **{first_goal}**")

        if argentina_red_card:
            st.write("Red card: **Argentina**")
        elif spain_red_card:
            st.write("Red card: **Spain**")
        else:
            st.write("Red card: **None**")

st.caption(
    "Every control in the sidebar affects the entire model, including match "
    "probabilities, expected goals, likely scorelines and player-event estimates."
)

play_tab, prediction_tab, simulator_tab, player_tab, events_tab, explanation_tab = st.tabs(
    [
        "PLAY THE FINAL — START HERE",
        "Match prediction",
        "Automatic simulator",
        "Player probabilities",
        "Match events",
        "Methodology"
    ]
)

# --------------------------------------------------
# MATCH-PREDICTION TAB
# --------------------------------------------------

with prediction_tab:

    st.subheader("Result probabilities")

    st.caption(
        "These probabilities reflect every active scenario selected in the sidebar."
    )

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Argentina win",
            f"{argentina_win_probability:.1f}%"
        )

    with result_col2:
        st.metric(
            "Draw after 90 minutes",
            f"{draw_probability:.1f}%"
        )

    with result_col3:
        st.metric(
            "Spain win",
            f"{spain_win_probability:.1f}%"
        )

    st.success(
        f"Current model favourite: {predicted_winner}"
    )

    st.divider()

    st.subheader("Expected match output")

    score_col1, score_col2, score_col3 = st.columns(3)

    with score_col1:
        st.metric(
            "Most likely score",
            (
                f"Argentina {most_likely_score[0]}–"
                f"{most_likely_score[1]} Spain"
            )
        )

    with score_col2:
        st.metric(
            "Argentina expected goals",
            f"{argentina_xg:.2f}",
            delta=(
                f"{argentina_xg - baseline_argentina_xg:+.2f} "
                "from baseline"
            )
        )

    with score_col3:
        st.metric(
            "Spain expected goals",
            f"{spain_xg:.2f}",
            delta=(
                f"{spain_xg - baseline_spain_xg:+.2f} "
                "from baseline"
            )
        )

    st.write(
        "Probability of the most likely scoreline: "
        f"**{highest_score_probability * 100:.1f}%**"
    )

    st.divider()

    st.subheader("How this prediction was produced")

    method_col1, method_col2 = st.columns(2)

    with method_col1:
        with st.container(border=True):
            st.write("Team-strength inputs")

            st.write(
                f"Argentina model rating: **{argentina_rating:.2f}**"
            )

            st.write(
                f"Spain model rating: **{spain_rating:.2f}**"
            )

            st.write(
                "Ratings combine Elo, tournament goals, expected goals, "
                "defensive performance, shots, possession and chances created."
            )

    with method_col2:
        with st.container(border=True):
            st.write("Score model")

            st.write(
                "The team ratings are converted into expected-goals estimates."
            )

            st.write(
                "A Poisson distribution calculates the probability of each "
                "scoreline from 0–0 through 7–7."
            )

            st.write(
                "Winning, drawing and losing scorelines are then added together "
                "to produce the result probabilities."
            )

    with st.expander("View the raw team statistics used by the model"):

        stat_col1, stat_col2, stat_col3 = st.columns(3)

        with stat_col1:
            st.write("Statistic")
            st.write("Elo rating")
            st.write("Goals per game")
            st.write("Expected goals per game")
            st.write("Goals conceded per game")
            st.write("Shots per game")
            st.write("Possession")
            st.write("Chances created per game")

        with stat_col2:
            st.write("Argentina")
            st.write(TEAM_DATA["Argentina"]["elo"])
            st.write(TEAM_DATA["Argentina"]["goals_per_game"])
            st.write(TEAM_DATA["Argentina"]["xg_per_game"])
            st.write(TEAM_DATA["Argentina"]["goals_against_per_game"])
            st.write(TEAM_DATA["Argentina"]["shots_per_game"])
            st.write(f'{TEAM_DATA["Argentina"]["possession"]}%')
            st.write(
                TEAM_DATA["Argentina"]["chances_created_per_game"]
            )

        with stat_col3:
            st.write("Spain")
            st.write(TEAM_DATA["Spain"]["elo"])
            st.write(TEAM_DATA["Spain"]["goals_per_game"])
            st.write(TEAM_DATA["Spain"]["xg_per_game"])
            st.write(TEAM_DATA["Spain"]["goals_against_per_game"])
            st.write(TEAM_DATA["Spain"]["shots_per_game"])
            st.write(f'{TEAM_DATA["Spain"]["possession"]}%')
            st.write(
                TEAM_DATA["Spain"]["chances_created_per_game"]
            )

# --------------------------------------------------
# PLAYER-PROBABILITY TAB
# --------------------------------------------------

with player_tab:

    st.subheader("Player-event estimates")

    st.caption(
        "These estimates automatically respond to all active scenarios, "
        "including fitness, player events, first goals and red cards."
    )

    with st.container(border=True):

        st.subheader("Lionel Messi")

        messi_col1, messi_col2 = st.columns(2)

        with messi_col1:
            st.metric(
                "Estimated goal probability",
                f"{messi_goal_probability:.1f}%"
            )

        with messi_col2:
            st.metric(
                "Estimated assist probability",
                f"{messi_assist_probability:.1f}%"
            )

        st.write(
            f"Current condition: **{messi_status}**"
        )

        st.write(
            f"Selected event scenario: **{messi_event}**"
        )

    with st.container(border=True):

        st.subheader("Lamine Yamal")

        yamal_col1, yamal_col2 = st.columns(2)

        with yamal_col1:
            st.metric(
                "Estimated goal probability",
                f"{yamal_goal_probability:.1f}%"
            )

        with yamal_col2:
            st.metric(
                "Estimated assist probability",
                f"{yamal_assist_probability:.1f}%"
            )

        st.write(
            f"Current condition: **{yamal_status}**"
        )

        st.write(
            f"Selected event scenario: **{yamal_event}**"
        )

    st.subheader("How player probabilities are estimated")

    st.write(
        "The current player probabilities use the team's adjusted expected-goals "
        "value as their starting point. Fitness and availability scenarios then "
        "increase or decrease the player's estimated involvement."
    )

    st.info(
    "Player goal estimates use tournament minutes, xG, shots and "
    "shots on target. Assist estimates use recorded assists with "
    "small-sample smoothing. Verified expected-assist data was not "
    "available from the current source, so xA is not used."
)

# --------------------------------------------------
# METHODOLOGY AND EXPLANATION TAB
# --------------------------------------------------
# --------------------------------------------------
# MATCH EVENTS TAB
# --------------------------------------------------

with events_tab:

    st.subheader("Projected match events")

    st.caption(
    "These projections begin with Argentina and Spain's real "
    "tournament averages, then update automatically for every "
    "active player, first-goal and red-card scenario."
)

    st.subheader("Corners")

    corner_col1, corner_col2, corner_col3 = st.columns(3)

    with corner_col1:
        st.metric(
            "Argentina expected corners",
            f"{expected_argentina_corners:.1f}"
        )

    with corner_col2:
        st.metric(
            "Spain expected corners",
            f"{expected_spain_corners:.1f}"
        )

    with corner_col3:
        st.metric(
            "Expected total corners",
            f"{expected_total_corners:.1f}"
        )

    st.caption(
        "Argentina have taken 37 corners in seven matches. "
        "Spain have taken 45 corners in seven matches."
    )

    st.divider()

    st.subheader("Fouls and foul-derived free kicks")

    foul_col1, foul_col2, foul_col3 = st.columns(3)

    with foul_col1:
        st.metric(
            "Argentina expected fouls",
            f"{expected_argentina_fouls:.1f}"
        )

    with foul_col2:
        st.metric(
            "Spain expected fouls",
            f"{expected_spain_fouls:.1f}"
        )

    with foul_col3:
        st.metric(
            "Expected total fouls",
            f"{expected_total_fouls:.1f}"
        )

    free_kick_col1, free_kick_col2, free_kick_col3 = st.columns(3)

    with free_kick_col1:
        st.metric(
            "Argentina foul-derived free kicks",
            f"{expected_argentina_free_kicks:.1f}"
        )

    with free_kick_col2:
        st.metric(
            "Spain foul-derived free kicks",
            f"{expected_spain_free_kicks:.1f}"
        )

    with free_kick_col3:
        st.metric(
            "Total foul-derived free kicks",
            f"{expected_total_foul_free_kicks:.1f}"
        )

    st.caption(
        "Free-kick estimates use opponent fouls committed. "
        "They do not include every offside or indirect free kick."
    )

    st.divider()

    st.subheader("Discipline")

    card_col1, card_col2, card_col3 = st.columns(3)

    with card_col1:
        st.metric(
            "Argentina expected yellow cards",
            f"{expected_argentina_yellows:.1f}"
        )

    with card_col2:
        st.metric(
            "Spain expected yellow cards",
            f"{expected_spain_yellows:.1f}"
        )

    with card_col3:
        st.metric(
            "Expected total yellow cards",
            f"{expected_total_yellow_cards:.1f}"
        )

    st.divider()

    st.subheader("Penalty likelihood")

    penalty_col1, penalty_col2 = st.columns(2)

    with penalty_col1:
        st.metric(
            "Chance of a penalty being awarded",
            f"{penalty_awarded_probability * 100:.1f}%"
        )

    with penalty_col2:
        st.metric(
            "Chance of a converted penalty goal",
            f"{penalty_goal_probability * 100:.1f}%"
        )

    st.caption(
        "Penalty likelihood is based on 52 penalties awarded "
        "across the 2018 and 2022 World Cups. The conversion "
        "estimate is approximately 75%."
    )

    st.info(
        "The model does not predict a penalty minute. We do not "
        "currently have reliable minute-by-minute historical data "
        "to support a defensible estimate."
    )
if event_scenario_notes:

    st.subheader("Active scenario effects")

    for note in event_scenario_notes:
        st.write(f"• {note}")

else:
    st.info(
        "Baseline event model active. No scenario adjustments are currently applied."
    )
    with st.expander("View the calculations"):

        st.write(
            f"Argentina corners per match: "
            f"37 ÷ 7 = {baseline_argentina_corners:.2f}"
        )

        st.write(
            f"Spain corners per match: "
            f"45 ÷ 7 = {baseline_spain_corners:.2f}"
        )

        st.write(
            f"Argentina fouls per match: "
            f"81 ÷ 7 = {baseline_argentina_fouls:.2f}"
        )

        st.write(
            f"Spain fouls per match: "
            f"80 ÷ 7 = {baseline_spain_fouls:.2f}"
        )

        st.write(
            "Penalty awarded probability: "
            "52 ÷ 128 = 40.63%"
        )

        st.write(
            "Estimated penalty conversion rate: "
            "39 ÷ 52 = 75.00%"
        )
with explanation_tab:

    st.subheader("Current scenario impact")

    if scenario_notes:

        st.write(
            "The following changes have been applied across the entire model:"
        )

        for note in scenario_notes:
            st.write(f"- {note}")

    else:
        st.write(
            "No scenario adjustments are active. The displayed results represent "
            "the model's baseline prediction."
        )

    st.divider()

    st.subheader("Baseline compared with current scenario")

    comparison_col1, comparison_col2 = st.columns(2)

    with comparison_col1:
        with st.container(border=True):
            st.write("Argentina")

            st.metric(
                "Baseline expected goals",
                f"{baseline_argentina_xg:.2f}"
            )

            st.metric(
                "Scenario expected goals",
                f"{argentina_xg:.2f}",
                delta=(
                    f"{argentina_xg - baseline_argentina_xg:+.2f}"
                )
            )

    with comparison_col2:
        with st.container(border=True):
            st.write("Spain")

            st.metric(
                "Baseline expected goals",
                f"{baseline_spain_xg:.2f}"
            )

            st.metric(
                "Scenario expected goals",
                f"{spain_xg:.2f}",
                delta=(
                    f"{spain_xg - baseline_spain_xg:+.2f}"
                )
            )

    st.divider()

    st.subheader("Model calculation process")

    st.write(
        "**1. Raw statistics:** The model begins with Elo ratings and current "
        "tournament performance data."
    )

    st.write(
        "**2. Normalisation:** Each statistic is converted to a comparable "
        "0–100 scale."
    )

    st.write(
        "**3. Weighting:** Elo, goals, expected goals, defence, shots, "
        "possession and chance creation receive different weights."
    )

    st.write(
        "**4. Team ratings:** The weighted statistics produce one overall "
        "rating for Argentina and one for Spain."
    )

    st.write(
        "**5. Expected goals:** The difference between the two ratings is "
        "converted into expected-goals estimates."
    )

    st.write(
        "**6. Scenario adjustments:** Player fitness, forced player events, "
        "first goals and red cards alter those expected-goals values."
    )

    st.write(
        "**7. Poisson score model:** The adjusted expected goals are used to "
        "calculate thousands of possible score outcomes mathematically."
    )

    st.write(
        "**8. Final results:** All winning, drawing and losing scorelines are "
        "combined into the displayed result probabilities."
    )

    st.divider()

    st.subheader("Model limitations")

    st.write(
        "- Several What-If multipliers remain provisional and require "
        "historical calibration."
    )

    st.write(
        "- Player-event estimates require official player-level tournament data."
    )

    st.write(
        "- The model does not yet account for confirmed starting lineups, "
        "substitution timing or tactical formations."
    )

    st.write(
        "- Expected goals are estimates rather than guarantees; individual "
        "match events remain highly unpredictable."
    )

# --------------------------------------------------
# KNOCKOUT MATCH SIMULATOR
# --------------------------------------------------

def calculate_draw_probability(home_xg, away_xg, max_goals=8):
    draw_chance = 0.0

    for goals in range(max_goals):
        draw_chance += (
            poisson.pmf(goals, home_xg)
            * poisson.pmf(goals, away_xg)
        )

    return draw_chance


# Probability that the match is level after 90 minutes.
ninety_minute_draw_probability = calculate_draw_probability(
    argentina_xg,
    spain_xg
)

# Extra time lasts one third as long as regulation time.
extra_time_argentina_xg = argentina_xg / 3
extra_time_spain_xg = spain_xg / 3

# Probability that extra time itself finishes level.
extra_time_draw_probability = calculate_draw_probability(
    extra_time_argentina_xg,
    extra_time_spain_xg
)

finish_in_90_probability = (
    1 - ninety_minute_draw_probability
)

finish_in_extra_time_probability = (
    ninety_minute_draw_probability
    * (1 - extra_time_draw_probability)
)

finish_on_penalties_probability = (
    ninety_minute_draw_probability
    * extra_time_draw_probability
)

# Convert to percentages.
finish_in_90_percentage = finish_in_90_probability * 100

finish_in_extra_time_percentage = (
    finish_in_extra_time_probability * 100
)

finish_on_penalties_percentage = (
    finish_on_penalties_probability * 100
)


def create_knockout_match_simulation():

    events = []
    used_minutes = set()

    def unique_minute(start, end):
        available_minutes = [
            minute
            for minute in range(start, end + 1)
            if minute not in used_minutes
        ]

        if not available_minutes:
            return end

        minute = random.choice(available_minutes)
        used_minutes.add(minute)
        return minute

    def add_event(minute, description):
        events.append(
            {
                "minute": minute,
                "description": description
            }
        )

    # --------------------------------------------------
    # REGULATION-TIME SCORE
    # --------------------------------------------------

    argentina_90_goals = min(
        int(poisson.rvs(mu=max(0.10, argentina_xg))),
        6
    )

    spain_90_goals = min(
        int(poisson.rvs(mu=max(0.10, spain_xg))),
        6
    )

    # Forced player goals must actually occur.
    if (
        messi_status != "Unavailable"
        and messi_event in ["Scores", "Scores and assists"]
        and argentina_90_goals == 0
    ):
        argentina_90_goals = 1

    if (
        yamal_status != "Unavailable"
        and yamal_event in ["Scores", "Scores and assists"]
        and spain_90_goals == 0
    ):
        spain_90_goals = 1

    # Forced first-goal teams must score.
    if first_goal == "Argentina" and argentina_90_goals == 0:
        argentina_90_goals = 1

    if first_goal == "Spain" and spain_90_goals == 0:
        spain_90_goals = 1

    argentina_goal_minutes = []
    spain_goal_minutes = []

    # --------------------------------------------------
    # FIRST-GOAL SCENARIO
    # --------------------------------------------------

    if first_goal == "Argentina":
        argentina_goal_minutes.append(
            unique_minute(5, 35)
        )

    elif first_goal == "Spain":
        spain_goal_minutes.append(
            unique_minute(5, 35)
        )

    # --------------------------------------------------
    # REMAINING REGULATION GOALS
    # --------------------------------------------------

    while len(argentina_goal_minutes) < argentina_90_goals:

        start_minute = 1

        if first_goal == "Spain" and spain_goal_minutes:
            start_minute = spain_goal_minutes[0] + 1

        argentina_goal_minutes.append(
            unique_minute(
                min(start_minute, 90),
                90
            )
        )

    while len(spain_goal_minutes) < spain_90_goals:

        start_minute = 1

        if first_goal == "Argentina" and argentina_goal_minutes:
            start_minute = argentina_goal_minutes[0] + 1

        spain_goal_minutes.append(
            unique_minute(
                min(start_minute, 90),
                90
            )
        )

    argentina_goal_minutes.sort()
    spain_goal_minutes.sort()

    # --------------------------------------------------
    # ARGENTINA GOALSCORERS
    # --------------------------------------------------

    forced_messi_goal_used = False

    for minute in argentina_goal_minutes:

        if (
            messi_status != "Unavailable"
            and messi_event in ["Scores", "Scores and assists"]
            and not forced_messi_goal_used
        ):
            scorer = "Lionel Messi"
            forced_messi_goal_used = True

        elif (
            messi_status != "Unavailable"
            and random.random()
            < messi_goal_probability / 100
        ):
            scorer = "Lionel Messi"

        else:
            scorer = random.choice(
                [
                    "Argentina forward",
                    "Argentina midfielder",
                    "Argentina set-piece scorer"
                ]
            )

        add_event(
            minute,
            f"Goal — {scorer} scores for Argentina"
        )

    # --------------------------------------------------
    # SPAIN GOALSCORERS
    # --------------------------------------------------

    forced_yamal_goal_used = False

    for minute in spain_goal_minutes:

        if (
            yamal_status != "Unavailable"
            and yamal_event in ["Scores", "Scores and assists"]
            and not forced_yamal_goal_used
        ):
            scorer = "Lamine Yamal"
            forced_yamal_goal_used = True

        elif (
            yamal_status != "Unavailable"
            and random.random()
            < yamal_goal_probability / 100
        ):
            scorer = "Lamine Yamal"

        else:
            scorer = random.choice(
                [
                    "Spain forward",
                    "Spain midfielder",
                    "Spain set-piece scorer"
                ]
            )

        add_event(
            minute,
            f"Goal — {scorer} scores for Spain"
        )

    # --------------------------------------------------
    # ASSIST SCENARIOS
    # --------------------------------------------------

    if (
        messi_status != "Unavailable"
        and messi_event in ["Assists", "Scores and assists"]
        and argentina_goal_minutes
    ):
        assisted_minute = random.choice(
            argentina_goal_minutes
        )

        add_event(
            assisted_minute,
            "Assist recorded — Lionel Messi"
        )

    if (
        yamal_status != "Unavailable"
        and yamal_event in ["Assists", "Scores and assists"]
        and spain_goal_minutes
    ):
        assisted_minute = random.choice(
            spain_goal_minutes
        )

        add_event(
            assisted_minute,
            "Assist recorded — Lamine Yamal"
        )

    # --------------------------------------------------
    # CORNERS
    # --------------------------------------------------

    argentina_corner_mean = globals().get(
        "expected_argentina_corners",
        5.0
    )

    spain_corner_mean = globals().get(
        "expected_spain_corners",
        5.0
    )

    argentina_corner_total = max(
        0,
        min(
            14,
            int(
                round(
                    random.gauss(
                        argentina_corner_mean,
                        1.4
                    )
                )
            )
        )
    )

    spain_corner_total = max(
        0,
        min(
            14,
            int(
                round(
                    random.gauss(
                        spain_corner_mean,
                        1.4
                    )
                )
            )
        )
    )

    for _ in range(argentina_corner_total):
        add_event(
            unique_minute(1, 90),
            "Corner — Argentina"
        )

    for _ in range(spain_corner_total):
        add_event(
            unique_minute(1, 90),
            "Corner — Spain"
        )

    # --------------------------------------------------
    # CARDS
    # --------------------------------------------------

    argentina_yellow_mean = globals().get(
        "expected_argentina_yellows",
        1.3
    )

    spain_yellow_mean = globals().get(
        "expected_spain_yellows",
        1.0
    )

    argentina_yellows = max(
        0,
        min(
            5,
            int(
                round(
                    random.gauss(
                        argentina_yellow_mean,
                        0.8
                    )
                )
            )
        )
    )

    spain_yellows = max(
        0,
        min(
            5,
            int(
                round(
                    random.gauss(
                        spain_yellow_mean,
                        0.8
                    )
                )
            )
        )
    )

    for _ in range(argentina_yellows):
        add_event(
            unique_minute(10, 90),
            "Yellow card — Argentina"
        )

    for _ in range(spain_yellows):
        add_event(
            unique_minute(10, 90),
            "Yellow card — Spain"
        )

    if argentina_red_card:
        add_event(
            unique_minute(20, 80),
            "Red card — Argentina"
        )

    if spain_red_card:
        add_event(
            unique_minute(20, 80),
            "Red card — Spain"
        )

    # --------------------------------------------------
    # CHANCES
    # --------------------------------------------------

    number_of_chances = random.randint(5, 9)

    for _ in range(number_of_chances):

        team = random.choices(
            ["Argentina", "Spain"],
            weights=[
                max(0.10, argentina_xg),
                max(0.10, spain_xg)
            ],
            k=1
        )[0]

        outcome = random.choice(
            [
                "shot saved",
                "shot blocked",
                "shot wide",
                "shot hits the post"
            ]
        )

        add_event(
            unique_minute(1, 90),
            f"{team} {outcome}"
        )

    argentina_final_goals = argentina_90_goals
    spain_final_goals = spain_90_goals

    resolution_stage = "90 minutes"
    penalty_result = None
    shootout_winner = None

    # --------------------------------------------------
    # EXTRA TIME
    # --------------------------------------------------

    if argentina_90_goals == spain_90_goals:

        add_event(
            90,
            "Level after 90 minutes — extra time begins"
        )

        argentina_extra_time_goals = min(
            int(
                poisson.rvs(
                    mu=max(
                        0.05,
                        argentina_xg / 3
                    )
                )
            ),
            3
        )

        spain_extra_time_goals = min(
            int(
                poisson.rvs(
                    mu=max(
                        0.05,
                        spain_xg / 3
                    )
                )
            ),
            3
        )

        for _ in range(argentina_extra_time_goals):

            minute = unique_minute(91, 120)

            if (
                messi_status != "Unavailable"
                and random.random()
                < messi_goal_probability / 100
            ):
                scorer = "Lionel Messi"
            else:
                scorer = "Argentina player"

            add_event(
                minute,
                (
                    f"Extra-time goal — {scorer} "
                    f"scores for Argentina"
                )
            )

        for _ in range(spain_extra_time_goals):

            minute = unique_minute(91, 120)

            if (
                yamal_status != "Unavailable"
                and random.random()
                < yamal_goal_probability / 100
            ):
                scorer = "Lamine Yamal"
            else:
                scorer = "Spain player"

            add_event(
                minute,
                (
                    f"Extra-time goal — {scorer} "
                    f"scores for Spain"
                )
            )

        argentina_final_goals += argentina_extra_time_goals
        spain_final_goals += spain_extra_time_goals

        resolution_stage = "extra time"

    # --------------------------------------------------
    # PENALTY SHOOTOUT
    # --------------------------------------------------

    if argentina_final_goals == spain_final_goals:

        argentina_shootout_strength = argentina_rating
        spain_shootout_strength = spain_rating

        if messi_status == "Fully fit":
            argentina_shootout_strength += 3

        elif messi_status == "Limited fitness":
            argentina_shootout_strength += 1

        elif messi_status == "Unavailable":
            argentina_shootout_strength -= 4

        if yamal_status == "Fully fit":
            spain_shootout_strength += 2

        elif yamal_status == "Limited fitness":
            spain_shootout_strength += 0.5

        elif yamal_status == "Unavailable":
            spain_shootout_strength -= 3

        if argentina_red_card:
            argentina_shootout_strength -= 6

        if spain_red_card:
            spain_shootout_strength -= 6

        if messi_event in ["Scores", "Scores and assists"]:
            argentina_shootout_strength += 2

        if yamal_event in ["Scores", "Scores and assists"]:
            spain_shootout_strength += 2

        argentina_shootout_strength = max(
            1,
            argentina_shootout_strength
        )

        spain_shootout_strength = max(
            1,
            spain_shootout_strength
        )

        argentina_shootout_probability = (
            argentina_shootout_strength
            / (
                argentina_shootout_strength
                + spain_shootout_strength
            )
        )

        if random.random() < argentina_shootout_probability:
            shootout_winner = "Argentina"
            argentina_penalties = random.choice([4, 5])
            spain_penalties = argentina_penalties - 1

        else:
            shootout_winner = "Spain"
            spain_penalties = random.choice([4, 5])
            argentina_penalties = spain_penalties - 1

        penalty_result = (
            f"{shootout_winner} win the shootout "
            f"{argentina_penalties}–{spain_penalties}"
        )

        add_event(
            121,
            penalty_result
        )

        resolution_stage = "penalty shootout"

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    if shootout_winner is not None:
        champion = shootout_winner

    elif argentina_final_goals > spain_final_goals:
        champion = "Argentina"

    else:
        champion = "Spain"

    events.sort(
        key=lambda event: event["minute"]
    )

    return {
        "argentina_90_goals": argentina_90_goals,
        "spain_90_goals": spain_90_goals,
        "argentina_final_goals": argentina_final_goals,
        "spain_final_goals": spain_final_goals,
        "resolution_stage": resolution_stage,
        "penalty_result": penalty_result,
        "champion": champion,
        "argentina_corners": argentina_corner_total,
        "spain_corners": spain_corner_total,
        "events": events
    }
    
# --------------------------------------------------
# SIMULATOR TAB
# --------------------------------------------------

with simulator_tab:

    st.title("🏆 FIFA World Cup Final Simulator")
    st.caption("Run thousands of possible World Cup Finals using live team strengths and your own What-If scenarios.")
    st.success(
    "🔥 Change any What-If scenario, then press **Run New Match Simulation** to create an entirely new World Cup Final."
)
    st.write(
        "Change the What-If controls in the sidebar, then run "
        "a complete knockout simulation. Every run uses the "
        "current expected goals, player probabilities and "
        "match-event projections."
    )

    st.info(
        "A drawn match after 90 minutes automatically continues "
        "to extra time and, if required, a penalty shootout."
    )

    st.subheader("How is the match likely to be decided?")

    stage_col1, stage_col2, stage_col3 = st.columns(3)

    with stage_col1:
        st.metric(
            "Decided in 90 minutes",
            f"{finish_in_90_percentage:.1f}%"
        )

    with stage_col2:
        st.metric(
            "Decided in extra time",
            f"{finish_in_extra_time_percentage:.1f}%"
        )

    with stage_col3:
        st.metric(
            "Decided by penalties",
            f"{finish_on_penalties_percentage:.1f}%"
        )

    st.caption(
        "These probabilities update with every active What-If "
        "because they are calculated from the scenario-adjusted "
        "expected goals."
    )

    st.divider()

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        run_simulation = st.button(
            "Run a new match simulation",
            type="primary",
            use_container_width=True
        )

    with button_col2:
        clear_simulation = st.button(
            "Clear current simulation",
            use_container_width=True
        )

    if clear_simulation:
        st.session_state.pop(
            "match_simulation",
            None
        )

    if run_simulation:
        st.session_state.match_simulation = (
            create_knockout_match_simulation()
        )

    if "match_simulation" not in st.session_state:

        st.warning(
            "No match has been simulated yet. Select scenarios "
            "in the sidebar and press 'Run a new match simulation'."
        )

    else:

        simulation = st.session_state.match_simulation

        st.subheader("🏆 WORLD CUP FINAL RESULT")

        result_col1, result_col2 = st.columns([2, 1])

        with result_col1:
            st.metric(
                "Score after play",
                (
                    f"Argentina "
                    f"{simulation['argentina_final_goals']}–"
                    f"{simulation['spain_final_goals']} "
                    f"Spain"
                )
            )

        with result_col2:
            st.metric(
                "Match decided",
                simulation["resolution_stage"].title()
            )

        if simulation["penalty_result"]:
            st.success(
                simulation["penalty_result"]
            )

        elif (
            simulation["argentina_final_goals"]
            > simulation["spain_final_goals"]
        ):
            st.success(
                "Argentina win the simulated final."
            )

        else:
            st.success(
                "Spain win the simulated final."
            )

        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:
            st.metric(
                "Argentina corners",
                simulation["argentina_corners"]
            )

        with summary_col2:
            st.metric(
                "Spain corners",
                simulation["spain_corners"]
            )

        st.divider()

        st.subheader("Match timeline")

        for event in simulation["events"]:

            if event["minute"] == 121:
                minute_label = "Shootout"

            elif event["minute"] == 90:
                minute_label = "90'"

            else:
                minute_label = f"{event['minute']}'"

            st.write(
                f"**{minute_label}** — "
                f"{event['description']}"
            )

        st.caption(
            "This represents one probability-driven simulation, "
            "not a guaranteed prediction. Run it repeatedly to "
            "explore different ways the final could unfold."
        )
        # --------------------------------------------------
# INSTANT FINAL GENERATOR
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader("Instant Final Generator")

st.sidebar.caption(
    "Generate a completely new World Cup Final using "
    "all active What-If scenarios."
)

instant_simulation_button = st.sidebar.button(
    "Generate a New Final",
    type="primary",
    use_container_width=True,
    key="instant_final_button"
)

if instant_simulation_button:

    st.session_state.match_simulation = (
        create_knockout_match_simulation()
    )

    instant_simulation = st.session_state.match_simulation

    total_goals = (
        instant_simulation["argentina_final_goals"]
        + instant_simulation["spain_final_goals"]
    )

    drama_score = 1

    if total_goals >= 3:
        drama_score += 1

    if total_goals >= 5:
        drama_score += 1

    if instant_simulation["resolution_stage"] == "extra time":
        drama_score += 1

    if instant_simulation["resolution_stage"] == "penalty shootout":
        drama_score += 2

    if argentina_red_card or spain_red_card:
        drama_score += 1

    drama_score = min(5, drama_score)

    st.session_state.simulation_drama_score = drama_score

    st.toast(
        f"New final generated: "
        f"{instant_simulation['champion']} are champions!"
    )

    if drama_score >= 4:
        st.balloons()


if "match_simulation" in st.session_state:

    sidebar_simulation = st.session_state.match_simulation

    st.sidebar.markdown("#### Latest simulated final")

    st.sidebar.metric(
        "Score after play",
        (
            f"Argentina "
            f"{sidebar_simulation['argentina_final_goals']}–"
            f"{sidebar_simulation['spain_final_goals']} "
            f"Spain"
        )
    )

    st.sidebar.write(
        f"**Champion:** {sidebar_simulation['champion']}"
    )

    st.sidebar.write(
        f"**Decided:** "
        f"{sidebar_simulation['resolution_stage'].title()}"
    )

    if sidebar_simulation["penalty_result"]:
        st.sidebar.write(
            f"**Shootout:** "
            f"{sidebar_simulation['penalty_result']}"
        )

    drama_score = st.session_state.get(
        "simulation_drama_score",
        1
    )

    drama_labels = {
        1: "Tactical battle",
        2: "Competitive final",
        3: "Exciting final",
        4: "Instant classic",
        5: "All-time World Cup classic"
    }

    st.sidebar.write(
        f"**Drama rating:** "
        f"{'★' * drama_score}{'☆' * (5 - drama_score)}"
    )

    st.sidebar.caption(
        drama_labels[drama_score]
    )

    st.sidebar.info(
        "Open the Interactive Simulator tab to view "
        "the complete minute-by-minute timeline."
    )
    # --------------------------------------------------
# PLAY THE WORLD CUP FINAL
# --------------------------------------------------

st.divider()
st.header("PLAY THE WORLD CUP FINAL")

st.write(
    "Take control of the biggest moments. Your decisions change "
    "the score, expected goals and live win probabilities."
)


# --------------------------------------------------
# GAME SETUP
# --------------------------------------------------

PLAYABLE_MOMENTS = [
    {
        "minute": 12,
        "title": "Messi receives the ball outside the penalty area.",
        "team": "Argentina",
        "choices": {
            "Shoot from distance": {
                "success": 0.13,
                "xg_change": 0.13,
                "success_text": "Messi finds the top corner.",
                "failure_text": "The shot is saved comfortably."
            },
            "Play a through ball": {
                "success": 0.25,
                "xg_change": 0.24,
                "success_text": "The pass unlocks Spain and Argentina score.",
                "failure_text": "Spain intercept the final pass."
            },
            "Keep possession": {
                "success": 0.70,
                "xg_change": 0.05,
                "success_text": "Argentina retain control and build pressure.",
                "failure_text": "Spain force Argentina backwards."
            }
        }
    },
    {
        "minute": 24,
        "title": "Lamine Yamal isolates the Argentina left-back.",
        "team": "Spain",
        "choices": {
            "Cut inside and shoot": {
                "success": 0.18,
                "xg_change": 0.18,
                "success_text": "Yamal curls the ball into the far corner.",
                "failure_text": "The shot bends narrowly wide."
            },
            "Cross into the area": {
                "success": 0.22,
                "xg_change": 0.21,
                "success_text": "The cross is converted by Spain.",
                "failure_text": "Argentina clear the danger."
            },
            "Recycle possession": {
                "success": 0.72,
                "xg_change": 0.05,
                "success_text": "Spain maintain pressure around the box.",
                "failure_text": "Argentina win possession."
            }
        }
    },
    {
        "minute": 38,
        "title": "Argentina win a dangerous free kick.",
        "team": "Argentina",
        "choices": {
            "Messi shoots directly": {
                "success": 0.16,
                "xg_change": 0.16,
                "success_text": "Messi scores directly from the free kick.",
                "failure_text": "The goalkeeper pushes it away."
            },
            "Cross toward the back post": {
                "success": 0.20,
                "xg_change": 0.19,
                "success_text": "Argentina score from the delivery.",
                "failure_text": "Spain head the cross clear."
            },
            "Use a rehearsed routine": {
                "success": 0.24,
                "xg_change": 0.22,
                "success_text": "The routine works perfectly and Argentina score.",
                "failure_text": "Spain read the routine and block it."
            }
        }
    },
    {
        "minute": 52,
        "title": "Spain begin the second half with sustained pressure.",
        "team": "Spain",
        "choices": {
            "Press aggressively": {
                "success": 0.24,
                "xg_change": 0.22,
                "success_text": "Spain win the ball high and score.",
                "failure_text": "Argentina escape the press."
            },
            "Attack through Yamal": {
                "success": 0.20,
                "xg_change": 0.19,
                "success_text": "Yamal creates Spain's goal.",
                "failure_text": "Argentina double-team Yamal successfully."
            },
            "Control possession": {
                "success": 0.75,
                "xg_change": 0.06,
                "success_text": "Spain take control of the match tempo.",
                "failure_text": "Argentina launch a counterattack."
            }
        }
    },
    {
        "minute": 67,
        "title": "Argentina break forward with space.",
        "team": "Argentina",
        "choices": {
            "Messi attacks the defence": {
                "success": 0.25,
                "xg_change": 0.24,
                "success_text": "Messi beats his defender and scores.",
                "failure_text": "Spain stop Messi at the edge of the area."
            },
            "Pass to the striker": {
                "success": 0.30,
                "xg_change": 0.28,
                "success_text": "The striker finishes Argentina's counterattack.",
                "failure_text": "The final pass is slightly overhit."
            },
            "Slow the attack down": {
                "success": 0.72,
                "xg_change": 0.05,
                "success_text": "Argentina retain possession in Spain's half.",
                "failure_text": "Spain recover their defensive shape."
            }
        }
    },
    {
        "minute": 78,
        "title": "Spain have a major decision with the match entering its final phase.",
        "team": "Spain",
        "choices": {
            "Commit players forward": {
                "success": 0.28,
                "xg_change": 0.27,
                "success_text": "Spain overload the defence and score.",
                "failure_text": "Argentina survive and threaten on the counter."
            },
            "Attempt a long-range shot": {
                "success": 0.11,
                "xg_change": 0.11,
                "success_text": "A stunning strike flies into the net.",
                "failure_text": "The attempt misses the target."
            },
            "Remain patient": {
                "success": 0.68,
                "xg_change": 0.06,
                "success_text": "Spain patiently create another opening.",
                "failure_text": "The move loses momentum."
            }
        }
    },
    {
        "minute": 88,
        "title": "Argentina create one final major opportunity.",
        "team": "Argentina",
        "choices": {
            "Give the ball to Messi": {
                "success": 0.27,
                "xg_change": 0.26,
                "success_text": "Messi delivers in the final minutes.",
                "failure_text": "Spain block Messi's attempt."
            },
            "Cross immediately": {
                "success": 0.21,
                "xg_change": 0.20,
                "success_text": "Argentina score from the late cross.",
                "failure_text": "The goalkeeper claims the ball."
            },
            "Wait for a clearer chance": {
                "success": 0.64,
                "xg_change": 0.07,
                "success_text": "Argentina create one final opening.",
                "failure_text": "The referee signals the end of the attack."
            }
        }
    }
]


def initialise_playable_final():
    st.session_state.play_final_active = True
    st.session_state.play_final_moment = 0
    st.session_state.play_final_argentina_goals = 0
    st.session_state.play_final_spain_goals = 0
    st.session_state.play_final_argentina_xg = 0.0
    st.session_state.play_final_spain_xg = 0.0
    st.session_state.play_final_history = []
    st.session_state.play_final_finished = False
    st.session_state.play_final_champion = None
    st.session_state.play_final_resolution = None


def calculate_live_probabilities():
    current_index = st.session_state.play_final_moment

    if current_index >= len(PLAYABLE_MOMENTS):
        current_minute = 90
    else:
        current_minute = PLAYABLE_MOMENTS[current_index]["minute"]

    remaining_fraction = max(
        0.02,
        (90 - current_minute) / 90
    )

    remaining_argentina_xg = max(
        0.05,
        argentina_xg * remaining_fraction
    )

    remaining_spain_xg = max(
        0.05,
        spain_xg * remaining_fraction
    )

    argentina_win = 0.0
    draw = 0.0
    spain_win = 0.0

    current_argentina_goals = (
        st.session_state.play_final_argentina_goals
    )

    current_spain_goals = (
        st.session_state.play_final_spain_goals
    )

    for argentina_remaining_goals in range(7):
        for spain_remaining_goals in range(7):

            probability = (
                poisson.pmf(
                    argentina_remaining_goals,
                    remaining_argentina_xg
                )
                * poisson.pmf(
                    spain_remaining_goals,
                    remaining_spain_xg
                )
            )

            final_argentina = (
                current_argentina_goals
                + argentina_remaining_goals
            )

            final_spain = (
                current_spain_goals
                + spain_remaining_goals
            )

            if final_argentina > final_spain:
                argentina_win += probability

            elif final_argentina == final_spain:
                draw += probability

            else:
                spain_win += probability

    total = argentina_win + draw + spain_win

    return (
        argentina_win / total * 100,
        draw / total * 100,
        spain_win / total * 100
    )


def resolve_playable_choice(choice_name):
    moment_index = st.session_state.play_final_moment
    moment = PLAYABLE_MOMENTS[moment_index]
    choice = moment["choices"][choice_name]

    success_probability = choice["success"]

    # Active What-Ifs affect the decision.
    if moment["team"] == "Argentina":

        if messi_status == "Limited fitness":
            success_probability *= 0.92

        elif messi_status == "Unavailable":
            success_probability *= 0.82

        if spain_red_card:
            success_probability *= 1.20

        if argentina_red_card:
            success_probability *= 0.75

    else:

        if yamal_status == "Limited fitness":
            success_probability *= 0.93

        elif yamal_status == "Unavailable":
            success_probability *= 0.84

        if argentina_red_card:
            success_probability *= 1.20

        if spain_red_card:
            success_probability *= 0.75

    success_probability = max(
        0.03,
        min(0.75, success_probability)
    )

    event_succeeds = (
        random.random() < success_probability
    )

    if moment["team"] == "Argentina":
        st.session_state.play_final_argentina_xg += (
            choice["xg_change"]
        )
    else:
        st.session_state.play_final_spain_xg += (
            choice["xg_change"]
        )

    if event_succeeds:

        if moment["team"] == "Argentina":
            st.session_state.play_final_argentina_goals += 1
        else:
            st.session_state.play_final_spain_goals += 1

        outcome_text = choice["success_text"]

    else:
        outcome_text = choice["failure_text"]

    st.session_state.play_final_history.append(
        {
            "minute": moment["minute"],
            "choice": choice_name,
            "outcome": outcome_text,
            "success_probability": success_probability * 100,
            "success": event_succeeds
        }
    )

    st.session_state.play_final_moment += 1

    if (
        st.session_state.play_final_moment
        >= len(PLAYABLE_MOMENTS)
    ):
        finish_playable_final()


def finish_playable_final():
    argentina_goals = (
        st.session_state.play_final_argentina_goals
    )

    spain_goals = (
        st.session_state.play_final_spain_goals
    )

    if argentina_goals > spain_goals:
        champion = "Argentina"
        resolution = "90 minutes"

    elif spain_goals > argentina_goals:
        champion = "Spain"
        resolution = "90 minutes"

    else:
        extra_argentina = int(
            poisson.rvs(
                mu=max(0.05, argentina_xg / 3)
            )
        )

        extra_spain = int(
            poisson.rvs(
                mu=max(0.05, spain_xg / 3)
            )
        )

        argentina_goals += extra_argentina
        spain_goals += extra_spain

        st.session_state.play_final_argentina_goals = (
            argentina_goals
        )

        st.session_state.play_final_spain_goals = (
            spain_goals
        )

        if argentina_goals > spain_goals:
            champion = "Argentina"
            resolution = "extra time"

        elif spain_goals > argentina_goals:
            champion = "Spain"
            resolution = "extra time"

        else:
            argentina_shootout_strength = argentina_rating
            spain_shootout_strength = spain_rating

            if messi_status == "Fully fit":
                argentina_shootout_strength += 3

            elif messi_status == "Unavailable":
                argentina_shootout_strength -= 4

            if yamal_status == "Fully fit":
                spain_shootout_strength += 2

            elif yamal_status == "Unavailable":
                spain_shootout_strength -= 3

            argentina_penalty_probability = (
                argentina_shootout_strength
                / (
                    argentina_shootout_strength
                    + spain_shootout_strength
                )
            )

            if (
                random.random()
                < argentina_penalty_probability
            ):
                champion = "Argentina"
            else:
                champion = "Spain"

            resolution = "penalty shootout"

    st.session_state.play_final_champion = champion
    st.session_state.play_final_resolution = resolution
    st.session_state.play_final_finished = True


# --------------------------------------------------
# PLAYABLE FINAL INTERFACE
# --------------------------------------------------

def get_choice_profile(choice_name):

    choice_name_lower = choice_name.lower()

    if (
        "shoot" in choice_name_lower
        or "attack" in choice_name_lower
    ):
        return {
            "style": "Aggressive",
            "risk": "Higher risk",
            "description": (
                "Attack the goal directly. This could create an "
                "immediate breakthrough, but may end the move."
            )
        }

    if (
        "cross" in choice_name_lower
        or "through ball" in choice_name_lower
        or "pass to" in choice_name_lower
        or "routine" in choice_name_lower
    ):
        return {
            "style": "Creative",
            "risk": "Balanced risk",
            "description": (
                "Attempt to unlock the defence and create a dangerous "
                "chance for a teammate."
            )
        }

    if (
        "possession" in choice_name_lower
        or "patient" in choice_name_lower
        or "slow" in choice_name_lower
        or "wait" in choice_name_lower
        or "recycle" in choice_name_lower
    ):
        return {
            "style": "Patient",
            "risk": "Lower risk",
            "description": (
                "Protect possession, control the tempo and wait for "
                "a clearer opening."
            )
        }

    return {
        "style": "Balanced",
        "risk": "Moderate risk",
        "description": (
            "A balanced tactical decision with both potential rewards "
            "and possible drawbacks."
        )
    }


with play_tab:

    # --------------------------------------------------
    # MAIN LANDING SCREEN
    # --------------------------------------------------

    if not st.session_state.get(
        "play_final_active",
        False
    ):

        st.title("FIFA WORLD CUP FINAL")

        st.markdown(
            """
            # Argentina vs Spain

            ## Predict it. Play it. Rewrite history.
            """
        )

        st.success(
            "This is the main interactive experience. Take control "
            "of the final's biggest moments and determine who becomes "
            "World Champion."
        )

        landing_col1, landing_col2, landing_col3 = st.columns(3)

        with landing_col1:
            st.metric(
                "Major decisions",
                len(PLAYABLE_MOMENTS)
            )

        with landing_col2:
            st.metric(
                "Possible endings",
                "90 / 120 / Pens"
            )

        with landing_col3:
            st.metric(
                "Prediction updates",
                "Live"
            )

        st.write(
            "Every choice changes the match story, expected goals, "
            "score and remaining win probabilities."
        )

        if st.button(
            "ENTER THE WORLD CUP FINAL",
            type="primary",
            use_container_width=True,
            key="enter_playable_final"
        ):
            initialise_playable_final()

            st.session_state.play_final_kicked_off = False

            st.rerun()

    # --------------------------------------------------
    # CINEMATIC INTRO
    # --------------------------------------------------

    elif not st.session_state.get(
        "play_final_kicked_off",
        False
    ):

        st.title("FIFA WORLD CUP FINAL")

        st.divider()

        st.markdown(
            """
            # Argentina 🇦🇷 vs Spain 🇪🇸
            """
        )

        intro_col1, intro_col2, intro_col3 = st.columns(3)

        with intro_col1:
            st.metric(
                "Venue",
                "MetLife Stadium"
            )

        with intro_col2:
            st.metric(
                "Attendance",
                "82,500"
            )

        with intro_col3:
            st.metric(
                "Kick-off",
                "20:00"
            )

        st.divider()

        st.markdown(
            """
            ## The world is watching.

            Ninety minutes separate these teams from football history.

            You will take control during the most important moments of
            the final. Your decisions will affect the score, momentum,
            expected goals and live result probabilities.

            **Your decisions will determine who becomes World Champion.**
            """
        )

        kickoff_col1, kickoff_col2 = st.columns([3, 1])

        with kickoff_col1:

            if st.button(
                "KICK OFF",
                type="primary",
                use_container_width=True,
                key="kickoff_playable_final"
            ):
                st.session_state.play_final_kicked_off = True

                st.rerun()

        with kickoff_col2:

            if st.button(
                "Return",
                use_container_width=True,
                key="leave_playable_intro"
            ):
                st.session_state.play_final_active = False
                st.session_state.play_final_kicked_off = False

                st.rerun()

    # --------------------------------------------------
    # LIVE PLAYABLE MATCH
    # --------------------------------------------------

    else:

        argentina_live, draw_live, spain_live = (
            calculate_live_probabilities()
        )

        current_index = (
            st.session_state.play_final_moment
        )

        if current_index < len(PLAYABLE_MOMENTS):
            displayed_minute = (
                PLAYABLE_MOMENTS[current_index]["minute"]
            )
        else:
            displayed_minute = 90

        st.title("Live World Cup Final")

        score_col1, score_col2, score_col3 = st.columns(
            [2, 1, 2]
        )

        with score_col1:
            st.metric(
                "Argentina",
                st.session_state.play_final_argentina_goals
            )

        with score_col2:
            st.metric(
                "Match clock",
                f"{displayed_minute}'"
            )

        with score_col3:
            st.metric(
                "Spain",
                st.session_state.play_final_spain_goals
            )

        st.progress(
            min(
                1.0,
                displayed_minute / 90
            )
        )

        st.subheader("Live result probabilities")

        probability_col1, probability_col2, probability_col3 = (
            st.columns(3)
        )

        with probability_col1:
            st.metric(
                "Argentina win",
                f"{argentina_live:.1f}%"
            )

        with probability_col2:
            st.metric(
                "Level after 90",
                f"{draw_live:.1f}%"
            )

        with probability_col3:
            st.metric(
                "Spain win",
                f"{spain_live:.1f}%"
            )

        st.caption(
            "These probabilities recalculate after every decision "
            "using the current score, remaining time and expected goals."
        )

        # --------------------------------------------------
        # ACTIVE DECISION
        # --------------------------------------------------

        if not st.session_state.play_final_finished:

            moment = PLAYABLE_MOMENTS[
                st.session_state.play_final_moment
            ]

            if moment["team"] == "Argentina":
                situation_title = "Argentina Attack"
            else:
                situation_title = "Spain Attack"

            st.divider()

            with st.container(border=True):

                st.header(
                    f"{moment['minute']}' — {situation_title}"
                )

                st.subheader(
                    moment["title"]
                )

                st.markdown(
                    f"""
                    You now control **{moment['team']}**.

                    ## What would you do?

                    Every option has strengths and risks. There is not
                    always one correct decision.
                    """
                )

                choice_names = list(
                    moment["choices"].keys()
                )

                choice_columns = st.columns(
                    len(choice_names)
                )

                for index, choice_name in enumerate(
                    choice_names
                ):

                    with choice_columns[index]:

                        profile = get_choice_profile(
                            choice_name
                        )

                        with st.container(border=True):

                            st.subheader(choice_name)

                            st.write(
                                f"**Approach:** "
                                f"{profile['style']}"
                            )

                            st.write(
                                f"**Risk profile:** "
                                f"{profile['risk']}"
                            )

                            st.caption(
                                profile["description"]
                            )

                            if st.button(
                                "Choose this action",
                                use_container_width=True,
                                key=(
                                    f"play_choice_"
                                    f"{st.session_state.play_final_moment}_"
                                    f"{index}"
                                )
                            ):
                                resolve_playable_choice(
                                    choice_name
                                )

                                st.rerun()

        # --------------------------------------------------
        # FULL-TIME RESULT
        # --------------------------------------------------

        else:

            st.divider()

            st.header("FULL TIME")

            final_argentina = (
                st.session_state.play_final_argentina_goals
            )

            final_spain = (
                st.session_state.play_final_spain_goals
            )

            with st.container(border=True):

                st.markdown(
                    f"""
                    # Argentina {final_argentina}–{final_spain} Spain
                    """
                )

                st.success(
                    f"{st.session_state.play_final_champion} "
                    f"are World Champions."
                )

                st.write(
                    "Match decided by: "
                    f"**{st.session_state.play_final_resolution.title()}**"
                )

            st.balloons()

            if st.button(
                "PLAY ANOTHER FINAL",
                type="primary",
                use_container_width=True,
                key="play_another_final"
            ):
                initialise_playable_final()

                st.session_state.play_final_kicked_off = False

                st.rerun()

        # --------------------------------------------------
        # MATCH STORY
        # --------------------------------------------------

        if st.session_state.play_final_history:

            st.divider()

            st.subheader("Your match story")

            for event in (
                reversed(
                    st.session_state.play_final_history
                )
            ):

                if event["success"]:
                    result_label = "SUCCESS"
                else:
                    result_label = "UNSUCCESSFUL"

                with st.container(border=True):

                    st.write(
                        f"**{event['minute']}' — "
                        f"{event['choice']}**"
                    )

                    st.write(
                        f"**{result_label}:** "
                        f"{event['outcome']}"
                    )

                    st.caption(
                        "Calculated probability of producing the "
                        "successful outcome: "
                        f"{event['success_probability']:.1f}%"
                    )

        st.divider()

        if st.button(
            "Restart from the pre-match presentation",
            use_container_width=True,
            key="restart_from_intro"
        ):
            initialise_playable_final()

            st.session_state.play_final_kicked_off = False

            st.rerun()