#!/usr/bin/env python
# coding: utf-8

# # California -- City Sustainability

# In[47]:


import pandas as pd
import seaborn as sns
import matplotlib as plt
import os

from census import Census
from us import states

import plotly.graph_objects as go


# In[48]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# **Greenhouse Gas Data:**

# In[49]:


ghg = pd.DataFrame()

for f in os.listdir('../data/2018_data_summary_spreadsheets'):
    temp = pd.read_excel('../data/2018_data_summary_spreadsheets/'+f, sheet_name=0)
    temp['Year'] = f.split('.')[0].split('_')[2]    
    ghg = pd.concat([temp, ghg], sort=False)
    
fips_map = pd.read_excel('../data/fips-codes.xls', sheet_name=0)

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


# ## Get's the 5 largest cities in California

# In[50]:


city_2010 = c.sf1.state_place(('NAME', 'H001001', 
                               'P013001', 'P002002', 'P002005', 
                               'P013001', 'H003001', 'P027001', 
                               'H005001', 'H005002', 'H005003', 
                               'H005004', 'H005005', 'H005006', 
                               'H005007', 'P002001'), 
                              states.CA.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010.rename(columns={
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
        'H005007': 'For_Migrant_Workers_2010'})


# In[51]:


c_pop_2010_50000.head()


# In[52]:


city_2000 = c.sf1.state_place(('NAME', 'H001001', 
                               'P013001', 'P002002', 'P002005', 
                               'P013001', 'H003001', 'P027001', 
                               'H005001', 'H005002', 'H005003', 
                               'H005004', 'H005005', 'H005006', 
                               'H005007', 'P002001'), states.CA.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000.rename(columns={
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
        'H005007': 'For_Migrant_Workers_2000'})


# In[53]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[54]:


c_pop_2000_50000.head()


# In[55]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[56]:


ca_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')
ca_join = ca_join.join(pivot_em, on='FIPS')


# In[57]:


ca_join.head()


# In[58]:


ca_join['Total_Population_2000'] = ca_join['Total_Population_2000'].astype('i8')


# In[59]:


ca_join = ca_join.nlargest(5, 'Total_Population_2000')


# In[60]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2010']),
    go.Bar(name='2000_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# In[61]:


fig = go.Figure(data=[
    go.Bar(name='2000_age', x=ca_join['City_Name'], y=ca_join['Median_Age_2000']),
    go.Bar(name='2010_age', x=ca_join['City_Name'], y=ca_join['Median_Age_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# ## American Community Servey

# In[62]:


i = 0
acs_years = []
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
                                   'B01003_001E',
                                   'B00002_001E',
                                   'B09018_007E',
                                   'B01002_001E'), states.CA.fips, '*', year=x)
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


# In[63]:


for x in acs_years:
    ca_join = ca_join.join(x)


# In[64]:


ca_join.head()


# In[65]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2010']),
    go.Bar(name='2012_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2012']),
    go.Bar(name='2013_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2013']),
    go.Bar(name='2014_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2014']),
    go.Bar(name='2015_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2015']),
    go.Bar(name='2016_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2016']),
    go.Bar(name='2017_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2017']),
    go.Bar(name='2000_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2010']),
    go.Bar(name='2012_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2012']),
    go.Bar(name='2013_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2013']),
    go.Bar(name='2014_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2014']),
    go.Bar(name='2015_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2015']),
    go.Bar(name='2016_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2016']),
    go.Bar(name='2017_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2017']),
    go.Bar(name='2000_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2012_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2012']),
    go.Bar(name='2013_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2013']),
    go.Bar(name='2014_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2014']),
    go.Bar(name='2015_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2015']),
    go.Bar(name='2016_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2016']),
    go.Bar(name='2017_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2017']),
])
fig.update_layout(barmode='group')
fig.show()


# **Plot with emissions data**

# In[66]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2010']),
    go.Bar(name='2012_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2012']),
    go.Bar(name='2013_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2013']),
    go.Bar(name='2014_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2014']),
    go.Bar(name='2015_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2015']),
    go.Bar(name='2016_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2016']),
    go.Bar(name='2017_pop', x=ca_join['City_Name'], y=ca_join['Total_Population_2017']),
    go.Bar(name='2000_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2010']),
    go.Bar(name='2012_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2012']),
    go.Bar(name='2013_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2013']),
    go.Bar(name='2014_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2014']),
    go.Bar(name='2015_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2015']),
    go.Bar(name='2016_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2016']),
    go.Bar(name='2017_housing', x=ca_join['City_Name'], y=ca_join['Total_Housing_2017']),
    go.Bar(name='2000_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2012_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2012']),
    go.Bar(name='2013_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2013']),
    go.Bar(name='2014_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2014']),
    go.Bar(name='2015_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2015']),
    go.Bar(name='2016_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2016']),
    go.Bar(name='2017_non-relatives', x=ca_join['City_Name'], y=ca_join['Presence_of_Non-Relatives_2017']),
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

