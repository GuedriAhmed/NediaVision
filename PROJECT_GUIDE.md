# Project Guide: `NediaVision`

## 1. What this project is

This repository is **NediaVision**, a custom project built on a **PyTorch reimplementation of Stable Diffusion inference**.

In simple words:

- It can **generate an image from text**.
- It can also **edit an existing image** by adding noise and denoising it again.
- It **does not train a model from scratch**.
- It expects **pretrained weights** and tokenizer files to be downloaded separately.

So NediaVision is mainly an **implementation of the architecture and generation pipeline**, not a full training framework.

## 2. Main idea of the project

Stable Diffusion works like this:

1. A text prompt is converted into numerical text features.
2. The image is represented in a smaller compressed space called **latent space**.
3. The model starts from random noise, or from a noised version of an input image.
4. A diffusion model predicts the noise step by step.
5. The sampler removes noise gradually.
6. The final latent representation is decoded into an image.

This repository implements those parts manually in Python using PyTorch.

## 3. What the client said about probability equations

That statement is broadly true.

This project is based on **diffusion probabilistic modeling**:

- noise is sampled from a Gaussian distribution
- the model learns or uses formulas related to noise schedules
- denoising follows DDPM-style equations
- variance, alpha, beta, cumulative products, and random sampling are part of the process

You can see the mathematical sampling logic mainly in:

- `sd/ddpm.py`
- `sd/pipeline.py`

## 4. What this project does not include

This repository does **not** include a full end-to-end training pipeline.

Missing pieces for training from scratch:

- no dataset loader
- no image dataset preprocessing pipeline
- no augmentation pipeline
- no optimizer setup
- no loss training loop
- no epoch loop
- no validation loop
- no checkpoint saving during training

It only includes **inference-time preprocessing**, such as:

- tokenizing text
- resizing an image
- converting images to tensors
- rescaling pixel values
- adding noise before image-to-image generation

## 5. External files required

According to `README.md`, this project needs files that are **not included** in the repository:

- `vocab.json`
- `merges.txt`
- `v1-5-pruned-emaonly.ckpt`

These are expected inside a `data` folder.

At the moment, this repository copy does **not** contain the `data` folder, so the project is **not runnable yet as-is**.

## 6. Technologies used

### Language

- **Python 3.11.3**

### Main libraries

- `torch`: deep learning tensors, layers, models, random sampling
- `numpy`: numerical arrays and timestep utilities
- `tqdm`: progress bar during denoising
- `transformers`: tokenizer support
- `pillow`: image loading and saving
- `lightning`: listed as a dependency, but not used in the current source files inspected

## 7. Repository structure

Top-level files:

- `README.md`: short usage notes and download instructions
- `requirements.txt`: Python dependencies
- `license.txt`: MIT license template
- `Stable_Diffusion_Diagrams_V2.pdf`: likely supporting diagrams/documentation
- `sd/`: source code and notebooks

Inside `sd/`:

- `attention.py`
- `clip.py`
- `ddpm.py`
- `decoder.py`
- `diffusion.py`
- `encoder.py`
- `model_converter.py`
- `model_loader.py`
- `pipeline.py`
- `demo.ipynb`
- `add_noise.ipynb`

## 8. High-level pipeline flow

The runtime flow of the project is:

1. Load pretrained weights from a checkpoint.
2. Build the model components in PyTorch.
3. Tokenize the prompt.
4. Encode the text with CLIP.
5. Create initial latents:
   - from random noise for text-to-image
   - from an encoded input image for image-to-image
6. Run denoising steps with the diffusion model and DDPM sampler.
7. Decode final latents into an RGB image.

Short version:

`Text -> CLIP -> Latent Noise Process -> Diffusion UNet -> Decoder -> Image`

## 9. The role of each file

### `README.md`

Role:

- tells the user what the repository is
- explains which tokenizer and checkpoint files must be downloaded
- mentions some tested fine-tuned Stable Diffusion models

Important point:

- it confirms this project depends on **external pretrained files**

### `requirements.txt`

Role:

- lists Python packages needed for the project

Important point:

- it pins versions, especially `torch==2.0.1`

### `license.txt`

Role:

- MIT license template

Important point:

- the placeholders `[year]` and `[fullname]` are still unfilled

### `Stable_Diffusion_Diagrams_V2.pdf`

Role:

- likely a reference document for architecture diagrams

Important point:

- it was not parsed here, so this guide only documents the code and visible repository files

