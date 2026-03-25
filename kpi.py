# kpi.py
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output

# -----------------------------
# Helper function: create KPI figure
# -----------------------------
def create_kpi_figure(value, title=None, number_format=None):
    return go.Figure(go.Indicator(
        mode="number",
        value=value,
        number={'valueformat': number_format} if number_format else {},
        title={'text': title} if title else None
    ))

# -----------------------------
# Dash callback registration
# -----------------------------
def register_callbacks(app, df):

    @app.callback(
        Output('kpi-avg-yield', 'figure'),
        Output('kpi-max-stress', 'figure'),
        Output('kpi-avg-irrigation', 'figure'),
        Output('kpi-total-economic', 'figure'),
        Input('country-filter', 'value'),
        Input('year-filter', 'value'),
        Input('region-filter', 'value'),
        Input('crop-filter', 'value')
    )
    def update_kpis(country, year, region, crop):
        dff = df.copy()

        if country:
            dff = dff[dff['Country'].isin(country)]
        if year:
            dff = dff[dff['Year'].isin(year)]
        if region:
            dff = dff[dff['Region'].isin(region)]
        if crop:
            dff = dff[dff['Crop_Type'].isin(crop)]

        return (
            create_kpi_figure(dff["Crop_Yield_Mt_Per_Ha"].mean(), "Avg Crop Yield (Mt/Ha)", ".2f"),
            create_kpi_figure(dff["Climate_Stress_Index"].max(), "Max Climate Stress", ".2f"),
            create_kpi_figure(dff["Irrigation_Access_%"].mean(), "Avg Irrigation Access (%)", ".2f"),
            create_kpi_figure(dff["Economic_Impact_Million_Usd"].sum(), "Total Economic Impact (M$)", ".2f")
        )

# -----------------------------
# Standalone testing
# -----------------------------
if __name__ == "__main__":
    df = pd.read_csv("cleaned_data.csv")
    print("Testing KPIs standalone...")

    fig1 = create_kpi_figure(df["Crop_Yield_Mt_Per_Ha"].mean(), "Avg Crop Yield (Mt/Ha)", ".2f")
    fig2 = create_kpi_figure(df["Climate_Stress_Index"].max(), "Max Climate Stress", ".2f")
    fig3 = create_kpi_figure(df["Irrigation_Access_%"].mean(), "Avg Irrigation Access (%)", ".2f")
    fig4 = create_kpi_figure(df["Economic_Impact_Million_Usd"].sum(), "Total Economic Impact (M$)", ".2f")

    fig1.show()
    fig2.show()
    fig3.show()
    fig4.show()