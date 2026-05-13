from clip import CLIP
from encoder import VAE_Encoder
from decoder import VAE_Decoder
from diffusion import Diffusion

import model_converter

_MODEL_CACHE = {}


def preload_models_from_standard_weights(ckpt_path, device):
    cache_key = (ckpt_path, device)
    cached_models = _MODEL_CACHE.get(cache_key)
    if cached_models is not None:
        return cached_models

    state_dict = model_converter.load_from_standard_weights(ckpt_path, device)

    encoder = VAE_Encoder().to(device)
    encoder.load_state_dict(state_dict['encoder'], strict=True)
    encoder.eval()

    decoder = VAE_Decoder().to(device)
    decoder.load_state_dict(state_dict['decoder'], strict=True)
    decoder.eval()

    diffusion = Diffusion().to(device)
    diffusion.load_state_dict(state_dict['diffusion'], strict=True)
    diffusion.eval()

    clip = CLIP().to(device)
    clip.load_state_dict(state_dict['clip'], strict=True)
    clip.eval()

    models = {
        'clip': clip,
        'encoder': encoder,
        'decoder': decoder,
        'diffusion': diffusion,
    }
    _MODEL_CACHE[cache_key] = models
    del state_dict
    return models
