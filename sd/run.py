import argparse
import json
import os
from pathlib import Path
import platform
from datetime import datetime, timezone

import torch
from PIL import Image, ImageFilter
from transformers import CLIPTokenizer

import model_loader
import pipeline


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "generatedoutputs"
HISTORY_FILE = OUTPUT_DIR / "history.jsonl"
_TOKENIZER_CACHE = {}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Stable Diffusion text-to-image or image-to-image generation."
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Text prompt used for generation.",
    )
    parser.add_argument(
        "--negative-prompt",
        default="",
        help="Negative or unconditional prompt.",
    )
    parser.add_argument(
        "--input-image",
        default=None,
        help="Optional path to an input image for image-to-image generation.",
    )
    parser.add_argument(
        "--mask-image",
        default=None,
        help="Optional path to a black-and-white mask image for inpainting. White areas are regenerated.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output image path. If omitted, a numbered file is created automatically.",
    )
    parser.add_argument(
        "--filter",
        choices=["grayscale", "blackwhite", "blur", "sharpen"],
        default=None,
        help="Apply a direct image filter instead of diffusion generation.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of denoising steps.",
    )
    parser.add_argument(
        "--cfg-scale",
        type=float,
        default=7.5,
        help="Classifier-free guidance scale.",
    )
    parser.add_argument(
        "--strength",
        type=float,
        default=0.8,
        help="Image-to-image strength. Ignored for text-to-image.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Execution device.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Output width. Must be divisible by 8.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Output height. Must be divisible by 8.",
    )
    parser.add_argument(
        "--low-spec",
        action="store_true",
        help="Use lighter defaults for low-memory or CPU-only machines.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Hide the denoising progress bar.",
    )
    return parser.parse_args()


def resolve_device(device_arg: str) -> str:
    if device_arg == "cpu":
        return "cpu"
    if device_arg == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested, but no CUDA device is available.")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_generation_settings(args, device: str):
    low_spec = args.low_spec or device == "cpu"

    if low_spec:
        steps = args.steps if args.steps is not None else 30
        width = args.width if args.width is not None else 512
        height = args.height if args.height is not None else 512
        cfg_scale = min(args.cfg_scale, 7.5)
    else:
        steps = args.steps if args.steps is not None else 30
        width = args.width if args.width is not None else 512
        height = args.height if args.height is not None else 512
        cfg_scale = args.cfg_scale

    return {
        "low_spec": low_spec,
        "steps": steps,
        "width": width,
        "height": height,
        "cfg_scale": cfg_scale,
    }


def get_next_output_path() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    max_index = 0
    for candidate in OUTPUT_DIR.glob("generated *.png"):
        suffix = candidate.stem.replace("generated ", "", 1)
        if suffix.isdigit():
            max_index = max(max_index, int(suffix))
    return OUTPUT_DIR / f"generated {max_index + 1}.png"


def get_noise_output_path(output_path: Path) -> Path:
    stem = output_path.stem
    if stem.startswith("generated "):
        suffix = stem.split("generated ", 1)[1]
        return output_path.with_name(f"noise image {suffix}{output_path.suffix}")
    return output_path.with_name(f"{stem} noise{output_path.suffix}")


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    if filter_name == "grayscale":
        return image.convert("L").convert("RGB")
    if filter_name == "blackwhite":
        grayscale = image.convert("L")
        thresholded = grayscale.point(lambda pixel: 255 if pixel > 128 else 0, mode="1")
        return thresholded.convert("RGB")
    if filter_name == "blur":
        return image.filter(ImageFilter.GaussianBlur(radius=2))
    if filter_name == "sharpen":
        return image.filter(ImageFilter.SHARPEN)
    raise ValueError(f"Unknown filter: {filter_name}")


def get_tokenizer():
    cache_key = (str(DATA_DIR / "vocab.json"), str(DATA_DIR / "merges.txt"))
    tokenizer = _TOKENIZER_CACHE.get(cache_key)
    if tokenizer is None:
        tokenizer = CLIPTokenizer(cache_key[0], merges_file=cache_key[1])
        _TOKENIZER_CACHE[cache_key] = tokenizer
    return tokenizer


def append_history(entry: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    args = parse_args()

    # Keep the Hugging Face cache inside the project so tokenization works cleanly.
    os.environ.setdefault("TRANSFORMERS_CACHE", str(DATA_DIR / "hf_cache"))

    if args.filter:
        if not args.input_image:
            raise ValueError("--input-image is required when using --filter")

        input_image = Image.open(args.input_image).convert("RGB")
        output_image = apply_filter(input_image, args.filter)
        output_path = Path(args.output) if args.output else get_next_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_image.save(output_path)
        append_history(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "mode": "filter",
                "filter": args.filter,
                "input_image": str(Path(args.input_image).resolve()),
                "output_image": str(output_path.resolve()),
            }
        )
        print(f"Applied filter: {args.filter}")
        print(f"Saved image to: {output_path}")
        return

    if not args.prompt:
        raise ValueError("--prompt is required for text-to-image and image-to-image generation")
    if args.mask_image and not args.input_image:
        raise ValueError("--input-image is required when using --mask-image")

    device = resolve_device(args.device)
    idle_device = "cpu"
    settings = get_generation_settings(args, device)

    if device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True

    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    tokenizer = get_tokenizer()

    model_file = DATA_DIR / "v1-5-pruned-emaonly.ckpt"
    models = model_loader.preload_models_from_standard_weights(str(model_file), device)

    input_image = Image.open(args.input_image).convert("RGB") if args.input_image else None
    mask_image = Image.open(args.mask_image).convert("L") if args.mask_image else None

    print(f"Using device: {device}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(
        f"Resolution: {settings['width']}x{settings['height']} | "
        f"Steps: {settings['steps']} | "
        f"Low-spec mode: {settings['low_spec']}"
    )
    print(f"Loading prompt: {args.prompt}")

    image, noise_preview = pipeline.generate(
        prompt=args.prompt,
        uncond_prompt=args.negative_prompt,
        input_image=input_image,
        mask_image=mask_image,
        strength=args.strength,
        do_cfg=True,
        cfg_scale=settings["cfg_scale"],
        sampler_name="ddpm",
        n_inference_steps=settings["steps"],
        models=models,
        seed=args.seed,
        device=device,
        idle_device=idle_device,
        tokenizer=tokenizer,
        width=settings["width"],
        height=settings["height"],
        show_progress=not args.no_progress,
        return_noise_preview=True,
    )

    output_path = Path(args.output) if args.output else get_next_output_path()
    noise_output_path = get_noise_output_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(noise_preview).save(noise_output_path)
    Image.fromarray(image).save(output_path)
    append_history(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mode": "edit" if args.input_image else "text",
            "prompt": args.prompt,
            "negative_prompt": args.negative_prompt,
            "input_image": str(Path(args.input_image).resolve()) if args.input_image else None,
            "mask_image": str(Path(args.mask_image).resolve()) if args.mask_image else None,
            "output_image": str(output_path.resolve()),
            "noise_image": str(noise_output_path.resolve()),
            "device": device,
            "width": settings["width"],
            "height": settings["height"],
            "steps": settings["steps"],
            "cfg_scale": settings["cfg_scale"],
            "strength": args.strength if args.input_image else None,
            "seed": args.seed,
            "low_spec": settings["low_spec"],
        }
    )
    print(f"Saved noise image to: {noise_output_path}")
    print(f"Saved image to: {output_path}")


if __name__ == "__main__":
    main()
