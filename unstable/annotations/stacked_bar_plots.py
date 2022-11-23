import pandas as pd
from unstable.annotations.load_anno_df import get_annotation_df
import holoviews as hv
from unstable.meta_tools import percent_tick
import hvplot.pandas
hv.extension('bokeh')

df = get_annotation_df()

annotation_ratios_per_prof = (
    df.groupby(["profession", "api"])
    ["annotation"]
    .value_counts(normalize=True)
    .rename('percentage')
)
ratios = annotation_ratios_per_prof

unstacked = ratios.unstack('annotation')
normalized = (
    unstacked.drop(columns='Pass')
    .apply(lambda x: x/x.sum(), axis=1)
    .sort_values('Male')
    .stack()
    .rename('percentage')
)

is_api = pd.IndexSlice[:, True, :]
not_api = pd.IndexSlice[:, False, :]

plots = []
for mask, title in zip([is_api, not_api], ['stable-diff', 'laion']):
    data = normalized.loc[mask]
    male = data.xs('Male', axis=0, level=1, drop_level=False).rename('male')
    female_background = (male / male).rename('female')
    trimmed = {} if title == 'laion' else {'xaxis': None, 'show_legend': False, 'height': 200}
    plots.append(
        (
            female_background.hvplot.bar(stacked=True).opts(xformatter=percent_tick, show_grid=True, color='orange')
            * male.hvplot.bar(stacked=True)
            * unstacked.Pass.rename('Skip %').loc[mask].hvplot.scatter(c='black')
            * hv.HLine(.5).opts(color='gray')
        ).opts(title=title, invert_axes=True, width=300, legend_position='bottom', **trimmed)
    )
hv.Layout(plots).cols(1)
