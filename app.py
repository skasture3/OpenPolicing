import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from safety_score import safetyScore

# Initialize the Dash app with a Bootstrap theme for better styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # For deployment purposes

# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Route Safety Score Calculator", className="text-center my-4"),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Start Location"),
                        dbc.Input(id="start-input", placeholder="Enter start address", type="text"),
                    ],
                    md=6
                ),
                dbc.Col(
                    [
                        dbc.Label("End Location"),
                        dbc.Input(id="end-input", placeholder="Enter end address", type="text"),
                    ],
                    md=6
                ),
            ],
            className="mb-3"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Race (optional)"),
                        dcc.Dropdown(
                            id="race-input",
                            options=[
                                {"label": "Asian", "value": "asian"},
                                {"label": "Black", "value": "black"},
                                {"label": "Hispanic", "value": "hispanic"},
                                {"label": "White", "value": "white"},
                                {"label": "Other", "value": "other"},
                            ],
                            placeholder="Select race",
                            clearable=True,
                        ),
                    ],
                    md=6
                ),
                dbc.Col(
                    [
                        dbc.Label("Sex (optional)"),
                        dcc.Dropdown(
                            id="sex-input",
                            options=[
                                {"label": "Male", "value": "male"},
                                {"label": "Female", "value": "female"},
                                {"label": "Other", "value": "other"},
                            ],
                            placeholder="Select sex",
                            clearable=True,
                        ),
                    ],
                    md=6
                ),
            ],
            className="mb-3"
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Calculate Safety Score",
                    id="calculate-button",
                    color="primary",
                    style={"width": "100%"}
                ),
                width=12
            ),
            className="mb-3"
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id="output-score", className="text-center"),
                width=12
            )
        ),
    ],
    fluid=True
)

# Define callback to update the safety score
@app.callback(
    Output("output-score", "children"),
    Input("calculate-button", "n_clicks"),
    State("start-input", "value"),
    State("end-input", "value"),
    State("race-input", "value"),
    State("sex-input", "value"),
)
def update_output(n_clicks, start, end, race, sex):
    if n_clicks is None:
        return ""
    if not start or not end:
        return dbc.Alert("Please enter both start and end locations.", color="warning")
    
    # Calculate the safety score
    score = safetyScore(start, end, race, sex)
    
    if score is None:
        return dbc.Alert("An error occurred while calculating the safety score. Please try again.", color="danger")
    
    # Determine the safety level based on the score
    if score >= 75:
        safety_level = "High Safety"
        color = "success"
    elif score >= 50:
        safety_level = "Moderate Safety"
        color = "warning"
    else:
        safety_level = "Low Safety"
        color = "danger"
    
    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Safety Score", className="card-title"),
                html.H2(f"{score:.2f} / 100", className="card-text"),
                html.H5(f"Safety Level: {safety_level}", className=f"text-{color}"),
            ]
        ),
        color=color,
        inverse=True,
    )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
