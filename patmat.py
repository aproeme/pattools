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

from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import ListedColormap, LogNorm, SymLogNorm

import numpy as np

from pattools.cmdin import parser

SHIFT=1.0e-8 # Values will be shifted by this amount

def mosaic_to_mat(mosaic, shift):

    N = len(mosaic)
    m = np.zeros((N, N))
    for i in range(N):
        for d in range(len(mosaic[i]) // 2):
            j = mosaic[i][2 * d]
            m[i][j] = mosaic[i][2 * d + 1]
            m[i][j] += shift # Shift zeros to enable logarithmic colour scales

    return m

def vmin(M, tol=1.0e-7):

    vmin = np.amax(M)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i][j]
            if ((v > tol) and (v < vmin)):
                vmin = v

    return vmin

def plot_mosaic(mosaic, outfile, node_ranks, coarsen):
    """ Given a mosaic, plot it to outfile. """

    cmap = cm.plasma_r
    cmap.set_under(color="white")
    if not isinstance(mosaic, np.ndarray):
        M = mosaic_to_mat(mosaic, SHIFT)
    else:
        M = mosaic
    if (np.amin(M) < 0):
        plt.matshow(M, cmap="RdBu_r",
                    norm=SymLogNorm(linthresh=SHIFT))
    else:
        plt.matshow(M, cmap=cmap,
                    norm=LogNorm(vmin=vmin(M, 10*SHIFT)))
        
    plt.colorbar()
    plt.xlabel("Destination")
    plt.ylabel("Source")

    if not coarsen:
        ax = plt.gca()
        ax.xaxis.set_major_locator(MultipleLocator(node_ranks))
        ax.yaxis.set_major_locator(MultipleLocator(node_ranks))
        plt.grid(True, color="black")
    
    plt.savefig(outfile)

def add_node(nodearr, node, nranks):

    while (node >= len(nodearr)):
        nodearr.append([0 for i in range(nranks)])

    return nodearr

def read_mosaic(infile, node_ranks, coarsen):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, convert to array of data. """

    mosaic = []
    
    with open(infile, "r") as csvfile:
        next(csvfile) # Skip the header
        for row in csvfile:

            words = row.split(",")

            source = int(words[0])
            dest = int(words[1])
            metric = float(words[2])

            if coarsen:

                source = source // node_ranks
                dest = dest // node_ranks

            while (source >= len(mosaic)):
                mosaic.append([])

            dest_found = False
            for d in range(len(mosaic[source]) // 2):
                if mosaic[source][2 * d] == dest:
                    dest_found = True
                    break
            if not dest_found:
                mosaic[source].append(dest)
                mosaic[source].append(metric)
            else:
                mosaic[source][2 * d + 1] += metric

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

def delta_mosaic(ref_mosaic, test_mosaic):
    """ Compute the difference between two mosaics. """

    if (len(ref_mosaic) != len(test_mosaic)):
        msg = "Communications matrices must be the same size!"
        raise RuntimeError(msg)

    return mosaic_to_mat(ref_mosaic, SHIFT) - mosaic_to_mat(test_mosaic, SHIFT)

def main(infile, node_ranks, outfile, mode, secondary, coarsen):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, compute the on-node/off-node
    ratio. """

    mosaic = read_mosaic(infile, node_ranks, coarsen)

    if (mode == "ratio"):
        if coarsen:
            msg = "Ratio mode doesn't currently support coarsening"
            raise RuntimeError(msg)
        onnode, totnode = parse_mosaic(mosaic, node_ranks)
        ratios = compute_ratios(onnode, totnode, node_ranks)
        report(ratios)
    else:
        if (outfile == None):
            raise RuntimeError("You need to provide an outfile to plot to!")
        if (mode == "delta"):
            test_mosaic = read_mosaic(secondary, node_ranks, coarsen)
            delta = delta_mosaic(mosaic, test_mosaic)
            plot_mosaic(delta, outfile, node_ranks, coarsen)
        else:
            plot_mosaic(mosaic, outfile, node_ranks, coarsen)
    
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
                        help="The mode (plot|ratio|delta) - plot plots the mosaic, ratio computes the on-node fraction of the metric, delta plots the difference of two mosaics.")
    parser.add_argument("-s",
                        dest='secondary',
                        type=str,
                        required=False,
                        default=None,
                        help="A second mosaic to compare against the input, for use with 'delta' mode.")
    parser.add_argument("-c",
                        dest='coarsen',
                        # type=bool,
                        required=False,
                        default=False,
                        action='store_true',
                        help="Perform coarsening of the comms graph to the per-node level (default: False)")
    args = parser.parse_args()
    main(args.input, args.node_ranks, args.outfile, args.mode, args.secondary, args.coarsen)
