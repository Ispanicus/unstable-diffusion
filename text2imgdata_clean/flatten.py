from pathlib import Path
from shutil import copy

this_dir = Path().resolve()
dest_dir = Path('..').resolve() / 'data'
assert this_dir.name == 'text2imgdata_clean'
assert dest_dir.name == 'data'
assert dest_dir.parent.name == 'unstable-diffusion'

for dir in Path().glob('*'):
    if not dir.is_dir():
        continue
    profession = dir.name
    for i, file in enumerate(dir.glob('*')):
        assert file.suffix == '.jpg'
        copy(file, this_dir / f'api_{profession}_{i}.jpg')