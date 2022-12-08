from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
import numpy as np
import krippendorff as kd

from unstable.annotations.load_anno_df import get_annotation_df

df = get_annotation_df()

df_api, df_not_api = df.copy(), df.copy()
df_api = df_api[df_api["api"]==True]
df_not_api = df_not_api[df_not_api["api"]==False]

def pivot_clean_agg(df,verbose=False):
    pivot_df = (
        df.drop(columns='profession')
        .pivot(index='filename', columns='annotator', values=['annotation'])
    )
    pivot_df.columns = [author for annotation, author in pivot_df.columns]

    if verbose:
        print('Nulls per person')
        print(pivot_df.isnull().sum())

    clean_label_df = np.array(pivot_df.dropna())
    agg_df, gender_categories = aggregate_raters(clean_label_df)
    return agg_df, gender_categories

agg_df, _ = pivot_clean_agg(df,verbose=True)
agg_df_api, _ = pivot_clean_agg(df_api)    
agg_df_not_api, _ = pivot_clean_agg(df_not_api)
    
# https://en.wikipedia.org/wiki/Fleiss%27_kappa
print(f'Full data: {fleiss_kappa(agg_df) = }')
print(f'Api data: {fleiss_kappa(agg_df_api) = }')
print(f'Non-Api data: {fleiss_kappa(agg_df_not_api) = }')

# https://en.wikipedia.org/wiki/Krippendorff%27s_alpha
print(f"Krippendorff's alpha: {kd.alpha(value_counts=agg_df, level_of_measurement='nominal')}")

annotation_ratios_per_prof = (
    df.groupby(["profession", "api"])
    ["annotation"]
    .value_counts(normalize=True)
)
print(annotation_ratios_per_prof.head(6))

annotation_df = df.groupby(['filename','annotation']).count().unstack()['api'].stack()[lambda x: x >= 2].reset_index('annotation', drop=True).reset_index().drop_duplicates()

print(f'Credibility: {annotation_df[0].sum()/(len(annotation_df))/4}')

