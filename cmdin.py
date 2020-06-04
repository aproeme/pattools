"""
       FILE: cmdin.py
DESCRIPTION: Provides a common command parser for pattools.
"""

import argparse

parser = argparse.ArgumentParser(description="Process output from CrayPAT.")
parser.add_argument("-i",
                    dest='input',
                    type=str,
                    required=True,
                    help="The file to parse from CrayPAT.")
