# Maybe we wont use this? Too messy
import holoviews as hv
from unstable.meta_tools import percent_tick
import hvplot.pandas
from unstable.occupations_and_prompts.parse_gendered_professions import get_female_work_percent
from unstable.statistics.bootstrap import get_gender_bootstrapped, get_bootstrap_df
from unstable.annotations.load_anno_df import profession_index_to_gender_index

def create_gender_aggregated_boxplot():
    female_work_percent = get_female_work_percent().pipe(
        profession_index_to_gender_index
    )
    scatter = female_work_percent.hvplot.scatter().opts(jitter=.2)

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
