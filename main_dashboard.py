# dashboard_interactive_clean.py

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ------------------------
# Helper function to clean figures (remove grids)
# ------------------------
def clean_fig(fig, y2=False):
    layout_updates = dict(
        xaxis=dict(showgrid=False, showline=True, linecolor='black'),
        yaxis=dict(showgrid=False, showline=True, linecolor='black')
    )
    if y2:
        layout_updates['yaxis2'] = dict(showgrid=False, showline=True, linecolor='black', overlaying='y', side='right')
    fig.update_layout(**layout_updates)
    return fig

# =========================
# 1. LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    df['Year'] = df['Year'].astype(int)
    return df

df = load_data()

# =========================
# 2. DASHBOARD LAYOUT
# =========================
st.set_page_config(page_title="Climate Agriculture Dashboard", layout="wide")
st.title("🌱 Climate Change Impact on Agriculture Dashboard")

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")
selected_countries = st.sidebar.multiselect(
    "Country", options=sorted(df['Country'].unique()), default=[]
)
selected_regions = st.sidebar.multiselect(
    "Region", options=sorted(df['Region'].unique()), default=[]
)
selected_crops = st.sidebar.multiselect(
    "Crop Type", options=sorted(df['Crop_Type'].unique()), default=[]
)
selected_years = st.sidebar.slider(
    "Year Range", int(df['Year'].min()), int(df['Year'].max()),
    (int(df['Year'].min()), int(df['Year'].max()))
)

# Apply filters
filtered_df = df[
    (df['Country'].isin(selected_countries) if selected_countries else True) &
    (df['Region'].isin(selected_regions) if selected_regions else True) &
    (df['Crop_Type'].isin(selected_crops) if selected_crops else True) &
    (df['Year'].between(selected_years[0], selected_years[1]))
]

# =========================
# 3. KPI SECTION
# =========================
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Avg Crop Yield (Mt/Ha)",
    f"{filtered_df['Crop_Yield_Mt_Per_Ha'].mean():.2f}" if not filtered_df.empty else "N/A"
)
col2.metric(
    "Max Climate Stress",
    f"{filtered_df['Climate_Stress_Index'].max():.2f}" if not filtered_df.empty else "N/A"
)
col3.metric(
    "Avg Irrigation Access (%)",
    f"{filtered_df['Irrigation_Access_%'].mean():.2f}" if not filtered_df.empty else "N/A"
)
col4.metric(
    "Total Economic Impact (M$)",
    f"{filtered_df['Economic_Impact_Million_Usd'].sum():,.0f}" if not filtered_df.empty else "N/A"
)

# =========================
# 4. BASIC VISUALIZATIONS
# =========================

# 4.1 Line Chart: Crop Yield Trend
yield_trend = filtered_df.groupby('Year')['Crop_Yield_Mt_Per_Ha'].mean().reset_index()
fig_line = clean_fig(px.line(
    yield_trend, x='Year', y='Crop_Yield_Mt_Per_Ha',
    title="Crop Yield Trend Over Time", markers=True
))

# 4.2 Horizontal Bar Chart — Top 3 Highlighted
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
        yaxis_title="Crop Type",
        yaxis=dict(autorange="reversed")  # top crop on top
    )

    return clean_fig(fig)

fig_bar = bar_chart(filtered_df)

# 4.3 Scatter Plot: Temperature vs Yield
fig_scatter = clean_fig(px.scatter(
    filtered_df, x='Average_Temperature_C', y='Crop_Yield_Mt_Per_Ha',
    color='Crop_Type', size='Economic_Impact_Million_Usd',
    hover_data=['Region','Crop_Type'], title="Temperature vs Crop Yield"
))

# 4.4 Box Plot: Yield Distribution by Region
top_regions = filtered_df.groupby('Region')['Crop_Yield_Mt_Per_Ha'].median().nlargest(3).index.tolist()
filtered_df['Region_Color'] = filtered_df['Region'].apply(
    lambda r: '#1f77b4' if r==top_regions[0] else '#17becf' if r==top_regions[1] else '#ff7f0e' if r==top_regions[2] else '#0d3d66'
)
fig_box = clean_fig(px.box(
    filtered_df, x='Region', y='Crop_Yield_Mt_Per_Ha', color='Region_Color',
    color_discrete_map={c:c for c in filtered_df['Region_Color'].unique()},
    title="Distribution of Crop Yield by Region (Top 3 Highlighted)"
))

