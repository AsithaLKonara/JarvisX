"""
Automated HF Space Training Pipeline
===================================

This module coordinates large-scale data generation against a deployed Hugging Face
Space (Gradio) endpoint. It covers prompt generation across configured domains,
response collection, automated evaluation, and dataset export for fine-tuning.
"""

from __future__ import annotations

import json
import logging
import math
import random
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------


class DomainConfigError(RuntimeError):
    """Raised when domain configuration is invalid."""


class DomainConfigManager:
    """Loads and serves domain configuration data."""

    def __init__(self, config_path: Path):
        if not config_path.exists():
            raise DomainConfigError(f"Domain config not found: {config_path}")

        try:
            with config_path.open("r", encoding="utf-8") as f:
                self._config = json.load(f)
        except json.JSONDecodeError as exc:
            raise DomainConfigError(f"Invalid JSON in {config_path}: {exc}") from exc

        self._domains = {domain["name"]: domain for domain in self._config.get("domains", [])}

        if not self._domains:
            raise DomainConfigError("No domains defined in configuration.")

        logger.debug("Loaded %s domains from %s", len(self._domains), config_path)

    @property
    def defaults(self) -> Dict[str, object]:
        """Return global defaults."""
        return self._config.get("defaults", {})

    def list_domains(self) -> List[str]:
        """Return available domain names."""
        return list(self._domains.keys())

    def get_domain(self, name: str) -> Dict[str, object]:
        """Retrieve domain configuration."""
        if name not in self._domains:
            raise DomainConfigError(f"Domain '{name}' not defined.")
        return self._domains[name]

    def expand_roles(self, domain_name: str) -> List[str]:
        """Expand role blueprint into concrete titles."""
        domain = self.get_domain(domain_name)
        blueprint = domain.get("role_blueprint")
        if not blueprint:
            raise DomainConfigError(f"Domain '{domain_name}' missing 'role_blueprint'.")

        base_titles = blueprint.get("base_titles", [])
        levels = blueprint.get("levels", [""])
        max_roles = blueprint.get("max_roles", len(base_titles) * len(levels))

        roles: List[str] = []
        for base_title in base_titles:
            for level in levels:
                title = f"{level} {base_title}".strip()
                if title not in roles:
                    roles.append(title)
                if len(roles) >= max_roles:
                    break
            if len(roles) >= max_roles:
                break

        return roles


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------


@dataclass
class PromptSpec:
    """Represent a generated prompt and its metadata."""

    domain: str
    role: str
    difficulty: str
    focus_area: str
    focus_theme: str
    challenge: str
    deliverable: str
    tone: str
    timeframe: str
    metric: str
    prompt: str


class PromptGenerator:
    """Generates prompts across domains/roles based on configuration."""

    def __init__(
        self,
        config_manager: DomainConfigManager,
        seed: Optional[int] = None,
    ):
        self._config = config_manager
        self._rng = random.Random(seed)

    def generate_prompts(
        self,
        domain_name: str,
        role: str,
        count: int,
        difficulties: Sequence[str],
    ) -> List[PromptSpec]:
        domain = self._config.get_domain(domain_name)
        focus_areas = domain.get("focus_areas", [])
        prompt_templates = domain.get("prompt_templates", {})
        tones = domain.get("tones", ["professional"])
        timeframes = domain.get("timeframes", ["over the next quarter"])
        metrics = domain.get("metrics", ["show measurable improvement"])

        if not focus_areas:
            raise DomainConfigError(f"Domain '{domain_name}' lacks 'focus_areas'.")

        specs: List[PromptSpec] = []
        difficulty_cycle = list(difficulties) or ["foundation"]

        for idx in range(count):
            difficulty = difficulty_cycle[idx % len(difficulty_cycle)]
            templates = prompt_templates.get(difficulty)
            if not templates:
                raise DomainConfigError(
                    f"Domain '{domain_name}' missing templates for difficulty '{difficulty}'."
                )
            template = self._rng.choice(templates)
            focus_area = self._rng.choice(focus_areas)
            focus_theme = self._rng.choice(focus_area["themes"])
            challenge = self._rng.choice(focus_area["challenges"])
            deliverable = self._rng.choice(focus_area["deliverables"])
            tone = self._rng.choice(tones)
            timeframe = self._rng.choice(timeframes)
            metric = self._rng.choice(metrics)

            prompt_text = template.format(
                role=role,
                focus_theme=focus_theme,
                challenge=challenge,
                deliverable=deliverable,
                tone=tone,
                timeframe=timeframe,
                metric=metric,
                domain=domain.get("label", domain_name),
            )

            specs.append(
                PromptSpec(
                    domain=domain_name,
                    role=role,
                    difficulty=difficulty,
                    focus_area=focus_area["name"],
                    focus_theme=focus_theme,
                    challenge=challenge,
                    deliverable=deliverable,
                    tone=tone,
                    timeframe=timeframe,
                    metric=metric,
                    prompt=prompt_text,
                )
            )

        return specs