### `sd/pipeline.py`

Role:

- the **main generation pipeline**
- coordinates all other model parts

What it does:

- receives prompt, negative prompt, image, settings, models, tokenizer, and device
- tokenizes text
- gets CLIP text embeddings
- initializes latents
- handles image-to-image encoding if an input image is provided
- creates a DDPM sampler
- loops over denoising timesteps
- applies classifier-free guidance
- decodes final latents into an image
- rescales output and returns a NumPy image array

Why it is important:

- this file is the **orchestrator**
- it does not define the full math of every module, but it connects all modules into one working workflow

### `sd/model_loader.py`

Role:

- builds the main PyTorch model objects
- loads the pretrained state dictionaries into them

What it creates:

- `CLIP`
- `VAE_Encoder`
- `VAE_Decoder`
- `Diffusion`

Why it matters:

- this is where architecture objects meet the pretrained checkpoint weights

### `sd/model_converter.py`

Role:

- converts weights from a standard Stable Diffusion checkpoint into the naming format expected by this repository

What it does:

- loads the checkpoint
- reads the original parameter names
- remaps them into four groups:
  - `diffusion`
  - `encoder`
  - `decoder`
  - `clip`
- concatenates attention projection weights where needed

Why it matters:

- the repository architecture names do not exactly match the original checkpoint names
- this file acts as a translation layer

Important point:

- this file is large because it contains many parameter mapping lines
- it does not train anything
- it only reorganizes pretrained weights

### `sd/ddpm.py`

Role:

- implements the DDPM sampler used during denoising

Main responsibilities:

- define beta schedule
- compute alpha and cumulative products
- choose inference timesteps
- add noise to images/latents
- remove noise step by step
- control image-to-image strength

Why it matters:

- this file contains much of the explicit diffusion probability logic

### `sd/attention.py`

Role:

- defines reusable attention modules

Classes:

- `SelfAttention`
- `CrossAttention`

What they do:

- `SelfAttention`: lets tokens/features attend to each other
- `CrossAttention`: lets image latent features attend to text embeddings

Why it matters:

- cross-attention is one of the core mechanisms that connects the text prompt to image generation

### `sd/clip.py`

Role:

- implements the text encoder side used to convert prompt tokens into embeddings

Main components:

- `CLIPEmbedding`
- `CLIPLayer`
- `CLIP`

What it does:

- embeds tokens
- adds positional embeddings
- passes embeddings through transformer-like layers
- outputs contextual text features used by the diffusion model

Why it matters:

- without this file, the model would not know what the prompt means

### `sd/encoder.py`

Role:

- implements the VAE encoder

What it does:

- takes an input image
- converts it into a lower-dimensional latent representation
- predicts mean and log-variance
- samples latent values using noise

Why it matters:

- this is required for image-to-image mode
- it maps images into latent space, where diffusion happens

### `sd/decoder.py`

Role:

- implements the VAE decoder and helper VAE blocks

Main classes:

- `VAE_AttentionBlock`
- `VAE_ResidualBlock`
- `VAE_Decoder`

What it does:

- takes final latent tensors
- upsamples and transforms them back into a 3-channel image

Why it matters:

- the diffusion model works in latent space, not directly in pixel space
- the decoder converts the latent result back into a visible image

### `sd/diffusion.py`

Role:

- implements the main diffusion model, based on a UNet with attention

Main classes:

- `TimeEmbedding`
- `UNET_ResidualBlock`
- `UNET_AttentionBlock`
- `Upsample`
- `SwitchSequential`
- `UNET`
- `UNET_OutputLayer`
- `Diffusion`

What it does:

- injects time information
- processes latent tensors through encoder and decoder paths
- uses self-attention and cross-attention
- predicts noise for each denoising step

Why it matters:

- this is the main neural network that drives generation quality

### `sd/demo.ipynb`

Role:

- provides a simple notebook example showing how to run the project

What it demonstrates:

- choosing device
- loading tokenizer
- loading model weights
- setting prompt and negative prompt
- switching between text-to-image and image-to-image
- choosing sampler, steps, and seed
- generating an image through `pipeline.generate(...)`

Why it matters:

- it is the clearest example of how the repository is intended to be used

### `sd/add_noise.ipynb`

Role:

- appears to be an exploratory notebook related to visualizing or experimenting with adding noise

Important point:

- the notebook file contains a large embedded image output
- it seems more like a demonstration/experiment notebook than a core runtime module

