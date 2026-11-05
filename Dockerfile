FROM runpod/worker-comfyui:5.10.0-base

# Pin core with native FLUX.2 Klein support. Keep the worker's CUDA torch build.
RUN git -C /comfyui fetch --depth 1 origin tag v0.34.0 \
 && git -C /comfyui checkout v0.34.0 \
 && /opt/venv/bin/python -m pip freeze | grep -E '^(torch|torchvision|torchaudio)==' > /tmp/sticker-constraints.txt \
 && printf 'transformers<5\nhuggingface-hub<1.0\n' >> /tmp/sticker-constraints.txt \
 && /opt/venv/bin/python -m pip install -c /tmp/sticker-constraints.txt -r /comfyui/requirements.txt

RUN git clone https://github.com/set-soft/ComfyUI-RemoveBackground_SET /comfyui/custom_nodes/ComfyUI-RemoveBackground_SET \
 && git -C /comfyui/custom_nodes/ComfyUI-RemoveBackground_SET checkout 879376ba9dd1aa2b186385ca88eb5f06edd12232 \
 && /opt/venv/bin/python -m pip install -c /tmp/sticker-constraints.txt -r /comfyui/custom_nodes/ComfyUI-RemoveBackground_SET/requirements.txt

COPY download_models.py /sticker/download_models.py
# GHCR limits individual layers to 10 GB; keep each model in its own layer.
RUN /opt/venv/bin/python /sticker/download_models.py --model diffusion_models/flux-2-klein-4b-fp8.safetensors
RUN /opt/venv/bin/python /sticker/download_models.py --model text_encoders/qwen_3_4b.safetensors
RUN /opt/venv/bin/python /sticker/download_models.py --model vae/flux2-vae.safetensors
RUN /opt/venv/bin/python /sticker/download_models.py --model RemBG/General-Lite.safetensors
COPY six-stickers-api.json check_server.py verify_build.py /sticker/
RUN /opt/venv/bin/python /sticker/verify_build.py

# Inherit the official worker handler and startup command.
# Portraits are supplied per request, never baked into the image.
