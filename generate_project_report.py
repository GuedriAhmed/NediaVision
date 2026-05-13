from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "NediaVision_Project_Report.docx"


TITLE = "NediaVision Project Report"


SECTIONS = [
    (
        "Project Identity",
        [
            "Project name: NediaVision",
            "Author branding used in the launcher: nedia melki",
            "Academic framing: Final Year Project, 2025-2026",
            "Repository type: local PyTorch Stable Diffusion implementation with a custom terminal launcher",
        ],
    ),
    (
        "What This Project Is",
        [
            "This project is a PyTorch implementation of Stable Diffusion inference.",
            "It can generate an image from a text prompt.",
            "It can also edit an existing image if an input image is provided.",
            "It is not a full training-from-scratch project.",
            "It depends on pretrained files stored in the data folder, especially the Stable Diffusion checkpoint and tokenizer files.",
        ],
    ),
    (
        "Required Files and Main Folders",
        [
            "Root folder contains the main project files, the data folder, the sd source folder, the launcher batch file, and generated images.",
            "data/ contains vocab.json, merges.txt, v1-5-pruned-emaonly.ckpt, and the local Hugging Face cache folder.",
            "sd/ contains the Python source files that implement the model and pipeline.",
            "run_text_to_image.bat is the terminal-style launcher.",
            "sd/run.py is the Python entry point for generation.",
            "generated.png is the default output image produced by the script.",
        ],
    ),
    (
        "Main Technologies Used",
        [
            "Python 3.11 is the runtime used for the project.",
            "PyTorch is used for tensors, neural network layers, model loading, and inference.",
            "Transformers is used for the CLIP tokenizer.",
            "Pillow is used to open and save images.",
            "NumPy is used for numerical arrays and image conversion.",
            "tqdm is used for the progress bar during the denoising loop.",
        ],
    ),
    (
        "How Generation Starts",
        [
            "The user runs run_text_to_image.bat.",
            "The batch file displays a styled terminal theme and asks the user to enter a prompt.",
            "The prompt is saved in the batch variable PROMPT.",
            "The batch file then calls Python with the command: py -3.11 run.py --prompt \"%PROMPT%\" --device auto",
            "At that moment the text moves from the terminal layer to the Python layer.",
        ],
    ),
    (
        "Role of run_text_to_image.bat",
        [
            "It is the user-facing launcher.",
            "It creates the terminal look and branding for NediaVision.",
            "It asks the user for a prompt.",
            "It passes that prompt to run.py.",
            "It shows the output path after generation finishes.",
            "It does not generate the image by itself. It only launches the Python program that performs generation.",
        ],
    ),
    (
        "Role of sd/run.py",
        [
            "sd/run.py is the command-line entry point of the Python side.",
            "It parses command-line arguments such as prompt, negative prompt, steps, seed, device, output file, and optional input image.",
            "It chooses the execution device using resolve_device(...).",
            "It loads the tokenizer from data/vocab.json and data/merges.txt.",
            "It loads the model weights from data/v1-5-pruned-emaonly.ckpt.",
            "It calls pipeline.generate(...).",
            "It receives the final NumPy image array and saves it using Image.fromarray(image).save(output_path).",
        ],
    ),
    (
        "Important Variables in run.py",
        [
            "args.prompt: the main text prompt entered by the user.",
            "args.negative_prompt: the negative or unconditional prompt. Default is an empty string.",
            "args.input_image: optional image path for image-to-image mode.",
            "args.output: output image path. Default points to generated.png in the root folder.",
            "args.steps: number of denoising steps. Default is 50.",
            "args.cfg_scale: classifier-free guidance strength. Default is 7.5.",
            "args.strength: image-to-image strength. Default is 0.8.",
            "args.seed: random seed for reproducibility. Default is 42.",
            "args.device: auto, cpu, or cuda.",
            "device: resolved final device actually used for inference.",
            "tokenizer: CLIP tokenizer object used to encode text.",
            "models: dictionary containing clip, encoder, decoder, and diffusion models.",
            "output_path: final saved image location.",
        ],
    ),
    (
        "How Device Resolution Works",
        [
            "run.py calls resolve_device(args.device).",
            "If the argument is cpu, the project runs on CPU.",
            "If the argument is cuda, the project requires a CUDA-capable GPU.",
            "If the argument is auto, the code uses CUDA when available, otherwise CPU.",
            "In this setup CUDA support was installed successfully, so the project can run on the NVIDIA GPU.",
        ],
    ),
    (
        "Tokenizer Stage",
        [
            "The tokenizer is created with CLIPTokenizer using vocab.json and merges.txt.",
            "Its role is to convert the user prompt from normal text into token IDs.",
            "These token IDs are the format expected by the CLIP text encoder.",
            "This stage happens before the diffusion model can understand the prompt.",
        ],
    ),
    (
        "Model Loading Stage",
        [
            "The function model_loader.preload_models_from_standard_weights(...) is used to load all model parts.",
            "This function creates four models: CLIP, VAE_Encoder, VAE_Decoder, and Diffusion.",
            "Their weights are loaded from a converted checkpoint state dictionary.",
            "The models are returned in a dictionary with the keys clip, encoder, decoder, and diffusion.",
        ],
    ),
    (
        "Role of sd/model_loader.py",
        [
            "This file builds the main PyTorch model objects.",
            "It connects the architecture classes to the pretrained weights.",
            "It returns a dictionary of ready-to-use model components.",
        ],
    ),
    (
        "Role of sd/model_converter.py",
        [
            "This file loads the original Stable Diffusion checkpoint.",
            "It remaps the original parameter names into the naming structure used by this repository.",
            "It separates the checkpoint into four groups: diffusion, encoder, decoder, and clip.",
            "It does not train the model. It only converts checkpoint naming so the current architecture can load the pretrained weights.",
        ],
    ),
    (
        "Role of sd/pipeline.py",
        [
            "sd/pipeline.py contains the main generation function called generate(...).",
            "It is the orchestrator of the whole inference process.",
            "It takes the prompt, negative prompt, optional input image, configuration values, tokenizer, device, and the loaded models.",
            "It does not store the pretrained knowledge itself. Instead, it coordinates the already loaded modules step by step.",
        ],
    ),
    (
        "Important Variables in pipeline.py",
        [
            "prompt: the text prompt to follow.",
            "uncond_prompt: unconditional or negative prompt.",
            "input_image: optional input image for image-to-image mode.",
            "strength: controls how strongly an input image is changed.",
            "do_cfg: whether classifier-free guidance is used.",
            "cfg_scale: strength of the prompt guidance.",
            "sampler_name: current sampler choice, here ddpm.",
            "n_inference_steps: number of denoising iterations.",
            "models: dictionary containing the loaded model parts.",
            "seed: random seed.",
            "device: active compute device.",
            "idle_device: device where inactive models can be moved.",
            "tokenizer: tokenizer object.",
            "generator: PyTorch random number generator.",
            "context: encoded text context used by the diffusion model.",
            "latents: current latent representation of the image.",
            "model_output: predicted noise at a given timestep.",
            "images: decoded image tensor before final conversion.",
        ],
    ),
    (
        "Step-by-Step Generation Flow",
        [
            "Step 1: The user types a prompt in the batch launcher.",
            "Step 2: The launcher stores the text in PROMPT and forwards it to run.py.",
            "Step 3: run.py parses the arguments and fills args.prompt.",
            "Step 4: run.py resolves the device and sets up the tokenizer.",
            "Step 5: run.py loads the pretrained models.",
            "Step 6: run.py calls pipeline.generate(...).",
            "Step 7: pipeline.py tokenizes the prompt and sends tokens to the CLIP model.",
            "Step 8: clip.py converts tokens into prompt embeddings.",
            "Step 9: pipeline.py creates random latent noise for text-to-image, or encoded noisy latents for image-to-image.",
            "Step 10: ddpm.py sets the timesteps used for denoising.",
            "Step 11: for each timestep, diffusion.py predicts the noise present in the current latent.",
            "Step 12: ddpm.py applies the denoising equations and produces a cleaner latent.",
            "Step 13: after the loop ends, decoder.py converts the final latent tensor into an RGB image tensor.",
            "Step 14: pipeline.py rescales the tensor into normal pixel values and returns a NumPy array.",
            "Step 15: run.py saves the image using Image.fromarray(...).",
        ],
    ),
    (
        "Role of sd/clip.py",
        [
            "sd/clip.py implements the CLIP text encoder side.",
            "It contains CLIPEmbedding, CLIPLayer, and CLIP classes.",
            "Its job is to transform prompt tokens into contextual text embeddings.",
            "Those embeddings are later used by the diffusion model through cross-attention.",
        ],
    ),
    (
        "Role of sd/encoder.py",
        [
            "sd/encoder.py implements the VAE encoder.",
            "Its role is to transform an input image into a compressed latent representation.",
            "This file is mainly used in image-to-image mode.",
            "It is usually not used in pure text-to-image generation.",
        ],
    ),
    (
        "Role of sd/decoder.py",
        [
            "sd/decoder.py implements the VAE decoder and helper VAE blocks.",
            "Its job is to convert the final latent representation back into a visible RGB image.",
            "The diffusion process itself works in latent space, so the decoder is necessary to produce the final image pixels.",
        ],
    ),
    (
        "Role of sd/diffusion.py",
        [
            "sd/diffusion.py contains the main diffusion neural network.",
            "It uses a UNet-like architecture with residual blocks, attention blocks, upsampling, and time embedding.",
            "Its job is to predict the noise present in the current latent image at each timestep.",
            "The predicted noise is then passed to the DDPM sampler for the next denoising step.",
        ],
    ),
    (
        "Role of sd/attention.py",
        [
            "sd/attention.py contains the self-attention and cross-attention implementations.",
            "Self-attention allows features or tokens to attend to each other.",
            "Cross-attention allows image latent features to attend to the text context.",
            "This is one of the key places where the prompt influences generation.",
        ],
    ),
    (
        "Role of sd/ddpm.py",
        [
            "sd/ddpm.py implements the DDPM sampler.",
            "DDPM means Denoising Diffusion Probabilistic Model.",
            "This file handles the mathematical denoising schedule.",
            "It defines the betas, alphas, alpha cumulative products, timestep selection, noise addition, and denoising step equations.",
            "This is one of the most important mathematical files in the project.",
        ],
    ),
    (
        "When the Mathematics Is Applied",
        [
            "The mathematics is applied throughout generation, but especially during the denoising loop in pipeline.py.",
            "Text encoding in clip.py applies neural network mathematics such as embeddings, matrix multiplications, attention, softmax, and normalization.",
            "Time encoding in pipeline.py uses sinusoidal functions such as cosine and sine.",
            "The diffusion network in diffusion.py applies convolutions, linear layers, residual connections, activations, and attention operations.",
            "The most explicit diffusion probability equations are applied in sd/ddpm.py, especially in DDPMSampler.step(...).",
            "That method uses values such as alpha, beta, cumulative products, variance, predicted original sample, and Gaussian noise to update the latent step by step.",
        ],
    ),
    (
        "What Happens in Text-to-Image Mode",
        [
            "No input image is used.",
            "The pipeline starts from random latent noise created with torch.randn(...).",
            "The text prompt is encoded by CLIP.",
            "The diffusion loop gradually turns the noise into a meaningful latent image representation.",
            "The decoder turns the final latent into a visible image.",
        ],
    ),
    (
        "What Happens in Image-to-Image Mode",
        [
            "An input image is provided.",
            "The image is resized and converted into a tensor.",
            "The VAE encoder converts the image into latent space.",
            "The DDPM sampler adds controlled noise according to the chosen strength.",
            "The diffusion process denoises the latent while following the text prompt.",
            "The decoder reconstructs the edited image.",
        ],
    ),
    (
        "Classifier-Free Guidance",
        [
            "The project uses classifier-free guidance when do_cfg is enabled.",
            "The pipeline computes both a conditional prediction and an unconditional prediction.",
            "Then it combines them with the formula cfg_scale * (output_cond - output_uncond) + output_uncond.",
            "This makes the result follow the prompt more strongly.",
        ],
    ),
    (
        "Image Saving Stage",
        [
            "After pipeline.generate(...) returns a NumPy image array, run.py calls Image.fromarray(image).save(output_path).",
            "Image.fromarray(...) converts the NumPy array into a Pillow image object.",
            "save(output_path) writes the generated image to disk.",
            "The default output path is generated.png in the project root.",
        ],
    ),
    (
        "Why This Is Not a Training Project",
        [
            "There is no dataset loader.",
            "There is no optimizer or loss function loop for training.",
            "There are no epochs or validation logic for training from scratch.",
            "The code uses a pretrained checkpoint rather than learning weights from zero.",
            "Therefore the project is best described as an inference pipeline implementation using pretrained weights.",
        ],
    ),
    (
        "How the Project Was Made Runnable",
        [
            "The missing files were added to the data folder.",
            "The required Python dependencies were installed with Python 3.11.",
            "A CUDA-enabled PyTorch build was installed to use the NVIDIA GPU.",
            "A setuptools compatibility issue was solved so checkpoint loading would work.",
            "A custom run.py launcher was added for easier command-line usage.",
            "A themed run_text_to_image.bat launcher was added for easier interactive usage.",
        ],
    ),
    (
        "How to Run the Project",
        [
            "Double-click run_text_to_image.bat.",
            "Wait for the terminal theme to appear.",
            "Type a prompt when asked.",
            "Press Enter.",
            "The script will use run.py, load the models, generate the image, and save it to generated.png.",
        ],
    ),
    (
        "One-Paragraph Technical Summary",
        [
            "When the user runs the batch launcher and enters a prompt, the prompt is forwarded to sd/run.py and stored in args.prompt. Then run.py resolves the execution device, initializes the CLIP tokenizer, loads the pretrained checkpoint through model_loader.py and model_converter.py, and calls pipeline.generate(...). Inside pipeline.py, the prompt is tokenized and encoded by clip.py, random or image-derived latents are prepared, the DDPM sampler from ddpm.py sets the denoising schedule, the diffusion model in diffusion.py predicts noise at each timestep, the sampler applies the denoising equations, and the decoder in decoder.py reconstructs the final image. The resulting NumPy array is then converted and saved through Image.fromarray(...).",
        ],
    ),
    (
        "Conclusion",
        [
            "NediaVision is a terminal-styled final year project built around a Stable Diffusion inference pipeline.",
            "Its core strength is the integration of pretrained diffusion models, custom launcher styling, GPU support, and a clearly structured generation pipeline.",
            "The project demonstrates how text prompts can be transformed into images through tokenization, latent diffusion, denoising mathematics, and decoding into final pixels.",
        ],
    ),
]


