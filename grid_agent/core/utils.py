"""Utility functions."""

import os
from datetime import datetime
import pandas as pd
from pathlib import Path


def ensure_dir(path: str) -> str:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> str:
    """Get data directory path."""
    return ensure_dir("data")


def get_output_dir() -> str:
    """Get output directory path."""
    return ensure_dir("output")


def get_report_dir() -> str:
    """Get report directory path."""
    return ensure_dir("reports")


def get_timestamp_string() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_filename_with_timestamp(base_name: str, ext: str = "csv") -> str:
    """Get filename with timestamp."""
    return f"{base_name}_{get_timestamp_string()}.{ext}"


def df_to_csv(df: pd.DataFrame, filename: str, directory: str = None) -> str:
    """Save DataFrame to CSV."""
    if directory is None:
        directory = get_output_dir()
    
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    return filepath


def load_csv_as_df(filepath: str) -> pd.DataFrame:
    """Load CSV as DataFrame."""
    return pd.read_csv(filepath)


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with specified decimals."""
    return f"{value:.{decimals}f}"
