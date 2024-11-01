import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import matplotlib as mpl

# Step 1: Load U.S. State Boundaries from Natural Earth Shapefile
def load_us_states(shapefile_path):
    # Load the shapefile
    states = gpd.read_file(shapefile_path)
    # Filter for U.S. states only (assuming 'iso_a2' or similar column for country code)
    us_states = states[states['iso_a2'] == 'US']
    return us_states

# Step 2: Load and Combine Traffic Stop Data for All States
def load_traffic_stop_data(folder_path):
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
    all_data = pd.DataFrame(columns=['name', 'stop_count'])

    for file in glob.glob(os.path.join(folder_path, "*.csv")):
        print(file)
        # Extract the state abbreviation from the filename and convert it to uppercase
        state_abbr = os.path.basename(file).split('_')[0].upper()  # Convert to uppercase
        
        # Convert the abbreviation to the full state name
        state_name = state_abbr_to_name.get(state_abbr, None)
        
        if state_name:  # Only process if the state name is found in the mapping
            # Load the CSV file and get the number of rows
            state_data = pd.read_csv(file)
            stop_count = len(state_data)
            
            # Print the state name and the first few rows of data for verification
            print(f"State: {state_name}, Stop Count: {stop_count}")
            print(state_data.head())  # Preview the first few rows of the file
            
            # Append to the all_data DataFrame
            temp_data = pd.DataFrame([{'name': state_name, 'stop_count': stop_count}])
            # Concatenate temp_data with all_data
            all_data = pd.concat([all_data, temp_data], ignore_index=True)
        else:
            print(f"Warning: State abbreviation {state_abbr} not found in mapping.")

    # Display the combined DataFrame for verification

    print(all_data)
    return all_data


def merge_data(us_states, traffic_stops):
    # Merge the GeoDataFrame with the traffic stops data
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

# Main Function to Execute All Steps
def main():
    shapefile_path = '/Users/sarvy/Downloads/ne_110m_admin_1_states_provinces/ne_110m_admin_1_states_provinces.shp'  # Update with your shapefile path
    folder_path = '/Users/sarvy/Desktop/policing_dataset'  # Update with the folder path containing CSV files

    # Load data
    us_states = load_us_states(shapefile_path)
    traffic_stops = load_traffic_stop_data(folder_path)
    us_map = merge_data(us_states, traffic_stops)

    # Plot the choropleth map
    plot_choropleth(us_map)

# Run the main function
if __name__ == "__main__":
    main()
