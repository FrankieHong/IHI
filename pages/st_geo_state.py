import streamlit as st
import pandas as pd
import plotly.express as px
from geo_data_retrieval import fetch_data, process_data, calculate_pct_diff, get_us_state_geojson

def load_geo_data():
    raw_df = fetch_data()
    processed_data = process_data(raw_df)
    return processed_data

st.title("Medicare Geographic Variation Dashboard")
st.markdown("""
This dashboard displays Medicare data for the years 2017-2021.
The data includes per capita costs for various healthcare categories and additional beneficiary information.
The data is sourced from the Centers for Medicare & Medicaid Services (CMS).
""")
dashboard_df = load_geo_data()
st.write("Preview of the dataset:")
st.dataframe(dashboard_df.head())

state_df = calculate_pct_diff(dashboard_df)

us_state_url = "https://raw.githubusercontent.com/FrankieHong/IHI/main/data/us_states.geojson"
us_state_geojson = get_us_state_geojson(us_state_url)

selected_year = st.sidebar.selectbox("Select Year", state_df['year'].unique())
per_capita_costs = [col for col in state_df.columns if 'per_capita' in col and '_national' not in col]
selected_cost = st.sidebar.selectbox("Select Cost Metric", per_capita_costs)

yearly_state_data = state_df[(state_df['year'] == selected_year) & (state_df['geo_level'] == 'State')]

# Choropleth map for the selected year and cost metric
fig = px.choropleth(
    yearly_state_data,
    geojson=us_state_geojson,
    locations='geo_desc',
    featureidkey='properties.STUSPS',
    color=selected_cost,
    scope='usa',
    hover_data={
        'geo_desc': True,
        selected_cost: ':.2f',
        f'{selected_cost}_pct_diff_to_national': ':.2%'
    },
    hover_name='geo_desc',
    title=f"{selected_cost} cost by State in {selected_year}",
    color_continuous_scale=px.colors.sequential.Sunset
)

fig.update_layout(width=800, height=600,
                  legend_title_text='Cost per Capita ($)',
                  legend=dict(
                      orientation='h',
                      yanchor='bottom',
                      y=-0.5,
                      xanchor='center',
                      x=0.5
                  )
                )
st.plotly_chart(fig)

def create_cost_breakdown_chart(state_df,selected_year,selected_state):
    year_df = state_df[state_df['year'] == selected_year]
    national_data = year_df[year_df['geo_level'] == 'National'].iloc[0]
    state_data = year_df[year_df['geo_desc'] == selected_state].iloc[0]

    chart_df = pd.DataFrame({
        'Cost':['Total','Inpatient','Ambulance','Post Acute Care','Durable Medical Equipment','Part B Drugs','Physician OPD','Hospice'],
        'State':[
            state_data['total_costs_per_capita'],
            state_data['inpatient_per_capita'],
            state_data['ambulance_per_capita'],
            state_data['post_acute_care_per_capita'],
            state_data['durable_medical_equipment_per_capita'],
            state_data['part_b_drug_per_capita'],
            state_data['physician_opd_per_capita'],
            state_data['hospice_per_capita']
        ],
        'Nation':[
            national_data['total_costs_per_capita'],
            national_data['inpatient_per_capita'],
            national_data['ambulance_per_capita'],
            national_data['post_acute_care_per_capita'],
            national_data['durable_medical_equipment_per_capita'],
            national_data['part_b_drug_per_capita'],
            national_data['physician_opd_per_capita'],
            national_data['hospice_per_capita']
        ],
        '% Diff to Nation':[
            state_data['total_costs_per_capita_pct_diff_to_national'],
            state_data['inpatient_per_capita_pct_diff_to_national'],
            state_data['ambulance_per_capita_pct_diff_to_national'],
            state_data['post_acute_care_per_capita_pct_diff_to_national'],
            state_data['durable_medical_equipment_per_capita_pct_diff_to_national'],
            state_data['part_b_drug_per_capita_pct_diff_to_national'],
            state_data['physician_opd_per_capita_pct_diff_to_national'],
            state_data['hospice_per_capita_pct_diff_to_national']
        ]
    })
    return chart_df

states = state_df[state_df['geo_level'] == 'State']['geo_desc'].unique()
selected_state = st.selectbox("Select State", sorted(states))

comparison_table = create_cost_breakdown_chart(state_df,selected_year,selected_state)
st.table(comparison_table)

