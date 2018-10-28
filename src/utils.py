
def printProgressBar(iteration, total, prefix='Progress:', suffix='Complete', 
                        decimals=2, length=50, fill='█'):
    """
    Call in a loop to create terminal progress bar
    
    Parameters
    ----------
    iteration: int 
        Current iteration
    total: int
        Total iterations
    prefix: str
        Prefix string 
    suffix: str
        Suffix string
    decimals: int
        Positive number of decimals in percent complete
    length: int 
        Character length of bar
    fill: str
        Bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / total))
    filledLength = int(length * iteration / total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()
