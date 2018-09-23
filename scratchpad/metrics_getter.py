import os, sys
from pdb import set_trace
sys.path.append("/Applications/Understand.app/Contents/MacOS/Python")
import understand as und
from collections import defaultdict

if __name__ == "__main__":
    db = und.open("abinit.udb")
    
    # for file in db.ents("File"):
    #     # print directory name
    #     print (file.longname())

    metrics = defaultdict(list)
    for classes in db.ents("class"):
        metric = classes.metric(classes.metrics())
        # metrics[classes.name()] = list(metric.values())
        print(classes.name(), classes.parent(), " ".join(map(str, list(metric.values()))), sep=' ')
        set_trace()
    


