#!/usr/bin/env python
# coding: utf-8

# # Final Project - Idaho Policy Institute 5
# ## Ryan Pacheco, Ashley Gilbert, Ben Whitehead
# 
# Our goal is to identify characteristics which make a city sustainable, then classify cities based on whether they are growing sustainably or not. We will be looking at the 5 largest cities in Idaho, California, and New York. 
# 
# ## How we chose our data
# We gathered data from three sources:
# - US Census (2000 compared to 2010)
# - American Community Survey Data (2011 -> 2017)
# - Greenhouse Gas Data From EPA (2010 -> 2018)
# 
# ### Census Data Columns Chosen
# - NAME: City Name 
# - P002001: Total Population
# - P002002: Total Urban Population
# - P002005: Total Rural Population
# - H001001: Housing Unit Count
# - P013001: Median Age (both sexes)
# - H003001: Occupancy Status For Housing Units Presence of Non-Relatives
# - P027001: Presence of Non-Relatives
# - H005001: Vacancy_Status,
# - H005002: For_Rent,
# - H005003: Rented_Not_Occupied_,
# - H005004: For_Sale_Only,
# - H005005: Sold_Not_Occupied,
# - H005006: For_Seasonal_Recreational_Or_Occasional_Use,
# - H005007: For_Migrant_Workers
# 
# 
# ### ACS Data Columns Chosen:
# - B01003_001E: Total_Population
# - B00002_001E: Total_Housing
# - B09018_007E: Presence_of_Non-Relatives
# - B01002_001E: Median_Age
# 
# **NOTE:** ACS data for 2011, is in a different format than 2012->2017 so we have excluded it from our analysis.
# 
# ### Greenhouse Gas Data
# The greenhouse gas data is sourced from the EPA. We have chosen to only use the total direct reported emissions column from this data, since we are not particularly concerned with one chemical, but all pollutants. it should be noted that this data does not include commuter emissions data, it is gathered per factory location in the various cities. We aggregate all factories in a given city/state combination, then sum those reported numbers and join into our census and community survey data.
# 
# ## Initial Setup
# Imports:

# In[1]:


import pandas as pd
import seaborn as sns
import matplotlib as plt
import os

from census import Census
from us import states

import plotly.graph_objects as go


# Now we will load data:
# 
# **Greenhouse Gas Data:**

# In[2]:


ghg = pd.DataFrame()

for f in os.listdir('data/2018_data_summary_spreadsheets'):
    temp = pd.read_excel('data/2018_data_summary_spreadsheets/'+f, sheet_name=0)
    temp['Year'] = f.split('.')[0].split('_')[2]    
    ghg = pd.concat([temp, ghg], sort=False)
    
fips_map = pd.read_excel('data/fips-codes.xls', sheet_name=0)

fips_map = fips_map[fips_map['Entity Description'] == 'city']

def str_func(x):
    return str(x).zfill(5)

fips_map['FIPS'] = fips_map['FIPS Entity Code'].apply(str_func)
fips_map['City'] = fips_map['GU Name']
fips_map['State'] = fips_map['State Abbreviation']

ghg_mapped = pd.merge(ghg, fips_map, on=['State', 'City'])
total_emissions = ghg_mapped.groupby(['FIPS','Year'])['Total reported direct emissions'].agg('sum').to_frame()

total_emissions.reset_index(inplace=True)

pivot_em = total_emissions.pivot(index='FIPS', columns='Year', values='Total reported direct emissions')


# **US Census Data:**

# In[3]:


#API key
c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')

#common variables used for working with the census data.
keys = ['NAME' ,'P002001','P002002','P002005','H001001','P013001','H003001','P027001','H005001','H005002','H005003','H005004','H005005','H005006','H005007']

renames_2000 = {
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'P002001': 'Total_Population_2000',
        'P002002':'Total_Urban_Population_2000',
        'P002005':'Total_Rural_Population_2000',
        'H001001': 'Total_Housing_2000',
        'P013001': 'Median_Age_2000',
        'H003001': 'Occupancy_Status_For_Housing_Units_2000',
        'P027001': 'Presence_of_Non-Relatives_2000',
        'H005001': 'Vacancy_Status_2000',
        'H005002': 'For_Rent_2000',
        'H005003': 'Rented_Not_Occupied_2000',
        'H005004': 'For_Sale_Only_2000',
        'H005005': 'Sold_Not_Occupied_2000',
        'H005006': 'For_Seasonal_Recreational_Or_Occasional_Use_2000',
        'H005007': 'For_Migrant_Workers_2000'
}

