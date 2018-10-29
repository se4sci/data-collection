import os
import argparse
from pdb import set_trace
from pathlib import Path
from src.metrics_getter import MetricsGetter

if __name__ == "__main__":
    # Create a parser
    parser = argparse.ArgumentParser(description="Project to process.")
    # Create an imput argument
    parser.add_argument('-p', '--project-name', type=str, help='Project name')
    # Get arguments
    args = parser.parse_args()
    # Determine commits path
    commits_path = Path('labeled_commits').joinpath(args.project_name)
    # Collect metrics
    with MetricsGetter(args.project_name, commits_path) as metrics:
        # Get metrics
        metrics.get_all_metrics()
        # Clean rows
        metrics.clean_rows()
        # Save as CSV
        metrics.save_to_csv()
