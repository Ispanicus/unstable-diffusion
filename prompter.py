import json

gender_profs = json.load(open('occupations.txt'))

for gender, profs in gender_profs.items():
    for prof in profs:
        print(f'A picture of a {prof}')