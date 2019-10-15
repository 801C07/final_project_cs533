#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('pip', 'install census us')


# In[2]:


import pandas as pd
import seaborn as sns
from census import Census
from us import states


# In[3]:


c = Census('831eb41b7dd4c3fea0cf93ad2c796ac94cd9f5a0')


# In[4]:


type(c)


# In[13]:


id_pop = c.sf1.state(('NAME', 'P002001', 'P002002', 'P002005'), states.ID.fips)
id_pop


# In[8]:


ca_pop = c.sf1.state(('NAME', 'P002001', 'P002002', 'P002005'), states.CA.fips)
ca_pop


# In[15]:


import requests


# In[18]:


r = requests.get('https://api.census.gov/data/2018/acs/acs1?get=NAME,group(B01001)&for=us:1&key=831eb41b7dd4c3fea0cf93ad2c796ac94cd9f5a0')


# In[27]:


import json
acs = json.loads(r.text)


# In[28]:


type(acs)


# In[40]:


acs


# In[34]:


acs[1]


# In[37]:


df = pd.DataFrame(list(zip(acs[0], acs[1])))


# In[39]:


df.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




