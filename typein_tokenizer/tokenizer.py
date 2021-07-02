
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
                  
# Common Commodore BASIC tokens
TOKENS = (
    ('end', 128),
    ('for', 129),
    ('next', 130),
    ('data', 131),
    ('input#', 132),
    ('input', 133),
    ('dim', 134),
    ('read', 135),
    ('let', 136),
    ('goto', 137),
    ('run', 138),
    ('if', 139),
    ('restore', 140),
    ('gosub', 141),
    ('return', 142),
    ('rem', 143),
    ('stop', 144),
    ('on', 145),
    ('wait', 146),
    ('load', 147),
    ('save', 148),
    ('verify', 149),
    ('def', 150),
    ('poke', 151),
    ('print#', 152),
    ('print', 153),
    ('cont', 154),
    ('list', 155),
    ('clr', 156),
    ('cmd', 157),
    ('sys', 158),
    ('open', 159),
    ('close', 160),
    ('get', 161),
    ('new', 162),
    ('tab(', 163),
    ('to', 164),
    ('fn', 165),
    ('spc(', 166),
    ('then', 167),
    ('not', 168),
    ('step', 169),
    ('+', 170),
    ('-', 171),
    ('*', 172),
    ('/', 173),
    ('^', 174),
    ('and', 175),
    ('or', 176),
    ('>', 177),
    ('=', 178),
    ('<', 179),
    ('sgn', 180),
    ('int', 181),
    ('abs', 182),
    ('usr', 183),
    ('fre', 184),
    ('pos', 185),
    ('sqr', 186),
    ('rnd', 187),
    ('log', 188),
    ('exp', 189),
    ('cos', 190),
    ('sin', 191),
    ('tan', 192),
    ('atn', 193),
    ('peek', 194),
    ('len', 195),
    ('str$', 196),
    ('val', 197),
    ('asc', 198),
    ('chr$', 199),
    ('left$', 200),
    ('right$', 201),
    ('mid$', 202),
    ('go', 203),
)

def parse_args(argv):

    # create parser object
    parser = argparse.ArgumentParser(description =\
    "A tokenizer for Commodore BASIC typein programs.",\
    formatter_class=RawTextHelpFormatter)

    # define arguments for parser object
    parser.add_argument("-l", "--loadaddr", type=str, nargs=1, required=False,
                        metavar = "load_address", default = ["0x0801"],
                        help = "Specifies the target BASIC memory address when loading:\n"
                                "- 0x0801 - C64 (default)\n"
                                "- 0x1001 - VIC20 Unexpanded\n"
                                "- 0x0401 - VIC20 +3K\n"
                                "- 0x1201 - VIC20 +8K\n"
                                "- 0x1201 - VIC20 +16\n"
                                "- 0x1201 - VIC20 +24K\n")

    parser.add_argument("-v", "--version", choices=['1', '2', '3', '4', '7'],
                        type=str, nargs=1, required=False,
                        metavar = "basic_version", default=['2'],
                        help = "Specifies the BASIC version for use in tokenizing file.\n"
                        "- 1 - Basic v1.0  PET\n"
                        "- 2 - Basic v2.0  C64/VIC20/PET (default)\n"
                        "- 3 - Basic v3.5  C16/C116/Plus/4\n"
                        "- 4 - Basic v4.0  PET/CBM2\n"
                        "- 7 - Basic v7.0  C128\n")

    parser.add_argument("-s", "--source", choices=["pet", "ahoy"], type=str,
                        nargs=1, required=False,
                        metavar = "source_format", default=["ahoy"],
                        help = "Specifies the source BASIC file format:\n"
                        "pet - use standard pet control character mnemonics\n"
                        "ahoy - use Ahoy! magazine control character mnemonics (default)\n")

    parser.add_argument("file_in", type=str, metavar="input_file",
                        help = "Specify the input file name including path\n"
                        "Note:  Output files will use input file basename\n"
                        "with extensions '.pet' for petcat-ready file and\n"
                        "'.prg' for Commordore run fule format.")

    # parse and return the arguments
    return parser.parse_args(argv)

# read input file and return list of lowercase strings
def read_file(filename):
    with open(filename) as file:
        lines = file.readlines()
        lower_lines = []
        for line in lines:
            # remove any lines with no characters
            if not line.strip():
                continue
            lower_lines.append(line.rstrip().lower())
        return lower_lines

# convert ahoy special characters to petcat special characters
def ahoy_lines_list(lines_list):

    new_lines = []
    
    for line in lines_list:
        # Check for loose braces and return error
        # Split each line on ahoy special characters
        str_split = re.split(r"\{\w{2}\}", line)

        # Check for loose braces in each substring, return error statement        
        for sub_str in str_split:
            loose_brace = re.search(r"\}|{", sub_str)
            if loose_brace is not None:
                return None
                
        # Replace ahoy special characters with petcat special characters
        # Create list of ahoy special character code strings
        code_split = re.findall(r"\{\w{2}\}", line)        
        new_codes = []
        for item in code_split:
            new_codes.append(AHOY_TO_PETCAT[item.upper()])
        if new_codes:
            new_codes.append('')

            new_line = []
            for count, segment in enumerate(new_codes):
                new_line.append(str_split[count])
                new_line.append(new_codes[count])
        else:
            new_line = str_split
        new_lines.append(''.join(new_line))
    return new_lines

# split each line into line number and remaining line
def split_line_num(line):
    line = line.lstrip()
    acc = []
    while line and line[0].isdigit():
        acc.append(line[0])
        line = line[1:]
    return (int(''.join(acc)), line.lstrip())
    
    
# convert unique magazine character codes to petcat character codes (preserve)
# tokenize remaining line
# - don't tokenize words within print quotes or in REM statements
# - 

def main(argv=None):
    # call function to parse command line input arguments
    args = parse_args(argv)

    # define load address from input argument
    addr = args.loadaddr[0]

    ''' print diagnostics - temp for debugging
    print(args)
    print(args.loadaddr[0])
    print(args.version[0])
    print(args.source[0])
    print(args.file_in)
    '''

    # call function to read input file lines
    try:
        lines_list = read_file(args.file_in)
    except IOError:
        print("File read failed - please check source file name and path.")
        sys.exit(1)

    # convert to petcat format and write petcat-ready file
    if args.source[0] == 'ahoy':
        lines_list = ahoy_lines_list(lines_list)
        if lines_list is None:
            print(f"Loose brace error in line:\n {line}")
            print("Special characters should be enclosed in two braces.")
            print("Please check for unmatched single braces in above line.")
            sys.exit(1)
        for line in lines_list:
            print(str(line))
        
    outfile = args.file_in.split('.')[0] + '.bas'
    overwrite = 'y'
    if path.isfile(outfile):
        overwrite = input(f'Output file "{outfile}" already exists. Overwrite? (Y = yes) ')
    if overwrite.lower() == 'y':
        with open(outfile, "w") as file:
            for line in lines_list:
                file.write(line + '\n')

'''        
    for line in lines_list:
        # split each line into line number and remaining text
        (line_num, line_txt) = split_line_num(line)
        print(line)
        print((line_num, line_txt))
'''

if __name__ == '__main__':
    sys.exit(main())

