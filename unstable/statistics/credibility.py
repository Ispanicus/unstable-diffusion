import pandas as pd
from unstable.annotations.load_anno_df import get_majority_annotation_df, get_annotation_df

def get_credibility_bootstrapped_conf_interval():
    gold_label = get_majority_annotation_df(drop_ties=False).index

    n_bootstraps = 1000
    def bootstrap(row):
        return pd.Series(row.sample(frac=n_bootstraps, replace=True).values)

    bootstraps_df = (
        get_annotation_df().pivot(
            columns='annotator',
            index='filename',
            values='annotation'
        )
        .apply(bootstrap, axis=1)
    )
    bootstraps_df.columns = (bootstraps_df.columns//4).rename('n_boot')

    counts = (
        bootstraps_df.stack()
        .groupby(['filename', 'n_boot'])
        .value_counts()
        .rename_axis(index={None: 'annotation'})
    )
    # We assume gold label is our "majority" vote (can be tied)
    correct = counts.reset_index('n_boot').loc[gold_label]#.set_index('n_boot', append=True)
    creds = correct.groupby('n_boot').mean() / 4
    return creds.quantile([0.025, 0.975])


def get_credibility():
    n_agree = get_majority_annotation_df(drop_ties=False)
    return n_agree.mean() / 4
