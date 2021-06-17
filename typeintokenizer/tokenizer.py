#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter
import sys

def main():
    # create parser object
    parser = argparse.ArgumentParser(description = "A tokenizer for Commodore BASIC typein programs.", formatter_class=RawTextHelpFormatter)

    # define arguments for parser object
    parser.add_argument("-l", "--loadaddr", type = str, nargs = 1,
                        metavar = "load_address", default = "$0801",
                        help = "Specifies the target BASIC memory address when loading:\n"
                                "- $8001 - C64 (default)\n"
                                "- $1001 - VIC20 Unexpanded\n"
                                "- $1200 - VIC20 +3K\n"
                                "- $1200 - VIC20 +8K\n"
                                "- $1200 - VIC20 +16\n"
                                "- $1200 - VIC20 +24K")

    parser.add_argument("-v", "--version", choices=[1, 2, 3, 4, 7], type = int, nargs = 1,
                        metavar = "basic_version", default = "2",
                        help = "Specifies the BASIC version for use in tokenizing file.\n"
                        "- 1 - Basic v1.0  PET\n"
                        "- 2 - Basic v2.0  C64/VIC20/PET\n"
                        "- 3 - Basic v3.5  C16/C116/Plus/4\n"
                        "- 4 - Basic v4.0  PET/CBM2\n"
                        "- 7 - Basic v7.0  C128")

    # parse the arguments from standard input
    args = parser.parse_args()

    # test args capture
    print(args.loadaddr)
    print(args.version)

if __name__ == '__main__':
    sys.exit(main())
