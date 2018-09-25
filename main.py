from pathlib import Path
from src.metrics_getter import MetricsGetter

if __name__ == "__main__":
    for project_name in ['abinit']:
        commits_path = Path('labeled_commits').joinpath(project_name)
        with MetricsGetter(project_name, commits_path) as metrics:
            metrics.get_all_metrics()
