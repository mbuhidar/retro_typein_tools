"""
Imports Commodore BASIC type-in programs in various magazine formats,
checks for errors, and converts to an executable file for use with an
emulator or on original hardware.
"""

import argparse
from argparse import RawTextHelpFormatter
from os import get_terminal_size
import sys
import math

from retrotype import (read_file,
                       check_line_number_seq,
                       ahoy_lines_list,
                       split_line_num,
                       scan_manager,
                       ahoy1_checksum,
                       ahoy2_checksum,
                       ahoy3_checksum,
                       write_binary,
                       write_checksums,
                       )


def parse_args(argv):
    """Parses command line inputs and generate command line interface and
    documentation.
    """
    parser = argparse.ArgumentParser(description=
        "A tokenizer for Commodore BASIC typein programs. Supports Ahoy "
        "magazine\nprograms for C64.",
        formatter_class=RawTextHelpFormatter,
        epilog=
        "Notes for entering programs from Ahoy issues prior to November "
        "1984:\n\n"
        "In addition to the special character codes contained in braces \n"
        "in the magazine, Ahoy also used a shorthand convention for \n"
        "specifying a key entry preceeded by either the Shift key or the \n"
        "Commodore key as follows:\n\n"
        "    - Underlined characters - preceed entry with Shift key\n"
        "    - Overlined characters - preceed entry with Commodore key\n\n"
        "Standard keyboard letters should be typed as follows for these "
        "two cases.\n"
        "    -{s A}, {s B}, {s *} etc.\n"
        "    -{c A}, {c B}, {c *}, etc.\n\n"
        "There are a few instances where the old hardware has keys not\n"
        "available on a modern keyboard or are otherwise ambiguous.\n"
        "Those should be entered as follows:\n"
        "    {EP} - British Pound symbol\n"
        "    {UP_ARROW} - up arrow symbol\n"
        "    {LEFT_ARROW} - left arrow symbol\n"
        "    {PI} - Pi symbol\n"
        "    {s RETURN} - shifted return\n"
        "    {s SPACE} - shifted space\n"
        "    {c EP} - Commodore-Bristish Pound symbol\n"
        "    {s UP_ARROW} - shifted up arrow symbol\n\n"
        "After the October 1984 issue, the over/under score representation\n"
        "was discontinued.  These special characters should be typed as\n"
        "listed in the magazines after that issue.\n\n"
    )

    parser.add_argument(
        "-l", "--loadaddr", type=str, nargs=1, required=False,
        metavar="load_address", default=["0x0801"],
        help="Specifies the target BASIC memory address when loading:\n"
             "- 0x0801 - C64 (default)\n"
             "- 0x1001 - VIC20 Unexpanded\n"
             "- 0x0401 - VIC20 +3K\n"
             "- 0x1201 - VIC20 +8K\n"
             "- 0x1201 - VIC20 +16\n"
             "- 0x1201 - VIC20 +24K\n"
    )

    parser.add_argument(
        "-s", "--source", choices=["ahoy1", "ahoy2", "ahoy3"], type=str,
        nargs=1, required=False, metavar="source_format", default=["ahoy2"],
        help="Specifies the magazine source for conversion and checksum:\n"
             "ahoy1 - Ahoy magazine (Apr-May 1984)\n"
             "ahoy2 - Ahoy magazine (Jun 1984-Apr 1987) (default)\n"
             "ahoy3 - Ahoy magazine (May 1987-)\n"
    )

    parser.add_argument(
        "file_in", type=str, metavar="input_file",
        help="Specify the input file name including path.\n"
             "Note:  Output file will use input file basename with\n"
             "extension '.prg' for Commodore file format."
    )

    return parser.parse_args(argv)


def print_checksums(ahoy_checksums, terminal_width):

    # Determine number of columns to print based on terminal window width
    columns = int(terminal_width / 12)
    # Determine number of rows based on column count
    rows = math.ceil(len(ahoy_checksums) / columns)

    # Print each line number, code combination in matrix format
    for i in range(rows):
        for j in range(columns):
            indx = i + (j * rows)
            if indx < len(ahoy_checksums):
                prt_line = str(ahoy_checksums[indx][0])
                prt_code = str(ahoy_checksums[indx][1])
                left_space = 7 - len(prt_line) - len(prt_code)
                print(" "*left_space, prt_line, prt_code, " "*2, end='')
        print(end='\n')

    print(f'\nLines: {len(ahoy_checksums)}\n')


def command_line_runner(argv=None, width=None):

    # call function to parse command line input arguments
    args = parse_args(argv)

    # call function to read input file lines
    try:
        lines_list = read_file(args.file_in)
    except IOError:
        print("File read failed - please check source file name and path.")
        sys.exit(1)

    # check each line to insure each starts with a line number
    check_line_number_seq(lines_list)

    # Create lines list while checking for loose brackets/braces and converting
    # to common special character codes in braces
    if args.source[0][:4] == 'ahoy':
        lines_list = ahoy_lines_list(lines_list)
        # handle loose brace error returned from ahoy_lines_list()
        if lines_list[0] is None:
            line_no = split_line_num(lines_list[1])[0]
            print(f"Loose brace/bracket error in line: {line_no}\n"
                  "Special characters should be enclosed in braces/brackets.\n"
                  "Please check for unmatched single brace/bracket in above "
                  "line.")
            sys.exit(1)

    addr = int(args.loadaddr[0], 16)

    out_list = []
    ahoy_checksums = []

    for line in lines_list:
        # split each line into line number and remaining text
        (line_num, line_txt) = split_line_num(line)

        token_ln = []
        # add load address at start of first line only
        if addr == int(args.loadaddr[0], 16):
            token_ln.append(addr.to_bytes(2, 'little'))
        byte_list = scan_manager(line_txt)

        addr = addr + len(byte_list) + 4

        token_ln.extend((addr.to_bytes(2, 'little'),
                         line_num.to_bytes(2, 'little'), byte_list))

        token_ln = [byte for sublist in token_ln for byte in sublist]

        # call checksum generator function to build list of tuples
        if args.source[0] == 'ahoy1':
            ahoy_checksums.append((line_num,
                                   ahoy1_checksum(byte_list)))
        elif args.source[0] == 'ahoy2':
            ahoy_checksums.append((line_num, 
                                   ahoy2_checksum(byte_list)))
        elif args.source[0] == 'ahoy3':
            ahoy_checksums.append((line_num,
                                   ahoy3_checksum(line_num, byte_list)))
        else:
            print("Magazine format not yet supported.")
            sys.exit(1)

        out_list.append(token_ln)

    out_list.append([0, 0])

    dec_list = [byte for sublist in out_list for byte in sublist]

    file_stem = args.file_in.split('.')[0]
    bin_file = f'{file_stem}.prg'

    # Write binary file compatible with Commodore computers or emulators
    write_binary(bin_file, dec_list)

    # Print line checksums to terminal, formatted based on screen width
    print('Line Checksums:\n')
    if not width:
        width = get_terminal_size()[0]
    print_checksums(ahoy_checksums, width)

    # Write text file containing line numbers, checksums, and line count
    chk_file = f'{file_stem}.chk'
    write_checksums(chk_file, ahoy_checksums)


if __name__ == '__main__':
    sys.exit(command_line_runner())
