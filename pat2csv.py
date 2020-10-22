"""
       FILE: pat2csv.py
DESCRIPTION: pat_report -s show_data="csv" will format tables as csv embedded within a text file.
             This program will extract each table into its own .csv file.

Copyright 2020 The University of Edinburgh

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
