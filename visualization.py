import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np
import plotly.graph_objects as go

# Set default template to white (clean background)
pio.templates.default = "plotly_white"


# ------------------------
# Helper function to remove grids but keep axes
# ------------------------
def clean_fig(fig):
    fig.update_layout(
        xaxis=dict(showgrid=False, showline=True, linecolor='black'),
        yaxis=dict(showgrid=False, showline=True, linecolor='black')
    )
    return fig

# =============================
# 1. LINE CHART — Crop Yield Trend
# =============================
def line_chart(df):
    yield_trend = df.groupby('Year')['Crop_Yield_Mt_Per_Ha'].mean().reset_index()
    fig = px.line(
        yield_trend,
        x='Year',
        y='Crop_Yield_Mt_Per_Ha',
        title="Crop Yield Trend Over Time",
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['#1f77b4']
    )
    return clean_fig(fig)

# # 2. BAR CHART — Average Crop Yield by Crop Type
# Compute average yield by crop
def bar_chart(df):
    crop_data = df.groupby('Crop_Type')['Crop_Yield_Mt_Per_Ha'].mean().reset_index()
    crop_data = crop_data.sort_values(by='Crop_Yield_Mt_Per_Ha', ascending=False)
    top3 = crop_data['Crop_Type'].iloc[:3].tolist()

    def assign_color(crop):
        if crop == top3[0]:
            return '#1f77b4'
        elif crop == top3[1]:
            return '#ff7f0e'
        elif crop == top3[2]:
            return '#9467bd'
        else:
            return '#7f7f7f'

    crop_data['Color'] = crop_data['Crop_Type'].apply(assign_color)

    fig = px.bar(
        crop_data,
        x='Crop_Yield_Mt_Per_Ha',   
        y='Crop_Type',              
        color='Color',
        text='Crop_Yield_Mt_Per_Ha',
        orientation='h',            
        color_discrete_map={c: c for c in crop_data['Color'].unique()},
        title="Average Crop Yield by Crop Type (Top 3 Highlighted)"
    )

    fig.update_layout(
        xaxis_title="Crop Yield (Mt per Ha)",
        yaxis_title="Crop Type"
    )

    return clean_fig(fig)

# =============================
# 3. SCATTER PLOT — Temp vs Yield by Crop Type
# =============================

# Identify top 3 crops by average yield
def scatter_chart(df):
    crop_avg = df.groupby('Crop_Type')['Crop_Yield_Mt_Per_Ha'].mean().sort_values(ascending=False)
    top3 = crop_avg.index[:3].tolist()

    def assign_color(crop):
        if crop == top3[0]:
            return '#1f77b4'
        elif crop == top3[1]:
            return '#ff7f0e'
        elif crop == top3[2]:
            return '#9467bd'
        else:
            return '#7f7f7f'

    df['Color'] = df['Crop_Type'].apply(assign_color)

    fig = px.scatter(
        df,
        x='Average_Temperature_C',
        y='Crop_Yield_Mt_Per_Ha',
        color='Color',
        size='Economic_Impact_Million_Usd',
        hover_data={
            'Crop_Yield_Mt_Per_Ha': ':.2f',
            'Average_Temperature_C': ':.2f',
            'Crop_Type': True
        },
        color_discrete_map={c: c for c in df['Color'].unique()},
        title="Effect of Temperature on Crop Yield (Top 3 Crops Highlighted)"
    )
    return clean_fig(fig)

# =============================
# 4. BOX PLOT — Yield Distribution by Region
# =============================
# Identify top 3 regions by median yield
def box_plot(df):
    top_regions = df.groupby('Region')['Crop_Yield_Mt_Per_Ha'].median().nlargest(3).index.tolist()

    def region_color(region):
        if region == top_regions[0]:
            return '#1f77b4'
        elif region == top_regions[1]:
            return '#17becf'
        elif region == top_regions[2]:
            return '#ff7f0e'
        else:
            return '#0d3d66'

    df['Region_Color'] = df['Region'].apply(region_color)

    fig = px.box(
        df,
        x='Region',
        y='Crop_Yield_Mt_Per_Ha',
        color='Region_Color',
        color_discrete_map={c: c for c in df['Region_Color'].unique()},
        title="Distribution of Crop Yield by Region (Top 3 Highlighted)"
    )
    return clean_fig(fig)

# =============================
# 5. HISTOGRAM — Rainfall Distribution
# =============================
def histogram(df):
    fig = px.histogram(
        df,
        x='Crop_Yield_Mt_Per_Ha',
        nbins=25,
        marginal="box",   # 🔥 adds boxplot on top
        title="Distribution of Crop Yield with Density Insight",
        color_discrete_sequence=['#1f77b4'],
        opacity=0.8
    )

    fig.update_layout(
        xaxis_title="Crop Yield (Mt per Ha)",
        yaxis_title="Frequency",
        bargap=0.05
    )

    return clean_fig(fig)

# =============================
# 6. HEATMAP — Correlation Between Key Variables
# =============================
def heatmap(df):
    corr_df = df[['Average_Temperature_C','Total_Precipitation_Mm','Co2_Emissions_Mt',
                   'Crop_Yield_Mt_Per_Ha','Economic_Impact_Million_Usd']].corr()
    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale='RdBu',
        zmin=-1, zmax=1,
        title="Correlation Between Key Variables"
    )
    return clean_fig(fig)

# =============================
# MAIN BLOCK — run standalone
# =============================
if __name__ == "__main__":
    print("This file is running directly!")
    df = pd.read_csv("cleaned_data.csv")
    line_chart(df).show()
    bar_chart(df).show()
    scatter_chart(df).show()
    box_plot(df).show()
    histogram(df).show()
    heatmap(df).show()
