#
# FILE: pat2dot.py
#

import csv

from pattools.pat2csv import getTables

class CGNode():
    """ Class representing a node on a callgraph. """

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.callees = []

    def addCallee(self, callee):
        self.callees.append(callee)

    def shortName(self):
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

def readCGcsv(filename):
    """ Read a .csv file of a callgraph into a dictionary keyed by callgraph level. """

    cg = {}
    with open(filename, "r") as cgcsv:
        cgreader = csv.DictReader(cgcsv)

        for row in cgreader:
            lvl = int(row['Level'])
            cost = row[r'Samp%']
            fname = row[r'Calltree/PE=HIDE']

            node = CGNode(fname, cost)
            if not lvl in cg.keys():
                cg[lvl] = []
            cg[lvl].append(node)
            if lvl > 0:
                cg[lvl - 1][-1].addCallee(node)

    return cg

def genCGcsv(filename):
    """ Read a csv-formatted CrayPAT callgraph and write out as .csv file """

    cgtable = getTables(filename)
    cgname = cgtable.keys()[0]
    cgstr = cgtable[cgname]

    with open(cgname, "w") as cgcsv:
        cgcsv.write(cgstr)

    return cgname

def main(filename="jm51.ct"):
    """ Given a csv-formatted CrayPAT callgraph, generate a .dot file of the callgraph. """
    cgname = genCGcsv(filename)
    cg = readCGcsv(cgname)
    dotstr = genDotStr(cg)

    with open ("jm76.dot", "w") as cgdot:
        cgdot.write(dotstr)

if __name__ == "__main__":
    main()
