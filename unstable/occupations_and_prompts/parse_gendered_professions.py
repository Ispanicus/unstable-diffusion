#!pip install pyarrow
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
def query():
    cache = 'gender_prof.parquet'

    if not Path(cache).exists():
        URL = 'https://www.bls.gov/cps/cpsaat11.htm'
        res = requests.get(URL)
        res.raise_for_status()

        # Replace classes (with implicit/unreadable indentation)
        # with explicit indentation class
        txt = re.sub('<p class="sub(\d)">', r'<p>\1', res.text)

        df, *rest = pd.read_html(txt, skiprows=2, attrs={'id': 'cps_eeann_emp_det_occu'})
        assert not rest

        # Cache as early as possible in preprocessing for flexibility
        df.to_parquet(cache) 

    return pd.read_parquet(cache)

def preprocessed():
    df = query()
    totals = df.columns.get_level_values(1)
    assert '0Total, 16 years and over' in totals

    # Discard blank line and totals
    df.columns = df.columns.get_level_values(0) 

    df = (
        df
        .iloc[:-1, :] # last row is a comment
        .replace('-', np.nan)
        .set_index('Occupation')
        .astype(float)
        .dropna()
        .sort_values('Women')
    )
    return df




df = preprocessed()
level_0 = df[df.Occupation.str.startswith('{0}')]
level_1 = df[df.Occupation.str.startswith('{1}')]
level_2 = df[df.Occupation.str.startswith('{2}')]
level_3 = df[df.Occupation.str.startswith('{3}')]

raw_occupations = df.Occupation.str.lstrip('01234').to_list()
with open('raw_occupations.txt', 'w') as f:
    f.write('\n'.join(map(str, raw_occupations)))

df.query('(Women < 0.2)')