# ---------------------------------------------------------------------------
# HF Space client
# ---------------------------------------------------------------------------


class HFSpaceClient:
    """Wrapper around gradio_client for robust requests."""

    def __init__(
        self,
        space_url: str,
        hf_token: Optional[str] = None,
        max_retries: int = 3,
        retry_backoff_seconds: Sequence[float] = (5, 10, 20),
    ):
        self._space_url = space_url
        self._hf_token = hf_token
        self._max_retries = max_retries
        self._retry_backoff = list(retry_backoff_seconds)
        self._client = self._make_client()

    def _make_client(self):
        """Instantiate a new Gradio client."""
        try:
            from gradio_client import Client
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'gradio_client'. Install with `pip install gradio_client`."
            ) from exc

        return Client(self._space_url, hf_token=self._hf_token)

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
    ) -> str:
        """Invoke the Gradio endpoint with retries."""
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                result = self._client.predict(
                    prompt,
                    max_new_tokens,
                    temperature,
                    api_name="/generate_response",
                )
                # Handle queued Job objects
                response_text = self._resolve_result(result)
                logger.debug("HF response received (len=%s)", len(response_text))
                return response_text
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc

                # Refresh client on 404 or serialization issues
                if hasattr(exc, "response") and getattr(exc.response, "status_code", None) == 404:
                    logger.info("Refreshing Gradio client after 404 response.")
                    self._client = self._make_client()

                sleep_seconds = (
                    self._retry_backoff[min(attempt, len(self._retry_backoff) - 1)]
                    if self._retry_backoff
                    else 5
                )
                logger.warning(
                    "HF request failed (attempt %s/%s): %s -> retrying in %ss",
                    attempt + 1,
                    self._max_retries,
                    exc,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)

        raise RuntimeError(f"HF request failed after retries: {last_error}") from last_error

    @staticmethod
    def _resolve_result(result) -> str:
        """Normalize different result shapes from gradio_client."""
        try:
            from gradio_client import Job  # type: ignore
        except ImportError:
            Job = None  # type: ignore

        if Job is not None and isinstance(result, Job):
            result = result.result()

        if isinstance(result, (list, tuple)):
            # Some Gradio apps return a list with a single string element.
            if not result:
                return ""
            return str(result[0])

        return str(result)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def _clamp(value: float, lower: float = 1.0, upper: float = 5.0) -> float:
    return max(lower, min(upper, value))


def _count_sentences(text: str) -> int:
    return max(1, text.count(".") + text.count("!") + text.count("?"))


def _has_structured_elements(text: str) -> bool:
    bullets = text.count("- ") + text.count("* ") + text.count("•")
    numbering = sum(text.count(f"{n}.") for n in range(1, 7))
    return bullets + numbering > 0


