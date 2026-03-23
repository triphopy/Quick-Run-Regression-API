from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_ENVIRONMENT = "UAT"
DATA_DIR_NAME = "data"
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"
TEMP_DIR_NAME = "temp"
ROBOT_DIR_NAME = "robot"


def resource_root() -> Path:
    env_path = os.environ.get("SONIC_RESOURCE_ROOT")
    if env_path:
        return Path(env_path)
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent


def project_root() -> Path:
    env_path = os.environ.get("SONIC_RUNTIME_ROOT")
    if env_path:
        return Path(env_path)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    path = project_root() / DATA_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def input_dir() -> Path:
    path = data_dir() / INPUT_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def output_root_dir() -> Path:
    path = data_dir() / OUTPUT_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def temp_dir() -> Path:
    path = data_dir() / TEMP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def output_dir(run_id: str) -> Path:
    path = output_root_dir() / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def robot_dir() -> Path:
    return resource_root() / ROBOT_DIR_NAME


def robot_generated_dir() -> Path:
    path = robot_dir() / "generated"
    path.mkdir(parents=True, exist_ok=True)
    return path
