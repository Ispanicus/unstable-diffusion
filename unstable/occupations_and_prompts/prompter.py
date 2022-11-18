import json
from unstable.meta_tools import get_path

def get_gender_occupations() -> dict:
    return json.load(open(get_path('data/occupations.json')))

PREFIX = 'A picture of a '

if __name__ == '__main__':
    gender_profs = get_gender_occupations()

    with open('prompts.txt', 'w') as f:
        for gender, profs in gender_profs.items():
            print(f'\n{gender}', file=f)
            for prof in profs:
                print(PREFIX + str(prof), file=f)