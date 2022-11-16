import pandas as pd
from unstable.annotations.load_anno_df import get_annotation_df
import holoviews as hv
import hvplot.pandas
hv.extension('bokeh')

df = get_annotation_df()

annotation_ratios_per_prof = (
    df.groupby(["profession", "api"])
    ["annotation"]
    .value_counts(normalize=True)
)
ratios = annotation_ratios_per_prof

unstacked = ratios.unstack('annotation')
unstacked['m_f_ratio'] = unstacked.apply(lambda row: row.Male/row.Female, axis=1).fillna(float('inf'))
ratios_sorted = unstacked.sort_values('m_f_ratio').drop(columns='m_f_ratio').stack()

is_api = pd.IndexSlice[:, True, :]
not_api = pd.IndexSlice[:, False, :]

ratios_sorted.loc[is_api].rename('stable-diff').hvplot.bar(stacked=True).opts(xrotation=30)
ratios_sorted.loc[not_api].rename('laion').hvplot.bar(stacked=True).opts(xrotation=30)