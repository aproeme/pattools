# PATtools

PATtools is a Python utility for extracting information generated by CrayPAT.

## Setup

After cloning, ensure that the directory containing pattools is on PYTHONPATH.
For example:

```
cd ~/src/python
git clone pattools
export PYTHONPATH=~/src/python:${PYTHONPATH}
```

you can confirm this by running `import pattools` at the python interpreter.

## Usage

Basic usage is to generate a profile using CrayPAT following a procedure similar
to:

```
module load perftools-base
module load perftools

make clean
make [FLAGS]

pat_build -o prog+pat prog
```

Replace the name of the program in any job submission scripts with prog+pat and
run, this will produce either a file like prog.xf or a directory prog.s/
These are then processed using pat_report to generate csv-formatted information
as follows:

```
pat_report -P -s show_data="csv" -o prog.pat-csv prog.xf
```

replacing prog.xf with prog.s/ as appropriate.
Unfortunately the csv-formatted data is embedded in a text report and thus not
(easily) machine or human readable, this is where pattools comes in!

The program pat2csv.py simply runs through the file generated by pat_report and
extracts each table into a separate .csv file:

```
python /path/to/pat2csv.py -i prog.pat-csv
```

this will generate multiple files of the form TableX-YYYY.csv that can then be
processed in whatever manner you like.

pat_report is also capable of producing call graphs, pat2dot.py converts these
into a .dot file for later processing by the dot program from graphviz:

```
pat_report -P -O ct -s show_data="csv" -o prog.ct-csv prog.xf
python /path/to/pat2dot.py -i prog.ct-csv -o prog.dot
```

The dot file can then be used to create a graphical callgraph in multiple formats,
for example:

```
dot -Tpng -o prog.png prog.dot
```