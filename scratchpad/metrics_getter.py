from glob2 import glob
from pdb import set_trace
import understand as und
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import shlex
import subprocess as sp

def get_buggy_clean_revision_pairs(commit_messages_path=os.path.abspath("../labeled_commits/abinit/*.csv")):
    for i in glob(commit_messages_path):
        set_trace()
    

def checkout_revision(commit_hash):
    pass

def generate_understand_reports(und_filename, sources_path):
    cmd = shlex.split(
    "und -db {}.udb create -languages python C++ Fortran add {} analyze report".format(und_filename, sources_path))
    sp.call(cmd)
    
def understand_report_to_class_metrics():
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

