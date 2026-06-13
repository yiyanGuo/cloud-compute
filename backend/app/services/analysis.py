from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AnalysisRun


def run_spark_analysis(db: Session) -> AnalysisRun:
    settings = get_settings()
    run = AnalysisRun(status="running", message="Spark analysis started")
    db.add(run)
    db.commit()
    db.refresh(run)

    script_path = Path(__file__).resolve().parents[2] / "spark" / "ecommerce_analysis.py"
    command = [
        settings.spark_submit_bin,
        "--master",
        settings.spark_master_url,
        "--jars",
        settings.spark_jdbc_driver_jar,
        "--driver-class-path",
        settings.spark_jdbc_driver_jar,
        str(script_path),
        "--jdbc-url",
        settings.spark_jdbc_url,
        "--user",
        settings.opengauss_user,
        "--password",
        settings.opengauss_password,
        "--driver",
        settings.spark_jdbc_driver_class,
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=settings.spark_submit_timeout_seconds,
        )
        run.finished_at = datetime.utcnow()
        if result.returncode == 0:
            run.status = "success"
            run.message = tail_output(result.stdout) or "Spark analysis completed"
        else:
            run.status = "failed"
            run.message = tail_output(result.stderr or result.stdout) or "Spark analysis failed"
    except subprocess.TimeoutExpired as exc:
        run.finished_at = datetime.utcnow()
        run.status = "failed"
        run.message = f"Spark analysis timeout after {exc.timeout} seconds"
    except OSError as exc:
        run.finished_at = datetime.utcnow()
        run.status = "failed"
        run.message = f"Unable to execute spark-submit: {exc}"

    db.commit()
    db.refresh(run)
    return run


def tail_output(output: str, max_chars: int = 1800) -> str:
    text = output.strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def latest_run(db: Session) -> AnalysisRun | None:
    return db.query(AnalysisRun).order_by(desc(AnalysisRun.started_at)).first()
