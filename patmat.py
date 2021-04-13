"""
       FILE: patmat.py
DESCRIPTION: Apprentice2 can output the communication mosaic for a given metric, this program takes
             the output.csv and computes the on-node/off-node ratio for a given size of compute
             nodes.

Copyright 2021 The University of Edinburgh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import numpy as np

from pattools.cmdin import parser

def mosaic_to_mat(mosaic):

    N = len(mosaic)
    m = np.zeros((N, N))
    for i in range(N):
        for d in range(len(mosaic[i]) // 2):
            j = mosaic[i][2 * d]
            m[i][j] = mosaic[i][2 * d + 1]

    return m
    
def plot_mosaic(mosaic, outfile, node_ranks):
    """ Given a mosaic, plot it to outfile. """

    plt.matshow(mosaic_to_mat(mosaic), cmap="YlGnBu")
    plt.colorbar()
    plt.xlabel("Destination")
    plt.ylabel("Source")

    ax = plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(node_ranks))
    ax.yaxis.set_major_locator(MultipleLocator(node_ranks))
    plt.grid(True, color="red")
    
    plt.savefig(outfile)

def add_node(nodearr, node, nranks):

    while (node >= len(nodearr)):
        nodearr.append([0 for i in range(nranks)])

    return nodearr

def read_mosaic(infile):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, convert to array of data. """

    mosaic = []
    
    with open(infile, "r") as csvfile:
        next(csvfile) # Skip the header
        for row in csvfile:

            words = row.split(",")

            source = int(words[0])
            dest = int(words[1])
            metric = float(words[2])

            while (source >= len(mosaic)):
                mosaic.append([])
            mosaic[source].append(dest)
            mosaic[source].append(metric)

    return mosaic

def parse_mosaic(mosaic, node_ranks):
    """ Given an Apprentice2 mosaic and nodes of size n, parse into on-node and total-node data. """
    
    onnode = []
    totnode = []

    def shift_rank(rank, node):
        
        return rank - node * node_ranks

    def parse_entry(onnode, totnode, source, sourcedata):

        source_node = source // node_ranks

        ndest = len(sourcedata) // 2
        for d in range(ndest):

            dest = sourcedata[2 * d]
            metric = sourcedata[2 * d + 1]
            
            dest_node = dest // node_ranks
            onnode = add_node(onnode, source_node, node_ranks)
            totnode = add_node(totnode, source_node, node_ranks)

            sourceloc = shift_rank(source, source_node)
            totnode[source_node][sourceloc] += metric
            if (dest_node == source_node):
                onnode[source_node][sourceloc] += metric

        return onnode, totnode

    for e in range(len(mosaic)):

        onnode, totnode = parse_entry(onnode, totnode, e, mosaic[e])
        
    return onnode, totnode

def compute_ratios(onnode, totnode, node_ranks):

    ratios = []
    for n in range(len(onnode)):
        ratios.append([0 for r in range(node_ranks)])
        for r in range(node_ranks):

            ratios[n][r] = onnode[n][r] / totnode[n][r]

    return ratios

def report(ratios):
    """ Report the metric ratio across nodes and the min, mean and max. """

    print("On-node/total-node comms ratios:")
    print(" min, max, mean, stddev")
    print("--------------------------------")
    nnodes = len(ratios)
    for n in range(nnodes):

        rmin = min(ratios[n])
        rmax = max(ratios[n])
        rmean = np.mean(ratios[n])
        rstd = np.std(ratios[n])

        print(f"Node {n}: {rmin:.6e}, {rmax:.6e}, {rmean:.6e}, {rstd:.6e}")
        
def main(infile, node_ranks, outfile, mode):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, compute the on-node/off-node
    ratio. """

    mosaic = read_mosaic(infile)

    if (mode == "ratio"):
        onnode, totnode = parse_mosaic(mosaic, node_ranks)
        ratios = compute_ratios(onnode, totnode, node_ranks)
        report(ratios)
    else:
        if (outfile == None):
            raise RuntimeError("You need to provide an outfile to plot to!")
        plot_mosaic(mosaic, outfile, node_ranks)
    
if __name__ == "__main__":

    parser.add_argument("-n",
                        dest='node_ranks',
                        type=int,
                        required=True,
                        help="The number of ranks per node of the system.")
    parser.add_argument("-o",
                        dest='outfile',
                        type=str,
                        required=False,
                        default=None,
                        help="The file mosaic plot should be saved to.")
    parser.add_argument("-m",
                        dest='mode',
                        type=str,
                        required=False,
                        default="ratio",
                        help="The mode (plot|ratio) - plot plots the mosaic, ratio computes the on-node fraction of the metric.")
    args = parser.parse_args()
    main(args.input, args.node_ranks, args.outfile, args.mode)
