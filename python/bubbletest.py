from yahooquery import Ticker
import plotly.graph_objects as go

etf='QQQ'
data=Ticker(etf.lower())


# Assuming 'sector_weights_dict' is your dictionary containing the sectors and their weights
sector_weights_dict = data.fund_sector_weightings.to_dict()[etf.lower()]
# Preparing data for the plot
sectors = list(sector_weights_dict.keys())
weights = list(sector_weights_dict.values())

# Create the bubble chart
fig = go.Figure(data=[go.Scatter(
    x=[0] * len(sectors),  # X, Y coordinates are not important for a packed bubble chart
    y=[0] * len(sectors),
    mode='markers',
    marker=dict(
        size=[weight * 1000 for weight in weights],  # Adjust size multiplier as needed
        sizemode='area',
        sizeref=2.*max([weight * 1000 for weight in weights])/(40.**2),
        sizemin=4,
    ),
    text=sectors,
)])

# Update layout for a more circular arrangement if necessary
fig.update_layout(
    title='QQQ Fund Sector Weightings',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
)

# Show the figure
#fig.show()

# To save the figure as a PNG file, you might need to use Plotly's image export feature, which requires Kaleido.
# You can install Kaleido with pip if you don't have it: pip install -U kaleido
# Then, to save the figure:
fig.write_image("qqq_fund_sector_bubble_chart.png")
