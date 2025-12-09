#!/usr/bin/env python3
"""
Automated HF Space Training Runner
==================================

CLI wrapper around `training.auto_training_pipeline.AutoTrainingPipeline`.
Use this script to generate thousands of prompt/response examples from the
Jarvis HF Space and export them for fine-tuning.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from training.auto_training_pipeline import (
    AutoTrainingPipeline,
    DomainConfigError,
    build_pipeline_config,
)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run automated data generation against a Hugging Face Space.",
    )
    parser.add_argument(
        "--space-url",
        required=True,
        help="Full URL to the Hugging Face Space (e.g. https://xxxx.gradio.live/).",
    )
    parser.add_argument(
        "--hf-token",
        default=os.getenv("HF_TOKEN"),
        help="Hugging Face access token (defaults to HF_TOKEN env).",
    )
    parser.add_argument(
        "--per-role",
        type=int,
        default=3,
        help="Number of prompts to generate per job role.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=None,
        help="Optional subset of domains to run (defaults to all).",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=None,
        help="Override max_new_tokens for HF generation.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Override temperature for HF generation.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=None,
        help="Seconds to sleep between HF requests.",
    )
    parser.add_argument(
        "--difficulties",
        nargs="*",
        choices=["foundation", "intermediate", "advanced"],
        default=None,
        help="Prompt difficulty mix (defaults to config).",
    )
    parser.add_argument(
        "--min-quality",
        type=float,
        default=4.0,
        help="Minimum average score to tag example as high-quality.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    parser.add_argument(
        "--evaluator-model",
        default=os.getenv("EVALUATOR_MODEL"),
        help="LLM model for evaluation (requires openai package & API key).",
    )
    parser.add_argument(
        "--openai-api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key. Required when --evaluator-model is provided.",
    )
    parser.add_argument(
        "--domain-config",
        default="training/domain_config.json",
        help="Path to domain configuration JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default="cursor_training_data/autogen",
        help="Directory to store session artifacts.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional log file path (default: logs/auto_training_<timestamp>.log).",
    )
    return parser.parse_args(argv)


def setup_logging(log_level: str, log_file: Optional[str]) -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.log_file is None:
        timestamp = __import__("time").strftime("%Y%m%d_%H%M%S")
        args.log_file = f"logs/auto_training_{timestamp}.log"

    setup_logging(args.log_level, args.log_file)

    logging.info("Starting automated training run.")
    logging.info("Space: %s", args.space_url)

    try:
        pipeline_config = build_pipeline_config(
            space_url=args.space_url,
            hf_token=args.hf_token,
            total_per_role=args.per_role,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            sleep_seconds=args.sleep,
            difficulties=args.difficulties,
            min_quality=args.min_quality,
            selected_domains=args.domains,
            seed=args.seed,
            evaluator_model=args.evaluator_model,
            openai_api_key=args.openai_api_key,
        )

        pipeline = AutoTrainingPipeline(
            config=pipeline_config,
            domain_config_path=Path(args.domain_config),
            output_dir=Path(args.output_dir),
        )

        result = pipeline.run()

    except DomainConfigError as exc:
        logging.error("Configuration error: %s", exc)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        logging.exception("Pipeline failed: %s", exc)
        return 1

    summary = result["summary"]
    artifacts = result["artifacts"]

    logging.info("Run summary: %s", summary)
    logging.info("Artifacts saved to: %s", ", ".join(str(path) for path in artifacts.values()))

    print("\n=== Automated Training Run Complete ===")
    print(f"Summary: {summary}")
    print("Artifacts:")
    for key, path in artifacts.items():
        print(f"  - {key}: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

