"""
       FILE: pat2csv.py
DESCRIPTION: pat_report -s show_data="csv" will format tables as csv embedded within a text file -
             not very useful!  This program will extract each table into its own .csv file.
"""

from pattools.cmdin import parser

def isnum(a):
    """ Test if a string is all numbers [0-9]. """
    return (not a.isalpha()) and a.isalnum()

def readTable(filehandle):
    """ Read a csv-formatted table in a CrayPAT file. """

    tabstr = ""
    for line in filehandle:
        words = line.rstrip('\n').split()
        if len(words):
            words = line.split()[0].split(',')
        else:
            continue

        if (words[0] != "Level") and (not isnum(words[0])):
            # We've reached the end of the table
            break

        tabstr += line

    return tabstr

def tableName(line):
    """ Generate the name of the table. """
    words = line.split()

    tableNum = words[1].replace(":", "")
    tname = "Table" + tableNum
    for w in words[2:]:
        tname += "-" + w
    tname += ".csv"

    return tname

def isTable(line):
    """ Look for the pattern Table X: . """
    words = line.split()

    return ("Table" in words) and (not "option:" in words)

def getTables(filename):

    tables = {}
    with open(filename, "r") as prof:
        for line in prof:
            if isTable(line):
                tables[tableName(line)] = readTable(prof)

    return tables

def main(infile):

    tables = getTables(infile)

    for t in tables:
        with open(t, "w") as tfile:
            tfile.write(tables[t])

if __name__ == "__main__":

    args = parser.parse_args()
    main(args.input)
