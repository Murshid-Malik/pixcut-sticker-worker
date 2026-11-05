"""Download public model weights at build time; validate safetensors structure."""
from pathlib import Path
import argparse
import urllib.request
from safetensors import safe_open

MODELS = {
    'diffusion_models/flux-2-klein-4b-fp8.safetensors': 'black-forest-labs/FLUX.2-klein-4b-fp8/resolve/main/flux-2-klein-4b-fp8.safetensors',
    'text_encoders/qwen_3_4b.safetensors': 'Comfy-Org/flux2-klein-4B/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors',
    'vae/flux2-vae.safetensors': 'Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors',
    'RemBG/General-Lite.safetensors': 'ZhengPeng7/BiRefNet_lite/resolve/main/model.safetensors',
}
parser = argparse.ArgumentParser()
parser.add_argument('--model', choices=list(MODELS), help='Download one model into its own Docker layer')
args = parser.parse_args()
selected = {args.model: MODELS[args.model]} if args.model else MODELS
for relative, remote in selected.items():
    path = Path('/comfyui/models') / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.part')
    print('Downloading', relative, flush=True)
    with urllib.request.urlopen('https://huggingface.co/' + remote, timeout=120) as response, temporary.open('wb') as output:
        while chunk := response.read(8 * 1024 * 1024):
            output.write(chunk)
    with safe_open(str(temporary), framework='pt', device='cpu') as model:
        if not model.keys():
            raise RuntimeError('Empty model: ' + relative)
    temporary.replace(path)
    print('Validated', relative, path.stat().st_size, flush=True)
