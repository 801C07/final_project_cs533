#!/usr/bin/env python
# coding: utf-8

# # Idaho -- City Sustainability

# In[1]:


get_ipython().run_line_magic('pip', 'install census us')


# In[2]:


import pandas as pd
import seaborn as sns
import matplotlib as plt

from census import Census
from us import states

import plotly.graph_objects as go


# In[3]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# ## Get's the 5 largest cities in Idaho

# In[4]:


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
        'P002002': 'Total_Urban_Population_2010',
        'P002005': 'Total_Rural_Population_2010',
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

city_2010 = c.sf1.state_place(keys, states.ID.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010.rename(columns=renames_2010)


# In[5]:


c_pop_2010_50000.head()


# In[6]:


city_2000 = c.sf1.state_place(keys, states.ID.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000.rename(columns=renames_2000)


# In[7]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[8]:


c_pop_2000_50000.head()


# In[9]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[10]:


id_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')


# In[11]:


id_join.head()


# In[12]:


id_join['Total_Population_2000'] = id_join['Total_Population_2000'].astype('i8')


# In[13]:


id_join =  id_join.nlargest(5, 'Total_Population_2000')


# In[14]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=id_join['City_Name'], y=id_join['Total_Population_2000']),
    go.Bar(name='2010_pop', x=id_join['City_Name'], y=id_join['Total_Population_2010']),
    go.Bar(name='2000_housing', x=id_join['City_Name'], y=id_join['Total_Housing_2000']),
    go.Bar(name='2010_housing', x=id_join['City_Name'], y=id_join['Total_Housing_2010']),
    go.Bar(name='2000_non-relatives', x=id_join['City_Name'], y=id_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=id_join['City_Name'], y=id_join['Presence_of_Non-Relatives_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# In[15]:


fig = go.Figure(data=[
    go.Bar(name='2000_age', x=id_join['City_Name'], y=id_join['Median_Age_2000']),
    go.Bar(name='2010_age', x=id_join['City_Name'], y=id_join['Median_Age_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# ## American Community Servey

# In[16]:


i = 0
acs_years = []
for x in range(2012, 2018):
    acs_test = c.acs5.state_place(('NAME',
                                   'B01003_001E',
                                   'B00002_001E',
                                   'B09018_007E',
                                   'B01002_001E'), states.ID.fips, '*', year=x)
    acs_years.append(pd.DataFrame.from_records(acs_test))
    print(x)
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


# In[17]:


for x in acs_years:
    id_join = id_join.join(x)


# In[18]:


id_join.head()


# In[ ]:





# In[ ]:




