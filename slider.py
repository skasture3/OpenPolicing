import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback_context
from datetime import datetime
import dash

app = Dash(__name__)

data_path = "/content/drive/My Drive/StateData/weekly_traffic_data.parquet"
data = pd.read_parquet(data_path)

data['week'] = pd.to_datetime(data['week'])
data = data.sort_values('week').reset_index(drop=True)

unique_weeks = sorted(data['week'].unique())
total_weeks = len(unique_weeks)

def find_start_index(start_date):
    if start_date in unique_weeks:
        return unique_weeks.index(start_date)
    for i, week in enumerate(unique_weeks):
        if week > start_date:
            return i
    return total_weeks - 1

app.layout = html.Div([
    html.H1("Interactive Weekly Cumulative Traffic Stops Map"),
    html.Div([
        html.Label("Select Start Date:"),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=min(unique_weeks),
            max_date_allowed=max(unique_weeks),
            initial_visible_month=min(unique_weeks),
            date=min(unique_weeks).date()
        )
    ], style={"marginBottom": "20px"}),
    dcc.Graph(id="choropleth-map"),
    dcc.Slider(
        id="week-slider",
        min=0,
        max=total_weeks - 1,
        step=1,
        value=total_weeks - 1,
        tooltip={"placement": "bottom", "always_visible": False},
        marks={},
        updatemode='drag'
    ),
    html.Div(id="slider-label", style={"textAlign": "center", "marginTop": "20px", "fontSize": "18px"})
])

@app.callback(
    [Output("week-slider", "min"),
     Output("week-slider", "max"),
     Output("week-slider", "marks"),
     Output("week-slider", "value")],
    [Input("start-date-picker", "date")]
)
def update_slider(start_date):
    if start_date is None:
        default_start_date = min(unique_weeks)
    else:
        try:
            start_date = pd.to_datetime(start_date)
            default_start_date = start_date
        except Exception:
            default_start_date = min(unique_weeks)

    try:
        start_index = find_start_index(default_start_date)
        max_index = total_weeks - 1
        num_weeks = max_index - start_index + 1

        if num_weeks <= 0:
            return 0, 0, {0: unique_weeks[max_index].strftime('%Y-%m-%d')}, 0

        marks = {}
        interval = max(1, num_weeks // 10)
        for i in range(start_index, max_index + 1, interval):
            week_label = unique_weeks[i].strftime('%Y-%m-%d')
            marks[i - start_index] = week_label

        if (max_index - start_index) % interval != 0:
            marks[num_weeks - 1] = unique_weeks[max_index].strftime('%Y-%m-%d')

        slider_value = num_weeks - 1
        return 0, num_weeks - 1, marks, slider_value
    except Exception as e:
        print(f"Error in update_slider: {e}")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("slider-label", "children"),
    [Input("week-slider", "value"),
     Input("start-date-picker", "date")]
)
def update_slider_label(selected_week_offset, start_date):
    if start_date is None:
        default_start_date = min(unique_weeks)
    else:
        try:
            default_start_date = pd.to_datetime(start_date)
        except Exception:
            default_start_date = min(unique_weeks)

    try:
        start_index = find_start_index(default_start_date)
        selected_week_index = start_index + selected_week_offset
        selected_week_index = min(selected_week_index, total_weeks - 1)
        selected_week = unique_weeks[selected_week_index]
        weeks_ago = total_weeks - (selected_week_index + 1)
        years = weeks_ago // 52
        weeks = weeks_ago % 52

        if weeks_ago == 0:
            return "This week"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''} and {weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    except Exception as e:
        print(f"Error in update_slider_label: {e}")
        return "Error updating label"

@app.callback(
    Output("choropleth-map", "figure"),
    [Input("week-slider", "value"),
     Input("start-date-picker", "date")]
)
def update_map(selected_week_offset, start_date):
    if start_date is None:
        default_start_date = min(unique_weeks)
    else:
        try:
            default_start_date = pd.to_datetime(start_date)
        except Exception:
            default_start_date = min(unique_weeks)

    try:
        start_index = find_start_index(default_start_date)
        selected_week_index = start_index + selected_week_offset
        selected_week_index = min(selected_week_index, total_weeks - 1)
        selected_week = unique_weeks[selected_week_index]
        filtered_data = data[data['week'] <= selected_week]
        filtered_data = filtered_data.groupby('state').last().reset_index()
        filtered_data['hover_text'] = (
            "State: " + filtered_data['state'] +
            "<br>Cumulative Traffic Stops: " + filtered_data['cumulative_traffic_stops'].apply(lambda x: f"{x:,.0f}")
        )
        fig = px.choropleth(
            filtered_data,
            locations="state",
            locationmode="USA-states",
            color="cumulative_traffic_stops",
            hover_name="state",
            scope="usa",
            title=f"Cumulative Traffic Stops up to {selected_week.strftime('%Y-%m-%d')}",
            color_continuous_scale="Plasma",
            hover_data={'hover_text': True},
        )
        fig.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        fig.update_layout(transition_duration=500)
        return fig
    except Exception as e:
        print(f"Error in update_map: {e}")
        return {
            "data": [],
            "layout": {
                "title": "Error updating the map.",
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
            }
        }

if __name__ == "__main__":
    app.run_server(debug=True)
