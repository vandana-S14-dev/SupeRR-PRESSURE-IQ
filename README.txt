# PRESSURE IQ — SupeRR Selector Season 2

## Included
- `top_10_batters.csv` — dropdown-constrained batting ranking
- `top_10_bowlers.csv` — dropdown-constrained bowling ranking
- `batting_candidate_audit.csv` / `bowling_candidate_audit.csv` — all 20 candidates and evidence
- `PRESSURE_IQ_Methodology_and_Rankings.pdf` — methodology, rankings, reliability and limitations
- `app.py` — Streamlit dashboard

## Run the dashboard
1. Extract this ZIP.
2. Open a terminal in this folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## Important interpretation
These rankings are relative to the exact 20 names supplied from the Unstop dropdowns. The batting top 10 requires at least 60 pressure balls across 5 matches. Bowling lists the 10 dropdown candidates with any pressure-overs bowling record; several have low confidence. Do not hide the confidence column or describe low-sample bowling ranks as conclusive.

## Pressure definition
- Chase: at most 90 legal balls remain and required run rate is >=9.0, OR >=7.5 with at least four wickets already lost.
- First innings: at most 30 legal balls remain and at least four wickets have fallen, OR at most 12 legal balls remain.
- Super Overs excluded.
- Chases use first-innings total + 1 as target. Revised target fields are not applied because the dataset's target convention was not independently verified.

This is a transparent descriptive scoring model, not a trained ML model. See the PDF for formulas and limitations.
