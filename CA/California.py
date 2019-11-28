#!/usr/bin/env python
# coding: utf-8

# # California -- City Sustainability

# In[2]:


get_ipython().run_line_magic('pip', 'install census us')


# In[3]:


import pandas as pd
import seaborn as sns
import matplotlib as plt

from census import Census
from us import states

import plotly.graph_objects as go


# In[4]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# ## Get's the 5 largest cities in California

# In[5]:


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


# In[6]:


c_pop_2010_50000.head()


# In[7]:


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


# In[8]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[9]:


c_pop_2000_50000.head()


# In[10]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[11]:


ca_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')


# In[12]:


ca_join.head()


# In[13]:


ca_join['Total_Population_2000'] = ca_join['Total_Population_2000'].astype('i8')


# In[14]:


ca_join = ca_join.nlargest(5, 'Total_Population_2000')


# In[15]:


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


# ## American Community Servey

# In[46]:


acs_years = {}
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
'B01003_001E',
'B00002_001E',
'B09018_007E'), states.CA.fips, '*', year=x)
    acs_years[x] = pd.DataFrame.from_records(acs_test)
    print(x)
    acs_years[x] = acs_years[x].rename(columns={
        'NAME' : 'City_Name',
        'place': 'FIPS',
        'B01003_001E': 'Total_Population_{}'.format(x),
        'B00002_001E': 'Total_Housing_{}'.format(x),
        'B09018_007E': 'Presence_of_Non-Relatives_{}'.format(x)})


# In[47]:


acs_years[2013].head()


# In[ ]:





# In[ ]:




