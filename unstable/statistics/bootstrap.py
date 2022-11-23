import pandas as pd
import numpy as np
from functools import lru_cache
from typing import List
import hvplot.pandas
from unstable.annotations.load_anno_df import expand_filename, get_majority_annotation_df, profession_index_to_gender_index, get_annotation_df

def bootstrap_mean_female(series: pd.Series, iterations=1000) -> List[float]:
    np.random.seed(0)
    means = [
        (
            series.sample(frac=1.00, replace=True) == 'Female'
        ).mean().squeeze()
        for _ in range(iterations)
    ]
    return means

@lru_cache # Only calculate bootstrap once
def get_bootstrap_df() -> pd.DataFrame:
    df = get_majority_annotation_df()
    index = ['profession', 'api']
    bootstraps = (
        expand_filename(df.reset_index())
        .set_index(index)['annotation']
        .groupby(['profession', 'api'])
        .apply(bootstrap_mean_female)
        .apply(pd.Series)
    )
    return bootstraps

def get_gender_bootstrapped():
    bootstraps = get_bootstrap_df()
    gender_indexed = profession_index_to_gender_index(bootstraps)

    gender_bootstrap = (
        gender_indexed.groupby(['gender', 'api'])
        .apply(
            lambda group: 
            pd.Series(
                group.to_numpy().flatten(), 
                name=group.name
            )
        )
    )
    return gender_bootstrap

if __name__ == '__main__':
    bootstraps = get_bootstrap_df()
    gender_bootstrap = get_gender_bootstrapped()

    # (lo < .5) & (.5 < hi)