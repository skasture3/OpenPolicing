import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
import requests
import os

# Load and preprocess data
data = pd.read_csv('output.csv')
data = data.dropna(subset=['lat', 'lng'])

# Clustering
num_clusters = 100
coords = data[['lat', 'lng']]
scaler = MinMaxScaler()
coords_scaled = scaler.fit_transform(coords)
kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
data['risk_zone'] = kmeans.fit_predict(coords_scaled)

# Identify high-risk zones
violation_counts = data.groupby('risk_zone').size()
high_risk_threshold = violation_counts.quantile(0.8)  
high_risk_zones = violation_counts[violation_counts >= high_risk_threshold].index.tolist()

zone_centroids = kmeans.cluster_centers_ 
data['risk_weight'] = 0.5 

if not high_risk_zones:
    print("Warning: No high-risk zones dynamically identified. Defaulting to uniform risk weights.")

for zone in high_risk_zones:
    zone_coords = zone_centroids[zone]
    indices_in_zone = data['risk_zone'] == zone
    coords_in_zone = coords_scaled[indices_in_zone]
    proximity_weight = np.exp(-np.linalg.norm(coords_in_zone - zone_coords, axis=1))
    
    data.loc[indices_in_zone, 'risk_weight'] += proximity_weight

data['risk_weight'] = MinMaxScaler().fit_transform(data[['risk_weight']])

# Prepare risk dictionaries
generalRisk = data.groupby('risk_zone')['risk_weight'].mean().to_dict()
demographicBasedRisk = defaultdict(
    lambda: 0,
    data.groupby(['risk_zone', 'subject_race', 'subject_sex'])['risk_weight'].mean().to_dict(),
)

def calculate_combined_risk(base_score, demographic_score, w1=0.7, w2=0.3):
    """
    Combine base risk and demographic risk using weighted scoring.
    """
    return (w1 * base_score) + (w2 * demographic_score)

def calculate_safety_score(route_steps, race=None, sex=None):
    """
    Calculate the safety score for a given route.
    Incorporates weighted scoring and distance contribution.
    """
    route_points = np.array([[step['start_location']['lat'], step['start_location']['lng']] for step in route_steps])
    route_points_df = pd.DataFrame(route_points, columns=['lat', 'lng']) 
    route_points_scaled = scaler.transform(route_points_df)  
    zones = kmeans.predict(route_points_scaled)

    distances = [step['distance']['value'] for step in route_steps] 
    total_distance = sum(distances)
    
    weighted_scores = []
    for i, zone in enumerate(zones):
        base_score = generalRisk.get(zone, 0)
        demographic_score = demographicBasedRisk.get((zone, race, sex), 0)
        combined_score = calculate_combined_risk(base_score, demographic_score)
        distance_weight = distances[i] / total_distance 
        weighted_scores.append(combined_score * distance_weight)
    
    if not weighted_scores:
        print("Warning: No weighted scores calculated. Defaulting to 100.")
        return 100 
    safety_score = (1 - sum(weighted_scores)) * 100
    safety_score = max(0, min(safety_score, 100))
    return safety_score

def fetch_route_data(start_location, end_location):
    """
    Fetch route data from Google Maps API.
    """
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Error fetching route data.")
    route_data = response.json()
    if 'routes' not in route_data or not route_data['routes']:
        raise ValueError("No route found between specified locations.")
    return route_data['routes'][0]['legs'][0]['steps']

def safetyScore(start_location, end_location, race=None, sex=None):
    """
    Main function to compute the safety score between two locations.
    """
    try:
        route_steps = fetch_route_data(start_location, end_location)
        score = calculate_safety_score(route_steps, race, sex)
        return score
    except Exception as e:
        print(f"Error calculating safety score: {e}")
        return None