## 10. Detailed explanation of imports

### Common external imports

#### `import torch`

Used for:

- tensors
- random number generation
- neural network computation
- moving tensors between CPU and GPU
- mathematical tensor operations

#### `from torch import nn`

Used for neural network building blocks:

- `nn.Module`
- `nn.Linear`
- `nn.Conv2d`
- `nn.LayerNorm`
- `nn.GroupNorm`
- `nn.Embedding`
- `nn.ModuleList`
- `nn.Sequential`
- `nn.Upsample`

#### `from torch.nn import functional as F`

Used for functional operations, such as:

- `F.silu`
- `F.gelu`
- `F.softmax`
- `F.interpolate`
- `F.pad`

This style is common when an operation is not stored as a layer object.

#### `import numpy as np`

Used for:

- arrays
- image conversion
- timestep generation
- some math utilities

#### `from tqdm import tqdm`

Used for:

- showing denoising progress during generation

#### `from PIL import Image`

Used in the notebook for:

- opening and returning images

#### `from transformers import CLIPTokenizer`

Used in the notebook for:

- converting prompt text into token IDs

### Internal module imports

#### `from attention import SelfAttention, CrossAttention`

Means:

- reuse attention modules from `attention.py`

#### `from decoder import VAE_AttentionBlock, VAE_ResidualBlock`

Means:

- reuse helper blocks already defined in `decoder.py`

#### `from clip import CLIP`
#### `from encoder import VAE_Encoder`
#### `from decoder import VAE_Decoder`
#### `from diffusion import Diffusion`

Means:

- build the full model by combining smaller components from different files

#### `import model_converter`

Means:

- use the checkpoint conversion logic before loading weights

## 11. Important syntax patterns used in the project

This project uses normal Python and standard PyTorch coding patterns.

### Function definitions

Example pattern:

```python
def generate(prompt, models={}, device=None):
    ...
```

Meaning:

- `def` creates a function
- arguments inside parentheses are inputs
- indented code under it is the function body

### Class definitions

Example pattern:

```python
class DDPMSampler:
    ...
```

Meaning:

- `class` defines an object blueprint
- it usually stores logic and state together

### Inheritance

Example patterns:

```python
class CLIP(nn.Module):
```

```python
class VAE_Encoder(nn.Sequential):
```

Meaning:

- the class inherits behavior from PyTorch base classes
- `nn.Module` is the standard base class for models
- `nn.Sequential` means layers run in order

### Constructor methods

Example pattern:

```python
def __init__(self):
    super().__init__()
```

Meaning:

- `__init__` runs when the object is created
- `super().__init__()` initializes the parent PyTorch class properly

### Forward methods

Example pattern:

```python
def forward(self, x):
    ...
```

Meaning:

- defines how input data moves through the model
- in PyTorch, `model(x)` internally calls `forward(x)`

### Tensor shape comments

This project frequently includes comments like:

```python
# (Batch_Size, Seq_Len, Dim) -> (Batch_Size, Seq_Len, Dim)
```

Meaning:

- these comments explain input and output tensor shapes
- they are very useful for understanding deep learning code

### List-like model containers

Example:

```python
self.layers = nn.ModuleList([...])
```

Meaning:

- a PyTorch-aware list of submodules

### Sequential execution

Example:

```python
super().__init__(
    nn.Conv2d(...),
    VAE_ResidualBlock(...),
)
```

Meaning:

- these layers will run one after another

### Context manager for inference

Example:

```python
with torch.no_grad():
```

Meaning:

- disables gradient tracking
- makes inference lighter and faster
- appropriate for generation when training is not happening

### Conditional logic

Example:

```python
if input_image:
    ...
else:
    ...
```

Meaning:

- switch between image-to-image and text-to-image logic

### Dictionary access

Example:

```python
clip = models["clip"]
```

Meaning:

- retrieve model components from a dictionary

### Tensor manipulation

Common operations used:

- `view(...)`: reshape tensor
- `transpose(...)`: swap dimensions
- `permute(...)`: reorder dimensions
- `unsqueeze(...)`: add a dimension
- `chunk(...)`: split tensor into pieces
- `cat(...)`: concatenate tensors
- `repeat(...)`: duplicate along dimensions

These are heavily used because deep learning models depend on exact tensor shapes.

## 12. What happens inside `pipeline.generate()`

This is the most important function in the repository.

### Input arguments

Main arguments:

