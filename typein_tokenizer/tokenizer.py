
import argparse
from argparse import RawTextHelpFormatter
import sys

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
    parser = argparse.ArgumentParser(description = "A tokenizer for Commodore BASIC typein programs.", formatter_class=RawTextHelpFormatter)

    # define arguments for parser object
    parser.add_argument("-l", "--loadaddr", type=str, nargs=1, required=False,
                        metavar = "load_address", default = ["0x0801"],
                        help = "Specifies the target BASIC memory address when loading:\n"
                                "- 0x0801 - C64 (default)\n"
                                "- 0x1001 - VIC20 Unexpanded\n"
                                "- 0x0401 - VIC20 +3K\n"
                                "- 0x1201 - VIC20 +8K\n"
                                "- 0x1201 - VIC20 +16\n"
                                "- 0x1201 - VIC20 +24K")

    parser.add_argument("-v", "--version", choices=['1', '2', '3', '4', '7'], type=str, nargs=1, required=False,
                        metavar = "basic_version", default=['2'],
                        help = "Specifies the BASIC version for use in tokenizing file.\n"
                        "- 1 - Basic v1.0  PET\n"
                        "- 2 - Basic v2.0  C64/VIC20/PET (default)\n"
                        "- 3 - Basic v3.5  C16/C116/Plus/4\n"
                        "- 4 - Basic v4.0  PET/CBM2\n"
                        "- 7 - Basic v7.0  C128")

    parser.add_argument("-s", "--source", choices=["pet", "ahoy"], type=str, nargs=1, required=False,
                        metavar = "source_format", default=["ahoy"],
                        help = "Specifies the source BASIC file format:\n"
                        "pet - use standard pet control character mnemonics\n"
                        "ahoy - use Ahoy! magazine control character mnemonics (default)")

    parser.add_argument("file_in", type=str, metavar="input_file",
                        help = "Specify the input file name including path")

    parser.add_argument("file_out", type=str, metavar="output_file",
                        help = "Specify the output file name including path")
                        
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

'''
class TokenizedLine():
    def __init__(self, line, addr):
        (line_num, bytes) = tokenize(line)
        self.line_num = line_num
        self.bytes = bytes
        self.addr = addr
        self.next_addr = None

    def __len__(self):
        return len(self.bytes) = 5
'''
        
def main(argv=None):
    # call function to parse command line input arguments
    args = parse_args(argv)

    # define load address from input argument
    addr = args.loadaddr[0]

    # print diagnostics - temp for debugging
    print(args)
    print(args.loadaddr[0])
    print(args.version[0])
    print(args.source[0])
    print(args.file_in)
    print(args.file_out)
    
    # call function to read input file lines and print each line
    lines_list = read_file(args.file_in)
    for line in lines_list:
        tokenized_line = TokenizedLine(line, addr)
        addr += len(tokenized_line)
        tokenized_lines.append(tokenized_line)
        print(line)

if __name__ == '__main__':
    sys.exit(main())

