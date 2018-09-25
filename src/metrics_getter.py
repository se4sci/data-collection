import os
import re
import shlex
import numpy as np
import pandas as pd
from git import Repo
from glob2 import glob
import subprocess as sp
import understand as und
from pathlib import Path
from pdb import set_trace
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
        # Reference current directory, so we can go back after we are done.
        self.cwd = Path(os.getcwd())

        # Create path to datasets
        self.datasets_path = self.cwd.joinpath("datasets", self.project_name)

        # Create a folder with the project name for the datasets
        if not self.datasets_path.is_dir():
            os.makedirs(self.datasets_path)

        # Generate path to store udb files
        self.udb_path = self.cwd.joinpath(".temp", "udb")

        # Create a folder to hold the udb files
        if not self.udb_path.is_dir():
            os.makedirs(self.udb_path)
        
        # Create a handle for storing *.udb file for the project 
        self.und_file = self.udb_path.joinpath("{}.udb".format(self.project_name))
        
        # Generate source path where the source file exist
        self.source_path = self.cwd.joinpath(".temp", "sources", self.project_name)
        
        # If project source doesn't exist, clone it.
        if not self.source_path.is_dir():
            self._os_cmd("git clone {} {}".format(REPO_LINKS[
                self.project_name], self.source_path))
        
        # Go to the udb path
        os.chdir(self.udb_path)

        # If the und file doesn't exist, create it.        
        if not self.und_file.is_file():
            # Generate udb file
            cmd = "und create -languages python C++ Fortran add {} analyze {}".format(
                str(self.source_path), str(self.und_file))
            self._os_cmd(cmd)

        # Go to the cloned repo
        os.chdir(self.udb_path)
        
        return self

    @staticmethod
    def _os_cmd(cmd):
        """
        Run a command on the shell
        
        Parameters
        ----------
        cmd: str
            A command to run.
        """
        cmd = shlex.split(cmd)
        with sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE) as p:
            out, err = p.communicate()
        return out, err

    def get_all_metrics(self):
        """
        Use the understand tool's API to generate metrics

        Notes
        -----
        
        """
        db = und.open(str(self.und_file))
        cplusplus_metrics = und.Metric.list('c')
        python_metrics = und.Metric.list('Python')
        fortran_metrics = und.Metric.list('Fortran')
        # -----------------------------------------------------------------------
        # ---------- FORTRAN METRICS --------------------------------------------
        # -----------------------------------------------------------------------
        searchstr = re.compile(".*\.F90", re.I)
        f90_metrics = defaultdict(list)
        for file in db.lookup(searchstr, "File"):
            set_trace()

        # -----------------------------------------------------------------------
        # ----------  PYTHON METRICS --------------------------------------------
        # -----------------------------------------------------------------------
        py_metrics = defaultdict(list)
        searchstr = re.compile(".*\.py", re.I)
        for file in db.lookup(searchstr, "File"):
            set_trace()
        
        # -----------------------------------------------------------------------
        # ----------    C and C++    --------------------------------------------
        # -----------------------------------------------------------------------
        c_metrics = defaultdict(list)
        searchstr = re.compile(".*\.c", re.I)
        for file in db.lookup(searchstr, "File"):
            set_trace()


    def __exit__(self, exception_type, exception_value, traceback):
        """
        Actions to take on exit.

        Notes
        -----
        Go back up one level, and then remove the cloned repo. We're done here.
        """

        os.chdir('..')
        self._os_cmd("rm -rf {}".format(self.source_path))
        os.chdir(self.cwd)


def get_buggy_clean_revision_pairs(commit_messages_path=os.path.abspath("../labeled_commits/abinit/*.csv")):
    for i in glob(commit_messages_path):
        set_trace()


def checkout_revision(commit_hash):
    pass
