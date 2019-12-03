#!/usr/bin/env python
# coding: utf-8

# # Final Project - Idaho Policy Institute 5
# ## Ryan Pacheco, Ashley Gilbert, Ben Whitehead
# 
# Our goal is to identify characteristics which make a city sustainable, then classify cities based on whether they are growing sustainably or not. We will be looking at the cities in Idaho, California, and New York (state) with a population over 50,000.
# 
# ## Initial Setup
# We will start bby loading all of our data sources:
# - US Census Data
# - American Community Survey Data
# - Greenhouse Gas Data (procured by the EPA)

# In[1]:


get_ipython().run_line_magic('pip', 'install census us')


# In[2]:


import pandas as pd
import seaborn as sns
import matplotlib as plt
import os

from census import Census
from us import states

import plotly.graph_objects as go


# In[3]:


states.ID.shapefile_urls('county')


# In[4]:


#load census data using API key
c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')

#American Community Survey Data for California
i = 0
acs_years_ca = []
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
                                   'B01003_001E',
                                   'B00002_001E',
                                   'B09018_007E',
                                   'B01002_001E'), states.CA.fips, '*', year=x)
    acs_years_ca.append(pd.DataFrame.from_records(acs_test))
    print(x)
    acs_years_ca[i] = acs_years_ca[i].rename(columns={
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'B01003_001E': 'Total_Population_{}'.format(x),
        'B00002_001E': 'Total_Housing_{}'.format(x),
        'B09018_007E': 'Presence_of_Non-Relatives_{}'.format(x),
        'B01002_001E': 'Median_Age_{}'.format(x),
    })
    acs_years_ca[i].set_index('FIPS', inplace=True)
    acs_years_ca[i].drop(columns=['City_Name', 'state'], inplace=True)
    acs_years_ca[i] = acs_years_ca[i].nlargest(5, 'Total_Population_{}'.format(x))
    i = i + 1


#American Community Survey Data for New York
i = 0
acs_years_ny = []
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
                                   'B01003_001E',
                                   'B00002_001E',
                                   'B09018_007E',
                                   'B01002_001E'), states.NY.fips, '*', year=x)
    acs_years_ny.append(pd.DataFrame.from_records(acs_test))
    print(x)
    acs_years_ny[i] = acs_years_ny[i].rename(columns={
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'B01003_001E': 'Total_Population_{}'.format(x),
        'B00002_001E': 'Total_Housing_{}'.format(x),
        'B09018_007E': 'Presence_of_Non-Relatives_{}'.format(x),
        'B01002_001E': 'Median_Age_{}'.format(x),
    })
    acs_years_ny[i].set_index('FIPS', inplace=True)
    acs_years_ny[i].drop(columns=['City_Name', 'state'], inplace=True)
    acs_years_ny[i] = acs_years_ny[i].nlargest(5, 'Total_Population_{}'.format(x))
    i = i + 1


#American Community Survey Data for Idaho
i = 0
acs_years_id = []
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
                                   'B01003_001E',
                                   'B00002_001E',
                                   'B09018_007E',
                                   'B01002_001E'), states.ID.fips, '*', year=x)
    acs_years_id.append(pd.DataFrame.from_records(acs_test))
    print(x)
    acs_years_id[i] = acs_years_id[i].rename(columns={
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'B01003_001E': 'Total_Population_{}'.format(x),
        'B00002_001E': 'Total_Housing_{}'.format(x),
        'B09018_007E': 'Presence_of_Non-Relatives_{}'.format(x),
        'B01002_001E': 'Median_Age_{}'.format(x),
    })
    acs_years_id[i].set_index('FIPS', inplace=True)
    acs_years_id[i].drop(columns=['City_Name', 'state'], inplace=True)
    acs_years_id[i] = acs_years_id[i].nlargest(5, 'Total_Population_{}'.format(x))
    i = i + 1


#Greenhouse Gas Data
ghg = pd.DataFrame()

for f in os.listdir('data/2018_data_summary_spreadsheets'):
    temp = pd.read_excel('data/2018_data_summary_spreadsheets/'+f, sheet_name=0)
    temp['Year'] = f.split('.')[0].split('_')[2]    
    ghg = pd.concat([temp, ghg])
    
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