renames_2010 = {
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'P002001': 'Total_Population_2010',
        'P002002':'Total_Urban_Population_2010',
        'P002005':'Total_Rural_Population_2010',
        'H001001': 'Total_Housing_2010',
        'P013001': 'Median_Age_2010',
        'H003001': 'Occupancy_Status_For_Housing_Units_2010',
        'P027001': 'Presence_of_Non-Relatives_2010',
        'H005001': 'Vacancy_Status_2010',
        'H005002': 'For_Rent_2010',
        'H005003': 'Rented_Not_Occupied_2010',
        'H005004': 'For_Sale_Only_2010',
        'H005005': 'Sold_Not_Occupied_2010',
        'H005006': 'For_Seasonal_Recreational_Or_Occasional_Use_2010',
        'H005007': 'For_Migrant_Workers_2010'}


#function used to get census data for given state
def load_census(state):
    #2010 census data 
    city_2010 = c.sf1.state_place(keys, state, '*', year=2010)
    c_pop_2010 = pd.DataFrame.from_records(city_2010)
    c_pop_2010_50000 = c_pop_2010.rename(columns=renames_2010)

    #2000 census data
    city_2000 = c.sf1.state_place(keys, state, '*', year=2000)
    c_pop_2000 = pd.DataFrame.from_records(city_2000)
    c_pop_2000_50000 = c_pop_2000.rename(columns=renames_2000)

    #drop extra columns for merge
    c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)

    #reset index for the join
    c_pop_2000_50000.set_index('FIPS', inplace=True)
    c_pop_2010_50000.set_index('FIPS', inplace=True)

    #join 2000 to 2010 for comparison
    state_joined = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')

    #join in greenhouse gas data
    state_joined = state_joined.join(pivot_em, on='FIPS')
    state_joined['Total_Population_2000'] = state_joined['Total_Population_2000'].astype('i8')

    #pick 5 largest cities in the state
    state_joined = state_joined.nlargest(5, 'Total_Population_2000')

    return state_joined

ca_join = load_census(states.CA.fips)
ny_join = load_census(states.NY.fips)
id_join = load_census(states.ID.fips)


# **American Community Survey Data:** 

# In[4]:


def load_acs(state):
    i = 0
    acs_years = []
    for x in range(2012, 2018):
        acs_test = c.acs5.state_place(('NAME',
                                    'B01003_001E',
                                    'B00002_001E',
                                    'B09018_007E',
                                    'B01002_001E'), state, '*', year=x)
        acs_years.append(pd.DataFrame.from_records(acs_test))
        acs_years[i] = acs_years[i].rename(columns={
            'NAME' : 'City_Name',
            'place': 'FIPS',
            'B01003_001E': 'Total_Population_{}'.format(x),
            'B00002_001E': 'Total_Housing_{}'.format(x),
            'B09018_007E': 'Presence_of_Non-Relatives_{}'.format(x),
            'B01002_001E': 'Median_Age_{}'.format(x),
        })
        acs_years[i].set_index('FIPS', inplace=True)
        acs_years[i].drop(columns=['City_Name', 'state'], inplace=True)
        acs_years[i] = acs_years[i].nlargest(5, 'Total_Population_{}'.format(x))
        i = i + 1

    return acs_years

acs_years_ca = load_acs(states.CA.fips)
acs_years_id = load_acs(states.ID.fips)
acs_years_ny = load_acs(states.NY.fips)


# ## Merge data and start analysis
# 
# Now that we have the data loaded, we can start our analysis. See state level python notebooks for additional details about the respective state.

# ## Census Data
# Join individual state census data to get a comparative understanding of the data.

# In[5]:


three_state_df = pd.concat([id_join, ca_join, ny_join])

three_state_df.reset_index(inplace=True)


# In[6]:


i = 0
three_state_acs = []
for x in acs_years_ca:
    acs_1 = pd.concat([acs_years_ca[i], acs_years_ny[i], acs_years_id[i]])
    three_state_acs.append(acs_1)
    i = i + 1


# In[7]:


three_state_df.set_index('FIPS', inplace=True)


# In[8]:


for x in three_state_acs:
    three_state_df = three_state_df.join(x, on="FIPS")


# In[9]:


three_state_df.reset_index(inplace=True)


# In[10]:


three_state_df.head()


# ### Plot Data Census Data From Three States

# In[11]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# #### Median Age
# We also wanted to compare median age across the various cities, since that could have an impact on sustainability. We decide to do this before adjusting our data, so we can see the full picture.

# In[12]:


fig = go.Figure(data=[
    go.Bar(name='2000_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2000']),
    go.Bar(name='2010_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2010']),
    go.Bar(name='2012_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2012']),
    go.Bar(name='2013_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2013']),
    go.Bar(name='2014_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2014']),
    go.Bar(name='2015_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2015']),
    go.Bar(name='2016_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2016']),
    go.Bar(name='2017_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2017']),
])
fig.update_layout(barmode='group')
fig.show()


