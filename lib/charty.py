# Chart libs
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def draw_pie_chart(percentage):
    labels = ["Not Match", "Match"]
    values=[100 - percentage, percentage]
    color_discrete_map=['#d3d3d378', 'lightgreen']

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=1, specs=[[{'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=values, name="resume matches"))

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.5, hoverinfo="label+percent")
    fig.update_traces(marker=dict(colors=color_discrete_map))

    fig.update_layout(
        title_text="Your resume matches")
    html = fig.to_html(include_plotlyjs="require", full_html=False)
    return html