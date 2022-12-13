from unstable.occupations_and_prompts.parse_gendered_professions import get_female_work_percent, align_work_index
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

    return (
        merge_multiindex(conf)
        .reset_index()
        .hvplot.errorbars('profession_source', 'center', 'width', legend=True)
        .opts(ylabel='Female %')
    )

def hypothesis_conf_plot():
    '''
    This is the nicest plot we have for this
    Includes
        Both gender and profession aggregation
        Confidence interval
        Labour stats points
        50% line
    '''
    female_work_percent = get_female_work_percent()

    boots = [
        get_bootstrap_df(),
        get_gender_bootstrapped()
    ]
    labours = [
        female_work_percent.pipe(
            align_work_index
        ),

        female_work_percent.pipe(
            profession_index_to_gender_index
        ).squeeze().pipe(
            align_work_index
        )
    ]
#.squeeze().sort_values().hvplot.scatter(),
    plots = []
    for boot, labour in zip(boots, labours):
        cols = ['us_female_percent', 'color']
        a = pd.DataFrame([[.35, 'white']], index=[''], columns=cols)
        b = pd.DataFrame([[.65, 'white']], index=[' '], columns=cols)
        scatter = (
            pd.concat(
                [labour.assign(color='#1f77b4'), a, b]
            )
            .rename_axis('source')
            .reset_index()
            .sort_values(['us_female_percent', 'source'])
            .hvplot.scatter(x='source', y='us_female_percent', color='color')
        )
        plots.append(
            hv.HLine(.5).opts(color='black', line_dash='dotted')
            *scatter.relabel('US labour statistics')
            *conf_interval_plot(boot)
        )
    return plots

# def kde():
#     bootstraps = merge_multiindex(get_bootstrap_df())
#     index = bootstraps.index.names
#     kde_plot = (
#         bootstraps
#         .stack()
#         .rename('female_mean')
#         .reset_index(index)
#         .hvplot.violin(by=index, y='female_mean')
#         #.opts(xrotation=45)
#     )
#     kde_plot
#     hv.Layout(kde_plot.values()).cols(1)

if __name__ == '__main__':
    plots = hypothesis_conf_plot()
    plots[0].opts(
        xlabel='profession & source',
        title='Annotation confidence intervals \n& US labour data scatter',
        invert_axes=True, width=400, height=400, legend_position='bottom')
    # plots[1].opts(
    #     xlabel='gender & source',
    #     invert_axes=True,
    #     width=400)
    
    legend = pd.Series([.50], index=['artist CR']).hvplot.scatter(
        marker='dash', color='black'
    ).relabel('95% interval')

    conf_plot = (plots[0]*legend).opts(
        xlabel='profession & source',
        title='Annotation confidence intervals \n& US labour data scatter',
        xformatter=percent_tick,
        invert_axes=True, width=400, height=500, legend_position='bottom'
    )
    conf_plot