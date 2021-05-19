import pandas as pd
import numpy as np
import sys
import getopt
import math

np.set_printoptions(threshold=sys.maxsize)

def main(argv):

    inputgraph = ''
    inputpartition = ''
    outputfile = ''
    nprocs = ''
    
    try:
        opts, args = getopt.getopt(argv,"hg:p:o:n:",["graph=","partition=","output=","nprocs="])
    except getopt.GetoptError:
        print('Usage: write_comms_stats.py -g <inputgraph> -p <inputparition> -o <outputfile> -n <nprocs>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: write_comms_stats.py -g <inputgraph> -p <inputpartition> -o <outputfile> -n <nprocs>')
            sys.exit()
        elif opt in ("-g", "--graph"):
            inputgraph = arg
        elif opt in ("-p", "--partition"):
            inputpartition = arg
        elif opt in ("-o", "--output"):
            outputfile = arg
        elif opt in ("-n", "--nprocs"):
            nprocs = arg
    print('Input graph is ', inputgraph)
    print('Input parition is ', inputpartition)
    print('Output file is ', outputfile)
    print('Nprocs is ', int(nprocs))
    
    ranks = int(nprocs)
    procs = np.arange(ranks)
    cols = ["A", "B", "C", "D"]
    
    df1 = pd.read_csv(inputgraph,names=cols,sep=' ',header=None)
    df2 = pd.read_csv(inputpartition,sep=' ',header=None)
    
    graph = df1.to_numpy(dtype=int)
    vertices = graph[0,0]
    adj = graph[1:,0:]
    
    partition = df2.to_numpy()
    numcores = partition.max()+1
    core_comms = np.zeros((numcores,numcores))
    
    for i in range(0,vertices):
        loc = int(partition[i]) # current location
        
        for j in range(0,4):
            vert = int(adj[i,j]) # vertex at current location
            if(vert >= 0): 
                vert_loc = int(partition[vert-1]) # shift by -1 

                # if current location and vertex location do not match
                # (i.e. are on different cores) communication takes place
                if vert_loc != loc: 
                    core_comms[loc][vert_loc] += 1

    with open(outputfile, 'w') as f: 
        for i in range(0,ranks):
            for j in range(0,ranks):
                if core_comms[i][j] != 0:
                    print(i,",",j,",",int(core_comms[i][j]),sep='',file=f)

    print(core_comms)
    
if __name__ == "__main__":
   main(sys.argv[1:])
