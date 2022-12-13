from unstable.occupations_and_prompts.parse_gendered_professions import get_female_work_percent, align_work_index, PLOT_ORDER
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
        conf.reset_index()
        .hvplot.errorbars('profession', 'center', 'width')
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
    order = [o.replace(' ', '_') if o.strip() else o for o in PLOT_ORDER]

    female_work_percent = get_female_work_percent().to_frame()
    female_work_percent.index = female_work_percent.index.str.replace(' ', '_')
    female_work_percent = female_work_percent.reindex(order)

    bootstrap = get_bootstrap_df()

    plots = []
    for is_api in [True, False]:
        boot = bootstrap.xs(is_api, level='api').reindex(order[::-1])
        cols = ['us_female_percent', 'color']
        a = pd.DataFrame([[.35, 'white']], index=[' '], columns=cols)
        b = pd.DataFrame([[.65, 'white']], index=['  '], columns=cols)
        scatter = (
            pd.concat(
                [female_work_percent.assign(color='#1f77b4'), a, b]
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
    h = 350
    title='Annotation confidence intervals \n& US labour data scatter'
    legend = pd.Series([.50], index=['artist CR']).hvplot.scatter(
        marker='dash', color='black'
    ).relabel('95% interval')
    plots[1] *= legend
    for p in plots:
        p.opts(
            xlabel='profession',
            invert_axes=True, width=400, height=h, legend_position='bottom',
            xformatter=percent_tick,
        )
    plots[0].opts(
        show_legend=False, xaxis=None, height=h-80, 
        title = title + '\nfor stable-diffusion (SD)')
    plots[1].opts(title='for clip-retrieval (CR)')
    hv.Layout(plots).cols(1)