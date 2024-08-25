# Import packages
from dash import Dash, html, dcc, dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Load data
df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

# Initialize the app
app = Dash(__name__)

# Define options for dropdown based on unique launch sites in the dataframe
launch_sites = df['Launch Site'].unique()
dropdown_options = [{'label': site, 'value': site} for site in launch_sites]
dropdown_options.insert(0, {'label': 'All Sites', 'value': 'ALL'})  # Add 'All Sites' option

# Define payload range for the slider
min_payload = df['Payload Mass (kg)'].min()
max_payload = df['Payload Mass (kg)'].max()

# App layout
app.layout = html.Div(children=[
    html.H1(children='SpaceX Launch Records Dashboard'),
    
    # Dropdown menu for selecting launch sites for the first pie chart
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    

    # Container for pie charts and scatter plot
    html.Div(children=[
        dcc.Graph(id='site-pie-chart'),
        # dcc.Graph(id='success-pie-chart'),
    ]),
    
    # Dropdown menu for selecting launch sites for the second pie chart
    dcc.Dropdown(
        id='success-site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site for Success Chart",
        searchable=True
    ),
    # Container for pie charts and scatter plot
    html.Div(children=[
        # dcc.Graph(id='site-pie-chart'),
        dcc.Graph(id='success-pie-chart'),
    ]),
    # Title and Range Slider for selecting payload
    html.Div(children=[
        html.H3(children='Select Payload Range (kg)'),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,  # Starting point of the slider
            max=10000,  # Ending point of the slider
            step=1000,  # Interval of the slider
            value=[min_payload, max_payload],  # Current selected range
            marks={i: str(i) for i in range(0, 10001, 1000)}  # Slider marks
        )
    ]),
    # Scatter plot
    html.Div(children=[
        dcc.Graph(id='success-payload-scatter-chart')
    ]),
])

# Callback to update pie charts based on dropdown and slider values
@app.callback(
    [Output('site-pie-chart', 'figure'),
     Output('success-pie-chart', 'figure'),
     Output('success-payload-scatter-chart', 'figure')],
    [Input('site-dropdown', 'value'),
     Input('success-site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_charts(selected_site, success_selected_site, payload_range):
    min_payload, max_payload = payload_range

    # Filter data based on payload range
    filtered_df = df[(df['Payload Mass (kg)'] >= min_payload) & (df['Payload Mass (kg)'] <= max_payload)]

    # Pie chart for the distribution of launches across different sites
    site_fig = px.pie(
        filtered_df,
        names='Launch Site',
        title='Total Success Launches By Site'
    )
    
    # Filter data based on dropdown selection for the success pie chart
    if success_selected_site == 'ALL':
        site_filtered_df = filtered_df
        title = 'Total Launch Outcomes for All Sites'
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == success_selected_site]
        title = f'Total Success Launches for site {success_selected_site}'
    
    # Pie chart for launch outcomes
    success_fig = px.pie(
        site_filtered_df,
        names='class',
        title=title,
        labels={'class': 'Launch Outcome'},
        color_discrete_map={0: 'red', 1: 'green'}
    )
    
    # Scatter plot for Payload Mass vs. Success
    scatter_fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success for all Sites',
        labels={'class': 'Launch Success'}
    )

    return site_fig, success_fig, scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
