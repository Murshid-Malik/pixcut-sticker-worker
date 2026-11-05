# PixCut six-sticker RunPod Serverless worker

Upload the CONTENTS of this directory to the root of a new GitHub repository
named `pixcut-sticker-worker`. Do not upload the full photobooth project or its
credentials. No API keys or portraits belong in this repository.

## Deploy through GitHub

1. In RunPod Serverless, create an endpoint using its GitHub repository deployment option.
2. Connect/select the new repository and branch `main`.
3. Set Dockerfile path to `Dockerfile` and build context to the repository root (`.`), if requested.
4. Name the endpoint `pixcut-six-stickers-test`; choose Queue routing.
5. Start with one GPU per worker, 24 GB VRAM or greater, minimum workers 0,
   maximum workers 1, idle timeout 5 seconds, execution timeout 600 seconds,
   and 40 GB container disk. These are starting settings, not measured requirements.
6. Deploy and watch build logs. Models are downloaded during the build.
   A CPU compatibility check must pass before the image finishes building.
7. Keep the existing ADNOC endpoint separate. No network volume is required
   for this image because the weights are baked in. Leave S3 unconfigured
   to receive base64 images from the standard worker.

The image inherits RunPod's handler and startup command. It does not start
an interactive ComfyUI editor for the user. Send API-format workflows per job.

## Prepare one portrait test

On your Mac, in this directory:

```sh
python3 make_runpod_input.py /path/to/portrait.png --out runpod-input.json
```

Paste the ENTIRE contents of `runpod-input.json` into the endpoint's request
test editor, replacing its example body (do not add another `input` wrapper).
Submit once, retain the job ID and poll that job to completion. For an API client,
POST this body to `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run` using your
RunPod Bearer key, then GET `/status/JOB_ID` on the same endpoint.

Expected output: six PNG images with prefixes 01_chibi, 02_comic, 03_clay,
04_watercolour, 05_vector, and 06_original_photo under sticker_options/.
Inspect identity, background removal, white borders and transparent exteriors.
This workflow does not create a print sheet or submit a printer job.

## Validation status

Local Python syntax and workflow structural checks only. The Docker image has
NOT been built here and GPU inference has NOT been run. The build-time check
validates node schemas/model names but cannot prove GPU memory use, speed,
portrait likeness or output quality. Model download URLs use upstream `main`;
archive tested model hashes before production deployment.

Official deployment reference:
https://github.com/runpod-workers/worker-comfyui/blob/main/docs/deployment.md