def _keyword_overlap(text: str, keywords: Sequence[str]) -> float:
    tokens = {token.strip(".,:;-").lower() for token in text.split()}
    matches = sum(1 for kw in keywords if kw.lower() in tokens)
    return matches / max(1, len(keywords))


def _estimate_readability(text: str) -> float:
    words = len(text.split())
    sentences = _count_sentences(text)
    syllables = sum(_estimate_syllables(word) for word in text.split())
    # Flesch-Kincaid reading ease (scaled to 1-5 range)
    if words == 0 or sentences == 0:
        return 1.0
    reading_ease = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    # Map reading ease (0-100) to 1-5 range, preferring 40-70 band.
    normalized = (reading_ease - 30) / 14  # approx -> 1-5
    return _clamp(normalized)


def _estimate_syllables(word: str) -> float:
    vowels = "aeiouy"
    word = word.lower().strip(".:;?!")
    if not word:
        return 0
    syllables = 0
    prev_char_vowel = False
    for char in word:
        if char in vowels:
            if not prev_char_vowel:
                syllables += 1
            prev_char_vowel = True
        else:
            prev_char_vowel = False
    if word.endswith("e") and syllables > 1:
        syllables -= 1
    return max(1, syllables)


@dataclass
class EvaluationResult:
    """Store evaluation metrics."""

    overall: float
    category_scores: Dict[str, float]
    rationale: str
    evaluator: str
    raw: Dict[str, object] = field(default_factory=dict)


