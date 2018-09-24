import os
import shlex
import numpy as np
import pandas as pd
from git import Repo
from glob2 import glob
import subprocess as sp
import understand as und
from pathlib import Path
from pdb import set_trace
from bs4 import BeautifulSoup
from collections import defaultdict

REPO_LINKS = {
    "abinit": "https://github.com/abinit/abinit"
}


class MetricsGetter:
    """
    Generate class, file, function, object oriented metrics for a project.

    Parameters
    ----------
    sources_path: str or pathlib.PosixPath

    Notes
    -----
    The class is designed to run in conjunction with a context manager.
    """

    def __init__(self, project_name, commits_path):
        self.project_name = project_name
        self.commits_path = Path(commits_path).absolute()

    def __enter__(self):
        """
        Actions take at entry.

        Notes
        -----
        Save the current working directory and cd to source directory.
        """
        self.cwd = Path(os.getcwd())

        # Create path to datasets
        self.datasets_path = self.cwd.joinpath("datasets", self.project_name)

        if not self.datasets_path.is_dir():
            # Create a folder with the project name for the datasets
            os.makedirs(self.datasets_path)

        # Generate clone path
        self.source_path = self.cwd.joinpath("sources", self.project_name)
        if not self.datasets_path.is_dir():
            cmd = shlex.split("git clone {} {}".format(REPO_LINKS[
                self.project_name], self.source_path))
            sp.call(cmd)
        os.chdir(self.source_path)
        return self

    def generate_understand_reports(self):
        """
        Use the understand tool's API to generate metrics
        """
        set_trace()

        # cmd = shlex.split(
        # "und -db {}.udb create -languages python C++ Fortran add {} analyze report".format(und_filename, sources_path))
        # sp.call(cmd)

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Actions to take on exit.

        Notes
        -----
        Go back up one level, and then remove the cloned repo. We're done here.
        """

        os.chdir('..')
        os.removedirs(self.project_name)
        os.chdir(self.cwd)


def get_buggy_clean_revision_pairs(commit_messages_path=os.path.abspath("../labeled_commits/abinit/*.csv")):
    for i in glob(commit_messages_path):
        set_trace()


def checkout_revision(commit_hash):
    pass


# def understand_report_to_class_metrics(report_path):
#     all_rows_m = []
#     all_rows_oo = []
#     for file in glob(os.path.join(report_path, 'classm*.html')):
#         soup = BeautifulSoup(open(file))
#         table = soup.select_one("table")
#         headers_m = [th.text for th in table.select("tr th")]
#         all_rows_m.extend([[td.text for td in row.find_all("td")]
#                 for row in table.select("tr + tr")])

#     for file in glob(os.path.join(report_path, 'classoom*.html')):
#         soup = BeautifulSoup(open(file))
#         table = soup.select_one("table")
#         headers_oo = [th.text for th in table.select("tr th")]
#         all_rows_oo.extend([[td.text for td in row.find_all("td")]
#                 for row in table.select("tr + tr")])

#     all_rows_m = pd.DataFrame(np.array(all_rows_m), columns=headers_m)
#     all_rows_oo = pd.DataFrame(np.array(all_rows_oo), columns=headers_oo)
#     return all_rows_oo.merge(all_rows_m)


# if __name__ == "__main__":
#     report_path = os.abspath('./sources/abinit/abinit_html')
#     understand_report_to_class_metrics(report_path)