# **We will drop New York City and Los Angeles from the graph since they are skewing the figure**

# In[13]:


three_state_df.drop(three_state_df[three_state_df['City_Name'] =='Los Angeles city, California'].index, inplace = True)
three_state_df.drop(three_state_df[three_state_df['City_Name'] =='New York city, New York'].index, inplace = True)


# In[14]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# **California is still being an issue, lets drop those cities form our graph**

# In[15]:


three_state_df.drop(three_state_df[three_state_df['state'] ==states.CA.fips].index, inplace = True)


# In[16]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# This allows us to visually compare the city census data for New York State and Idaho easily. **NOTE:** Double click on a legend item in the graph to isolate specifc data.

# ## American Community Survey
# Now let's look at the ACS data with the census and emissions data to expand the timeframe of our analysis.
# 

# ### Plot all the data

# In[17]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2012_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2012']),
    go.Bar(name='2013_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2013']),
    go.Bar(name='2014_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2014']),
    go.Bar(name='2015_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2015']),
    go.Bar(name='2016_pop', x=t hree_state_df['City_Name'], y=three_state_df['Total_Population_2016']),
    go.Bar(name='2017_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2017']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2012_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2012']),
    go.Bar(name='2013_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2013']),
    go.Bar(name='2014_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2014']),
    go.Bar(name='2015_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2015']),
    go.Bar(name='2016_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2016']),
    go.Bar(name='2017_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2017']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2012_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2012']),
    go.Bar(name='2013_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2013']),
    go.Bar(name='2014_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2014']),
    go.Bar(name='2015_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2015']),
    go.Bar(name='2016_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2016']),
    go.Bar(name='2017_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2017']),
    go.Bar(name='2010_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2010']),
    go.Bar(name='2011_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2011']),
    go.Bar(name='2012_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2012']),
    go.Bar(name='2013_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2013']),
    go.Bar(name='2014_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2014']),
    go.Bar(name='2015_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2015']),
    go.Bar(name='2016_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2016']),
    go.Bar(name='2017_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2017']),
    go.Bar(name='2018_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2018'])
])
fig.update_layout(barmode='group')
fig.show()


# In[ ]:





# In[ ]:





# **Idaho Falls and Rochester are skewing the graph, due to high level of emissions data so we will remove them.**

# In[ ]:


three_state_df.drop(three_state_df[three_state_df['City_Name'] =='Idaho Falls city, Idaho'].index, inplace = True)
three_state_df.drop(three_state_df[three_state_df['City_Name'] =='Rochester city, New York'].index, inplace = True)


# In[ ]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2012_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2012']),
    go.Bar(name='2013_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2013']),
    go.Bar(name='2014_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2014']),
    go.Bar(name='2015_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2015']),
    go.Bar(name='2016_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2016']),
    go.Bar(name='2017_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2017']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2012_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2012']),
    go.Bar(name='2013_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2013']),
    go.Bar(name='2014_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2014']),
    go.Bar(name='2015_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2015']),
    go.Bar(name='2016_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2016']),
    go.Bar(name='2017_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2017']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2012_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2012']),
    go.Bar(name='2013_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2013']),
    go.Bar(name='2014_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2014']),
    go.Bar(name='2015_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2015']),
    go.Bar(name='2016_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2016']),
    go.Bar(name='2017_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2017']),
    go.Bar(name='2010_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2010']),
    go.Bar(name='2011_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2011']),
    go.Bar(name='2012_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2012']),
    go.Bar(name='2013_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2013']),
    go.Bar(name='2014_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2014']),
    go.Bar(name='2015_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2015']),
    go.Bar(name='2016_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2016']),
    go.Bar(name='2017_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2017']),
    go.Bar(name='2018_direct_emissions', x=three_state_df['City_Name'], y=three_state_df['2018'])
])
fig.update_layout(barmode='group')
fig.show()


# In[ ]:





# ## Modeling Sustainability
# Using the data we've been working with, we will now make a model to represent whether a city is growing sustainably or not. 

# In[ ]:


import statsmodels.api as sm
import statsmodels.formula.api as smf
import sklearn.metrics
import sys
from pandas_ml import ConfusionMatrix


# In[ ]:


#Restore Data Frame, such that we have all the cities that have been dropped
three_state_df = pd.concat([id_join, ca_join, ny_join])
three_state_df.reset_index(inplace=True)


# In[ ]:


mod = smf.glm('Total_Population_2000 ~ Total_Population_2010  + Total_Population_2013', three_state_df, family=sm.families.Binomial()).fit()
mod.summary()


# In[ ]:




