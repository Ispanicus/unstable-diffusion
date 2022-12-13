import pandas as pd
from unstable.annotations.load_anno_df import get_annotation_df
from unstable.occupations_and_prompts.parse_gendered_professions import get_female_work_percent, align_work_index
import holoviews as hv
from unstable.meta_tools import percent_tick
import hvplot.pandas
hv.extension('bokeh')

female_work_percent = get_female_work_percent().to_frame().assign(color='black')
female_work_percent.index = female_work_percent.index.str.replace(' ', '_')
female_work_percent.loc[' ', :] = [.35, 'white']
female_work_percent.loc['  ', :] = [.65, 'white']

is_api = pd.IndexSlice[:, True, :]
not_api = pd.IndexSlice[:, False, :]
api_grouping = list(zip([is_api, not_api], ['stable-diff', 'laion']))

def get_annotation_ratios():
    df = get_annotation_df()

    annotation_ratios_per_prof = (
        df.groupby(["profession", "api"])
        ["annotation"]
        .value_counts(normalize=True)
        .rename('percentage')
    )
    ratios = annotation_ratios_per_prof

    return ratios.unstack('annotation')

def get_ratio_bars():
    unstacked = get_annotation_ratios()

    normalized = (
        unstacked.drop(columns='Pass')
        .apply(lambda x: x/x.sum(), axis=1)
        .sort_values('Male')
        .stack()
        .rename('percentage')
    )
    normalized = normalized.reindex(pd.MultiIndex.from_product(normalized.index.levels)).fillna(0)

    plots = []
    for api_mask, title in api_grouping:
        data = normalized.loc[api_mask]
        female = data.xs('Female', axis=0, level=1, drop_level=True).rename('female')
        male = (female / female).fillna(1).rename('male')
        all_df = pd.concat(
            [male, female, female_work_percent],
            axis=1
        ).sort_values('us_female_percent')
        all_df
        trimmed = {} if title == 'laion' else {'xaxis': None, 'show_legend': False, 'height': 200}
        plots.append(
            (
                all_df.hvplot.bar(x='profession', y='male').relabel('M')
                * all_df.hvplot.bar(x='profession', y='female').relabel('F')
                * all_df.hvplot.scatter(x='profession', y='us_female_percent', color='color').relabel('US')
                * hv.HLine(.5).opts(color='black', line_dash='dashed')
            ).opts(title=title, ylabel='Female %', xformatter=percent_tick, invert_axes=True, width=300, legend_position='bottom', **trimmed)
        )
    return hv.Layout(plots).cols(1)


def get_pass_bars():
    unstacked = get_annotation_ratios()

    plots = []
    for api_mask, title in api_grouping:
        pass_percent = (
            unstacked.apply(lambda x: x/x.sum(), axis=1)
            .stack()
            .rename('percent')
            .loc[api_mask]
            .xs('Pass', level='annotation')
        )
        # df = pass_percent.sort_values().to_frame().assign(x=[0, -.5, .5, -.5, .5, 0, 0, -.5, .5, 0, 0, 0])
        # points = df.hvplot.points(x='x', y='percent', by='profession', color='black', marker = 'plus')
        # labels = hv.Labels({('y', 'x'): df, 'text': df.index}, ['x', 'y'], 'text')
        # (points*labels).opts(hv.opts.Labels(yoffset=0.01)).opts(xaxis=None, xlim=(-1, 1.5), show_legend=False, ylabel='% pass', yformatter=percent_tick, width=270)

        trimmed = {'height': 250} if title == 'laion' else {'xaxis': None, 'show_legend': False, 'height': 200}
        df = female_work_percent.merge(pass_percent, on='profession', how='outer').fillna(0)
        plot = df.sort_values('us_female_percent').hvplot.bar(
            y='percent', color='color'
        ).opts(
            invert_axes=True,
            line_width=0,
            width=300,
            xformatter=percent_tick,
            ylabel='% labels marked "Pass"',
            title = title,
            **trimmed
        )
        plots.append(plot)
    return hv.Layout(plots).cols(1)

if __name__ == '__main__':
    ratio_plot = get_ratio_bars()
    pass_plot = get_pass_bars()
