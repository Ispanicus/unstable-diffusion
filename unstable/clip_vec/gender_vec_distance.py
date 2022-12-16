from unstable.clip_vec.modules import FrozenCLIPTextEmbedder
import holoviews as hv
from bokeh.models import PrintfTickFormatter
import pandas as pd
from unstable.meta_tools import get_path
from unstable.occupations_and_prompts.prompter import PREFIX
from unstable.occupations_and_prompts.parse_gendered_professions import PLOT_ORDER
import hvplot.pandas
import torch
import numpy as np
from typing import NamedTuple
from math import acos

def to_numpy_vec(u):
    return np.squeeze(u.detach().cpu().numpy())

def cosine_dist(u, v):
    u, v = map(to_numpy_vec, [u, v])

    norm = np.linalg.norm
    return np.dot(u, v) / (norm(u)*norm(v))

def get_prompts():
    prompt_path = get_path('data/prompts.txt')
    return [prompt for prompt in open(prompt_path).readlines() if prompt.startswith(PREFIX)]

def load_model(device = 'cuda', clip_version='ViT-L/14'):
    dev = torch.device(device)
    return FrozenCLIPTextEmbedder(clip_version).to(
        device=torch.device(device)
    )

class GenderDist(NamedTuple):
    prompt: str
    man_dist: float
    woman_dist: float

pi = r'$\pi$'
class GenderAngle(NamedTuple):
    prompt: str
    man_radians: float
    woman_radians: float
    diff: float

    @staticmethod
    def latex_header() -> str: 
        return f'prompt & "man" angle {pi} & "woman" angle {pi} & angle diff \\\\\n'

    def latex(s) -> str:
        prof = s.prompt.strip().split(" a ")[-1]
        return f'{prof} & {s.man_radians:.2f} & {s.woman_radians:.2f} & {s.diff:.2f} \\\\\n'

    def __str__(s) -> str: 
        return f'{s.prompt.strip():<35} {s.man_radians=:.2f} {s.woman_radians=:.2f} {s.diff=:.2f}\n'

def gender_dist_plot():
    sd_clip = 'ViT-L/14'
    cr_clip = 'ViT-B/32'

    plots = []
    for clip_version in [sd_clip, cr_clip]:
        model = load_model(clip_version=clip_version)

        man_vec = model.encode(PREFIX + 'man')
        woman_vec = model.encode(PREFIX + 'woman')

        prompts = get_prompts()
        prompt_vecs = model.encode(prompts)
        del model

        dists = [
            GenderDist(prompt, cosine_dist(vec, man_vec), cosine_dist(vec, woman_vec))
            for prompt, vec in zip(prompts, prompt_vecs)
        ]
        angles = sorted([
                GenderAngle(r.prompt, acos(r.man_dist), acos(r.woman_dist), acos(r.woman_dist)-acos(r.man_dist))
                for r in dists
            ], key=lambda r: r.diff
        )
        angles_df = pd.DataFrame(angles)
        angles_df['profession'] = angles_df.prompt.str.replace(r'A picture of a (.*)\n', r'\1', regex=True)
        diff = angles_df.set_index('profession')['diff'].reindex(PLOT_ORDER[::-1]).fillna(0)
        diff *= 360

        plots.append(
            diff.hvplot.bar(alpha=0.5,color='diff', cmap='RdYlBu').opts(
                invert_axes=True, 
                colorbar=True, 
                title="Gender proximity difference", 
                xlabel = 'Profession',
                ylabel = 'Δ Similarity [degrees]',
                xformatter=PrintfTickFormatter(format='%f°')
            )
        )
    return hv.Layout(plots)


def print_prof_gender_dists(latex: bool = True, clip_version: str = 'ViT-L/14'):
    model = load_model(clip_version=clip_version)

    man_vec = model.encode(PREFIX + 'man')
    woman_vec = model.encode(PREFIX + 'woman')

    prompts = get_prompts()
    prompt_vecs = model.encode(prompts)

    dists = [
        GenderDist(prompt, cosine_dist(vec, man_vec), cosine_dist(vec, woman_vec))
        for prompt, vec in zip(prompts, prompt_vecs)
    ]
    angles = sorted([
            GenderAngle(r.prompt, acos(r.man_dist), acos(r.woman_dist), acos(r.man_dist)-acos(r.woman_dist))
            for r in dists
        ], key=lambda r: r.diff
    )
        
    if latex:
        print(GenderAngle.latex_header(), end='\hline\n')
        print(''.join(map(GenderAngle.latex, angles)))
    else:
        print(''.join(map(str, angles)))


if __name__ == '__main__':
    plot = gender_dist_plot()