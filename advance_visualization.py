import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load your dataset ---
df = pd.read_csv("cleaned_data.csv")  

# 1. Multi-Dimensional Analysis of Climate Factors and Agricultural Output
filtered_df = df[df['Year'] == 2023]  # choose the year you want to visualize

# --- Optional: Sort/filter for cleaner display ---
filtered_df = filtered_df.sort_values('Total_Precipitation_Mm', ascending=False)

# # --- Create scatter bubble chart ---
def climate_vs_yield_chart(filtered_df):
    fig = px.scatter(
        filtered_df,
        x='Total_Precipitation_Mm',       
        y='Average_Temperature_C',        
        size='Crop_Yield_Mt_Per_Ha',      
        color='Economic_Impact_Million_Usd', 
        hover_name='Region',
        size_max=40,
        color_continuous_scale='RdBu',
        title='Climate & Agriculture: Precipitation vs Temperature',
        labels={
            'Total_Precipitation_Mm':'Total Precipitation (mm)',
            'Average_Temperature_C':'Avg Temperature (°C)',
            'Crop_Yield_Mt_Per_Ha':'Crop Yield (Mt/Ha)',
            'Economic_Impact_Million_Usd':'Economic Impact (M$)'
    }
)

# # --- Update layout for clarity ---
    fig.update_layout(
        template='plotly_white',
        xaxis=dict(title='Total Precipitation (mm)'),
        yaxis=dict(title='Average Temperature (°C)'),
        legend_title_text='Economic Impact (M$)',
        hovermode='closest'
    )
    return fig


#2. Crop Stress VS Crop Yield With Irrigation Impact
def stress_yield_irrigation_chart(filtered_df):
    region_df = filtered_df.groupby('Region').agg({
        'Climate_Stress_Index': 'mean',
        'Crop_Yield_Mt_Per_Ha': 'mean',
        'Irrigation_Access_%': 'mean'
    }).reset_index()

    region_df = region_df.sort_values(by='Climate_Stress_Index', ascending=False).head(10)

    region_df['Stress_Normalized'] = (
        region_df['Climate_Stress_Index'] - region_df['Climate_Stress_Index'].min()
    ) / (
        region_df['Climate_Stress_Index'].max() - region_df['Climate_Stress_Index'].min()
    )

    fig = go.Figure()

    # BAR: Climate Stress
    fig.add_trace(go.Bar(
        x=region_df['Region'],
        y=region_df['Stress_Normalized'],
        name='Climate Stress',
        marker=dict(color='#264653'),
        opacity=0.85,
        hovertemplate='<b>%{x}</b><br>Stress: %{customdata[0]:.2f}<extra></extra>',
        customdata=region_df[['Climate_Stress_Index']].values
    ))

    # LINE: Crop Yield
    fig.add_trace(go.Scatter(
        x=region_df['Region'],
        y=region_df['Crop_Yield_Mt_Per_Ha'],
        name='Crop Yield',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#e76f51', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Yield: %{y:.2f}<extra></extra>'
    ))

    # BUBBLE: Irrigation
    fig.add_trace(go.Scatter(
        x=region_df['Region'],
        y=region_df['Stress_Normalized'],
        mode='markers',
        showlegend=False,
        marker=dict(
            size=region_df['Irrigation_Access_%'],
            sizemode='area',
            sizeref=2.*max(region_df['Irrigation_Access_%'])/(40.**2),
            color=region_df['Irrigation_Access_%'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title='Irrigation Access (%)', x=1.15),
            opacity=0.7
        ),
        hovertemplate='<b>%{x}</b><br>Irrigation: %{marker.color:.2f}%<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title="Climate Stress vs Crop Yield with Irrigation Impact (Top 10 Regions)",
        xaxis=dict(title="Region", tickangle=-30, showgrid=False, showline=True, linecolor='black'),
        yaxis=dict(title="Normalized Climate Stress", showgrid=False, showline=True, linecolor='black'),
        yaxis2=dict(title="Crop Yield (Mt/Ha)", overlaying='y', side='right', showgrid=False),
        legend=dict(x=1.02, y=1, bgcolor='rgba(255,255,255,0)'),
        template='plotly_white',
        margin=dict(l=40, r=120, t=80, b=80)
    )
    return fig

# 3. Map: Global Agricultural Vulnerability
def global_agriculture_map(filtered_df):
    map_df = filtered_df.groupby('Country').agg({
        'Climate_Stress_Index':'mean',
        'Crop_Yield_Mt_Per_Ha':'mean',
        'Irrigation_Access_%':'mean'
    }).reset_index()

    fig = go.Figure()

    # Choropleth
    fig.add_trace(go.Choropleth(
        locations=map_df['Country'],
        locationmode='country names',
        z=map_df['Climate_Stress_Index'],
        colorscale='Oranges',  
        colorbar_title='Climate Stress',
        hovertemplate='<b>%{location}</b><br>Climate Stress: %{z:.2f}<extra></extra>'
    ))

    # Bubble overlay
    bubble_size = map_df['Crop_Yield_Mt_Per_Ha']*25
    fig.add_trace(go.Scattergeo(
        locations=map_df['Country'],
        locationmode='country names',
        text=map_df['Country'],
        mode='markers+text',
        marker=dict(
            size=bubble_size,
            color=map_df['Irrigation_Access_%'],     
            colorscale='Viridis',      
            colorbar=dict(title='Irrigation Access (%)', x=1.15),
            opacity=0.85,
            line=dict(width=2, color='black'),
            sizemode='area'
        ),
        textposition="top center",
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Crop Yield: %{marker.size:.2f} Mt/Ha<br>'
            'Irrigation Access: %{marker.color:.2f}%<extra></extra>'
        ),
        name='Crop Yield'
    ))

    fig.update_layout(
        title='Global Agricultural Vulnerability and Performance',
        template='plotly_white',
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor='black',
                 projection_type='natural earth', landcolor='lightgray'),
        margin=dict(l=0, r=200, t=100, b=0)
    )
    return fig

# ----------------------------
# Standalone run
# ----------------------------
if __name__ == "__main__":
    # 1. Default filtered df for standalone (Year 2023)
    filtered_df = df[df['Year'] == 2023].sort_values('Total_Precipitation_Mm', ascending=False)

    fig1 = climate_vs_yield_chart(filtered_df)
    fig2 = stress_yield_irrigation_chart(filtered_df)
    fig3 = global_agriculture_map(filtered_df)

    # Show charts
    fig1.show()
    fig2.show()
    fig3.show()