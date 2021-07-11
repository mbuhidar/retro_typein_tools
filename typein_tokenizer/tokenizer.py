#! /usr/bin/python3

import argparse
from argparse import RawTextHelpFormatter
from os import path
import re
import sys

# Dictionary for special character conversion from ahoy to petcat
AHOY_TO_PETCAT = {
    "{SC}": "{clr}",
    "{HM}": "{home}",
    "{CU}": "{up}",
    "{CD}": "{down}",
    "{CL}": "{left}",
    "{CR}": "{rght}",
    "{SS}": "{$a0}",
    "{IN}": "{inst}",
    "{RV}": "{rvon}",
    "{RO}": "{rvof}",
    "{BK}": "{blk}",
    "{WH}": "{wht}",
    "{RD}": "{red}",
    "{CY}": "{cyn}",
    "{PU}": "{pur}",
    "{GN}": "{grn}",
    "{BL}": "{blu}",
    "{YL}": "{yel}",
    "{OR}": "{orng}",
    "{BR}": "{brn}",
    "{LR}": "{lred}",
    "{G1}": "{gry1}",
    "{G2}": "{gry2}",
    "{LG}": "{lgrn}",
    "{LB}": "{lblu}",
    "{G3}": "{gry3}",
    "{F1}": "{f1}",
    "{F2}": "{f2}",
    "{F3}": "{f3}",
    "{F4}": "{f4}",
    "{F5}": "{f5}",
    "{F6}": "{f6}",
    "{F7}": "{f7}",
    "{F8}": "{f8}",
}
                  
# Core Commodore BASIC tokens
CORE_TOKENS = (
    ('end',     128),
    ('for',     129),
    ('next',    130),
    ('data',    131),
    ('input#',  132),
    ('input',   133),
    ('dim',     134),
    ('read',    135),
    ('let',     136),
    ('goto',    137),
    ('run',     138),
    ('if',      139),
    ('restore', 140),
    ('gosub',   141),
    ('return',  142),
    ('rem',     143),
    ('stop',    144),
    ('on',      145),
    ('wait',    146),
    ('load',    147),
    ('save',    148),
    ('verify',  149),
    ('def',     150),
    ('poke',    151),
    ('print#',  152),
    ('print',   153),
    ('cont',    154),
    ('list',    155),
    ('clr',     156),
    ('cmd',     157),
    ('sys',     158),
    ('open',    159),
    ('close',   160),
    ('get',     161),
    ('new',     162),
    ('tab(',    163),
    ('to',      164),
    ('fn',      165),
    ('spc(',    166),
    ('then',    167),
    ('not',     168),
    ('step',    169),
    ('+',       170),
    ('-',       171),
    ('*',       172),
    ('/',       173),
    ('^',       174),
    ('and',     175),
    ('or',      176),
    ('>',       177),
    ('=',       178),
    ('<',       179),
    ('sgn',     180),
    ('int',     181),
    ('abs',     182),
    ('usr',     183),
    ('fre',     184),
    ('pos',     185),
    ('sqr',     186),
    ('rnd',     187),
    ('log',     188),
    ('exp',     189),
    ('cos',     190),
    ('sin',     191),
    ('tan',     192),
    ('atn',     193),
    ('peek',    194),
    ('len',     195),
    ('str$',    196),
    ('val',     197),
    ('asc',     198),
    ('chr$',    199),
    ('left$',   200),
    ('right$',  201),
    ('mid$',    202),
    ('go',      203),
)

global TOKENS_V2
TOKENS_V2 = CORE_TOKENS # case for Commodore BASIC v2. TODO: Add versions

# Tokens for special character designations used by petcat
PETCAT_TOKENS = (
    ('{clr}',  147),
    ('{home}',  19),
    ('{up}',   145),
    ('{down}',  17),
    ('{left}', 157),
    ('{rght}',  29),
    ('{$a0}',  160),
    ('{inst}', 148),
    ('{rvon}',  18),
    ('{rvof}', 146),
    ('{blk}',  144),
    ('{wht}',    5),
    ('{red}',   28),
    ('{cyn}',  159),
    ('{pur}',  156),
    ('{grn}',   30),
    ('{blu}',   31),
    ('{yel}',  158),
    ('{orng}', 129),
    ('{brn}',  149),
    ('{lred}', 150),
    ('{gry1}', 151),
    ('{gry2}', 152),
    ('{lgrn}', 153),
    ('{lblu}', 154),
    ('{gry3}', 155),
    ('{f1}',   133),
    ('{f2}',   134),
    ('{f3}',   135),
    ('{f4}',   136),
    ('{f5}',   137),
    ('{f6}',   138),
    ('{f7}',   139),
    ('{f8}',   140),
)

