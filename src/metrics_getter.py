import os
import re
import shlex
import numpy as np
import pandas as pd
from glob2 import glob, iglob
import subprocess as sp
import understand as und
from pathlib import Path
from pdb import set_trace
from collections import defaultdict
from .utils import printProgressBar

REPO_LINKS = {
    "abinit": {
        "url" :"https://github.com/abinit/abinit",
        "lang": "FORTRAN"
        },
    "mdanalysis": {
        "url": "https://github.com/MDAnalysis/mdanalysis", 
        "lang": "python"
        },
    "libmesh": {
        "url": "https://github.com/libMesh/libmesh",           
        "lang": "C"
        },
    "lammps": {
        "url": "https://github.com/lammps/lammps",
        "lang": "C"
    }
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

        # Generate path to store udb files
        self.udb_path = self.cwd.joinpath(".temp", "udb")

        # Create a folder to hold the udb files
        if not self.udb_path.is_dir():
            os.makedirs(self.udb_path)

        # Generate source path where the source file exist
        self.source_path = self.cwd.joinpath(
            ".temp", "sources", self.project_name)

        # If project source doesn't exist, clone it.
        if not self.source_path.is_dir():
            self._os_cmd("git clone {} {}".
                         format(REPO_LINKS[self.project_name]["url"], self.source_path))

        # Read all commit files.
        files = []
        for file in glob(str(self.commits_path.joinpath('*.csv'))):
            files.append(pd.read_csv(file))

        all_commits = pd.concat(files).sort_values(
            by='time').drop_duplicates(subset='message').reset_index()

        # Find before after pairs for all the buggy commits
        self.buggy_clean_pairs = []
        for i in range(1, len(all_commits)):
            if all_commits.iloc[i]['buggy']:
                self.buggy_clean_pairs.append(
                    #     Buggy commit hash              Clean commit hash
                    (all_commits.iloc[i-1]['hash'], all_commits.iloc[i]['hash']))

        return self

    def _create_und_files(self, file_name_suffix):
        """
        Creates understand project files

        Parameters
        ----------
        file_name_suffix : str
            A suffix for the understand_filenames
        """

        # Create a handle for storing *.udb file for the project
        und_file = self.udb_path.joinpath(
            "{}_{}.udb".format(self.project_name, file_name_suffix))

        # Go to the udb path
        os.chdir(self.udb_path)

        # find and replace all F90 to f90
        for filename in glob(os.path.join(self.source_path, '*/**')):
            if ".F90" in filename:
                os.rename(filename, filename[:-4] + '.f90')

        # Generate udb file
        cmd = "und create -languages python C++ Fortran add {} analyze {}".format(
            str(self.source_path), str(und_file))
        self._os_cmd(cmd)

        if file_name_suffix == "buggy":
            self.buggy_und_file = und_file
        elif file_name_suffix == "clean":
            self.clean_und_file = und_file

        # Go to the cloned repo
        os.chdir(self.source_path)

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
        with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL) as p:
            out, err = p.communicate()
        return out, err

    def _files_changed_in_git_diff(self, hash_1, hash_2):
        """
        Get a list of all the files changed between two hashes

        Parameters
        ----------
        hash_1 : str
            Commit hash 1.
        hash_2 : bool
            Commit hash 2.

        Returns
        -------
        List[str]:
            A list of all files changed. For simplicity we only include *.py
            *.F90, *.c, *.cpp, *.java.         
        """

        os.chdir(self.source_path)
        out, __ = self._os_cmd(
            "git diff {} {} --name-only".format(hash_1, hash_2))

        files_changed = []
        for file in out.splitlines():
            for wanted in [".py", ".c", ".cpp", ".F90", ".f90", ".java"]:
                if wanted in str(file):
                    files_changed.append(Path(str(file)).name[:-1])
        
        # A work around for FORTRAN file extensions.
        if REPO_LINKS[self.project_name]["lang"] == "fortran":
            files_changed = list(map(lambda x: x[:-4]+".f90", files_changed))
        
        return files_changed

    def get_all_metrics(self):
        """
        Use the understand tool's API to generate metrics

        Notes
        -----
        + For every clean and buggy pairs of hashed, do the following:
            1. Get the diff of the files changes
            2. Checkout the snapshot at the buggy commit 
            3. Compute the metrics of the files in that commit.
            4. Next, checkout the snapshot at the clean commit.
            5. Compute the metrics of the files in that commit.
        """

        self.metrics_dataframe = pd.DataFrame()

        printProgressBar(0, len(self.buggy_clean_pairs), prefix='Progress:',
                         suffix='Complete', length=50)

        # 1. For each clean-buggy commit pairs
        for i, (buggy_hash, clean_hash) in enumerate(self.buggy_clean_pairs):
            # Go the the cloned project path
            os.chdir(self.source_path)

            # Checkout the master branch first, we'll need this
            # to find what files have changed.
            self._os_cmd("git checkout master")

            # Get a list of files changed between the two hashes
            files_changed = self._files_changed_in_git_diff(
                buggy_hash, clean_hash)
            # ------------------------------------------------------------------
            # ---------------------- BUGGY FILES METRICS -----------------------
            # ------------------------------------------------------------------
            # Checkout the buggy commit hash
            self._os_cmd("git checkout {}".format(buggy_hash))
            # Create a understand file for this hash
            self._create_und_files("buggy")
            db = und.open(str(self.buggy_und_file))
            for file in db.ents("File"):
                # print directory name
                if str(file) in files_changed:
                    metrics = file.metric(file.metrics())
                    metrics["Name"] = file.name()
                    metrics["Bugs"] = 1
                    self.metrics_dataframe = self.metrics_dataframe.append(
                        pd.Series(metrics), ignore_index=True)

            # ------------------------------------------------------------------
            # ---------------------- CLEAN FILES METRICS -----------------------
            # ------------------------------------------------------------------
            # Checkout the clean commit hash
            self._os_cmd("git checkout {}".format(clean_hash))
            # Create a understand file for this hash
            self._create_und_files("clean")
            db = und.open(str(self.clean_und_file))
            for j, file in enumerate(db.ents("File")):
                # print directory name
                if str(file) in files_changed:
                    metrics = file.metric(file.metrics())
                    metrics["Name"] = file.name()
                    metrics["Bugs"] = 0
                    self.metrics_dataframe = self.metrics_dataframe.append(
                        pd.Series(metrics), ignore_index=True)

            printProgressBar(i, len(self.buggy_clean_pairs),
                             prefix='Progress:', suffix='Complete', length=50)

    def clean_rows(self):
        """
        Remove duplicate rows
        """
        # Select columns which are considered for duplicate removal
        metric_cols = [
            col for col in self.metrics_dataframe.columns if not col in [
                "Name", "Bugs"]]

        # Drop duplicate rows
        self.metrics_dataframe.drop_duplicates(subset="CountLine", inplace=True)

        # Rearrange columns
        self.metrics_dataframe = self.metrics_dataframe[
            ["Name"]+metric_cols+["Bugs"]]

    def save_to_csv(self):
        """ 
        Save the metrics dataframe to CSV
        """
        # Determine the path to save file
        save_path = self.cwd.joinpath('datasets', self.project_name+".csv")
        # Save the dataframe (no index column)
        self.metrics_dataframe.to_csv(save_path, index=False)

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Actions to take on exit.

        Notes
        -----
        Go back up one level, and then remove the cloned repo. We're done here.
        """
        os.chdir(self.cwd)
        self._os_cmd("rm -rf {}/*und".format(self.udb_path))
        # Optional -- remove the clone repo to save some space.
        # self._os_cmd("rm -rf {}".format(self.source_path))
