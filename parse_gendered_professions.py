import pandas as pd
import numpy as np

renames = {'Unnamed: 0': 'Occupation',
           'Unnamed: 1': 'Total',
           'Black or\nAfrican\nAmerican': 'Black_or_aa',
           'Hispanic\nor Latino': 'Hispanic_or_latino'}
df = (
    pd.read_excel('cpsaat11.xlsx', skiprows=5)
    .rename(columns=renames)
    .replace('–', np.nan) # Note, shitty version of "-"
    .dropna() # We dont bother with partial data
    .sort_values('Women')
)
df['Men'] = 100-df['Women']