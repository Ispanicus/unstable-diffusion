import pandas as pd
from functools import lru_cache
import holoviews as hv
from unstable.meta_tools import percent_tick
from typing import List
import hvplot.pandas
from unstable.occupations_and_prompts.prompter import get_gender_occupations
from unstable.annotations.load_anno_df import get_majority_annotation_df
from unstable.occupations_and_prompts.parse_gendered_professions import preprocessed, SPECIFIC_OCCUPATIONS

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

def boxplot():
    bootstraps = get_bootstrap_df()
    index = bootstraps.index.names
    df = bootstraps.reset_index()
    df.profession = df.profession.str.replace('_', '\n')
    plot = (
        df.set_index(index)
        .stack()
        .rename('female_mean')
        .hvplot.box(y='female_mean', by=index)
        .opts(xrotation=45)
    )
    return plot

def conf_intervals():
    bootstraps = get_bootstrap_df()
    conf = bootstraps.quantile([.025, .975], axis=1)
    conf.index = conf.index.astype(str)
    return conf.T

def profession_index_to_gender_index(df):
    gender_occ = get_gender_occupations()
    occ_to_gender = {
        prof: gender 
        for gender, prof_list in gender_occ.items() 
        for prof in prof_list
    }

    index_w_o_prof = [c for c in df.index.names if c != 'profession']
    profession = df.index.get_level_values('profession')
    with_gender_index = (
        df.reset_index()
        .assign(
            gender=profession.str.replace('_', ' ').map(occ_to_gender)
        ).drop(columns='profession')
        .set_index(index_w_o_prof + ['gender'])
    )
    return with_gender_index


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

def create_gender_aggregated_boxplot():
    occupation_df = preprocessed()
    occupation_df.index = occupation_df.index.map(
        {full: prompt for prompt, full in SPECIFIC_OCCUPATIONS.items()}
    )
    gender_group_woman_percent = (
        occupation_df[occupation_df.index.notnull()]
        .rename_axis(index={'Occupation': 'profession'})
        .pipe(profession_index_to_gender_index)
        .Women
        .rename('us_female_percent') / 100
    )
    scatter = gender_group_woman_percent.hvplot.scatter().opts(jitter=.2)

    gender_bootstrap = get_gender_bootstrapped()
    # This creates a single composite/nice plot, but it doesnt allow overlaying a scatter
    # boxplots = gender_bootstrap.stack().hvplot.box(by=['gender', 'api']).opts(show_legend=False)
    boxplots = [
        df.hvplot.box(y='percent', by='gender').opts(
            title = 'Stable-diffusion' if is_api else 'LAION',
            show_legend=False,
            yformatter=percent_tick
        )*scatter.opts(color='orange')
        *hv.HLine(.5).opts(color='black', line_dash='dotted', show_legend=False)
        for is_api, df in gender_bootstrap.stack().rename('percent').groupby('api')
    ]
    return hv.Layout(boxplots).cols(1)

if __name__ == '__main__':
    conf = conf_intervals()
    lo = conf['0.025']
    hi = conf['0.975']
    (lo < .5) & (.5 < hi)

    create_gender_aggregated_boxplot()