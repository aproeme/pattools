"""
       FILE: pat2dot.py
DESCRIPTION: Converts a csv-formatted callgraph produced by CrayPAT to a .dot file for
             processing by dot (a graphviz program).

Copyright 2020-2021 The University of Edinburgh

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

import csv

from pattools.pat2csv import getTables
from pattools.cmdin import parser

class CGNode():
    """ Class representing a node on a callgraph. """

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.callees = []

    def addCallee(self, callee):
        """ Add a callee to this node. """
        self.callees.append(callee)

    def shortName(self):
        """ CrayPAT callgraphs come like a filepath - the called function is at the end of the
            path.
        """

        return self.name.split('/')[-1]

def angleStr(s):
    """ Returns a copy of string surrounded by angle brackets. """
    return "<" + s + ">"

def genDotStr(cgdict):
    """ Convert a dictionary of a callgraph into a .dot file string. """

    dotstr = "digraph {\n"
    for lvl in cgdict.keys():
        for node in cgdict[lvl]:
            label = node.shortName() + "<BR />" + node.cost
            dotstr += angleStr(node.name) + ' [label=' + angleStr(label) + '];\n'

    for lvl in cgdict.keys():
        for node in cgdict[lvl]:
            for callee in node.callees:
                dotstr += angleStr(node.name) + ' -> ' + angleStr(callee.name) + ';\n'
    dotstr += "}"

    return dotstr

def readCGcsv(filename, levels):
    """ Read a .csv file of a callgraph into a dictionary keyed by callgraph level. """

    cgdict = {}
    with open(filename, "r") as cgcsv:
        cgreader = csv.DictReader(cgcsv)

        for row in cgreader:
            lvl = int(row['Level'])
            if (lvl < levels) or (levels <= 0):
                cost = row[r'Samp%']
                fname = row[r'Calltree/PE=HIDE']

                node = CGNode(fname, cost)
                if lvl not in cgdict.keys():
                    cgdict[lvl] = []
                cgdict[lvl].append(node)
                if lvl > 0:
                    cgdict[lvl - 1][-1].addCallee(node)

    return cgdict

def genCGcsv(filename):
    """ Read a csv-formatted CrayPAT callgraph and write out as .csv file """

    cgtable = getTables(filename)
    cgname = list(cgtable.keys())[0]
    cgstr = cgtable[cgname]

    with open(cgname, "w") as cgcsv:
        cgcsv.write(cgstr)

    return cgname

def main(infile, outfile, levels):
    """ Given a csv-formatted CrayPAT callgraph, generate a .dot file of the callgraph. """
    cgname = genCGcsv(infile)
    cgdict = readCGcsv(cgname, levels)
    dotstr = genDotStr(cgdict)

    with open(outfile, "w") as cgdot:
        cgdot.write(dotstr)

if __name__ == "__main__":

    parser.add_argument("-o",
                        dest='output',
                        type=str,
                        required=True,
                        help="The file to write dot file to.")
    parser.add_argument("-l",
                        dest='levels',
                        type=int,
                        required=False,
                        default=0,
                        help="How many levels of call tree to show? <= 0 shows all (default).")
    args = parser.parse_args()
    main(args.input, args.output, args.levels)
