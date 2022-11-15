import json

PREFIX = 'A picture of a '

if __name__ == '__main__':
    gender_profs = json.load(open('occupations.txt'))

    with open('prompts.txt', 'w') as f:
        for gender, profs in gender_profs.items():
            print(f'\n{gender}', file=f)
            for prof in profs:
                print(PREFIX + str(prof), file=f)