# Now that all of our data is loaded, we will work on putting it all together for analysis

# In[5]:


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


# ## Merge data and start analysis

# ### California

# In[6]:


city_2010 = c.sf1.state_place(keys, states.CA.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010.rename(columns=renames_2010)


# In[7]:


c_pop_2010_50000.head()


# In[8]:


city_2000 = c.sf1.state_place(keys, states.CA.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000.rename(columns=renames_2000)


# In[9]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[10]:


c_pop_2000_50000.head()


# In[11]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[12]:


ca_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')

ca_join = ca_join.join(pivot_em, on='FIPS')


# In[13]:


ca_join.head()


# In[14]:


ca_join['Total_Population_2000'] = ca_join['Total_Population_2000'].astype('i8')


# In[15]:


ca_join = ca_join.nlargest(5, 'Total_Population_2000')


# In[16]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2010']),
    go.Bar(name='2000_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2010_direct_emissions', x=ca_join['City_Name'], y=ca_join['2010']),
    go.Bar(name='2011_direct_emissions', x=ca_join['City_Name'], y=ca_join['2011']),
    go.Bar(name='2012_direct_emissions', x=ca_join['City_Name'], y=ca_join['2012']),
    go.Bar(name='2013_direct_emissions', x=ca_join['City_Name'], y=ca_join['2013']),
    go.Bar(name='2014_direct_emissions', x=ca_join['City_Name'], y=ca_join['2014']),
    go.Bar(name='2015_direct_emissions', x=ca_join['City_Name'], y=ca_join['2015']),
    go.Bar(name='2016_direct_emissions', x=ca_join['City_Name'], y=ca_join['2016']),
    go.Bar(name='2017_direct_emissions', x=ca_join['City_Name'], y=ca_join['2017']),
    go.Bar(name='2018_direct_emissions', x=ca_join['City_Name'], y=ca_join['2018'])
])
fig.update_layout(barmode='group')
fig.show()


# ## Get's the 5 largest cities in New York

# In[17]:


