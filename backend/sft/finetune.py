"""
Le Sésame — Mistral SFT Fine-Tuning Pipeline

Uploads training/validation JSONL files to the Mistral API and launches
a supervised fine-tuning job that embeds the secret into the model's
weights for Level 5 (Xal'Thar, Le Cryptique).

Prerequisites:
    pip install mistralai
    export MISTRAL_API_KEY=your_key_here

Usage:
    cd backend

    # Quick start (all defaults):
    python -m sft.finetune

    # Custom:
    python -m sft.finetune \\
        --train sft/data/train.jsonl \\
        --val sft/data/val.jsonl \\
        --model mistral-small-latest \\
        --training-steps 100 \\
        --learning-rate 0.0001 \\
        --auto-start

    # Resume / check status of an existing job:
    python -m sft.finetune --status JOB_UUID

    # Start a validated but not yet started job:
    python -m sft.finetune --start JOB_UUID

Author: Petros Raptopoulos
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


def _get_client():
    """Create and return a Mistral client."""
    try:
        from mistralai import Mistral
    except ImportError:
        print("  ✗ 'mistralai' package not found. Install it:")
        print("    pip install mistralai")
        sys.exit(1)

    api_key = os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        print("  ✗ MISTRAL_API_KEY environment variable not set.")
        print("    export MISTRAL_API_KEY=your_key_here")
        sys.exit(1)

    return Mistral(api_key=api_key)


def upload_file(client, filepath: Path, purpose: str = "fine-tune") -> str:
    """Upload a JSONL file to Mistral and return the file ID."""
    print(f"  Uploading {filepath} ...")
    with open(filepath, "rb") as f:
        result = client.files.upload(
            file={"file_name": filepath.name, "content": f},
            purpose=purpose,
        )
    file_id = result.id
    print(f"  ✓ Uploaded → file_id={file_id}")
    return file_id


def create_job(
    client,
    training_file_id: str,
    validation_file_id: str | None,
    model: str,
    training_steps: int,
    learning_rate: float,
    auto_start: bool,
    suffix: str | None,
    wandb_project: str | None,
    wandb_api_key: str | None,
) -> str:
    """Create a fine-tuning job and return the job ID."""
    kwargs: dict = {
        "model": model,
        "training_files": [{"file_id": training_file_id, "weight": 1}],
        "hyperparameters": {
            "training_steps": training_steps,
            "learning_rate": learning_rate,
        },
        "auto_start": auto_start,
    }

    if validation_file_id:
        kwargs["validation_files"] = [validation_file_id]

    if suffix:
        kwargs["suffix"] = suffix

    # Weights & Biases integration
    if wandb_project and wandb_api_key:
        kwargs["integrations"] = [
            {
                "type": "wandb",
                "project": wandb_project,
                "api_key": wandb_api_key,
            }
        ]

    print(f"\n  Creating fine-tuning job ...")
    print(f"    Model:          {model}")
    print(f"    Training steps: {training_steps}")
    print(f"    Learning rate:  {learning_rate}")
    print(f"    Auto start:     {auto_start}")
    if suffix:
        print(f"    Suffix:         {suffix}")

    job = client.fine_tuning.jobs.create(**kwargs)
    job_id = job.id
    print(f"  ✓ Job created → job_id={job_id}")
    print(f"    Status: {job.status}")
    return job_id


def check_status(client, job_id: str) -> dict:
    """Check and display the status of a fine-tuning job."""
    job = client.fine_tuning.jobs.get(job_id=job_id)

    info = {
        "job_id": job.id,
        "status": job.status,
        "model": job.model,
        "created_at": str(job.created_at) if hasattr(job, "created_at") else "N/A",
    }

    # Access fine_tuned_model if available
    if hasattr(job, "fine_tuned_model") and job.fine_tuned_model:
        info["fine_tuned_model"] = job.fine_tuned_model

    print(f"\n  Job Status")
    print(f"  {'─' * 40}")
    for key, value in info.items():
        print(f"    {key}: {value}")
    print(f"  {'─' * 40}")

    return info


def check_status_detailed(client, job_id: str) -> dict:
    """
    Check and display FULL status of a fine-tuning job including checkpoints,
    events, and all available metadata. Useful for diagnosing failed jobs.
    """
    job = client.fine_tuning.jobs.get(job_id=job_id)

    print(f"\n{'═' * 70}")
    print(f"  DETAILED JOB STATUS: {job_id}")
    print(f"{'═' * 70}\n")

    # Core info
    print(f"  Status:       {job.status}")
    print(f"  Model:        {job.model}")
    print(f"  Created:      {getattr(job, 'created_at', 'N/A')}")
    print(f"  Modified:     {getattr(job, 'modified_at', 'N/A')}")

    # Fine-tuned model (if available)
    if hasattr(job, "fine_tuned_model") and job.fine_tuned_model:
        print(f"  ✓ Fine-tuned: {job.fine_tuned_model}")

    # Hyperparameters
    if hasattr(job, "hyperparameters"):
        print(f"\n  Hyperparameters:")
        hyp = job.hyperparameters
        if isinstance(hyp, dict):
            for k, v in hyp.items():
                print(f"    {k}: {v}")
        else:
            print(f"    training_steps: {getattr(hyp, 'training_steps', 'N/A')}")
            print(f"    learning_rate:  {getattr(hyp, 'learning_rate', 'N/A')}")

    # Error info (for failed jobs)
    if hasattr(job, "error") and job.error:
        print(f"\n  ✗ Error:")
        print(f"    {job.error}")

    # Checkpoints (CRITICAL for recovery)
    if hasattr(job, "checkpoints") and job.checkpoints:
        print(f"\n  Checkpoints ({len(job.checkpoints)}):")
        for i, cp in enumerate(job.checkpoints):
            print(f"    [{i}] Step: {getattr(cp, 'step', 'N/A')}")
            if hasattr(cp, "metrics"):
                metrics = cp.metrics if isinstance(cp.metrics, dict) else {}
                print(f"        train_loss: {metrics.get('train_loss', 'N/A')}")
                print(f"        valid_loss: {metrics.get('valid_loss', 'N/A')}")
            # Check if checkpoint has a model ID
            if hasattr(cp, "checkpoint_id"):
                print(f"        checkpoint_id: {cp.checkpoint_id}")
            if hasattr(cp, "fine_tuned_model"):
                print(f"        ✓ Model saved: {cp.fine_tuned_model}")
    else:
        print(f"\n  Checkpoints: None")

    # Events timeline
    if hasattr(job, "events") and job.events:
        print(f"\n  Events ({len(job.events)}):")
        for evt in job.events[-10:]:  # Show last 10 events
            ts = getattr(evt, "created_at", "N/A")
            msg = getattr(evt, "message", getattr(evt, "level", "N/A"))
            print(f"    [{ts}] {msg}")
    else:
        print(f"\n  Events: None")

    # Dump all attributes for debugging
    print(f"\n  All Available Attributes:")
    all_attrs = [a for a in dir(job) if not a.startswith("_")]
    for attr in all_attrs:
        try:
            val = getattr(job, attr)
            if not callable(val):
                print(f"    {attr}: {val}")
        except:
            pass

    print(f"\n{'═' * 70}\n")

    # Return structured info
    return {
        "job_id": job.id,
        "status": job.status,
        "model": job.model,
        "fine_tuned_model": getattr(job, "fine_tuned_model", None),
        "checkpoints": getattr(job, "checkpoints", []),
        "error": getattr(job, "error", None),
        "hyperparameters": getattr(job, "hyperparameters", {}),
        "events": getattr(job, "events", []),
    }


def start_job(client, job_id: str):
    """Start a validated job."""
    print(f"  Starting job {job_id} ...")
    client.fine_tuning.jobs.start(job_id=job_id)
    print(f"  ✓ Job started")


def wait_for_completion(client, job_id: str, poll_interval: int = 30):
    """Poll a job until it completes or fails."""
    print(f"\n  Waiting for job {job_id} to complete ...")
    print(f"  (polling every {poll_interval}s — press Ctrl+C to stop waiting)\n")

    terminal_statuses = {"SUCCEEDED", "FAILED", "FAILED_VALIDATION", "CANCELLED"}

    try:
        while True:
            job = client.fine_tuning.jobs.get(job_id=job_id)
            status = job.status
            timestamp = time.strftime("%H:%M:%S")
            print(f"  [{timestamp}] Status: {status}")

            if status in terminal_statuses:
                print()
                if status == "SUCCEEDED":
                    ft_model = getattr(job, "fine_tuned_model", None)
                    print(f"  ✓ Fine-tuning SUCCEEDED!")
                    if ft_model:
                        print(f"  ✓ Fine-tuned model ID: {ft_model}")
                        print(f"\n  Use this model ID in your config:")
                        print(f"    model_id: {ft_model}")
                        print(f"    provider: mistral")
                    return job
                else:
                    print(f"  ✗ Job ended with status: {status}")
                    if hasattr(job, "error") and job.error:
                        print(f"    Error: {job.error}")
                    return job

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print(f"\n\n  Stopped waiting. Job {job_id} is still running.")
        print(f"  Check status later:  python -m sft.finetune --status {job_id}")
        return None


def list_jobs(client, limit: int = 10):
    """List recent fine-tuning jobs."""
    print(f"\n  Recent fine-tuning jobs (last {limit}):")
    print(f"  {'─' * 70}")
    jobs = client.fine_tuning.jobs.list()

    job_list = list(jobs.data) if hasattr(jobs, "data") else list(jobs)
    for job in job_list[:limit]:
        ft_model = getattr(job, "fine_tuned_model", None) or ""
        model = getattr(job, "model", "N/A")
        status = getattr(job, "status", "N/A")
        print(f"    {job.id}  [{status}]  base={model}  ft={ft_model}")

    print(f"  {'─' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description="Mistral SFT fine-tuning pipeline for Le Sésame Level 5.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Data files
    parser.add_argument(
        "--train",
        default="sft/data/train.jsonl",
        help="Path to training JSONL file (default: sft/data/train.jsonl)",
    )
    parser.add_argument(
        "--val",
        default="sft/data/val.jsonl",
        help="Path to validation JSONL file (default: sft/data/val.jsonl)",
    )

    # Model & hyperparameters
    parser.add_argument(
        "--model",
        default="mistral-small-latest",
        help="Base model to fine-tune (default: mistral-small-latest)",
    )
    parser.add_argument(
        "--training-steps",
        type=int,
        default=100,
        help="Number of training steps (default: 100)",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.0001,
        help="Learning rate (default: 0.0001)",
    )
    parser.add_argument(
        "--suffix",
        default="le-sesame-l5",
        help="Model name suffix (default: le-sesame-l5)",
    )
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="Automatically start the job after validation",
    )

    # W&B integration
    parser.add_argument(
        "--wandb-project",
        default=None,
        help="Weights & Biases project name for tracking",
    )
    parser.add_argument(
        "--wandb-api-key",
        default=None,
        help="Weights & Biases API key",
    )

    # Job management
    parser.add_argument(
        "--status",
        metavar="JOB_ID",
        help="Check the status of an existing job",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed status including checkpoints, events, and all metadata (use with --status)",
    )
    parser.add_argument(
        "--start",
        metavar="JOB_ID",
        help="Start a validated (but not started) job",
    )
    parser.add_argument(
        "--wait",
        metavar="JOB_ID",
        help="Wait for a job to complete (poll status)",
    )
    parser.add_argument(
        "--list-jobs",
        action="store_true",
        help="List recent fine-tuning jobs",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Seconds between status polls when waiting (default: 30)",
    )

    args = parser.parse_args()
    client = _get_client()

    print(f"\n{'═' * 60}")
    print(f"  LE SÉSAME — MISTRAL SFT FINE-TUNING PIPELINE")
    print(f"{'═' * 60}")

    # ── Job management commands ──
    if args.list_jobs:
        list_jobs(client)
        return

    if args.status:
        if args.detailed:
            check_status_detailed(client, args.status)
        else:
            check_status(client, args.status)
        return

    if args.start:
        start_job(client, args.start)
        check_status(client, args.start)
        return

    if args.wait:
        wait_for_completion(client, args.wait, args.poll_interval)
        return

    # ── Full pipeline: upload → create job → (optionally wait) ──
    train_path = Path(args.train)
    val_path = Path(args.val)

    if not train_path.exists():
        print(f"  ✗ Training file not found: {train_path}")
        print(f"  → Run data generation first:")
        print(f"    python -m sft.generate_data")
        sys.exit(1)

    # Upload training file
    training_file_id = upload_file(client, train_path)

    # Upload validation file (if exists)
    validation_file_id = None
    if val_path.exists():
        validation_file_id = upload_file(client, val_path)
    else:
        print(f"  ⚠ Validation file not found: {val_path} — skipping")

    # Create the job
    job_id = create_job(
        client=client,
        training_file_id=training_file_id,
        validation_file_id=validation_file_id,
        model=args.model,
        training_steps=args.training_steps,
        learning_rate=args.learning_rate,
        auto_start=args.auto_start,
        suffix=args.suffix,
        wandb_project=args.wandb_project,
        wandb_api_key=args.wandb_api_key,
    )

    # If auto-start, wait for completion
    if args.auto_start:
        result = wait_for_completion(client, job_id, args.poll_interval)
        if result and result.status == "SUCCEEDED":
            ft_model = getattr(result, "fine_tuned_model", None)
            if ft_model:
                _save_model_id(ft_model, args.model)
    else:
        print(f"\n  Job created but NOT started (auto_start=False).")
        print(f"  To start it after validation:")
        print(f"    python -m sft.finetune --start {job_id}")
        print(f"\n  To wait for completion:")
        print(f"    python -m sft.finetune --wait {job_id}")

    print()


def _save_model_id(fine_tuned_model: str, base_model: str):
    """Save the fine-tuned model ID to a config file for easy reference."""
    config_path = Path("sft/model_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "fine_tuned_model": fine_tuned_model,
        "base_model": base_model,
        "provider": "mistral",
        "level": 5,
        "guardian": "Xal'Thar",
        "description": "Level 5 guardian with secret embedded in weights via SFT",
        "usage": {
            "model_config": {
                "provider": "mistral",
                "model_id": fine_tuned_model,
                "args": {"temperature": 0.7, "max_tokens": 1024},
            }
        },
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n  ✓ Model config saved to {config_path}")
    print(f"  ✓ Use in Level 5: model_id = {fine_tuned_model}")


if __name__ == "__main__":
    main()
