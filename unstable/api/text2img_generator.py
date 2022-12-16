import requests
import json
import tqdm
from pathlib import Path
import os

gender_profs = json.load(open("occupations.txt"))
prompts = []
images_per_profession = 100//4

for gender,profs in gender_profs.items():
	for prof in profs:
		prompts.append((prof,f"A picture of a {prof}"))


output = dict()
for prof, prompt in prompts:

	print(f"generating images for: {prompt}")
	output[prof] = dict()
	path_dir = Path(f"text2imgdata",prof)
	path_dir.mkdir(parents=True,exist_ok=True)
	files = [int(x[:-4]) for x in os.listdir(path_dir)]
	if len(files) == 0:
		max_image_num=0
	else:
		max_image_num = max(files)
	for idx in tqdm.trange(images_per_profession):
		try:
			r = requests.post(
			    "https://api.deepai.org/api/text2img",
			    data={
			        'text': prompt,
			    },
			    headers={'api-key': 'your-key-here'}
			)
			if r.status_code == 200:
				url = r.json()["output_url"]
				r2 = requests.get(url)
				
				path = Path(path_dir,f"{max_image_num+idx+1}.jpg")
				with open(path,"wb") as file:
					file.write(r2.content)

		except Exception as e:
			print(e)
		output[prof][idx] = r.json()
with open("text2img_output.json","w") as outfile:
	json.dump(output, outfile)
