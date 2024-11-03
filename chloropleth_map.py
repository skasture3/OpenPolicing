import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import matplotlib as mpl
from ipywidgets import interact, Dropdown, fixed

# Step 1: Load U.S. State Boundaries from Natural Earth Shapefile
def load_us_states(shapefile_path):
    # Load the shapefile
    states = gpd.read_file(shapefile_path)
    # Filter for U.S. states only (assuming 'iso_a2' or similar column for country code)
    us_states = states[states['iso_a2'] == 'US']
    return us_states

# Step 2: Load and Combine Traffic Stop Data for All States
def load_traffic_stop_data(file_path, age=None, sex=None, race=None):
    # Initialize an empty DataFrame to store all states' data

    state_abbr_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
        'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
        'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
        'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
        'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }

    # Initialize an empty DataFrame to store all states' data
    traffic_data = pd.read_csv(file_path)
    
    # Check if 'state' column exists
    if 'state' not in traffic_data.columns:
        print("Missing 'state' column in the dataset.")
        return None
    
    traffic_data['subject_age'] = traffic_data['subject_age'].fillna('Unknown')
    traffic_data['subject_race'] = traffic_data['subject_race'].fillna('Unknown')
    traffic_data['subject_sex'] = traffic_data['subject_sex'].fillna('Unknown')

    # Aggregate by state to get the total count of stops per state
    grouped_data = traffic_data.groupby(['state', 'subject_age', 'subject_race', 'subject_sex'], as_index=False)['count'].sum()

    # Map state abbreviations to full names
    grouped_data['state'] = grouped_data['state'].map(state_abbr_to_name)

    # Now aggregate by state, summing the 'count' column to get the total count per state
    aggregated_data = grouped_data.groupby('state', as_index=False)['count'].sum()
    aggregated_data = aggregated_data.rename(columns={'count': 'stop_count'})

    print("Aggregated Data by State:")

    print(aggregated_data)
    
    return aggregated_data


def merge_data(us_states, traffic_stops):
    # Merge the GeoDataFrame with the traffic stops data
    print("Columns in us_states:", us_states.columns)
    print("Columns in traffic_stops:", traffic_stops.columns)
    traffic_stops = traffic_stops.rename(columns={'state': 'name'})
    us_map = us_states.merge(traffic_stops, on='name', how='left')
    return us_map

# Step 4: Plot the Choropleth Map
def plot_choropleth(us_map):
    # Create the plot
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Plot the choropleth without the legend parameter
    us_map.plot(
        column='stop_count', 
        cmap='OrRd', 
        linewidth=0.8, 
        ax=ax, 
        edgecolor='0.8'
    )
    
    # Create a color bar as a separate item
    sm = plt.cm.ScalarMappable(cmap='OrRd', norm=mpl.colors.Normalize(vmin=us_map['stop_count'].min(), vmax=us_map['stop_count'].max()))
    sm._A = []  # Dummy array for the color bar
    
    # Add the color bar to the plot
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Traffic Stop Counts", fontsize=12)
    
    # Customize the plot
    ax.set_title("Traffic Stops by State", fontsize=15)
    ax.set_axis_off()  # Hide axes for a cleaner look
    plt.show()

def interactive_map(shapefile_path, data_file_path, age, sex, race):
    us_states = load_us_states(shapefile_path)
    traffic_stops = load_traffic_stop_data(data_file_path, age=age, sex=sex, race=race)
    print(traffic_stops)
    us_map = merge_data(us_states, traffic_stops)
    plot_choropleth(us_map)

# Main Function to Execute All Steps
def main():
    shapefile_path = '/Users/sarvy/Downloads/ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces.shp'  # Update with your shapefile path
    folder_path = '/Users/sarvy/Desktop/OpenPolicing/OpenPolicing/aggregated_data.csv'  # Update with the folder path containing CSV files

    # Load data
    age_dropdown = Dropdown(
        options=['Unknown', '20-29', '30-39', '40-49', None], 
        value=None, 
        description='Age:'
    )
    sex_dropdown = Dropdown(
        options=['Unknown', 'Male', 'Female', None], 
        value=None, 
        description='Sex:'
    )
    race_dropdown = Dropdown(
        options=['Unknown', 'White', 'Black', 'Asian', 'Hispanic', None], 
        value=None, 
        description='Race:'
    )
    def f(x):
        return x
    
    interact(f, x=10)

    # Display the interactive map with dropdowns for age, sex, and race filters
    interact(
        interactive_map, 
        shapefile_path=fixed(shapefile_path), 
        data_file_path=fixed(folder_path),
        age=age_dropdown, 
        sex=sex_dropdown, 
        race=race_dropdown
    )

# Run the main function
if __name__ == "__main__":
    main()
