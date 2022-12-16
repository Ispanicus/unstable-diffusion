# unstable-diffusion
Data in the wild course project

data/metadata.csv contains annotations for each image, as well as image source and profession
data/imgs contains all images generated with Stable Diffusion (api_{profession}_n.jpg) and scraped from CLIP Retrieval ({profession}_n.jpg)
data/annotations contains the raw annotation json files output by Label Studio

The CLIP Retrieval scraping can be reproduced using the script found at scraper/laion_scraper.py
The Stable Diffusion image generation can be done using the script at api/text2img_generator.py (important to note the api is a paid service)
