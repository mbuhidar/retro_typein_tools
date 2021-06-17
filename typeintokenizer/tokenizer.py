#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter
import sys

def main():
    # create parser object
    parser = argparse.ArgumentParser(description = "A tokenizer for Commodore BASIC typein programs.", formatter_class=RawTextHelpFormatter)

    # define arguments for parser object
    parser.add_argument("-l", "--loadaddr", type=str, nargs=1, required=False,
                        metavar = "load_address", default = "0x0801",
                        help = "Specifies the target BASIC memory address when loading:\n"
                                "- 0x0801 - C64 (default)\n"
                                "- 0x1001 - VIC20 Unexpanded\n"
                                "- 0x0401 - VIC20 +3K\n"
                                "- 0x1201 - VIC20 +8K\n"
                                "- 0x1201 - VIC20 +16\n"
                                "- 0x1201 - VIC20 +24K")

    parser.add_argument("-v", "--version", choices=[1, 2, 3, 4, 7], type=int, nargs=1, required=False,
                        metavar = "basic_version", default=2,
                        help = "Specifies the BASIC version for use in tokenizing file.\n"
                        "- 1 - Basic v1.0  PET\n"
                        "- 2 - Basic v2.0  C64/VIC20/PET (default)\n"
                        "- 3 - Basic v3.5  C16/C116/Plus/4\n"
                        "- 4 - Basic v4.0  PET/CBM2\n"
                        "- 7 - Basic v7.0  C128")

    parser.add_argument("-s", "--source", choices=["pet", "ahoy"], type=str, nargs=1, required=False,
                        metavar = "source_format", default="ahoy",
                        help = "Specifies the source BASIC file format:\n"
                        "pet - use standard pet control character mnemonics\n"
                        "ahoy - use Ahoy! magazine control character mnemonics (default)")

    parser.add_argument("file_in", type=str, metavar="input_file",
                        help = "Specify the input file name including path")

    parser.add_argument("file_out", type=str, metavar="output_file",
                        help = "Specify the output file name including path")
                        
    # parse the arguments from standard input
    args = parser.parse_args()

    # test args capture
    print(args.loadaddr)
    print(args.version)
    print(args.source)
    print(args.file_in)
    print(args.file_out)
    
if __name__ == '__main__':
    sys.exit(main())
