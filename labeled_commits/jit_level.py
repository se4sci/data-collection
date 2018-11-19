from __future__ import print_function
import os, sys, shlex
import pandas as pd
import numpy as np
from pdb import set_trace
import warnings
from datetime import datetime
import dateutil
from pathlib import Path
import understand as und
import subprocess as sp
import sys

warnings.filterwarnings("ignore")
main_path = os.getcwd()
#print(main_path)
p_df = {}

REPO_LINKS = {
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
    }, 
    "abinit": {
        "url": "https://github.com/abinit/abinit",
        "lang": "fortran"
    }
}

def _os_cmd(cmd, verbose=False):
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

        if verbose:
            print(out)
            print(err)
        return out, err

def _files_changed_in_git_diff(hash_1, hash_2):
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
        #project_path build_jit_datasets= "/home/huyqt7/Projects/PhD/eager/data/projects/%s/" % p
        #os.chdir(project_path)
        out, __ = _os_cmd("git diff {}..{} --name-only".format(hash_1, hash_2))
        files_changed = []
        for f in out.splitlines():
            if f and "__init__.py" not in str(f):
                type_f = str(f)[2:-1].split(".")
                #print(str(f), type_f)
                if type_f:
                    if type_f[-1] in set(["c", "cc", "cxx", "C", "cpp", "CPP", "h", "H", 
                                   "f90", "f", "f77", "f03", "f95", "for", "ftn",
                                   "F9build_jit_datasets0", "F", "F77", "F03", "F95", "For", "Ftn", 
                                   "py", "java"]):
                        file_name = f.decode("utf-8") 
                        files_changed.append(file_name)
                        #print(file_name)
                        #if type_f[-1][0] == "F":
                        #    file_name[-4] == "f"
                        #    files_changed.append(file_name)'''
        return files_changed

