import pandas as pd
from functools import lru_cache
from typing import List
import hvplot.pandas
from unstable.annotations.load_anno_df import get_majority_annotation_df, profession_index_to_gender_index, get_annotation_df
from tqdm import tqdm

def bootstrap_mean_female(series: pd.Series, iterations=1000) -> List[float]:
    means = [
        (
            series.sample(frac=1.00, replace=True) == 'Female'
        ).mean().squeeze()
        for _ in range(iterations)
    ]
    return means

@lru_cache # Only calculate bootstrap once
def get_bootstrap_df() -> pd.DataFrame:
    majority_df = get_majority_annotation_df()
    index = ['profession', 'api']
    series = majority_df.set_index(index)
    bootstraps = (
        series.groupby(index)
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

def get_credibility_bootstrapped():
    df = get_annotation_df()
    annotation_df = df.groupby(['filename','annotation']).count().unstack()['api'].stack()[lambda x: x >= 2].reset_index('annotation', drop=True).reset_index().drop_duplicates()
    annotation_df[0].sum()/(len(annotation_df))/4

    # bootstrapping
    creds = []

    for _ in tqdm(range(100)):
        bootstrap_df = (
            df.pivot(columns='annotator', index=['filename', 'api','profession'], values='annotation')
            .reset_index(['profession', 'api'], drop=True)
            .apply(lambda row: row.sample(frac=1, replace=True).values, axis=1)
            .apply(pd.Series)
        )
        annotation_df = (
            bootstrap_df
            .stack()
            .rename('annotation')
            .reset_index()
            .groupby(['filename','annotation'])
            .count()
            .stack()[lambda x: x >= 2]
            .reset_index(['annotation',None], drop=True)
            .reset_index()
            .drop_duplicates()
        )
        creds.append(annotation_df[0].sum()/(len(annotation_df))/4)

    pd.Series(creds).quantile([0.025,0.975])

if __name__ == '__main__':
    bootstraps = get_bootstrap_df()
    gender_bootstrap = get_gender_bootstrapped()

    # (lo < .5) & (.5 < hi)