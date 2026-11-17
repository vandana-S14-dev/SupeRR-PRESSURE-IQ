import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="PRESSURE IQ | SupeRR Selector",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent
bat = pd.read_csv(BASE / "top_10_batters.csv")
bowl = pd.read_csv(BASE / "top_10_bowlers.csv")
bat_audit = pd.read_csv(BASE / "batting_candidate_audit.csv")
bowl_audit = pd.read_csv(BASE / "bowling_candidate_audit.csv")

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.7rem; padding-bottom: 2rem; max-width: 1450px;}
.hero {
  padding: 1.4rem 1.6rem; border-radius: 18px;
  background: linear-gradient(115deg, #101b35 0%, #1d3760 55%, #315a76 100%);
  color: white; margin-bottom: 1.1rem;
}
.hero h1 {font-size: 2.25rem; margin: 0; letter-spacing: .06em;}
.hero p {color: #d7e4f4; margin: .35rem 0 0 0; font-size: 1rem;}
.kicker {text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; color: #9fc5e9;}
.small-note {font-size: .83rem; color: #8b96a8;}
div[data-testid="stMetric"] {
  background: rgba(120,140,170,.08); padding: 14px 16px;
  border: 1px solid rgba(120,140,170,.18); border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="kicker">SupeRR Selector · Season 2</div>
  <h1>🏏 PRESSURE IQ</h1>
  <p>Measuring who performs when the match situation gets difficult.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Match intelligence")
    st.caption("IPL + T20I · 2022 onward")
    section = st.radio(
        "Explore dashboard",
        ["Executive overview", "Batting leaderboard", "Bowling leaderboard", "Player Comparison", "Candidate audit", "Methodology & caveats"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Candidate pool: 20 players supplied in the Unstop dropdowns.")
    st.caption("Scores are relative to this candidate pool, not universal player ratings.")

# Summary metrics
eligible_bat = int(bat_audit.get("eligible_top10", pd.Series(dtype=bool)).fillna(False).sum())
bowling_with_data = int((bowl_audit["pressure_legal_balls"] > 0).sum())
if section == "Executive overview":
    st.subheader("Executive overview")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Batting candidates", len(bat_audit))
    m2.metric("Bowling candidates with pressure balls", bowling_with_data)
    m3.metric("Batting leaderboard", len(bat))
    m4.metric("Bowling leaderboard", len(bowl))
    st.info(
        "This dashboard compares the dropdown-eligible players using pressure-state statistics. "
        "Read confidence and sample-size columns alongside every rank."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Leading batting performers")
        fig = px.bar(
            bat.sort_values("rank", ascending=True),
            x="pressure_iq", y="player", orientation="h",
            color="confidence", hover_data=["pressure_balls", "matches", "sr"],
            labels={"pressure_iq":"Pressure IQ (relative)", "player":"", "confidence":"Evidence"},
        )
        fig.update_layout(height=430, yaxis={"categoryorder":"total ascending"}, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### Leading bowling performers")
        fig = px.bar(
            bowl.sort_values("rank", ascending=True),
            x="pressure_iq", y="player", orientation="h",
            color="confidence", hover_data=["pressure_legal_balls", "matches", "econ"],
            labels={"pressure_iq":"Pressure IQ (relative)", "player":"", "confidence":"Evidence"},
        )
        fig.update_layout(height=430, yaxis={"categoryorder":"total ascending"}, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### How to read the score")
    st.write(
        "A higher Pressure IQ indicates a stronger composite performance within this 20-player candidate pool. "
        "It should not be interpreted as a probability of winning or as a career-wide player rating."
    )

elif section == "Batting leaderboard":
    st.subheader("Batting pressure leaderboard")
    st.caption("Rankings are candidate-pool-relative. Use pressure balls and matches to judge evidence strength.")
    min_balls = st.slider("Minimum pressure balls to display", 0, int(max(60, bat["pressure_balls"].max())), 0, 10)
    view = bat[bat["pressure_balls"] >= min_balls].sort_values("rank")
    st.dataframe(
        view[["rank","player","pressure_iq","pressure_balls","matches","pressure_runs","sr","boundary_rate","dismissal_rate","confidence"]],
        use_container_width=True, hide_index=True,
        column_config={
            "pressure_iq": st.column_config.NumberColumn("Pressure IQ", format="%.3f"),
            "sr": st.column_config.NumberColumn("Pressure strike rate", format="%.1f"),
            "boundary_rate": st.column_config.NumberColumn("Boundary-ball %", format="%.1f"),
            "dismissal_rate": st.column_config.NumberColumn("Dismissal rate", format="%.1f"),
        }
    )
    fig = px.scatter(
        view, x="pressure_balls", y="sr", size="pressure_runs", color="confidence",
        hover_name="player", text="rank",
        labels={"pressure_balls":"Pressure balls faced","sr":"Pressure strike rate","confidence":"Evidence"},
        size_max=42,
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)
    st.download_button("Download batting leaderboard CSV", view.to_csv(index=False), "pressure_iq_batters.csv", "text/csv")

elif section == "Bowling leaderboard":
    st.subheader("Bowling pressure leaderboard")
    st.caption("Low-sample bowlers are shown for completeness; their ranks are highly uncertain.")
    st.warning(
        f"{len(bowl)} candidates have pressure bowling records in the dataset. "
        "Some have very small samples; do not treat a low-sample rank as strong evidence."
    )
    min_balls = st.slider("Minimum pressure legal balls to display", 0, int(max(100, bowl["pressure_legal_balls"].max())), 0, 10)
    view = bowl[bowl["pressure_legal_balls"] >= min_balls].sort_values("rank")
    st.dataframe(
        view[["rank","player","pressure_iq","pressure_legal_balls","matches","conceded","wickets","econ","wickets_per6","dot_rate","confidence"]],
        use_container_width=True, hide_index=True,
        column_config={
            "pressure_iq": st.column_config.NumberColumn("Pressure IQ", format="%.3f"),
            "econ": st.column_config.NumberColumn("Pressure economy", format="%.2f"),
            "wickets_per6": st.column_config.NumberColumn("Wickets / 6 balls", format="%.2f"),
            "dot_rate": st.column_config.NumberColumn("Dot-ball %", format="%.1f"),
        }
    )
    fig = px.scatter(
        view, x="pressure_legal_balls", y="econ", size="wickets", color="confidence",
        hover_name="player", text="rank",
        labels={"pressure_legal_balls":"Pressure legal balls","econ":"Pressure economy rate","confidence":"Evidence"},
        size_max=42,
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=480, yaxis_autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.download_button("Download bowling leaderboard CSV", view.to_csv(index=False), "pressure_iq_bowlers.csv", "text/csv")

elif section == "Player Comparison":
    st.subheader("Player Performance Comparison")

    role = st.radio(
        "Select comparison type",
        ["Batting", "Bowling"],
        horizontal=True
    )

    player_df = bat if role == "Batting" else bowl

    col1, col2 = st.columns(2)

    with col1:
        player1 = st.selectbox(
            "Select Player 1",
            player_df["player"].tolist(),
            key="compare_player1"
        )

    with col2:
        player2 = st.selectbox(
            "Select Player 2",
            player_df["player"].tolist(),
            index=min(1, len(player_df) - 1),
            key="compare_player2"
        )

    if player1 == player2:
        st.warning("Please select two different players.")
    else:
        p1 = player_df[player_df["player"] == player1].iloc[0]
        p2 = player_df[player_df["player"] == player2].iloc[0]

        if role == "Batting":
            metrics = {
                "Pressure IQ": "pressure_iq",
                "Strike Rate": "sr",
                "Boundary Rate": "boundary_rate",
                "Reliability": "reliability"
            }
        else:
            metrics = {
                "Pressure IQ": "pressure_iq",
                "Economy Rate": "econ",
                "Wickets per 6 balls": "wickets_per6",
                "Reliability": "reliability"
            }

        comparison = pd.DataFrame({
            "Metric": metrics.keys(),
            player1: [p1[m] for m in metrics.values()],
            player2: [p2[m] for m in metrics.values()]
        })

        st.markdown("### Side-by-side comparison")
        st.dataframe(comparison, use_container_width=True, hide_index=True)

        
        # Normalize metrics against the full candidate pool (0–100)
        radar_columns = list(metrics.values())
        radar_labels = list(metrics.keys())

        ref_min = player_df[radar_columns].min()
        ref_max = player_df[radar_columns].max()
        ranges = (ref_max - ref_min).replace(0, 1)

        def normalize_player(row):
            values = ((row[radar_columns] - ref_min) / ranges) * 100

            # Lower economy rate is better, so reverse its score
            if role == "Bowling":
                values["econ"] = 100 - values["econ"]

            result = values.tolist()
            return result + [result[0]]

        radar_labels_closed = radar_labels + [radar_labels[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=normalize_player(p1),
            theta=radar_labels_closed,
            fill="toself",
            name=player1
        ))

        fig.add_trace(go.Scatterpolar(
            r=normalize_player(p2),
            theta=radar_labels_closed,
            fill="toself",
            name=player2
        ))

        fig.update_layout(
            title="Normalized Player Performance Comparison",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[0, 20, 40, 60, 80, 100]
                )
            ),
            showlegend=True,
            height=550
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------- Automatic Player Insights ----------
        st.markdown("### Player Insights")

        if p1["pressure_iq"] > p2["pressure_iq"]:
            better_player = player1
        elif p2["pressure_iq"] > p1["pressure_iq"]:
            better_player = player2
        else:
            better_player = "Both players are equal"

        st.info(f"Pressure IQ leader: {better_player}")

        st.markdown("#### Metric-by-metric analysis")

        for label, metric in metrics.items():
            value1 = float(p1[metric])
            value2 = float(p2[metric])

            if value1 == value2:
                st.write(f"**{label}:** Both players are equal.")
            elif role == "Bowling" and metric == "econ":
                winner = player1 if value1 < value2 else player2
                st.write(f"**{label}:** {winner} has the better economy.")
            else:
                winner = player1 if value1 > value2 else player2
                st.write(f"**{label}:** {winner} performs better.")

        st.caption(
            "All metrics are normalized against the full candidate pool. "
            "For bowling, lower economy receives a higher normalized score."
        )


elif section == "Candidate audit":
    st.subheader("Full dropdown candidate audit")
    role = st.radio("Candidate role", ["Batting", "Bowling"], horizontal=True)
    if role == "Batting":
        cols = [c for c in ["player","pressure_balls","matches","pressure_runs","sr","boundary_rate","dismissal_rate","reliability","pressure_iq","confidence","eligible_top10"] if c in bat_audit]
        st.dataframe(bat_audit[cols], use_container_width=True, hide_index=True)
        st.download_button("Download all batting candidates", bat_audit.to_csv(index=False), "batting_candidate_audit.csv", "text/csv")
    else:
        cols = [c for c in ["player","pressure_legal_balls","matches","conceded","wickets","econ","wickets_per6","dot_rate","reliability","pressure_iq","confidence","ranked"] if c in bowl_audit]
        st.dataframe(bowl_audit[cols], use_container_width=True, hide_index=True)
        st.download_button("Download all bowling candidates", bowl_audit.to_csv(index=False), "bowling_candidate_audit.csv", "text/csv")

else:
    st.subheader("Methodology & caveats")
    st.markdown("""
**Dataset scope**
- IPL seasons 2022–2026 and T20I competitions from 2022 onward.
- Super Overs are excluded from normal innings analysis.
- Sixteen selected matches have no ball-by-ball records and therefore cannot contribute to player-level calculations.

**Pressure concept**
- Pressure is represented through difficult match states, including late-innings situations and high required-run-rate chase states.
- Batting and bowling are evaluated separately because their performance outcomes differ.

**Score interpretation**
- Pressure IQ is a descriptive composite, adjusted for evidence volume and standardised within the supplied dropdown candidate pool.
- It is not a trained machine-learning model, a causal estimate, or a prediction of future performance.

**Reliability**
- Pressure balls and match counts are displayed beside every rank.
- Low sample sizes can produce unstable estimates. Treat low-confidence positions as provisional.

**Data limitations**
- Dataset coverage, role definitions, revised targets, extras and missing match records can affect calculations.
- Rankings are only as representative as the available ball-by-ball sample.
""")
    st.info("For a competition submission, retain the accompanying PDF methodology and be prepared to explain the pressure-state definition, scoring weights and limitations.")

st.divider()
st.caption("PRESSURE IQ · SupeRR Selector Season 2 · Analytical prototype")

