#!/usr/bin/env python
# coding: utf-8

# # California -- City Sustainability

# In[50]:


get_ipython().run_line_magic('pip', 'install census us')


# In[64]:


import pandas as pd
import seaborn as sns
import matplotlib as plt

from census import Census
from us import states


# In[65]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# ### Get's the cities in Idaho that have a population greater than 50,000

# In[66]:


city_2010 = c.sf1.state_place(('NAME', 'P001001', 'H001001', 'P013001'), states.CA.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010[c_pop_2010['P001001'].astype(int) >= 50000].rename(columns={'P001001': 'Total_2010', 'place': 'FIPS', 'H001001': 'Total_Housing_2010', 'P013001': 'Median_Age_2010'})


# In[67]:


c_pop_2010_50000.head()


# In[68]:


city_2000 = c.sf1.state_place(('NAME', 'P001001', 'H001001', 'P013001'), states.CA.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000[c_pop_2000['P001001'].astype(int) >= 30000].rename(columns={'P001001': 'Total_2000', 'place': 'FIPS', 'H001001': 'Total_Housing_2000', 'P013001': 'Median_Age_2000'})


# In[70]:


c_pop_2000_50000.drop(columns=['NAME', 'state'], inplace=True)


# In[71]:


c_pop_2000_50000.head()


# In[72]:


c_pop_2000_50000.set_index('FIPS', inplace=True)
c_pop_2010_50000.set_index('FIPS', inplace=True)


# In[73]:


city_join = c_pop_2000_50000.join(c_pop_2010_50000, on='FIPS')


# In[74]:


city_join.head()


# In[96]:


city_join['Total_2000'] = city_join['Total_2000'].astype('i8')


# In[98]:


city_join = city_join.nlargest(5, 'Total_2000')


# In[99]:


import plotly.graph_objects as go


# In[100]:


fig = go.Figure(data=[
    go.Bar(name='2000_pop', x=city_join['NAME'], y=city_join['Total_2000']),
    go.Bar(name='2000_housing', x=city_join['NAME'], y=city_join['Total_Housing_2000']),
    go.Bar(name='2010_pop', x=city_join['NAME'], y=city_join['Total_2010']),
    go.Bar(name='2010_housing', x=city_join['NAME'], y=city_join['Total_Housing_2010'])
])
fig.update_layout(barmode='group')
fig.show()


# In[ ]:





# In[ ]:





# In[ ]:




