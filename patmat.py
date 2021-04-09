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

import numpy as np

from pattools.cmdin import parser

def add_node(nodearr, node, nranks):

    while (node >= len(nodearr)):
        nodearr.append([0 for i in range(nranks)])

    return nodearr

    
def parse_mosaic(infile, node_ranks):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, compute the on-node/off-node
    ratio. """

    onnode = []
    totnode = []

    def shift_rank(rank, node):
        
        return rank - node * node_ranks

    def parse_entry(onnode, totnode, row):

        words = row.split(",")

        source = int(words[0])
        dest = int(words[1])
        metric = float(words[2])

        source_node = source // node_ranks
        dest_node = dest // node_ranks
        onnode = add_node(onnode, source_node, node_ranks)
        totnode = add_node(totnode, source_node, node_ranks)

        source = shift_rank(source, source_node)
        totnode[source_node][source] += metric
        if (dest_node == source_node):
            onnode[source_node][source] += metric

        return onnode, totnode

    def compute_ratios(onnode, totnode):

        ratios = []
        for n in range(len(onnode)):
            ratios.append([0 for r in range(node_ranks)])
            for r in range(node_ranks):

                ratios[n][r] = onnode[n][r] / totnode[n][r]

        return ratios

    with open(infile, "r") as csvfile:
        next(csvfile) # Skip the header
        for row in csvfile:

            onnode, totnode = parse_entry(onnode, totnode, row)

    return compute_ratios(onnode, totnode)

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
        
def main(infile, node_ranks):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, compute the on-node/off-node
    ratio. """

    ratios = parse_mosaic(infile, node_ranks)
    report(ratios)
    
if __name__ == "__main__":

    parser.add_argument("-n",
                        dest='node_ranks',
                        type=int,
                        required=True,
                        help="The number of ranks per node of the system.")
    args = parser.parse_args()
    main(args.input, args.node_ranks)