city_2010 = c.sf1.state_place(keys, states.NY.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010.rename(columns=renames_2010)


# In[18]:


c_pop_2010_50000.head()


# In[19]:


city_2000 = c.sf1.state_place(keys, states.NY.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000.rename(columns=renames_2000)


# In[20]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[21]:


c_pop_2000_50000.head()


# In[22]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[23]:


ny_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')
ny_join = ny_join.join(pivot_em, on='FIPS')


# In[24]:


ny_join.head()


# In[25]:


ny_join['Total_Population_2000'] = ny_join['Total_Population_2000'].astype('i8')


# In[26]:


ny_join = ny_join.nlargest(5, 'Total_Population_2000')


# In[27]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=ny_join['City_Name'], y=ny_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=ny_join['City_Name'], y=ny_join['Total_Population_2010']),
    go.Bar(name='2000_housing', x=ny_join['City_Name'], y=ny_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=ny_join['City_Name'], y=ny_join['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=ny_join['City_Name'], y=ny_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=ny_join['City_Name'], y=ny_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2010_direct_emissions', x=ca_join['City_Name'], y=ca_join['2010']),
    go.Bar(name='2011_direct_emissions', x=ca_join['City_Name'], y=ca_join['2011']),
    go.Bar(name='2012_direct_emissions', x=ca_join['City_Name'], y=ca_join['2012']),
    go.Bar(name='2013_direct_emissions', x=ca_join['City_Name'], y=ca_join['2013']),
    go.Bar(name='2014_direct_emissions', x=ca_join['City_Name'], y=ca_join['2014']),
    go.Bar(name='2015_direct_emissions', x=ca_join['City_Name'], y=ca_join['2015']),
    go.Bar(name='2016_direct_emissions', x=ca_join['City_Name'], y=ca_join['2016']),
    go.Bar(name='2017_direct_emissions', x=ca_join['City_Name'], y=ca_join['2017']),
    go.Bar(name='2018_direct_emissions', x=ca_join['City_Name'], y=ca_join['2018'])

])
fig.update_layout(barmode='group')
fig.show()


# ## Get's the 5 largest cities in Idaho

# In[28]:


city_2010 = c.sf1.state_place(keys, states.ID.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010.rename(columns=renames_2010)


# In[29]:


c_pop_2010_50000.head()


# In[30]:


city_2000 = c.sf1.state_place(keys, states.ID.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000.rename(columns=renames_2000)


# In[31]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[32]:


c_pop_2000_50000.head()


# In[33]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[34]:


id_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')
id_join = id_join.join(pivot_em, on='FIPS')


# In[35]:


id_join.head()


# In[36]:


id_join['Total_Population_2000'] = id_join['Total_Population_2000'].astype('i8')


# In[37]:


id_join =  id_join.nlargest(5, 'Total_Population_2000')


# In[38]:


id_join.head()


# In[39]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=id_join['City_Name'], y=id_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=id_join['City_Name'], y=id_join['Total_Population_2010']),
    go.Bar(name='2000_housing', x=id_join['City_Name'], y=id_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=id_join['City_Name'], y=id_join['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=id_join['City_Name'], y=id_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=id_join['City_Name'], y=id_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2010_direct_emissions', x=id_join['City_Name'], y=id_join['2010']),
    go.Bar(name='2011_direct_emissions', x=id_join['City_Name'], y=id_join['2011']),
    go.Bar(name='2012_direct_emissions', x=id_join['City_Name'], y=id_join['2012']),
    go.Bar(name='2013_direct_emissions', x=id_join['City_Name'], y=id_join['2013']),
    go.Bar(name='2014_direct_emissions', x=id_join['City_Name'], y=id_join['2014']),
    go.Bar(name='2015_direct_emissions', x=id_join['City_Name'], y=id_join['2015']),
    go.Bar(name='2016_direct_emissions', x=id_join['City_Name'], y=id_join['2016']),
    go.Bar(name='2017_direct_emissions', x=id_join['City_Name'], y=id_join['2017']),
    go.Bar(name='2018_direct_emissions', x=id_join['City_Name'], y=id_join['2018'])

])
fig.update_layout(barmode='group')
fig.show()


# In[56]:


three_state_df = pd.concat([id_join, ca_join, ny_join])


# In[57]:


three_state_df.reset_index(inplace=True)


# In[58]:


three_state_df.head()


# In[59]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
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


# * This graph is hard to gather any useful data from due to how New York City and Los Angeles are skewing the graph, let's drop those cities from the graph

# In[60]:


three_state_df.drop(three_state_df[three_state_df['City_Name'] =='Los Angeles city, California'].index, inplace = True)
three_state_df.drop(three_state_df[three_state_df['City_Name'] =='New York city, New York'].index, inplace = True)


# In[61]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
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


# * California is still being an issue, lets drop those cities form our graph

# In[62]:


three_state_df.drop(three_state_df[three_state_df['state'] ==states.CA.fips].index, inplace = True)


# In[63]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2000']),
    go.Bar(name='2010_pop', x=three_state_df['City_Name'], y=three_state_df['Total_Population_2010']),
    go.Bar(name='2000_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=three_state_df['City_Name'], y=three_state_df['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=three_state_df['City_Name'], y=three_state_df['Presence_of_Non-Relatives_2010']),
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


# In[64]:


fig = go.Figure(data=[
    go.Bar(name='2000_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2000']),
    go.Bar(name='2010_age', x=three_state_df['City_Name'], y=three_state_df['Median_Age_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# ## American Community Survey

# In[65]:


i = 0
three_state_acs = []
for x in acs_years_ca:
    acs_1 = pd.concat([acs_years_ca[i], acs_years_ny[i], acs_years_id[i]])
    three_state_acs.append(acs_1)
    i = i + 1


# In[66]:


three_state_df.set_index('FIPS', inplace=True)


# In[67]:


for x in three_state_acs:
    three_state_df = three_state_df.join(x, on="FIPS")


# In[68]:


three_state_df.head()


# In[69]:


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


# In[70]:


import statsmodels.api as sm
import statsmodels.formula.api as smf
import sklearn.metrics
import sys
from pandas_ml import ConfusionMatrix


# In[71]:


mod = smf.glm('Total_Population_2000 ~ Total_Population_2010 + Total_Population_2012 + Total_Population_2013', three_state_df, family=sm.families.Binomial()).fit()
mod.summary()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




