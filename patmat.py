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

from pattools.cmdin import parser

def add_node(nodearr, node):

    while (node >= len(nodearr)):

        nodearr.append(0)

    return nodearr

def parse_mosaic(infile, node_ranks):
    """ Given a csv-formatted Apprentice2 mosaic and nodes of size n, compute the on-node/off-node
    ratio. """

    onnode = []
    totnode = []
    with open(infile, "r") as csvfile:
        next(csvfile) # Skip the header
        for row in csvfile:

            words = row.split(",")

            source = int(words[0])
            dest = int(words[1])
            metric = float(words[2])

            source_node = source // node_ranks
            dest_node = dest // node_ranks
            onnode = add_node(onnode, source_node)
            totnode = add_node(totnode, source_node)
            totnode[source_node] += metric
            if (dest_node == source_node):
                onnode[source_node] += metric

    ratios = []
    for n in range(len(onnode)):
        ratios.append(onnode[n] / totnode[n])
    return ratios

def report(ratios):

    avg = 0
    for n in range(len(ratios)):

        msg = "Node " + str(n) + ": " + str(ratios[n])
        print(msg)
        avg += ratios[n]

    print(avg / len(ratios))
    
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
