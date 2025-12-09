# Gradio on Google Cloud Run

This starter folder packages a minimal Gradio interface so you can deploy it directly to Google Cloud Run.

## Structure

```
deploy/cloud_run_gradio/
├── app.py             # Gradio entrypoint (listens on 0.0.0.0:8080)
├── requirements.txt   # Pinned dependencies
├── Dockerfile         # Container definition for Cloud Run
└── .dockerignore      # Keeps build context small
```

## Quickstart

```bash
cd deploy/cloud_run_gradio

# Optional: test locally
docker build -t gradio-app .
docker run -p 8080:8080 gradio-app

# Deploy with Cloud Build + Cloud Run (requires gcloud auth)
gcloud run deploy gradio-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

After the deploy command finishes, Google Cloud prints the HTTPS URL for the service. Visit it to see the app live.

