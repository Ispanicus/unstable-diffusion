import pandas as pd
import requests
import re
import numpy as np
from pathlib import Path
from unstable.meta_tools import get_path

SPECIFIC_OCCUPATIONS = {
    'secretary': 'Secretaries and administrative assistants, except legal, medical, and executive',
    'maid': 'Maids and housekeeping cleaners',
    'nurse': 'Registered nurses',
    'social worker': 'Social workers, all other',
    'artist': 'Artists and related workers',
    'professor': 'Postsecondary teachers',
    'photographer': 'Photographers',
    'manager': 'Management occupations',
    'software developer': 'Software developers',
    'police officer': 'Police officers',
    'carpenter': 'Carpenters',
    'electrician': 'Electricians',
}

def query():
    cache = get_path('data/gender_prof.parquet')

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

def preprocessed(include_layer_information=False):
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
    if not include_layer_information:
        df.index = df.index.str.strip('0123')
    return df

def get_female_work_percent():
    occupation_df = preprocessed()
    occupation_df.index = occupation_df.index.map(
        {full: prompt for prompt, full in SPECIFIC_OCCUPATIONS.items()}
    )
    female_work_percent = (
        occupation_df[occupation_df.index.notnull()]
        .rename_axis(index={'Occupation': 'profession'})
        .Women
        .rename('us_female_percent') / 100
    )
    return female_work_percent



if __name__ == '__main__':
    df = preprocessed()

    # raw_occupations = df.Occupation.str.lstrip('01234').to_list()
    # with open(get_path('data/raw_occupations.txt'), 'w') as f:
    #     f.write('\n'.join(map(str, raw_occupations)))

    
    occs = SPECIFIC_OCCUPATIONS.values()
    assert 4 == len(df.query('0  < Women < 20')[lambda df: df.index.isin(occs)])
    assert 4 == len(df.query('40 < Women < 60')[lambda df: df.index.isin(occs)])
    assert 4 == len(df.query('80 < Women <100')[lambda df: df.index.isin(occs)])