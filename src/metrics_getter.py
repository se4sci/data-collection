import os
import understand as und
from glob2 import glob
from pdb import set_trace
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import shlex
import subprocess as sp
from pathlib import Path


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

    def __init__(self, source_path, commits_path):
        self.source_path = Path(source_path).absolute()
        self.commits_path = Path(commits_path).absolute()
    
    def __enter__(self):
        """
        Actions take at entry.

        Notes
        -----
        Save the current working directory and cd to source directory.
        """
        self.cwd = os.getcwd()
        
        # Generate project filename
        self.project_filename = self.source_path.name

        # Create path to datasets
        self.datasets_path = self.cwd.joinpath("datasets", self.project_filename)
        
        # Create a folder with the project name for the datasets
        os.mkdirs(self.datasets_path)

        # 
        os.chdir(self.source_path)

    def generate_understand_reports(self, und_filename, sources_path):
        """

        """
        cmd = shlex.split(
        "und -db {}.udb create -languages python C++ Fortran add {} analyze report".format(und_filename, sources_path))
        sp.call(cmd)

    def __exit__(self):
        os.chdir(self.cwd)

def get_buggy_clean_revision_pairs(commit_messages_path=os.path.abspath("../labeled_commits/abinit/*.csv")):
for i in glob(commit_messages_path):
    set_trace()
    

def checkout_revision(commit_hash):
    pass

    
def understand_report_to_class_metrics(report_path):
    all_rows_m = []
    all_rows_oo = []
    for file in glob(os.path.join(report_path, 'classm*.html')):
        soup = BeautifulSoup(open(file))
        table = soup.select_one("table")
        headers_m = [th.text for th in table.select("tr th")]
        all_rows_m.extend([[td.text for td in row.find_all("td")]
                for row in table.select("tr + tr")])

    for file in glob(os.path.join(report_path, 'classoom*.html')):
        soup = BeautifulSoup(open(file))
        table = soup.select_one("table")
        headers_oo = [th.text for th in table.select("tr th")]
        all_rows_oo.extend([[td.text for td in row.find_all("td")]
                for row in table.select("tr + tr")])
    
    all_rows_m = pd.DataFrame(np.array(all_rows_m), columns=headers_m)
    all_rows_oo = pd.DataFrame(np.array(all_rows_oo), columns=headers_oo)
    return all_rows_oo.merge(all_rows_m)


if __name__ == "__main__":
    report_path = os.abspath('./sources/abinit/abinit_html')
    understand_report_to_class_metrics(report_path)

