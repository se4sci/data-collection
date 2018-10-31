import pandas as pd
import numpy as np
from pdb import set_trace
from sklearn.model_selection import StratifiedKFold


def chunk_data():
    skf = StratifiedKFold(n_splits = 10, shuffle=True)
    dframe = pd.read_csv("mdanalysis.csv")
    X = dframe[dframe.columns[:-1]]
    y = dframe[dframe.columns[-1]]
    
    for i, (train_index, test_index) in enumerate(skf.split(X, y)):
        dframe.ix[test_index].to_csv(
            "mdanalysis/mdanalysis_{}.csv".format(i+1), index=False)
        
if __name__ == "__main__":
    chunk_data()