def parse_args(argv):
    # parse command line inputs and generate cli documentation
    parser = argparse.ArgumentParser(description =\
    "A tokenizer for Commodore BASIC typein programs. So far, supports Ahoy \n"
    "magazine and Commodore BASIC 2.0 (C64 and VIC20).",\
    formatter_class=RawTextHelpFormatter)

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
        "-v", "--version", choices=['1', '2', '3', '4', '7'], type=str,
        nargs=1, required=False, metavar="basic_version", default=['2'],
        help = "Specifies the BASIC version for use in tokenizing file.\n"
               "- 1 - Basic v1.0  PET\n"
               "- 2 - Basic v2.0  C64/VIC20/PET (default)\n"
               "- 3 - Basic v3.5  C16/C116/Plus/4\n"
               "- 4 - Basic v4.0  PET/CBM2\n"
               "- 7 - Basic v7.0  C128\n"
    )

    parser.add_argument(
        "-s", "--source", choices=["pet", "ahoy"], type=str, nargs=1,
        required=False, metavar = "source_format", default=["ahoy"],
        help="Specifies the source BASIC file format:\n"
             "pet - use standard pet control character mnemonics\n"
             "ahoy - use Ahoy! magazine control character mnemonics "
             "(default)\n"
    )

    parser.add_argument(
        "file_in", type=str, metavar="input_file",
        help = "Specify the input file name including path\n"
               "Note:  Output files will use input file basename\n"
               "with extensions '.pet' for petcat-ready file and\n"
               "'.prg' for Commordore run fule format."
    )

    return parser.parse_args(argv)

def read_file(filename):
    """Opens and reads magazine source, strips whitespace, and
       returns a list of lines converted to lowercase 

    Args:
        filename (str): The file name of the magazine source file

    Returns:
        list: a list of strings for each non-blank line from the source file
            converted to lowercase
    """

    with open(filename) as file:
        lines = file.readlines()
        lower_lines = []
        for line in lines:
            # remove any lines with no characters
            if not line.strip():
                continue
            lower_lines.append(line.rstrip().lower())
        return lower_lines

def write_binary(filename, int_list):
    """Write binary file readable on Commodore computers or emulators

    Args:
        filename (str): The file name of the file to write as binary
        int_list (list): List of integers to convert to binary bytes and 
            output write to file

    Returns:
        None: implicit return
    """
    
    with open(filename, "wb") as file:
        for byte in int_list:
            file.write(byte.to_bytes(1, byteorder='big'))

# convert ahoy special characters to petcat special characters
def ahoy_lines_list(lines_list):

    new_lines = []
    
    for line in lines_list:
        # split each line on ahoy special characters
        str_split = re.split(r"\{\w{2}\}", line)

        # check for loose braces in each substring, return error indication        
        for sub_str in str_split:
            loose_brace = re.search(r"\}|{", sub_str)
            if loose_brace is not None:
                return (None, line)
                
        # create list of ahoy special character code strings
        code_split = re.findall(r"\{\w{2}\}", line)        

        new_codes = []
        
        # for each ahoy special character, append the petcat equivalent
        for item in code_split:
            new_codes.append(AHOY_TO_PETCAT[item.upper()])
            
        # add blank item to list of special characters to aide enumerate
        if new_codes:
            new_codes.append('')

            new_line = []

            # piece the string segments and petcat codes back together
            for count, segment in enumerate(new_codes):
                new_line.append(str_split[count])
                new_line.append(new_codes[count])
        # handle case where line contained no special characters
        else:
            new_line = str_split
        new_lines.append(''.join(new_line))
    return new_lines

def split_line_num(line):
    """Split each line into line number and remaining line text

    Args:
        line (str): Text of each line to split

    Returns:
        tuple consisting of:
            line number (int): Line number split from the beginning of line
            remaining text (str): Text for remainder of line with whitespace 
                stripped
    """
    
    line = line.lstrip()
    acc = []
    while line and line[0].isdigit():
        acc.append(line[0])
        line = line[1:]
    return (int(''.join(acc)), line.lstrip())
    
# manage the tokenization process for each line text string
def scan_manager(ln):
    in_quotes = False
    in_remark = False
    bytes = []
    
    while ln:
        (byte, ln) = scan(ln, tokenize = not (in_quotes or in_remark))
        bytes.append(byte)
        if byte == ord('"'):
            in_quotes = not in_quotes
        if byte == 143:
            in_remark = True
    bytes.append(0)
    return bytes

