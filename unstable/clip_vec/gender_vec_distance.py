from clip_vec.modules import CLIPTextModel, CLIPTokenizer, FrozenCLIPEmbedder, FrozenCLIPTextEmbedder
from pathlib import Path
from occupations_and_prompts.prompter import PREFIX
import torch
import numpy as np
from typing import NamedTuple, Literal

assert Path().resolve().name == 'unstable-diffusion', 'Make sure you run this from the git root directory'

def to_numpy_vec(u):
    return np.squeeze(u.detach().cpu().numpy())

def cosine_dist(u, v):
    u, v = map(to_numpy_vec, [u, v])

    norm = np.linalg.norm
    return np.dot(u, v) / (norm(u)*norm(v))

def get_prompts():
    prompt_path = Path() / 'occupations_and_prompts/prompts.txt'
    return [prompt for prompt in open(prompt_path).readlines() if prompt.startswith(PREFIX)]

def load_model(device = 'cuda'):
    dev = torch.device(device)
    return FrozenCLIPTextEmbedder().to(
        device=torch.device(device)
    )

class GenderDist(NamedTuple):
    prompt: str
    man_dist: float
    woman_dist: float

def find_gender_ratios():
    model = load_model()
    man_vec = model.encode(PREFIX + 'man')
    woman_vec = model.encode(PREFIX + 'woman')

    prompts = get_prompts()
    prompt_vecs = model.encode(prompts)

    dists = [
        GenderDist(prompt, cosine_dist(vec, man_vec), cosine_dist(vec, woman_vec))
        for prompt, vec in zip(prompts, prompt_vecs)
    ]
    m_w_ratios = {r.prompt: r.man_dist/r.woman_dist for r in dists}
    formatted_result = sorted([(f'{r:.2f}', prompt) for prompt, r in m_w_ratios.items()])
    print('\n'.join(map(str, formatted_result)))