# 4.5 Histogram: Crop Yield Distribution with Box
def histogram(df):
    fig = px.histogram(
        df,
        x='Crop_Yield_Mt_Per_Ha',
        nbins=25,
        marginal="box",
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

fig_hist = histogram(filtered_df)

# 4.6 Heatmap: Correlation
corr_df = filtered_df[['Average_Temperature_C','Total_Precipitation_Mm','Co2_Emissions_Mt',
                       'Crop_Yield_Mt_Per_Ha','Economic_Impact_Million_Usd']].corr()
fig_heatmap = clean_fig(px.imshow(
    corr_df, text_auto=".2f", color_continuous_scale='RdBu', zmin=-1, zmax=1,
    title="Correlation Between Key Variables"
))

# ------------------------
# Display charts in 2 columns
# ------------------------
col1, col2 = st.columns(2)
col1.plotly_chart(fig_line, use_container_width=True)
col2.plotly_chart(fig_bar, use_container_width=True)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_scatter, use_container_width=True)
col2.plotly_chart(fig_box, use_container_width=True)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_hist, use_container_width=True)
col2.plotly_chart(fig_heatmap, use_container_width=True)

# =========================
# 5. ADVANCED VISUALIZATIONS (FULL WIDTH)
# =========================
year_df = filtered_df[filtered_df['Year']==selected_years[1]]

# 5.1 Climate vs Yield Bubble
fig_bubble = clean_fig(px.scatter(
    year_df, x='Total_Precipitation_Mm', y='Average_Temperature_C',
    size='Crop_Yield_Mt_Per_Ha', color='Economic_Impact_Million_Usd',
    hover_name='Region', size_max=40, color_continuous_scale='RdBu',
    title='Climate & Agriculture: Precipitation vs Temperature'
))
st.plotly_chart(fig_bubble, use_container_width=True)

# 5.2 Stress vs Yield with Irrigation
region_df = year_df.groupby('Region').agg({
    'Climate_Stress_Index':'mean',
    'Crop_Yield_Mt_Per_Ha':'mean',
    'Irrigation_Access_%':'mean'
}).reset_index().sort_values('Climate_Stress_Index', ascending=False).head(10)
region_df['Stress_Normalized'] = (region_df['Climate_Stress_Index']-region_df['Climate_Stress_Index'].min())/(region_df['Climate_Stress_Index'].max()-region_df['Climate_Stress_Index'].min())

fig_stress = go.Figure()
fig_stress.add_trace(go.Bar(
    x=region_df['Region'], y=region_df['Stress_Normalized'], name='Climate Stress', marker_color='#264653'
))
fig_stress.add_trace(go.Scatter(
    x=region_df['Region'], y=region_df['Crop_Yield_Mt_Per_Ha'], name='Crop Yield',
    mode='lines+markers', yaxis='y2', line=dict(color='#e76f51', width=3)
))
fig_stress.add_trace(go.Scatter(
    x=region_df['Region'], y=region_df['Stress_Normalized'], mode='markers',
    marker=dict(size=region_df['Irrigation_Access_%'], sizemode='area',
                sizeref=2.*max(region_df['Irrigation_Access_%'])/(40.**2),
                color=region_df['Irrigation_Access_%'], colorscale='Blues',
                showscale=True, colorbar=dict(title='Irrigation Access (%)')),
    showlegend=False
))
fig_stress.update_layout(
    title="Climate Stress vs Crop Yield with Irrigation (Top 10 Regions)",
    yaxis2=dict(overlaying='y', side='right')
)
fig_stress = clean_fig(fig_stress, y2=True)
st.plotly_chart(fig_stress, use_container_width=True)

# 5.3 Global Agriculture Map
map_df = year_df.groupby('Country').agg({
    'Climate_Stress_Index':'mean',
    'Crop_Yield_Mt_Per_Ha':'mean',
    'Irrigation_Access_%':'mean'
}).reset_index()

fig_map = go.Figure()
fig_map.add_trace(go.Choropleth(
    locations=map_df['Country'], locationmode='country names', z=map_df['Climate_Stress_Index'],
    colorscale='Oranges', colorbar_title='Climate Stress',
    hovertemplate='<b>%{location}</b><br>Climate Stress: %{z:.2f}<extra></extra>'
))
bubble_size = map_df['Crop_Yield_Mt_Per_Ha']*25
fig_map.add_trace(go.Scattergeo(
    locations=map_df['Country'], locationmode='country names', text=map_df['Country'],
    mode='markers+text',
    marker=dict(size=bubble_size, color=map_df['Irrigation_Access_%'], colorscale='Viridis',
                colorbar=dict(title='Irrigation Access (%)', x=1.15), opacity=0.85, line=dict(width=2, color='black'), sizemode='area'),
    textposition="top center",
    hovertemplate='<b>%{text}</b><br>Crop Yield: %{marker.size:.2f} Mt/Ha<br>Irrigation Access: %{marker.color:.2f}%<extra></extra>'
))
fig_map.update_layout(
    title='Global Agricultural Vulnerability and Performance',
    geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth', landcolor='lightgray')
)
st.plotly_chart(fig_map, use_container_width=True)