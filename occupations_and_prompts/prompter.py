import json

gender_profs = json.load(open('occupations.txt'))

with open('prompts.txt', 'w') as f:
    for gender, profs in gender_profs.items():
        print(f'\n{gender}', file=f)
        for prof in profs:
            print(f'A picture of a {prof}', file=f)