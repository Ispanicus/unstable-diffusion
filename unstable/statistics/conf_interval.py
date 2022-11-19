from unstable.occupations_and_prompts.parse_gendered_professions import get_female_work_percent
import pandas as pd
import holoviews as hv
from unstable.meta_tools import percent_tick
import hvplot.pandas
from unstable.annotations.load_anno_df import merge_multiindex, profession_index_to_gender_index
from unstable.statistics.bootstrap import get_bootstrap_df, get_gender_bootstrapped
import holoviews as hv
from unstable.meta_tools import percent_tick

def conf_intervals(bootstraps):
    conf = bootstraps.quantile([.025, .975], axis=1)
    conf.index = conf.index.astype(str)
    return conf.T

def conf_interval_plot(bootstraps):
    conf = conf_intervals(bootstraps)
    conf['center'] = conf.mean(axis=1)
    conf['width'] = conf.center - conf['0.025']

    ylabel = 'Female percentage'
    return (
        merge_multiindex(conf)
        .reset_index()
        .hvplot.errorbars('profession_source', 'center', 'width')
        .opts(xrotation=30, ylabel=ylabel, yformatter=percent_tick)
    )

def align_work_index(female_work_percentage):
    df = female_work_percentage.to_frame()
    df.index = df.index.str.replace(' ', '_')
    return pd.concat([
        df.set_index(df.index + ' SD'),
        df.set_index(df.index + ' CR')
    ])

def hypothesis_conf_plot():
    '''
    This is the nicest plot we have for this
    Includes
        Both gender and profession aggregation
        Confidence interval
        Labour stats points
        50% line
    '''

if __name__ == '__main__':
    female_work_percent = get_female_work_percent()

    boots = [
        get_bootstrap_df(),
        get_gender_bootstrapped()
    ]
    jitters = [
        female_work_percent.pipe(
            align_work_index
        ).hvplot.scatter(),

        female_work_percent.pipe(
            profession_index_to_gender_index
        ).squeeze().pipe(
            align_work_index
        ).hvplot.scatter().opts(jitter=.2),
    ]
    plots = []
    for boot, jitter in zip(boots, jitters):
        plots.append(
            conf_interval_plot(boot)
            *jitter
            *hv.HLine(.5).opts(color='black', line_dash='dotted')
        )
    plots[0].opts(xlabel='profession & source', title='Image label confidence intervals vs Labour data scatter')
    plots[1].opts(xlabel='gender & source')
    hv.Layout(plots).cols(1).opts(shared_axes=False)