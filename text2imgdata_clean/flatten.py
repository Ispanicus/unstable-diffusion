from pathlib import Path
from shutil import copy

this_dir = Path().resolve()
assert this_dir.name == 'text2imgdata_clean'

for dir in Path().glob('*'):
    if not dir.is_dir():
        continue
    profession = dir.name
    for i, file in enumerate(dir.glob('*')):
        assert file.suffix == '.jpg'
        copy(file, this_dir / f'api_{profession}_{i}.jpg')