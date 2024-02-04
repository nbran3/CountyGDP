### Import libraries
import folium
import os
import pandas as pd
import json
import pypyodbc

### Create a variable for folium to read the JSON file. This might not be needed if you are working with countries for example, but since I was using counties I got a shapefile (json). 
counties = os.path.join('data', 'counties.geojson')

### You can either connect to a local SQL database or just use a CSV for the data. I would recommend using a CSV file unless the data you are using is extremely big, but I did this for experimental reasons. 
conn = pypyodbc.connect('Driver={SQL SERVER};'
                        'Server=DESKTOP-K4HURDS\SQLEXPRESS01;'
                        'Database=Projects;'
                        'Trusted_Connection=yes;')
query = """
SELECT GeoFips, GeoName, GDP2022
FROM Projects.dbo.counties
WHERE GDP2022 < 200000
"""

rpiResults = pd.read_sql(query, conn)


### You do not need to do this, but since I wanted to make a tooltip that displays the GDP value with the county name, the SQL query needs to be ingested into the JSON file so it can work.  
rpiJSON = rpiResults[['geofips', 'gdp2022']]

# Load the existing GeoJSON file
with open(r'C:\Users\nbwan\Python\New folder\data\counties.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

# Create a dictionary to map geofips to GDP values
geofips_gdp_mapping = dict(zip(rpiJSON['geofips'], rpiJSON['gdp2022']))

# Update the GeoJSON properties with GDP values based on geofips
for feature in geojson_data['features']:
    geoid = feature['properties']['GEOID']
    if geoid in geofips_gdp_mapping:
        feature['properties']['gdp2022'] = geofips_gdp_mapping[geoid]

# Save the updated GeoJSON
with open('updated_geojson_file.json', 'w') as updated_geojson_file:
    json.dump(geojson_data, updated_geojson_file, indent=2)

### Create folium map, folium will write the HTML, Leaflet for you as long as you input and key the data correctly between the two sources.
map = folium.Map(location=[46.879002,-103.789879], zoom_start=5.4, tiles=r'https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', attr="US GDP 2022 Choropleth map by county.")

folium.Choropleth(
    geo_data = counties,
    name = 'US County GDP 2022',
    data = rpiResults,
    columns = ['geofips' , 'gdp2022'],
    key_on = 'properties.GEOID',
    fill_color = 'Pastel1',
    fill_opacity = 1,
    line_opacity = 1,
    nan_fill_color = '#f2efe9',
    line_color = 'white'
).add_to(map)

SQLJson = os.path.join('data', 'updated_geojson_file.json')

### This is to add a hover effect when the cursor is above a county, it will display its name. I tried to add the GDP result but since that is in a SQL query its a bit hard to add to a JSON file. 
g = folium.GeoJson(
    SQLJson,
    name='geojson'
).add_to(map)

folium.GeoJsonTooltip(fields=["NAME", 'gdp2022'], aliases=["County Name", "GDP 2022"]).add_to(g)

### Save to index.html and then view it in the browser  
map.save('index.html')


### Save to index.html and then view it in