def jit_metrics_building(p, commit_hash, delta_files, udb_path):
    str_files = " "
    for f in delta_files:
        str_files += str(f) + " " 
    re_commits = []
    commit_cmd = "git reset --hard {}".format(commit_hash)
    sp.call(commit_cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    path = udb_path
    if REPO_LINKS[p]["lang"] == "fortran":
        cmd = "und create -db {} -languages Fortran python C++ ".format(str(path))
        cmd += "settings -FileTypes .F90=Fortran .F77=Fortran .F03=Fortran .F95=Fortran .F=Fortran "
        cmd += "add {} analyze -all".format(str_files)
    elif REPO_LINKS[p]["lang"] == "python":
        cmd = "und create -db {} -languages python add {} analyze -all".format(
            str(path), str_files)
    elif REPO_LINKS[p]["lang"] == "C":
        cmd = "und create -db {} -languages C++ python add {} analyze -all".format(
            str(path), str_files)
    elif REPO_LINKS[p]["lang"] == "Java":
        cmd = "und create -db {} -languages Java add {} analyze -all".format(
            str(path), str_files)
    sp.call(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
        #print(commit_cmd, cmd, dfs[index], p)

def create_udb_temp_folders(p):
    project_path = "/home/huyqt7/Projects/PhD/eager/data/projects/%s/" % p
    os.chdir(project_path)
    cwd = Path(os.getcwd())
    udb_path = cwd.joinpath(".temp", "udb")
    if not udb_path.is_dir():
        os.makedirs(udb_path)
    return project_path, udb_path
    
def get_und_type(udb_path, p, type_label, udb_type):
    udb_file_path = udb_path.joinpath("{}_{}_{}.udb".format(p, type_label, udb_type))
    return udb_file_path

def get_buggy_clean_pairs(main_path, p, index, type_label):
    type_label = type_label.split("_")[0] + "_buggy"
    c_fname = "%s/preprocessed_commits/%s/%s_%s.csv" % (main_path, p, p, index + 1)
    df_commits = pd.read_csv(c_fname, index_col=None)
    fixed_bugs_indices = df_commits[df_commits[type_label] == 1].index.values.tolist()
    fixed_bugs_indices = [idx for idx in fixed_bugs_indices if idx > 1]
    previous_bugs_indices = [idx-1 for idx in fixed_bugs_indices]
    fixed_bugs = df_commits.loc[fixed_bugs_indices]['hash'].values.tolist()
    previous_bugs = df_commits.loc[previous_bugs_indices]['hash'].values.tolist()
    return zip(previous_bugs, fixed_bugs)

def update_changed_df(udb_path, files_changed, type_label, commit_hash, f_status):
    curr_udb = und.open(udb_path)
    metrics_df = pd.DataFrame() 
    for file in curr_udb.ents("File"):
        # print directory name
        for f_c in files_changed:
            if str(file) in f_c:
                metrics = file.metric(file.metrics())
                metrics["File"] = f_c
                metrics["Hash"] = commit_hash
                metrics[type_label] = f_status
                metrics_df = metrics_df.append(pd.Series(metrics), 
                                               ignore_index=True)
    # Purge und file
    curr_udb.close()
    _os_cmd("rm {}".format(udb_path))
    return metrics_df

def build_jit_datasets(type_label, p):
    commits_dir = main_path + "/preprocessed_commits/" + p
    files = [filename for filename in os.listdir(commits_dir) if filename.endswith(".csv")]
    files = sorted(files)
    no_versions = len(files)
    p_path, udb_folder = create_udb_temp_folders(p)
    print(os.getcwd())
    #print(p, end=" ")
    for index in range(no_versions):
        m_fname = "%s/release_level/%s/%s_%s_%s_jit_file.csv" % (main_path, p, p, index, type_label.split("_")[0])
        if not Path(m_fname).is_file():
            print(index, end=" ")
            buggy_clean_pairs = get_buggy_clean_pairs(main_path, p, index, type_label)
            metrics_dataframe = pd.DataFrame()
            for buggy, cleanny in buggy_clean_pairs:
                sp.call("git reset --hard master", shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
                files_changed = _files_changed_in_git_diff(buggy, cleanny)
                if files_changed:
                    print("hello")
                    # ------------------------------------------------------------------
                    # ---------------------- BUGGY FILES METRICS -----------------------
                    # ------------------------------------------------------------------
                    # Create a understand file for this hash
                    udb_path_buggy = str(get_und_type(udb_folder, p, type_label, "buggy"))
                    jit_metrics_building(p, buggy, files_changed, udb_path_buggy)
                    temp_df_1 = update_changed_df(udb_path_buggy, files_changed, type_label, buggy, 1)


                    sp.call("git reset --hard master", shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
                    # ------------------------------------------------------------------
                    # ---------------------- CLEAN FILES METRICS -----------------------
                    # ------------------------------------------------------------------
                    # Create a understand p, file for this hash
                    udb_path_cleanny = str(get_und_type(udb_folder, p, type_label, "cleanny"))
                    jit_metrics_building(p, cleanny, files_changed, udb_path_cleanny)
                    temp_df_2 = update_changed_df(udb_path_cleanny, files_changed, type_label, cleanny, 0)
                    metrics_dataframe = pd.concat([metrics_dataframe, temp_df_1, temp_df_2], 
                                                    ignore_index=True)
                    #print(files_changed, metrics_dataframe.shape, temp_df_1.shape[0], temp_df_2.shape[0])
                
            columns_order = ['File'] + [a for a in metrics_dataframe.columns if a not in ['File', 'Hash', type_label]] 
            metrics_dataframe = metrics_dataframe.reindex(columns=(columns_order))
            #metrics_dataframe = metrics_dataframe.drop_duplicates(subset='File', keep="last").reset_index()
            #metrics_dataframe = metrics_dataframe.dropna()
            print(metrics_dataframe.shape)
            metrics_dataframe.to_csv(m_fname)
    print()
    print()

if __name__== "__main__":
    file_type = sys.argv[1]
    project = sys.argv[2]
    #print(sys.argv)
    build_jit_datasets(file_type, project)