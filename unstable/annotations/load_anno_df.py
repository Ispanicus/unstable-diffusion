import json
import pandas as pd
import re
from unstable.occupations_and_prompts.prompter import get_gender_occupations
from unstable.meta_tools import get_path

def load(name):
    path = get_path(f"data/annotations/{name}.json")

    with open(path, "r") as f:
        return json.load(f)

def get_annotation_df(dropna=True):
    """Returns all annotation data in pandas dataframe

    Returns:
        df: columns=["filename","api","profession","annotator","annotation"]
    """
    data_list =[]
    skips = 0
    names = ["johan","chris","karl","alan"]
    for name in names:
        data = load(name)
        for annotation in data:
            filename = annotation["file_upload"].split("-")[1]

            match = re.match(r"(api_)?(.*)_\d+.jpg",filename)
            groups = match.groups()

            is_api = bool(groups[0])
            profession = groups[1]
            try:
                annotation["annotations"][0]["result"][0]["value"]["choices"][0]
            except IndexError as e:
                skips += 1
                continue
            data_list.append([filename,
                            is_api,
                            profession,
                            name,
                            annotation["annotations"][0]["result"][0]["value"]["choices"][0]])
    df = pd.DataFrame(data_list,columns=["filename","api","profession","annotator","annotation"])
    if dropna:
        df = df.pivot(
            columns='annotator',
            index=['filename', 'api','profession'],
            values='annotation'
        ).dropna().stack().rename('annotation').reset_index()
    return df

def get_krippendorff_df():
    df = get_annotation_df()
    vals = (
        df.pivot(columns='annotator',
                 index='filename',
                 values='annotation'
        )
        .stack()
        .map({'Male': 0, 'Female': 1, 'Pass': 2})
        .unstack()
        .values
    )
    return vals

def expand_filename(df):
    split = (
        df.filename
        .str.split(
            r"(api_)?(.*)_\d+.jpg", regex=True, expand=True
        )[[1, 2]]
        .rename(columns={1: 'api', 2: 'profession'})
        .astype({'api': bool})
    )
    return pd.concat([df, split], axis=1)

def get_majority_annotation_df(drop_ties=True):
    df = get_annotation_df()
    counts = (
        df.pivot(columns='annotator',
                 index='filename',
                 values='annotation')
        .stack()
        .groupby(['filename'])
        .value_counts()
        .rename_axis(index={None: 'annotation'})
    )
    if drop_ties:
        tie_filenames = (
            counts.groupby('filename')
            .filter(lambda x: (x==2).all())
            .index
        )
        counts = counts[~counts.index.isin(tie_filenames)]
    majority = counts.groupby(['filename']).idxmax()
    return counts[majority].rename('n_agree')

def merge_multiindex(df):
    '''
    Index transformation.
    Turns ('nurse', True) -> "nurse SD" 
    '''
    return df.set_index(
        df.index
        .to_frame()
        .astype(str)
        .apply(' '.join, axis=1)
        .str.replace('True', 'SD')
        .str.replace('False', 'CR')
        .rename('profession_source')
    )

def profession_index_to_gender_index(df):
    ''' 
    Index transformation
    Turns 'nurse' -> 'female'
    '''
    gender_occ = get_gender_occupations()
    occ_to_gender = {
        prof: gender 
        for gender, prof_list in gender_occ.items() 
        for prof in prof_list
    }

    index_w_o_prof = [c for c in df.index.names if c != 'profession']
    profession = df.index.get_level_values('profession')
    with_gender_index = (
        df.reset_index()
        .assign(
            gender=profession.str.replace('_', ' ').map(occ_to_gender)
        ).drop(columns='profession')
        .set_index(index_w_o_prof + ['gender'])
    )
    return with_gender_index


if __name__ == '__main__':
    df = get_annotation_df()
    majority_df = get_majority_annotation_df()

    print(df.sample(3))
    print(majority_df.sample(3))