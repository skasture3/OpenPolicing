import dash
from dash import dcc, html, Input, Output
import geopandas as gpd
import pandas as pd
import plotly.express as px

counties = gpd.read_file('ne_10m_admin_2_counties/ne_10m_admin_2_counties.shp')  # Replace with your file path
georgia_counties = counties[counties['ISO_3166_2'] == 'US-13']

# Load crime data for Georgia
crime_data_path = "crime_count_by_county.csv"  # Replace with your file path
crime_data = pd.read_csv(crime_data_path)

# Ensure county names match between datasets
georgia_counties['county_name'] = georgia_counties['NAME']  # Adjust column name if necessary
merged_data = georgia_counties.merge(crime_data, on='county_name', how='left')

# Load the traffic stop data
csv_file_path = "aggregated_data.csv"
aggregated_data = pd.read_csv(csv_file_path)

# Aggregate the data by state
state_counts = aggregated_data.groupby("state")["count"].sum().reset_index()

# Load shapefile data function from notebook
def load_us_states(shapefile_path):
    states = gpd.read_file(shapefile_path)
    us_states = states[states['iso_a2'] == 'US']
    return us_states

# Sample shapefile path (replace with actual path in your environment)
shapefile_path = "ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces.shp"

# Initialize app
app = dash.Dash(__name__)

# Load and prepare GeoDataFrame
try:
    us_states = load_us_states(shapefile_path)
except Exception as e:
    us_states = None
    print(f"Error loading shapefile: {e}")

# Layout
app.layout = html.Div([
    html.H1("Traffic Data Visualization App"),
    html.Label("Select Age Range:"),
    dcc.Dropdown(
        id="age-range",
        options=[
            {"label": "18-25", "value": "18-25"},
            {"label": "26-35", "value": "26-35"},
            {"label": "36-45", "value": "36-45"},
            {"label": "46-60", "value": "46-60"},
            {"label": "60+", "value": "60-100"}
        ],
        value=None,
        placeholder="Select age range (optional)"
    ),
    html.Label("Select Race:"),
    dcc.Dropdown(
        id="race",
        options=[
            {"label": "White", "value": "white"},
            {"label": "Black", "value": "black"},
            {"label": "Asian", "value": "asian"},
            {"label": "Hispanic", "value": "hispanic"},
            {"label": "Other", "value": "other"}
        ],
        value=None,
        placeholder="Select race (optional)"
    ),
    html.Label("Select Sex:"),
    dcc.Dropdown(
        id="sex",
        options=[
            {"label": "Male", "value": "male"},
            {"label": "Female", "value": "female"}
        ],
        value=None,
        placeholder="Select sex (optional)"
    ),
    dcc.Graph(id="map-graph"),
    html.Div(id="state-info", style={"margin-top": "20px", "font-size": "18px"}),
    dcc.Graph(id="state-map", style={"margin-top": "20px"})  # Placeholder for county maps
])


def filter_by_age(data, age):
    if age is None:
        return data
    data['subject_age'] = pd.to_numeric(data['subject_age'], errors='coerce')
    data = data.dropna(subset=['subject_age'])
    data['subject_age'] = data['subject_age'].astype(int)
    min_age, max_age = map(int, age.split("-"))
    data = data[(data['subject_age'] >= min_age) & (data['subject_age'] <= max_age)]
    return data

def filter_by_race(data, race):
    if race is None:
        return data
    return data[data['subject_race'] == race]

def filter_by_sex(data, sex):
    if sex is None:
        return data
    return data[data['subject_sex'] == sex]


# Callback
@app.callback(
    Output("map-graph", "figure"),
    [Input("age-range", "value"),
     Input("race", "value"),
     Input("sex", "value")]
)
def update_map(age, race, sex):
    # Apply filters
    filtered_data = filter_by_age(aggregated_data, age)
    filtered_data = filter_by_race(filtered_data, race)
    filtered_data = filter_by_sex(filtered_data, sex)

    # Aggregate data by state
    state_data = filtered_data.groupby("state")["count"].sum().reset_index()

    # Generate the choropleth map
    fig = px.choropleth(
        state_data,
        locations="state",
        locationmode="USA-states",
        color="count",
        hover_name="state",
        hover_data={"count": True},
        title="Traffic Stops by State",
        color_continuous_scale="Viridis",
    )

    # Focus map on the US
    fig.update_geos(scope="usa")

    return fig

@app.callback(
    [Output("state-info", "children"), Output("state-map", "figure")],
    Input("map-graph", "clickData")
)
def display_state_info(click_data):
    if click_data:
        state = click_data["points"][0]["location"]  # Extract the clicked state

        # If Georgia is clicked, show its county map
        if state == "GA":
            fig = px.choropleth(
                merged_data,
                geojson=merged_data.__geo_interface__,
                locations=merged_data.index,
                color="crime_count",  # Use crime data for coloring
                hover_name="county_name",
                hover_data={"crime_count": True},
                title="Crime Counts by County in Georgia",
                color_continuous_scale="OrRd",
            )
            fig.update_geos(fitbounds="locations", visible=False)

            return f"State: {state}, Clicked: Georgia", fig

    # Default message and empty map
    return "Click on a state to see more information.", {}


# Run server
if __name__ == "__main__":
    app.run_server(debug=True)
