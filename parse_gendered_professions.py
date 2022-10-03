import pandas as pd
import requests
import re
import numpy as np
from pathlib import Path

# df = (
#     pd.read_excel('cpsaat11.xlsx', skiprows=5)
#     .rename(columns=renames)
#     .replace('–', np.nan) # Note, shitty version of "-"
#     .dropna() # We dont bother with partial data
#     .sort_values('Women')
# )
# df['Men'] = 100-df['Women']
if not Path('gender_prof.parquet').exists():
    URL = 'https://www.bls.gov/cps/cpsaat11.htm'
    res = requests.get(URL)
    res.raise_for_status()

    # For some reason, we get 2 duplicate dfs
    txt = re.sub('<p class="sub(\d)">', r'<p>{\1}', res.text)

    df, *rest = pd.read_html(txt, skiprows=2, attrs={'id': 'cps_eeann_emp_det_occu'})
    assert not rest
    # Cache as early as possible for flexibility
    df.to_parquet('gender_prof.parquet') 

df = pd.read_parquet('gender_prof.parquet')

totals = df.columns.get_level_values(1)
assert '{0}Total, 16 years and over' in totals

# Discard blank line and totals
df.columns = df.columns.get_level_values(0) 

df = (
    df.replace('-', np.nan)
    .dropna()
    .sort_values('Women')
    .iloc[:-1, :] # last row is a comment
)

level_0 = df[df.Occupation.str.startswith('{0}')]
level_1 = df[df.Occupation.str.startswith('{1}')]
level_2 = df[df.Occupation.str.startswith('{2}')]
level_3 = df[df.Occupation.str.startswith('{3}')]