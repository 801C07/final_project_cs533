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


# In[3]:


c = Census('fb97753783c42ae57fe1a640e38fe04e921e5d1a')


# ### Get's the cities in Idaho that have a population greater than 50,000

# In[4]:


city_2010 = c.sf1.state_place(('NAME', 'P001001', 'H001001', 'P013001'), states.ID.fips, '*', year=2010)
c_pop_2010 = pd.DataFrame.from_records(city_2010)
c_pop_2010_50000 = c_pop_2010[c_pop_2010['P001001'].astype(int) >= 50000].rename(columns={'P001001': 'Total', 'H001001': 'Total Housing', 'P013001': 'Median Age'})


# In[5]:


c_pop_2010_50000


# In[6]:


city_2000 = c.sf1.state_place(('NAME', 'P001001', 'H001001', 'P013001'), states.ID.fips, '*', year=2000)
c_pop_2000 = pd.DataFrame.from_records(city_2000)
c_pop_2000_50000 = c_pop_2000[c_pop_2000['P001001'].astype(int) >= 30000].rename(columns={'P001001': 'Total', 'H001001': 'Total Housing', 'P013001': 'Median Age'})


# In[7]:


c_pop_2000_50000


# In[8]:


city_joined = pd.merge(c_pop_2000_50000, c_pop_2010_50000, on='place', suffixes=('2000','2010'))


# In[9]:


city_joined


# In[10]:


city_joined['Growth'] = city_joined['Total2010'].astype('float64') - city_joined['Total2000'].astype('float64')


# In[11]:


city_joined['RelativeGrowth'] = city_joined['Growth']/city_joined['Total2000'].astype('float64')


# In[12]:


city_joined['Housing Growth'] = city_joined['Total Housing2010'].astype('float64') - city_joined['Total Housing2000'].astype('float64')


# In[13]:


city_joined['Housing Relative Growth'] = city_joined['Housing Growth']/city_joined['Total Housing2000'].astype('float64')


# In[14]:


city_joined


# In[ ]:




