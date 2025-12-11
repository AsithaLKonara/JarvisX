# Automated Training Playbook

This guide explains how to use the new automated pipeline to stream thousands of curated prompts through the live Jarvis HF Space and capture high-quality conversation data for continuous improvement.

## Overview

- **Endpoint:** `https://992520aba0989bb006.gradio.live/` (private Space running the Mistral-7B + custom LoRA brain)  
- **Automation entrypoint:** `scripts/run_auto_training.py`  
- **Config:** `training/domain_config.json` (7 domains, 169 job-role permutations, multi-level prompt templates)  
- **Outputs:** JSON/JSONL exports in `cursor_training_data/autogen/` with score metadata for immediate fine-tuning

## Prerequisites

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   (Adds `gradio_client` for space access. `openai` is already included.)

2. **Secrets**
   ```bash
   export HF_TOKEN="hf_xxx"            # Required for the private Space
   export OPENAI_API_KEY="sk-xxx"     # Optional: enables GPT-4o-mini evaluation
   export EVALUATOR_MODEL="gpt-4o-mini"
   ```
   Without `OPENAI_API_KEY` the pipeline falls back to deterministic heuristics.

3. **HF Space health check**
   ```bash
   python3 cloud_llm_client.py  # or curl https://992520aba0989bb006.gradio.live/config
   ```

## Running a Bulk Session

```bash
python3 scripts/run_auto_training.py \
  --space-url https://992520aba0989bb006.gradio.live/ \
  --per-role 3 \
  --domains technical_engineering marketing_growth \
  --min-quality 4.0 \
  --sleep 1.2 \
  --seed 42
```

- `--per-role 3` with 169 roles ⇒ ~507 prompts per pass (adjust upward as GPU budget allows).
- Omitting `--domains` covers all seven domains in the config.
- Logs stream to `logs/auto_training_<timestamp>.log`; artifacts land in `cursor_training_data/autogen/`.
- Outputs include:
  - A full JSON session report
  - A JSONL file with every dialogue
  - A filtered JSONL (≥ `min_quality`) ready for LoRA fine-tuning

### Switching on LLM-based evaluation

```bash
python3 scripts/run_auto_training.py \
  --space-url https://992520aba0989bb006.gradio.live/ \
  --per-role 2 \
  --evaluator-model gpt-4o-mini \
  --openai-api-key "$OPENAI_API_KEY"
```

The evaluator produces 1–5 star scores across six criteria plus a rationale paragraph, mirroring the training GUI rubric.

## One-Week Acceleration Plan

| Day | Focus | Target Volume | Notes |
| --- | ----- | ------------- | ----- |
| 1 | Technical Engineering + Data & AI | 400 prompts | Validate pipeline end-to-end, tune `sleep` to keep queue stable. |
| 2 | Business Strategy + Operations | 600 prompts | Enable GPT-4o-mini scoring; start building HQ dataset snapshots. |
| 3 | Marketing + Design | 700 prompts | Review responses manually, adjust domain templates if gaps appear. |
| 4 | Finance/People Ops + catch-up | 600 prompts | Push new prompt variants (run with different seeds). |
| 5 | Mixed domains, advanced prompts | 800 prompts | Increase `per-role` to 4 for top-performing roles. |
| 6 | Regression sweep | 600 prompts | Re-run earlier prompts to measure quality drift (store alongside new runs). |
| 7 | Consolidation | 1,000 prompts | Export combined HQ JSONL, feed into LoRA training + deploy refreshed Space. |

This cadence yields ~4,700 scored examples in a week with balanced coverage and allows daily QA before continuing scale-up.

## Data Management Checklist

- **Daily snapshot:** keep each run’s `_hq.jsonl` for incremental fine-tunes.  
- **Backing up:** sync `cursor_training_data/autogen/` to cloud storage nightly.  
- **Analytics:** monitor `summary.acceptance_rate` to spot regressions.  
- **Retraining:** once 3–5k new HQ examples are assembled, run the standard LoRA workflow in `training/finetuning_manager.py`.

With the Space live and this automation in place, you can continuously expand the dataset, re-train weekly, and keep Jarvis’ brain sharper than ever.

