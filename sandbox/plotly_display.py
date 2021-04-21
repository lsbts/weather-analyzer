import plotly.express as px
from pathlib import Path

fig = px.scatter(x=range(10), y=range(10))
out_path = Path(__file__).parent / 'docs' / 'fig-plotly.html'
fig.write_html(str(out_path))
