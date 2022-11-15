from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
import numpy as np

from unstable.annotations.load_anno_df import get_annotation_df

df = get_annotation_df()

pivot_df = (
    df.drop(columns='profession')
    .pivot(index='filename', columns='annotator', values=['annotation'])
)
pivot_df.columns = [author for annotation, author in pivot_df.columns]

print('Nulls per person')
print(pivot_df.isnull().sum())

clean_label_df = np.array(pivot_df.dropna())
agg_df, gender_categories = aggregate_raters(clean_label_df)

# https://en.wikipedia.org/wiki/Fleiss%27_kappa
print(f'{fleiss_kappa(agg_df) = }')

annotation_ratios_per_prof = (
    df.groupby(["profession", "api"])
    ["annotation"]
    .value_counts(normalize=True)
)
print(annotation_ratios_per_prof.head(6))