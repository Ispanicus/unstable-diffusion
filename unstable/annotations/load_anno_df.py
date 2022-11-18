import json
import pandas as pd
import re

from unstable.meta_tools import get_path

def load(name):
    path = get_path(f"/data/annotations/{name}.json")

    with open(path, "r") as f:
        return json.load(f)

def get_annotation_df():
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

    return pd.DataFrame(data_list,columns=["filename","api","profession","annotator","annotation"])

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

def get_majority_annotation_df():
    df = get_annotation_df()
    majority_df = (
        df.groupby(['filename', 'annotation'])
        .count()
        .iloc[:, 0]
        .rename('count')
        [lambda x: x >= 3]
        .reset_index()
        .pipe(expand_filename)
    )
    formatted_df = majority_df.set_index('filename')[['profession', 'api', 'annotation']]
    return formatted_df


if __name__ == '__main__':
    df = get_annotation_df()
    majority_df = get_majority_annotation_df()

    print(df.sample(3))
    print(majority_df.sample(3))