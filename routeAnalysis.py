import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import requests


data = pd.read_csv('output.csv')
data = data.dropna(subset=['lat', 'lng'])


num_clusters = 100
coords = data[['lat', 'lng']]
scaler = MinMaxScaler()
coords_scaled = scaler.fit_transform(coords)
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
data['risk_zone'] = kmeans.fit_predict(coords_scaled)

generalRisk = data['risk_zone'].value_counts(normalize=True).to_dict()
demographicBasedRisk = data.groupby(['risk_zone', 'subject_race', 'subject_sex']).size().div(len(data)).to_dict()

def safetyScore(start_location, end_location, race=None, sex=None):
   #replace temp key with API key
    routeVals = requests.get(
        f"https://maps.googleapis.com/maps/api/directions/json?origin={start_location}&destination={end_location}&key=tempKey"
    )
    routeData = routeVals.json()
    
    if 'routes' not in routeData or not routeData['routes']:
        raise ValueError("No route found between specified locations.")
    
   
    routeSteps = routeData['routes'][0]['legs'][0]['steps']
    routePoints = [(step['start_location']['lat'], step['start_location']['lng']) for step in routeSteps]


    scores = []
    for lat, lng in routePoints:
        point_scaled = scaler.transform(pd.DataFrame([[lat, lng]], columns=['lat', 'lng']))
        zone = kmeans.predict(point_scaled)[0]
        
        baseScore = generalRisk.get(zone, 0)
    
        demographicScore = demographicBasedRisk.get((zone, race, sex), 0) if race and sex else 0
        combinedScore = baseScore + (demographicScore * 2)
        scores.append(combinedScore)
    
    safetyScore = (1 - np.mean(scores)) * 100
    print(f"Safety Score: {safetyScore:.2f}")
    return safetyScore

start = "Atlanta, GA"
end = "Savannah, GA"
safetyScore = safetyScore(start, end, race='black', sex='male')
print(f"Calculated Safety Score: {safetyScore}")