class ResponseEvaluator:
    """Evaluates responses using LLM-based or heuristic scoring."""

    HEURISTIC_EVALUATOR_NAME = "heuristic:v1"

    def __init__(
        self,
        domain_config: DomainConfigManager,
        preferred_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        self._config = domain_config
        self._use_openai = False
        self._client = None
        self._model = preferred_model

        if openai_api_key or preferred_model:
            try:
                from openai import OpenAI  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "OpenAI evaluator requested but dependency missing. Install with `pip install openai`."
                ) from exc

            self._client = OpenAI(api_key=openai_api_key)
            self._use_openai = True
            if not self._model:
                self._model = "gpt-4o-mini"
            logger.info("LLM-based evaluator enabled with model %s", self._model)
        else:
            logger.info("Using heuristic evaluator (no LLM model supplied).")

    def evaluate(self, prompt: PromptSpec, response: str) -> EvaluationResult:
        if self._use_openai and self._client:
            try:
                return self._evaluate_with_llm(prompt, response)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("LLM evaluation failed (%s). Falling back to heuristic.", exc)

        return self._evaluate_heuristic(prompt, response)

    # ------------------------------------------------------------------
    # Heuristic evaluation
    # ------------------------------------------------------------------

    def _evaluate_heuristic(self, prompt: PromptSpec, response: str) -> EvaluationResult:
        domain_cfg = self._config.get_domain(prompt.domain)
        keywords = domain_cfg.get("role_blueprint", {}).get("keywords", [])
        focus_tokens = [part for part in prompt.focus_theme.split() if len(part) > 3]
        combined_keywords = list(dict.fromkeys(keywords + focus_tokens))

        word_count = len(response.split())
        sentence_count = _count_sentences(response)
        structure = _has_structured_elements(response)
        overlap = _keyword_overlap(response, combined_keywords)
        readability = _estimate_readability(response)

        depth_score = _clamp(word_count / 80 * 5)
        clarity_score = readability
        structure_score = 5.0 if structure else 3.0
        relevance_score = _clamp(2 + overlap * 3)
        actionability_score = 5.0 if any(
            token in response.lower()
            for token in ("step", "plan", "roadmap", "checklist", "next", "action")
        ) else 3.0
        nuance_score = _clamp(sentence_count / 6 * 5)

        category_scores = {
            "depth": round(depth_score, 2),
            "clarity": round(clarity_score, 2),
            "structure": round(structure_score, 2),
            "relevance": round(relevance_score, 2),
            "actionability": round(actionability_score, 2),
            "nuance": round(nuance_score, 2),
        }

        overall = round(
            statistics.mean(category_scores.values()),
            2,
        )

        rationale = (
            f"Heuristic scoring - {word_count} words, {sentence_count} sentences, "
            f"{'structured' if structure else 'unstructured'} format, "
            f"keyword overlap {overlap:.2f}."
        )

        return EvaluationResult(
            overall=overall,
            category_scores=category_scores,
            rationale=rationale,
            evaluator=self.HEURISTIC_EVALUATOR_NAME,
            raw={
                "word_count": word_count,
                "sentence_count": sentence_count,
                "keyword_overlap": overlap,
            },
        )

    # ------------------------------------------------------------------
    # LLM evaluation
    # ------------------------------------------------------------------

    def _evaluate_with_llm(self, prompt: PromptSpec, response: str) -> EvaluationResult:
        assert self._client is not None
        assert self._model is not None

        system_prompt = (
            "You are an evaluation assistant assigning 1-5 scores (whole numbers) "
            "for AI generated answers. Score strictly: 1=poor, 5=excellent. "
            "Return JSON with keys overall, depth, clarity, structure, relevance, "
            "actionability, nuance, and rationale (string)."
        )
        user_prompt = (
            f"Domain: {prompt.domain}\n"
            f"Role: {prompt.role}\n"
            f"Difficulty: {prompt.difficulty}\n"
            f"Focus theme: {prompt.focus_theme}\n"
            f"Challenge: {prompt.challenge}\n"
            f"Prompt sent to model:\n{prompt.prompt}\n\n"
            f"Model response:\n{response}\n"
        )

        completion = self._client.responses.create(
            model=self._model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = completion.output[0].content[0].text  # type: ignore[attr-defined]
        payload = json.loads(content)

        overall = float(payload.get("overall", 0))
        category_scores = {
            key: float(payload.get(key, 0))
            for key in ("depth", "clarity", "structure", "relevance", "actionability", "nuance")
        }
        rationale = payload.get("rationale", "")

        return EvaluationResult(
            overall=overall,
            category_scores=category_scores,
            rationale=rationale,
            evaluator=f"openai:{self._model}",
            raw=payload,
        )


# ---------------------------------------------------------------------------
# Session recording and export
# ---------------------------------------------------------------------------


@dataclass
class SessionItem:
    prompt: PromptSpec
    response: str
    evaluation: EvaluationResult
    timestamp: float


class SessionRecorder:
    """Keeps track of session items and exports datasets."""

    def __init__(self, output_dir: Path, min_quality: float = 4.0):
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._items: List[SessionItem] = []
        self._min_quality = min_quality

    def add(self, prompt: PromptSpec, response: str, evaluation: EvaluationResult) -> None:
        self._items.append(SessionItem(prompt, response, evaluation, time.time()))

    def results(self) -> List[SessionItem]:
        return list(self._items)

    def summary(self) -> Dict[str, object]:
        total = len(self._items)
        high_quality = [item for item in self._items if item.evaluation.overall >= self._min_quality]
        return {
            "total": total,
            "high_quality": len(high_quality),
            "acceptance_rate": round(len(high_quality) / total, 3) if total else 0.0,
            "average_score": round(
                statistics.mean(item.evaluation.overall for item in self._items),
                2,
            )
            if self._items
            else 0.0,
        }

    def export(self, session_name: str, metadata: Dict[str, object]) -> Dict[str, Path]:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_filename = f"{session_name}_{timestamp}"

        session_payload = {
            "session": session_name,
            "timestamp": timestamp,
            "metadata": metadata,
            "summary": self.summary(),
            "items": [
                {
                    "prompt": item.prompt.prompt,
                    "role": item.prompt.role,
                    "domain": item.prompt.domain,
                    "difficulty": item.prompt.difficulty,
                    "focus_area": item.prompt.focus_area,
                    "focus_theme": item.prompt.focus_theme,
                    "challenge": item.prompt.challenge,
                    "deliverable": item.prompt.deliverable,
                    "evaluation": {
                        "overall": item.evaluation.overall,
                        "category_scores": item.evaluation.category_scores,
                        "rationale": item.evaluation.rationale,
                        "evaluator": item.evaluation.evaluator,
                    },
                    "response": item.response,
                    "timestamp": item.timestamp,
                }
                for item in self._items
            ],
        }

        session_file = self._output_dir / f"{base_filename}.json"
        with session_file.open("w", encoding="utf-8") as f:
            json.dump(session_payload, f, indent=2, ensure_ascii=False)

        jsonl_file = self._output_dir / f"{base_filename}.jsonl"
        with jsonl_file.open("w", encoding="utf-8") as f:
            for item in self._items:
                record = {
                    "messages": [
                        {"role": "user", "content": item.prompt.prompt},
                        {"role": "assistant", "content": item.response},
                    ],
                    "metadata": {
                        "domain": item.prompt.domain,
                        "role": item.prompt.role,
                        "difficulty": item.prompt.difficulty,
                        "focus_area": item.prompt.focus_area,
                        "metric": item.prompt.metric,
                        "score": item.evaluation.overall,
                    },
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        high_quality_file = self._output_dir / f"{base_filename}_hq.jsonl"
        with high_quality_file.open("w", encoding="utf-8") as f:
            for item in self._items:
                if item.evaluation.overall < self._min_quality:
                    continue
                record = {
                    "messages": [
                        {"role": "user", "content": item.prompt.prompt},
                        {"role": "assistant", "content": item.response},
                    ],
                    "score": item.evaluation.overall,
                    "domain": item.prompt.domain,
                    "role": item.prompt.role,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(
            "Session exported: %s (full), %s (jsonl), %s (high-quality jsonl)",
            session_file,
            jsonl_file,
            high_quality_file,
        )

        return {
            "session": session_file,
            "jsonl": jsonl_file,
            "high_quality": high_quality_file,
        }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


@dataclass
class PipelineConfig:
    space_url: str
    hf_token: Optional[str]
    total_per_role: int
    max_new_tokens: int
    temperature: float
    sleep_seconds: float
    difficulties: Sequence[str]
    min_quality: float
    selected_domains: Sequence[str]
    seed: Optional[int]
    evaluator_model: Optional[str]
    openai_api_key: Optional[str]


class AutoTrainingPipeline:
    """High-level orchestrator for automated data generation."""

    def __init__(self, config: PipelineConfig, domain_config_path: Path, output_dir: Path):
        self._domain_config = DomainConfigManager(domain_config_path)
        defaults = self._domain_config.defaults
        difficulties = config.difficulties or defaults.get("difficulty_mix", ["foundation"])

        self._config = PipelineConfig(
            space_url=config.space_url,
            hf_token=config.hf_token,
            total_per_role=config.total_per_role,
            max_new_tokens=config.max_new_tokens or int(defaults.get("max_new_tokens", 256)),
            temperature=config.temperature or float(defaults.get("temperature", 0.7)),
            sleep_seconds=config.sleep_seconds or float(defaults.get("sleep_between_calls", 1.0)),
            difficulties=difficulties,
            min_quality=config.min_quality,
            selected_domains=config.selected_domains or self._domain_config.list_domains(),
            seed=config.seed,
            evaluator_model=config.evaluator_model,
            openai_api_key=config.openai_api_key,
        )

        self._prompt_generator = PromptGenerator(self._domain_config, seed=self._config.seed)

        retry_backoff = defaults.get("retry_backoff_seconds", [5, 10, 20])
        self._client = HFSpaceClient(
            self._config.space_url,
            hf_token=self._config.hf_token,
            retry_backoff_seconds=retry_backoff,
        )

        self._evaluator = ResponseEvaluator(
            self._domain_config,
            preferred_model=self._config.evaluator_model,
            openai_api_key=self._config.openai_api_key,
        )

        self._recorder = SessionRecorder(output_dir, min_quality=self._config.min_quality)

    def run(self) -> Dict[str, object]:
        """Execute the automated session."""
        logger.info("Starting automated training pipeline for domains: %s", ", ".join(self._config.selected_domains))

        for domain in self._config.selected_domains:
            roles = self._domain_config.expand_roles(domain)
            logger.info("Domain '%s' -> %s roles", domain, len(roles))

            for role in roles:
                prompt_specs = self._prompt_generator.generate_prompts(
                    domain,
                    role,
                    self._config.total_per_role,
                    self._config.difficulties,
                )

                for idx, prompt_spec in enumerate(prompt_specs, start=1):
                    logger.info(
                        "[%s] %s (%s) prompt %s/%s",
                        domain,
                        role,
                        prompt_spec.difficulty,
                        idx,
                        len(prompt_specs),
                    )
                    try:
                        response = self._client.generate(
                            prompt_spec.prompt,
                            max_new_tokens=self._config.max_new_tokens,
                            temperature=self._config.temperature,
                        )
                    except Exception as exc:  # pylint: disable=broad-except
                        logger.error("Generation failed for %s/%s: %s", domain, role, exc)
                        continue

                    evaluation = self._evaluator.evaluate(prompt_spec, response)
                    self._recorder.add(prompt_spec, response, evaluation)

                    logger.info(
                        "Score %.2f (%s) | prompt length=%s chars | response length=%s chars",
                        evaluation.overall,
                        evaluation.evaluator,
                        len(prompt_spec.prompt),
                        len(response),
                    )

                    if self._config.sleep_seconds:
                        time.sleep(self._config.sleep_seconds)

        summary = self._recorder.summary()
        logger.info("Session complete. %s", summary)

        metadata = {
            "space_url": self._config.space_url,
            "max_new_tokens": self._config.max_new_tokens,
            "temperature": self._config.temperature,
            "difficulties": list(self._config.difficulties),
            "domains": list(self._config.selected_domains),
            "min_quality": self._config.min_quality,
            "seed": self._config.seed,
            "evaluator": self._evaluator._model if self._evaluator._use_openai else ResponseEvaluator.HEURISTIC_EVALUATOR_NAME,  # pylint: disable=protected-access
        }

        exported_paths = self._recorder.export("hf_autotrain_session", metadata)

        return {
            "summary": summary,
            "artifacts": exported_paths,
        }


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def build_pipeline_config(
    space_url: str,
    hf_token: Optional[str],
    total_per_role: int,
    max_new_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    sleep_seconds: Optional[float] = None,
    difficulties: Optional[Sequence[str]] = None,
    min_quality: float = 4.0,
    selected_domains: Optional[Sequence[str]] = None,
    seed: Optional[int] = None,
    evaluator_model: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> PipelineConfig:
    """Convenience factory for tests or scripts."""
    return PipelineConfig(
        space_url=space_url,
        hf_token=hf_token,
        total_per_role=total_per_role,
        max_new_tokens=max_new_tokens or 0,
        temperature=temperature or 0.0,
        sleep_seconds=sleep_seconds or 0.0,
        difficulties=difficulties or (),
        min_quality=min_quality,
        selected_domains=selected_domains or (),
        seed=seed,
        evaluator_model=evaluator_model,
        openai_api_key=openai_api_key,
    )


__all__ = [
    "AutoTrainingPipeline",
    "DomainConfigManager",
    "PromptGenerator",
    "PipelineConfig",
    "build_pipeline_config",
    "HFSpaceClient",
    "ResponseEvaluator",
    "EvaluationResult",
    "DomainConfigError",
]

