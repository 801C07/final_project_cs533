#!/usr/bin/env python
# coding: utf-8

# # California -- City Sustainability

# In[1]:


get_ipython().run_line_magic('pip', 'install census us')


# In[13]:


import pandas as pd
import seaborn as sns
import matplotlib as plt

from census import Census
from us import states


# In[22]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# ### Get's the cities in Idaho that have a population greater than 50,000

# In[46]:


city_2010 = c.sf1.state_place(('NAME', 'H001001', 
                               'P013001', 'P002002', 'P002005', 
                               'P013001', 'H003001', 'P027001', 
                               'H005001', 'H005002', 'H005003', 
                               'H005004', 'H005005', 'H005006', 
                               'H005007', 'P002001'), 
                              states.CA.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010[c_pop_2010['P002001'].astype(int) >= 50000].rename(columns={
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


# In[47]:


c_pop_2010_50000.head()


# In[51]:


city_2000 = c.sf1.state_place(('NAME', 'H001001', 
                               'P013001', 'P002002', 'P002005', 
                               'P013001', 'H003001', 'P027001', 
                               'H005001', 'H005002', 'H005003', 
                               'H005004', 'H005005', 'H005006', 
                               'H005007', 'P002001'), states.CA.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000[c_pop_2000['P002001'].astype(int) >= 30000].rename(columns={
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


# In[52]:


c_pop_2000_50000.drop(columns=['City_Name', 'state'], inplace=True)


# In[53]:


c_pop_2000_50000.head()


# In[54]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[55]:


city_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')


# In[56]:


city_join.head()


# In[58]:


city_join['Total_Population_2000'] = city_join['Total_Population_2000'].astype('i8')


# In[60]:


city_join = city_join.nlargest(5, 'Total_Population_2000')


# In[61]:


import plotly.graph_objects as go


# In[65]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=city_join['City_Name'], y=city_join['Total_Population_2000']),
    go.Bar(name='2000_housing', x=city_join['City_Name'], y=city_join['Total_Housing_2000']),
    go.Bar(name='2010_pop', x=city_join['City_Name'], y=city_join['Total_Population_2010']),
    go.Bar(name='2010_housing', x=city_join['City_Name'], y=city_join['Total_Housing_2010']),
    go.Bar(name='2000_urban_pop', x=city_join['City_Name'], y=city_join['Total_Urban_Population_2000']),
    go.Bar(name='2010_urban_pop', x=city_join['City_Name'], y=city_join['Total_Urban_Population_2010']),
    go.Bar(name='2000_rural_pop', x=city_join['City_Name'], y=city_join['Total_Rural_Population_2000']),
    go.Bar(name='2010_rural_pop', x=city_join['City_Name'], y=city_join['Total_Rural_Population_2010']),
    go.Bar(name='2000_median_age', x=city_join['City_Name'], y=city_join['Median_Age_2000']),
    go.Bar(name='2010_median_age', x=city_join['City_Name'], y=city_join['Median_Age_2010']),
    go.Bar(name='2000_occupancy_status', x=city_join['City_Name'], y=city_join['Occupancy_Status_For_Housing_Units_2000']),
    go.Bar(name='2010_occupancy_status', x=city_join['City_Name'], y=city_join['Occupancy_Status_For_Housing_Units_2010']),
    go.Bar(name='2000_non-relatives', x=city_join['City_Name'], y=city_join['Presence_of_Non-Relatives_2000']),
    go.Bar(name='2010_non-relatives', x=city_join['City_Name'], y=city_join['Presence_of_Non-Relatives_2010']),
    go.Bar(name='2000_vacancy_status', x=city_join['City_Name'], y=city_join['Vacancy_Status_2000']),
    go.Bar(name='2010_vacancy_status', x=city_join['City_Name'], y=city_join['Vacancy_Status_2010']),
    go.Bar(name='2000_for_rent', x=city_join['City_Name'], y=city_join['For_Rent_2000']),
    go.Bar(name='2010_for_rent', x=city_join['City_Name'], y=city_join['For_Rent_2010']),
    go.Bar(name='2000_rented_not_occupied', x=city_join['City_Name'], y=city_join['Rented_Not_Occupied_2000']),
    go.Bar(name='2010_rented_not_occupied', x=city_join['City_Name'], y=city_join['Rented_Not_Occupied_2010']),
    go.Bar(name='2000_for_sale', x=city_join['City_Name'], y=city_join['For_Sale_Only_2000']),
    go.Bar(name='2010_for_sale', x=city_join['City_Name'], y=city_join['For_Sale_Only_2010']),
    go.Bar(name='2000_sold_not_occupied', x=city_join['City_Name'], y=city_join['Sold_Not_Occupied_2000']),
    go.Bar(name='2010_sold_not_occupied', x=city_join['City_Name'], y=city_join['Sold_Not_Occupied_2010']),
    go.Bar(name='2000_seasonal_housing', x=city_join['City_Name'], y=city_join['For_Seasonal_Recreational_Or_Occasional_Use_2000']),
    go.Bar(name='2010_seasonal_housing', x=city_join['City_Name'], y=city_join['For_Seasonal_Recreational_Or_Occasional_Use_2010']),
    go.Bar(name='2000_migrant_housing', x=city_join['City_Name'], y=city_join['For_Migrant_Workers_2000']),
    go.Bar(name='2010_migrant_housing', x=city_join['City_Name'], y=city_join['For_Migrant_Workers_2010']),
])
fig.update_layout(barmode='group')
fig.show()


# In[ ]:


'H005002': 'For_Rent_2000',
'H005003': 'Rented_Not_Occupied_2000',
'H005004': 'For_Sale_Only_2000',
'H005005': 'Sold_Not_Occupied_2000',
'H005006': 'For_Seasonal_Recreational_Or_Occasional_Use_2000',
'H005007': 'For_Migrant_Workers_2000'


# In[ ]:





# In[ ]:




