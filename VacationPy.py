#!/usr/bin/env python
# coding: utf-8

# # VacationPy
# ----
# 
# #### Note
# * Keep an eye on your API usage. Use https://developers.google.com/maps/reporting/gmp-reporting as reference for how to monitor your usage and billing.
# 
# * Instructions have been included for each segment. You do not have to follow them exactly, but they are included to help you think through the steps.

# In[1]:


# Dependencies and Setup
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import gmaps
import os

# Import API key
from api_keys import g_key


# ### Store Part I results into DataFrame
# * Load the csv exported in Part I to a DataFrame

# In[19]:


weather_data = pd.read_csv("../output_data/cities.csv")
weather_data.head()


# ### Humidity Heatmap
# * Configure gmaps.
# * Use the Lat and Lng as locations and Humidity as the weight.
# * Add Heatmap layer to map.

# In[29]:


gmaps.configure(api_key=g_key)
locations = weather_data[["Lat", "Lng"]]
humidity = weather_data["Humidity"]


# In[30]:


fig = gmaps.figure(center=(46.0, -5.0), zoom_level=2)
max_intensity = np.max(humidity)

heat_layer = gmaps.heatmap_layer(locations, weights = humidity, dissipating=False, max_intensity=100, point_radius=3)

fig.add_layer(heat_layer)
fig


# ### Create new DataFrame fitting weather criteria
# * Narrow down the cities to fit weather conditions.
# * Drop any rows will null values.

# In[10]:


narrowed_city_df = weather_data.loc[(weather_data["Wind Speed"] <= 10) & (weather_data["Cloudiness"] == 0) &                                    (weather_data["Max Temp"] >= 70) & (weather_data["Max Temp"] <= 80)].dropna()

narrowed_city_df


# ### Hotel Map
# * Store into variable named `hotel_df`.
# * Add a "Hotel Name" column to the DataFrame.
# * Set parameters to search for hotels with 5000 meters.
# * Hit the Google Places API for each city's coordinates.
# * Store the first Hotel result into the DataFrame.
# * Plot markers on top of the heatmap.

# In[11]:


hotel_df = narrowed_city_df.loc[:,["City","Country", "Lat", "Lng"]]

hotel_df["Hotel Name"] = ""

hotel_df


# In[14]:


base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

params = {"type" : "hotel",
          "keyword" : "hotel",
          "radius" : 5000,
          "key" : g_key}

for index, row in hotel_df.iterrows():
    # get city name, lat, lnt from df
    lat = row["Lat"]
    lng = row["Lng"]
    city_name = row["City"]
    
    # add keyword to params dict
    params["location"] = f"{lat},{lng}"

    # assemble url and make API request
    print(f"Retrieving Results for Index {index}: {city_name}.")
    response = requests.get(base_url, params=params).json()
    
    # extract results
    results = response['results']
    
    # save the hotel name to dataframe
    try:
        print(f"Closest hotel in {city_name} is {results[0]['name']}.")
        hotel_df.loc[index, "Hotel Name"] = results[0]['name']

    # if there is no hotel available, show missing field
    except (KeyError, IndexError):
        print("Missing field/result... skipping.")
        
    print("------------")
    

# Print end of search once searching is completed
print("-------End of Search-------")


# In[25]:


# NOTE: Do not change any of the code in this cell

# Using the template add the hotel marks to the heatmap
info_box_template = """
<dl>
<dt>Name</dt><dd>{Hotel Name}</dd>
<dt>City</dt><dd>{City}</dd>
<dt>Country</dt><dd>{Country}</dd>
</dl>
"""
# Store the DataFrame Row
# NOTE: be sure to update with your DataFrame name
hotel_info = [info_box_template.format(**row) for index, row in hotel_df.iterrows()]
locations = hotel_df[["Lat", "Lng"]]


# In[26]:


markers = gmaps.marker_layer(locations, info_box_content = hotel_info)
fig.add_layer(markers)
fig


# In[ ]:




