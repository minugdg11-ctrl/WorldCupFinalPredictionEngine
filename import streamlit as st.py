import streamlit as st

st.set_page_config(
    page_title="World Cup Prediction Engine",
    page_icon="⚽",
    layout="wide"
)


import streamlit as st

st.set_page_config(
    page_title="World Cup Prediction Engine",
    page_icon="⚽",
    layout="wide"
)

# ⬇️ PASTE THE TEAM_DATA HERE

TEAM_DATA = {
    ...
}


def calculate_team_rating(team):

    data = TEAM_DATA[team]

    rating = (
        data["elo"] * 0.20 +
        data["recent_form"] * 0.15 +
        data["attack"] * 0.15 +
        data["defence"] * 0.15 +
        data["squad_quality"] * 0.10 +
        data["tournament_form"] * 0.10 +
        data["manager"] * 0.05 +
        data["experience"] * 0.05 +
        data["injuries"] * 0.03 +
        data["neutral_advantage"] * 0.02
    )

    return round(rating, 2)
st.title("⚽ World Cup Prediction Engine")

st.subheader("Version 0.1")

st.write("Welcome! This software will predict the 2026 FIFA World Cup Final.")


argentina_rating = calculate_team_rating("Argentina")
spain_rating = calculate_team_rating("Spain")
st.write("### Team Ratings")

st.write(f"🇦🇷 Argentina: {argentina_rating}")

st.write(f"🇪🇸 Spain: {spain_rating}")