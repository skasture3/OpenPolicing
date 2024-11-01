import pandas as pd
import os
import glob

# Initialize an empty DataFrame to store aggregated data for all states
all_data = pd.DataFrame()

# Path to the folder containing all state CSV files
folder_path = '/Users/sarvy/Desktop/policing_dataset'  # Update with your actual folder path

# Loop through each .csv file in the folder
for file in glob.glob(os.path.join(folder_path, "*.csv")):
    print(os.path.basename(file))
    # Extract the state abbreviation from the filename
    state_abbr = os.path.basename(file).split('_')[0].upper()  # Adjust if needed

    # Load the CSV file
    state_data = pd.read_csv(file)

    print(state_data.columns)

    grouping_columns = []
    if 'subject_age' in state_data.columns:
        grouping_columns.append('subject_age')
    if 'subject_sex' in state_data.columns:
        grouping_columns.append('subject_sex')
    if 'subject_race' in state_data.columns:
        grouping_columns.append('subject_race')
    if 'violation' in state_data.columns:
        grouping_columns.append('violation')

    # Group by age, race, and sex to get the count of each combination
    grouped_data = state_data.groupby(grouping_columns).size().reset_index(name='count')

    # Add a new column for the state based on the filename
    grouped_data['state'] = state_abbr


    # Append the grouped data to the all_data DataFrame
    all_data = pd.concat([all_data, grouped_data], ignore_index=True)

# Check columns in the combined DataFrame
print("Columns in combined DataFrame:", all_data.columns)

# Save the aggregated data to a new CSV file
output_file = '/Users/sarvy/Desktop/OpenPolicing/aggregated_data.csv'  # Update with your desired output file path
all_data.to_csv(output_file, index=False)

print(f"Aggregated data saved to {output_file}")