def paragraph(text: str, style: str | None = None) -> str:
    ppr = f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>" if style else ""
    return (
        "<w:p>"
        f"{ppr}"
        "<w:r><w:t xml:space=\"preserve\">"
        f"{escape(text)}"
        "</w:t></w:r></w:p>"
    )


def build_document_xml() -> str:
    parts = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>",
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">",
        "<w:body>",
        paragraph(TITLE, "Title"),
        paragraph("NediaVision by nedia melki | Final Year Project | 2025-2026"),
    ]

    for heading, items in SECTIONS:
        parts.append(paragraph(heading, "Heading1"))
        for item in items:
            parts.append(paragraph(item))

    parts.extend(
        [
            "<w:sectPr>",
            "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>",
            "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
            "w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/>",
            "<w:cols w:space=\"720\"/>",
            "<w:docGrid w:linePitch=\"360\"/>",
            "</w:sectPr>",
            "</w:body></w:document>",
        ]
    )
    return "".join(parts)


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""


STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="10"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/>
      <w:sz w:val="32"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/>
      <w:sz w:val="26"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>NediaVision Project Report</dc:title>
  <dc:creator>OpenAI Codex</dc:creator>
  <cp:lastModifiedBy>OpenAI Codex</cp:lastModifiedBy>
  <dc:description>Project explanation and generation flow report for NediaVision.</dc:description>
</cp:coreProperties>
"""


APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
</Properties>
"""


def main():
    document_xml = build_document_xml()
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        zf.writestr("word/styles.xml", STYLES)
        zf.writestr("docProps/core.xml", CORE)
        zf.writestr("docProps/app.xml", APP)
    print(OUTPUT)


if __name__ == "__main__":
    main()
