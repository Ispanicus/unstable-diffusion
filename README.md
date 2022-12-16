# unstable-diffusion

To install environment, look at install.bat

## Data access
If you just want the data, see unstable/data/metadata.csv, which contains annotations for each image, as well as image source and profession

unstable/data/imgs contains all images generated with Stable Diffusion (api_{profession}_n.jpg) and scraped from CLIP Retrieval ({profession}_n.jpg)

Annotation guidelines can be found at unstable/annotations/Annotation_Guidlines.txt

## Data reconstruction
To reconstruct the metadata in convenient formats, see unstable/annotations/load_anno_df.py

unstable/data/annotations contains the raw annotation json files output by Label Studio

The CLIP Retrieval scraping can be reproduced using the script found at unstable/scraper/laion_scraper.py

The Stable Diffusion image generation can be done using the script at unstable/api/text2img_generator.py (important to note the api is a paid service)


## Figures
To recreate the figures, examine the main section of the following files:

Embeddings (4-8gb GPU): unstable/clip_vec/gender_vec_distance.py

M/F ratio and Pass barplots: unstable/annotations/stacked_bar_plots.py

Confidence intervals: unstable/statistics/conf_interval.py

