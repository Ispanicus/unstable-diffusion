import pandas as pd
from functools import lru_cache
from typing import List
import hvplot.pandas
from unstable.annotations.load_anno_df import get_majority_annotation_df
from unstable.occupations_and_prompts.parse_gendered_professions import preprocessed

def bootstrap_mean_male(series: pd.Series, iterations=1000) -> List[float]:
    means = [
        (
            series.sample(frac=1.00, replace=True) == 'Male'
        ).mean().squeeze()
        for _ in range(iterations)
    ]
    return means

@lru_cache # Only calculate bootstrap once
def bootstrap() -> pd.DataFrame:
    majority_df = get_majority_annotation_df()
    index = ['profession', 'api']
    series = majority_df.set_index(index)
    bootstraps = (
        series.groupby(index)
        .apply(bootstrap_mean_male)
        .apply(pd.Series)
    )
    return bootstraps

def boxplot():
    bootstraps = bootstrap()
    index = bootstraps.index.names
    df = bootstraps.reset_index()
    df.profession = df.profession.str.replace('_', '\n')
    plot = (
        df.set_index(index)
        .stack()
        .rename('male_mean')
        .hvplot.box(y='male_mean', by=index)
        .opts(xrotation=45)
    )
    return plot

def conf_intervals():
    bootstraps = bootstrap()
    bootstraps
    conf = bootstraps.quantile([.025, .975], axis=1)
    return conf

if __name__ == '__main__':
    conf = conf_intervals()
    conf
    lo = conf.loc[0.025]
    hi = conf.loc[0.975]
    (lo < .5) & (.5 < hi)

    df = preprocessed()
    df