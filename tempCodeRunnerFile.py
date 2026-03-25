def histogram(df):
    hist_data = df['Total_Precipitation_Mm']
    counts, bin_edges = np.histogram(hist_data, bins=20)
    top_bins_idx = counts.argsort()[-3:]

    colors = []
    highlight_palette = ['#ff7f0e', '#17becf', '#1f77b4']
    for i in range(len(counts)):
        if i in top_bins_idx:
            colors.append(highlight_palette[list(top_bins_idx).index(i)])
        else:
            colors.append('#0d3d66')

    bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(counts))]
    bin_width = bin_edges[1] - bin_edges[0]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=counts,
        marker_color=colors,
        width=bin_width,
        hovertemplate='Precipitation: %{x:.2f} mm<br>Frequency: %{y}<extra></extra>'
    ))
    fig.update_layout(
        title="Distribution of Total Precipitation (Top 3 Bins Highlighted)",
        xaxis_title="Total Precipitation (mm)",
        yaxis_title="Frequency",
        template="plotly_white",
        bargap=0 
    )
    return clean_fig(fig)