- `prompt`: user text prompt
- `uncond_prompt`: unconditional or negative prompt
- `input_image`: optional image for image-to-image
- `strength`: how strongly to transform an input image
- `do_cfg`: whether to use classifier-free guidance
- `cfg_scale`: guidance strength
- `sampler_name`: currently only `ddpm`
- `n_inference_steps`: number of denoising steps
- `models`: dictionary of loaded models
- `seed`: random seed
- `device`: execution device
- `idle_device`: device for parking unused models
- `tokenizer`: text tokenizer

### Main stages

#### Stage 1: check and initialize

- validates `strength`
- creates a random generator
- sets seed if provided

#### Stage 2: encode text

- tokenizes prompt text
- runs tokens through CLIP
- if CFG is enabled, also encodes an unconditional prompt
- concatenates conditional and unconditional contexts

#### Stage 3: create latents

Two modes:

- **Text-to-image**: start from random latent noise
- **Image-to-image**:
  - resize input image
  - convert to NumPy array
  - convert to tensor
  - rescale to `[-1, 1]`
  - move channels into PyTorch format
  - encode image into latents
  - add controlled noise according to `strength`

#### Stage 4: denoising loop

For every timestep:

- build time embedding
- prepare model input
- if CFG is on, duplicate input for conditional and unconditional passes
- predict noise with diffusion model
- combine outputs using CFG formula
- update latents through sampler step

#### Stage 5: decode output

- send final latents to decoder
- convert from latent space to image space
- rescale output from `[-1, 1]` to `[0, 255]`
- return image as a CPU NumPy array

## 13. Model architecture summary

### Text side

- tokenizer converts text to token IDs
- `CLIP` converts token IDs to text embeddings

### Image latent side

- `VAE_Encoder` compresses image to latent space
- `Diffusion` predicts noise inside latent space
- `DDPMSampler` updates latents through the denoising schedule
- `VAE_Decoder` reconstructs pixels from final latents

## 14. Important concepts used in the code

### Latent space

Instead of working on full-size images directly, the model works in a smaller compressed representation.

Benefits:

- faster
- lower memory use
- still preserves useful image structure

### VAE

The encoder/decoder pair is a VAE-like latent compressor.

Role:

- encoder: image -> latent
- decoder: latent -> image

### UNet

The diffusion model is a UNet-style network.

Role:

- predict the noise present in the latent image at each timestep

### Attention

Attention helps the model relate information across tokens or image positions.

Types used:

- self-attention
- cross-attention

### Classifier-Free Guidance (CFG)

CFG improves prompt alignment by mixing:

- a conditional prediction
- an unconditional prediction

The code uses:

```python
cfg_scale * (output_cond - output_uncond) + output_uncond
```

This strengthens prompt influence.

### Time embedding

The diffusion model needs to know which denoising step it is currently on.

Time embeddings provide that information numerically.

## 15. Why some files are educational

This repository looks partly educational because:

- comments explain tensor shapes in detail
- architecture pieces are split clearly
- the code manually implements attention, UNet blocks, and VAE blocks
- the notebook demonstrates usage simply

So this code is useful both as:

- a small inference project
- a learning resource for Stable Diffusion internals

## 16. Current limitations and practical notes

### Missing runtime assets

- `data/` folder is missing
- pretrained checkpoint is missing
- tokenizer files are missing

### Import style

Files import sibling modules like:

```python
from ddpm import DDPMSampler
```

This means the project is expected to be run with the `sd` folder as the working module context, such as from the notebook.

### Only one sampler exposed

- pipeline currently supports only `"ddpm"`

### Fixed image size in pipeline

- `WIDTH = 512`
- `HEIGHT = 512`

So generation is built around 512x512.

## 17. Simple conclusion

This project is best described as:

> A PyTorch implementation of the Stable Diffusion inference pipeline that rebuilds the core architecture manually and uses external pretrained weights for text-to-image and image-to-image generation.

In even simpler language:

- the code **builds the model structure**
- the checkpoint **provides learned knowledge**
- the pipeline **runs image generation**
- the repository **does not train the model from zero**

## 18. Best short explanation to tell someone else

You can describe it like this:

> This project is not a training framework for building a diffusion model from scratch. It is an inference-oriented PyTorch implementation of Stable Diffusion. The repository defines the architecture modules manually, loads pretrained weights from an external checkpoint, converts text prompts into embeddings, performs latent denoising step by step with DDPM, and decodes the final latent into an image.
