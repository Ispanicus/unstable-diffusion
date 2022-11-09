import requests # http requests
import json
import tqdm
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# send a HTTP GET request and store the response
gender_occupations = {"male": [
    "police officer",
    "electrician",
    "carpenter",
    "software developer"],
"female": [
    "social worker",
    "maid",
    "secretary",
    "nurse"],
"general": [
    "professor",
    "photographer",
    "artist",
    "manager"]
}
N_IMGS = 200

url = 'https://knn5.laion.ai/knn-service'
occs = [o for occupations in gender_occupations.values() for o in occupations]

def get_urls_for_occ(occ):
    data = {"text": f"A picture of a {occ}","image":None,"image_url":None,"embedding_input":None,"modality":"image","num_images":N_IMGS*4,"indice_name":"laion5B","num_result_ids":3000,"use_mclip":False,"deduplicate":True,"use_safety_model":False,"use_violence_detector":False,"aesthetic_score":"","aesthetic_weight":"0.5"}
    response = requests.post(url, data=json.dumps(data))
    response.raise_for_status()
    return [dic['url'] for dic in json.loads(response.text) if 'url' in dic]

def write(i_occ_content):
    i, occ, content = i_occ_content
    with open(f'laion_{occ}_{i}.jpg') as f:
        f.write(content)

def write_content(i_occ_url):
    i, occ, url = i_occ_url
    if N_IMGS <= len(list(Path('pics').glob(f'*{occ}*'))):
        return
    try: 
        r = requests.get(url)
        r.raise_for_status()
        with open(f'./pics/laion_{occ}_{i}.jpg', 'wb') as f:
            f.write(r.content)
    except Exception as e: 
        print(e)

url_dicts = {occ: get_urls_for_occ(occ) for occ in occs}
with ThreadPoolExecutor(max_workers = 10) as executor:
    for occ, urls in tqdm.tqdm(url_dicts.items()):
        executor.map(write_content, 
            [(i, occ, url) for i, url in enumerate(urls)]
        )

for occ in url_dicts:
    print(occ, len(list(Path('pics').glob(f'*{occ}*'))))