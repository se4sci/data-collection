import pandas as pd
import numpy as np
from pdb import set_trace


def chunk_data():
    dframe = pd.read_csv("abinit.csv")
    set_trace()
    chunks = np.array_split(dframe, indices_or_sections=50)
    for i, chunk in enumerate(chunks):
        chunk = chunk.set_index(keys=chunk.columns[0])
        chunk.to_csv("abinit/abinit_{}.csv".format(i+1), index=True)


if __name__ == "__main__":
    chunk_data()
