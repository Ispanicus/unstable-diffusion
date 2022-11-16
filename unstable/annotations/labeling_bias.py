from tqdm import tqdm
import os

from unstable.annotations.load_anno_df import get_annotation_df
from unstable.meta_tools import get_path


df = get_annotation_df()
female_count, male_count, mixed_count_pass,mixed_count, pass_count, pure_count = 0,0,0,0,0,0
mixed_dict = dict()
for val in tqdm(df["filename"].unique()):
    df_cut = df[df["filename"]==val]
    df_cut_val = df_cut["annotation"].unique()
    if "Pass" in df_cut_val:
        if "Male" in df_cut_val and "Female" in df_cut_val:
            mixed_count_pass += 1
        elif "Male" in df_cut_val:
            male_count += 1
        elif "Female" in df_cut_val:
            female_count += 1
        else:
            pass_count += 1
    elif "Male" in df_cut_val and "Female" in df_cut_val:
        mixed_dict[mixed_count]= {"filename":df_cut["filename"].unique()[0]}
        mixed_dict[mixed_count]["johan"] = df_cut[df["annotator"] == "johan"]["annotation"]
        mixed_dict[mixed_count]["chris"] = df_cut[df["annotator"] == "chris"]["annotation"]
        mixed_dict[mixed_count]["alan"] = df_cut[df["annotator"] == "alan"]["annotation"]
        mixed_dict[mixed_count]["karl"] = df_cut[df["annotator"] == "karl"]["annotation"]
        mixed_count += 1
    else:
        pure_count += 1
        
        
print(f"Female in difficult label: {female_count=}")
print(f"Male in difficult label: {male_count=}")
print(f"Male and Female in difficult: {mixed_count_pass=}")
print(f"Male and Female without Passes {mixed_count=}") 
print(f"Agreement on Pass label: {pass_count=}")
print(f"Agreement on Male or Female label: {pure_count=}")
print(f"Count of images: sum={sum([female_count,male_count,mixed_count,pass_count,pure_count])}")


if False:
    for key in mixed_dict.keys():
        filename = mixed_dict[key]["filename"]
        print("johan= ", mixed_dict[key]["johan"])
        print("chris= ", mixed_dict[key]["chris"])
        print("alan= ", mixed_dict[key]["alan"])
        print("karl= ", mixed_dict[key]["karl"])
        if len(filename.split("_")) == 3:
            s = filename.split("_")
            filename = s[0] + " " + s[1] + "_" + s[2]
        os.system(f'explorer.exe "{get_path("/data/imgs/"+filename)}"')
        input()