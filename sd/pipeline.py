import torch
import numpy as np
from torch.nn import functional as F
from tqdm import tqdm
from ddpm import DDPMSampler

DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512


def create_noise_preview(latents, width, height):
    # Build a lightweight preview directly from the latent tensor instead of
    # decoding it through the VAE, which avoids an expensive extra decode pass.
    preview = latents[0, :3].detach().to("cpu", torch.float32)
    preview_min = preview.amin(dim=(1, 2), keepdim=True)
    preview_max = preview.amax(dim=(1, 2), keepdim=True)
    preview = (preview - preview_min) / (preview_max - preview_min).clamp_min(1e-6)
    preview = F.interpolate(
        preview.unsqueeze(0),
        size=(height, width),
        mode="bilinear",
        align_corners=False,
    )
    preview = preview.squeeze(0).permute(1, 2, 0)
    return (preview.clamp(0, 1) * 255).to(torch.uint8).numpy()

def generate(
    prompt,
    uncond_prompt=None,
    input_image=None,
    mask_image=None,
    strength=0.8,
    do_cfg=True,
    cfg_scale=7.5,
    sampler_name="ddpm",
    n_inference_steps=50,
    models={},
    seed=None,
    device=None,
    idle_device=None,
    tokenizer=None,
    width=DEFAULT_WIDTH,
    height=DEFAULT_HEIGHT,
    show_progress=True,
    return_noise_preview=False,
):
    def preprocess_image(image):
        image = image.resize((width, height))
        image = np.array(image)
        image = torch.tensor(image, dtype=torch.float32, device=device)
        image = rescale(image, (0, 255), (-1, 1))
        image = image.unsqueeze(0)
        return image.permute(0, 3, 1, 2)

    def preprocess_mask(mask):
        mask = mask.resize((latents_width, latents_height))
        mask = np.array(mask, dtype=np.float32) / 255.0
        mask = torch.tensor(mask, dtype=torch.float32, device=device)
        mask = (mask > 0.5).to(torch.float32)
        mask = mask.unsqueeze(0).unsqueeze(0)
        return mask

    with torch.inference_mode():
        if not 0 < strength <= 1:
            raise ValueError("strength must be between 0 and 1")
        if width % 8 != 0 or height % 8 != 0:
            raise ValueError("width and height must be divisible by 8")
        if mask_image is not None and input_image is None:
            raise ValueError("mask_image requires an input_image")

        latents_width = width // 8
        latents_height = height // 8

        if idle_device:
            to_idle = lambda x: x.to(idle_device)
        else:
            to_idle = lambda x: x

        # Initialize random number generator according to the seed specified
        generator = torch.Generator(device=device)
        if seed is None:
            generator.seed()
        else:
            generator.manual_seed(seed)

        clip = models["clip"]
        clip.to(device)
        
        if do_cfg:
            # Convert into a list of length Seq_Len=77
            cond_tokens = tokenizer.batch_encode_plus(
                [prompt], padding="max_length", max_length=77
            ).input_ids
            # (Batch_Size, Seq_Len)
            cond_tokens = torch.tensor(cond_tokens, dtype=torch.long, device=device)
            # (Batch_Size, Seq_Len) -> (Batch_Size, Seq_Len, Dim)
            cond_context = clip(cond_tokens)
            # Convert into a list of length Seq_Len=77
            uncond_tokens = tokenizer.batch_encode_plus(
                [uncond_prompt], padding="max_length", max_length=77
            ).input_ids
            # (Batch_Size, Seq_Len)
            uncond_tokens = torch.tensor(uncond_tokens, dtype=torch.long, device=device)
            # (Batch_Size, Seq_Len) -> (Batch_Size, Seq_Len, Dim)
            uncond_context = clip(uncond_tokens)
            # (Batch_Size, Seq_Len, Dim) + (Batch_Size, Seq_Len, Dim) -> (2 * Batch_Size, Seq_Len, Dim)
            context = torch.cat([cond_context, uncond_context])
        else:
            # Convert into a list of length Seq_Len=77
            tokens = tokenizer.batch_encode_plus(
                [prompt], padding="max_length", max_length=77
            ).input_ids
            # (Batch_Size, Seq_Len)
            tokens = torch.tensor(tokens, dtype=torch.long, device=device)
            # (Batch_Size, Seq_Len) -> (Batch_Size, Seq_Len, Dim)
            context = clip(tokens)
        to_idle(clip)

        if sampler_name == "ddpm":
            sampler = DDPMSampler(generator)
            sampler.set_inference_timesteps(n_inference_steps)
        else:
            raise ValueError("Unknown sampler value %s. ")

        latents_shape = (1, 4, latents_height, latents_width)

        init_latents = None
        mask = None
        latent_noise = None

        if input_image:
            encoder = models["encoder"]
            encoder.to(device)

            input_image_tensor = preprocess_image(input_image)

            # (Batch_Size, 4, Latents_Height, Latents_Width)
            encoder_noise = torch.randn(latents_shape, generator=generator, device=device)
            # (Batch_Size, 4, Latents_Height, Latents_Width)
            init_latents = encoder(input_image_tensor, encoder_noise)
            latent_noise = torch.randn(latents_shape, generator=generator, device=device)

            # Add noise to the latents (the encoded input image)
            # (Batch_Size, 4, Latents_Height, Latents_Width)
            sampler.set_strength(strength=strength)
            latents = sampler.add_noise(init_latents, sampler.timesteps[0], noise=latent_noise)

            if mask_image is not None:
                mask = preprocess_mask(mask_image)
                latents = mask * latents + (1 - mask) * init_latents

            to_idle(encoder)
        else:
            # (Batch_Size, 4, Latents_Height, Latents_Width)
            latents = torch.randn(latents_shape, generator=generator, device=device)

        noise_preview = None
        if return_noise_preview:
            noise_preview = create_noise_preview(latents, width, height)

        diffusion = models["diffusion"]
        diffusion.to(device)

        timesteps = tqdm(sampler.timesteps, disable=not show_progress)
        time_embeddings = {
            int(timestep): get_time_embedding(int(timestep)).to(device)
            for timestep in sampler.timesteps.tolist()
        }
        for i, timestep in enumerate(timesteps):
            if mask is not None:
                source_latents = sampler.add_noise(init_latents, timestep, noise=latent_noise)
                latents = mask * latents + (1 - mask) * source_latents

            # (1, 320)
            time_embedding = time_embeddings[int(timestep)]

            # (Batch_Size, 4, Latents_Height, Latents_Width)
            model_input = latents

            if do_cfg:
                # (Batch_Size, 4, Latents_Height, Latents_Width) -> (2 * Batch_Size, 4, Latents_Height, Latents_Width)
                model_input = model_input.repeat(2, 1, 1, 1)

            # model_output is the predicted noise
            # (Batch_Size, 4, Latents_Height, Latents_Width) -> (Batch_Size, 4, Latents_Height, Latents_Width)
            model_output = diffusion(model_input, context, time_embedding)

            if do_cfg:
                output_cond, output_uncond = model_output.chunk(2)
                model_output = cfg_scale * (output_cond - output_uncond) + output_uncond

            # (Batch_Size, 4, Latents_Height, Latents_Width) -> (Batch_Size, 4, Latents_Height, Latents_Width)
            latents = sampler.step(timestep, latents, model_output)

            if mask is not None:
                prev_timestep = sampler._get_previous_timestep(int(timestep))
                if prev_timestep >= 0:
                    source_latents = sampler.add_noise(init_latents, prev_timestep, noise=latent_noise)
                else:
                    source_latents = init_latents
                latents = mask * latents + (1 - mask) * source_latents

        to_idle(diffusion)

        decoder = models["decoder"]
        decoder.to(device)
        # (Batch_Size, 4, Latents_Height, Latents_Width) -> (Batch_Size, 3, Height, Width)
        images = decoder(latents)
        to_idle(decoder)

        images = rescale(images, (-1, 1), (0, 255), clamp=True)
        # (Batch_Size, Channel, Height, Width) -> (Batch_Size, Height, Width, Channel)
        images = images.permute(0, 2, 3, 1)
        images = images.to("cpu", torch.uint8).numpy()
        if return_noise_preview:
            return images[0], noise_preview
        return images[0]
    
def rescale(x, old_range, new_range, clamp=False):
    old_min, old_max = old_range
    new_min, new_max = new_range
    x -= old_min
    x *= (new_max - new_min) / (old_max - old_min)
    x += new_min
    if clamp:
        x = x.clamp(new_min, new_max)
    return x

def get_time_embedding(timestep):
    # Shape: (160,)
    freqs = torch.pow(10000, -torch.arange(start=0, end=160, dtype=torch.float32) / 160) 
    # Shape: (1, 160)
    x = torch.tensor([timestep], dtype=torch.float32)[:, None] * freqs[None]
    # Shape: (1, 160 * 2)
    return torch.cat([torch.cos(x), torch.sin(x)], dim=-1)
