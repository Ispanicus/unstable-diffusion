import pandas as pd
from unstable.annotations.load_anno_df import get_annotation_df
import holoviews as hv
import hvplot.pandas
from bokeh.models import NumeralTickFormatter
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

yticks = NumeralTickFormatter(format='0 %')

plots = []
for mask, title in zip([is_api, not_api], ['stable-diff', 'laion']):
    data = normalized.loc[mask]
    male = data.xs('Male', axis=0, level=1, drop_level=False).rename('male')
    female_background = (male / male).rename('female')
    plots.append(
        (
            female_background.hvplot.bar(stacked=True).opts(xrotation=30, yformatter=yticks, show_grid=True, color='orange')
            * male.hvplot.bar(stacked=True)
            * unstacked.Pass.rename('Skip %').loc[mask].hvplot.scatter(c='black')
            * hv.HLine(.5).opts(color='gray')
        ).opts(title=title)
    )
hv.Layout(plots).cols(1)