# scan each line segement and convert to tokenized bytes.  
# returns byte and remaining line segment
def scan(ln, tokenize=True):
    """Scan beginning of each line for BASIC keywords, petcat special 
       characters, or ascii characters, convert to tokenized bytes, and
       return remaining line segment after converted characters are removed

    Args:
        ln (str): Text of each line segment to parse and convert
        tokenize (bool): Flag to indicate if start of line segment should be
            tokenized (False if line segment start is within quotes or after
            a REM statement) 

    Returns:
        tuple consisting of:
            character/token value (int): Decimal value of ascii character or
                tokenized word
            remainder of line (str): Text for remainder of line with keyword, 
                specical character, or alphanumeric character stripped
    """

    # check if each line passed in starts with a petcat special character
    # if so, return value of token and line with token string removed
    for (token, value) in PETCAT_TOKENS:
        if ln.startswith(token):
            return (value, ln[len(token):])
    # if tokenize flag is True (i.e. line beginning is not inside quotes or
    # after a REM statement), check if line starts with a BASIC keyword
    # if so, return value of token and line with BASIC keyword removed
    if tokenize:
        for (token, value) in TOKENS_V2:
            if ln.startswith(token):
                return (value, ln[len(token):])
    # for characters without token values, convert to unicode (ascii) value
    # and, for latin letters, shift values by -32 to account for difference
    # between ascii and petscii used by Commodore BASIC
    # finally, return character value and line with character removed
    char_val = ord(ln[0])
    if char_val >= 97 and char_val <= 122:
       char_val = char_val - 32
    return (char_val, ln[1:])

def check_overwrite(filename):
    overwrite = 'y'
    if path.isfile(filename):
        overwrite = input(f'Output file "{filename}" already exists. '
                           'Overwrite? (Y = yes) ')
    if overwrite.lower() == 'y':
        return True
    else:
        print('File not overwritten - exiting.')
        sys.exit(1)

def hex_to_ahoy_repellent_code(hex_value):
    '''
    Function to convert hex to alpha only representation that the
    Ahoy Bug Repellent tool uses.  Algorithm:  First hex character maps
    directly to the alpha character shown in the below mapping. Second 
    alpha character is determined by indexing from first character by the
    value of the second hex digit.

    hex:   0 1 2 3 4 5 6 7 8 9 a b c d e f
    alpha: A B C D E F G H I J K L M N O P
    
    So, hex 47 is alpha EL, hex 97 is alpha JA, hex df is alpha NM  
    '''

    alpha_map = "ABCDEFGHIJKLMNOP"
    
    hex_chars =  str(hex_value)[-2:]
    idx0 = int(hex_chars[0], 16)
    idx1 = int(hex_chars[0], 16) + int(hex_chars[1], 16)
    if idx1 > 15:
        idx1 = idx1 - 16

    return alpha_map[idx0] + alpha_map[idx1]

def main(argv=None):
    # call function to parse command line input arguments
    args = parse_args(argv)

    # define load address from input argument
    load_addr = args.loadaddr[0]
    
    # TODO: Improve implementation of input file reading using with block
    # call function to read input file lines
    try:
        lines_list = read_file(args.file_in)
    except IOError:
        print("File read failed - please check source file name and path.")
        sys.exit(1)

    # convert to petcat format and write petcat-ready file
    # TODO: Add COMPUTE and other magazine format
    if args.source[0] == 'ahoy':
        lines_list = ahoy_lines_list(lines_list)
        # handle loose brace error returned from ahoy_lines_list()
        if lines_list[0] is None:
            print(f"Loose brace error in line:\n {lines_list[1]}\n"\
                   "Special characters should be enclosed in two braces.\n"\
                   "Please check for unmatched single braces in above line.")
            sys.exit(1)
        for line in lines_list:
            print(str(line))
        
    # Write petcat ready file with extension .bas 
    outfile = args.file_in.split('.')[0] + '.bas'
    if check_overwrite(outfile):
        with open(outfile, "w") as file:
            for line in lines_list:
                file.write(line + '\n')

    addr = int(load_addr, 16)

    out_list = []
    
    for line in lines_list:
        # split each line into line number and remaining text
        (line_num, line_txt) = split_line_num(line)
        
        token_ln = []
        # add load address at start of first line only
        if addr == int(load_addr, 16):
            token_ln.append(addr.to_bytes(2, 'little'))

        byte_list = scan_manager(line_txt)

        addr = addr + len(byte_list) + 4
        
        token_ln.append(addr.to_bytes(2, 'little'))
        token_ln.append(line_num.to_bytes(2, 'little'))
        token_ln.append(byte_list)
        token_ln = [byte for sublist in token_ln for byte in sublist]
        
        print(line)
        print(token_ln)

        out_list.append(token_ln)
        
    out_list.append([0, 0])
    
    out_list = [byte for sublist in out_list for byte in sublist]

    print(out_list) 
    print([f'{byte:08b}' for byte in out_list])
    
    # Write binary file compatible with Commodore computers or emulators
    bin_file = args.file_in.split('.')[0] + '.prg'
    if check_overwrite(bin_file):
        write_binary(bin_file, out_list)

if __name__ == '__main__':
    sys.exit(main())

