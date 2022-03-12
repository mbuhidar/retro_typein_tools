"""
Imports Commodore BASIC type-in programs in various magazine formats,
checks for errors, and converts to an executable file for use with an
emulator or on original hardware.
"""

import argparse
from argparse import RawTextHelpFormatter
from os import remove, get_terminal_size
import re
import sys
import math

try:
    from src.debug_tokenize import char_maps
except ImportError:
    import char_maps

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
        "-s", "--source", choices=["ahoy1", "ahoy2", "ahoy3"], type=str, nargs=1,
        required=False, metavar="source_format", default=["ahoy2"],
        help="Specifies the magazine source for conversion and checksum:\n"
             "ahoy1 - Ahoy magazine (Apr-May 1984)\n"
             "ahoy2 - Ahoy magazine (Jun 1984-Oct 1984) (default)\n"
             "ahoy3 - Ahoy magazine (Nov 1984-)\n"
    )

    parser.add_argument(
        "file_in", type=str, metavar="input_file",
        help="Specify the input file name including path.\n"
             "Note:  Output file will use input file basename with\n"
             "extension '.prg' for Commodore file format."
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
        None: Implicit return
    """

    print(f'Writing binary output file "{filename}"...\n')

    try:
        with open(filename, "xb") as file:
            for byte in int_list:
                file.write(byte.to_bytes(1, byteorder='big'))
            print(f'File "{filename}" written successfully.\n')

    except FileExistsError:
        if confirm_overwrite(filename):
            remove(filename)
            write_binary(filename, int_list)
        else:
            print(f'File "{filename}" not overwritten.\n')
       

def confirm_overwrite(filename):

    overwrite = input(f'Output file "{filename}" already exists. '
                      'Overwrite? (Y = yes) ')

    if overwrite.lower() == 'y':
        return True
    return False


def check_line_number_seq(lines_list):
    """Check each line in the program that either does not start with a line
       number or starts with an out of sequence line number.

    Args:
        lines_list (list): List of lines (str) in program.

    Returns:
        None: implicit return
    """

    line_no = 0  # handles case where first line does not have a line number
    ln_num_buffer = [0]  # first popped after three line numbers are appended
    for line in lines_list:
        try:
            line_no = split_line_num(line)[0]
            ln_num_buffer.append(line_no)

            if not ln_num_buffer[0] < ln_num_buffer[1]:
                print("Entry error after line "
                      f"{ln_num_buffer[0]} - lines should be in sequential "
                      "order.  Exiting.")
                sys.exit(1)
            ln_num_buffer.pop(0)

        except ValueError:
            print(f"Entry error after line {line_no} - each line should start "
                  "with a line number.  Exiting.")
            sys.exit(1)


def ahoy_lines_list(lines_list, char_maps):
    """For each line in the program, convert Ahoy special characters to Petcat
       special characters.

    Args:
        lines_list (list): List of lines (str) in program.
        char_maps (module): Module containing conversion maps between various
                            Commodore and magazine formats.

    Returns:
        new_lines (list): List of new lines (str) after special characters are
                            converted from Ahoy to petcat format.
    """

    new_lines = []

    for line in lines_list:
        # replace braces with brackets since Ahoy used both over time
        line = line.replace('[', '{')
        line = line.replace(']', '}')

        # split each line on ahoy special characters
        str_split = re.split(r"{\d+\s?\".+?\"}|{.+?}", line)

        # check for loose braces in each substring, return error indication
        for sub_str in str_split:
            loose_brace = re.search(r"\}|{", sub_str)
            # Improve loose brace error handling, inconsistent return
            if loose_brace is not None:
                return (None, line)

        # create list of ahoy special character code strings
        code_split = re.findall(r"{\d+\s?\".+?\"}|{.+?}", line)

        new_codes = []

        # for each ahoy special character, append the petcat equivalent
        num = 0

        for item in code_split:

            if item.upper() in char_maps.AHOY_TO_PETCAT:
                new_codes.append(char_maps.AHOY_TO_PETCAT[item.upper()])

            elif re.match(r"{\d+\s?\".+?\"}", item):
                # Extract number of times to repeat special character
                char_count = int(re.search(r"\d+\b", item).group())
                # Get the string inside the brackets and strip quotes on ends
                char_code = re.search(r"\".+?\"", item).group()[1:-1]

                if char_code.upper() in char_maps.AHOY_TO_PETCAT:
                    new_codes.append(char_maps.AHOY_TO_PETCAT
                                     [char_code.upper()])

                    while char_count > 1:
                        new_codes.append(char_maps.AHOY_TO_PETCAT
                                         [char_code.upper()])
                        str_split.insert(num + 1, '')
                        num += 1
                        char_count -= 1

                else:
                    new_codes.append(char_code)
                    while char_count > 1:
                        new_codes.append(char_code)
                        str_split.insert(num + 1, '')
                        num += 1
                        char_count -= 1

            else:
                new_codes.append(item)
            num += 1

        # add blank item to list of special characters prior to blending strs
        if new_codes:
            new_codes.append('')
         
            new_line = []

            # piece the string segments and petcat codes back together
            for count in range(len(new_codes)):
                new_line.extend((str_split[count], new_codes[count]))

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
    bytestr = []

    while ln:
        (byte, ln) = scan(ln, char_maps, tokenize=not (in_quotes or in_remark))
        # if byte is not None:
        bytestr.append(byte)
        if byte == ord('"'):
            in_quotes = not in_quotes
        if byte == 143:
            in_remark = True
    bytestr.append(0)
    return bytestr


# scan each line segement and convert to tokenized bytes.
# returns byte and remaining line segment
def scan(ln, char_maps, tokenize=True):
    """Scan beginning of each line for BASIC keywords, petcat special
       characters, or ascii characters, convert to tokenized bytes, and
       return remaining line segment after converted characters are removed

    Args:
        ln (str): Text of each line segment to parse and convert
        char_maps (module): Module containing conversion maps between various
                            Commodore and magazine formats.
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
    for (token, value) in char_maps.PETCAT_TOKENS:
        if ln.startswith(token):
            return (value, ln[len(token):])
    # check if each line passed in starts with shifted or commodore special
    # character.  if so, return value of token, line with token string removed
    for (token, value) in char_maps.SHIFT_CMDRE_TOKENS:
        if ln.startswith(token):
            return (value, ln[len(token):])
    # if tokenize flag is True (i.e. line beginning is not inside quotes or
    # after a REM statement), check if line starts with a BASIC keyword
    # if so, return value of token and line with BASIC keyword removed
    if tokenize:
        for (token, value) in char_maps.TOKENS_V2:
            if ln.startswith(token):
                return (value, ln[len(token):])
    # for characters without token values, convert to unicode (ascii) value
    # and, for latin letters, shift values by -32 to account for difference
    # between ascii and petscii used by Commodore BASIC
    # finally, return character value and line with character removed
    char_val = ord(ln[0])
    if char_val >= 97 and char_val <= 122:
        char_val -= 32
    return (char_val, ln[1:])


def ahoy1_checksum(byte_list):
    '''
    Function to create Ahoy checksums from passed in byte list to match the
    codes printed in the magazine to check each line for typed in accuracy.
    Covers Ahoy Bug Repellent version for Mar-Apr 1984 issues.
    '''

    next_value = 0

    for char_val in byte_list:
        # Detect spaces that are outside of quotes and ignore them, else
        # execute primary checksum generation algorithm
        if char_val == 32:
            continue
        else:
            next_value = char_val + next_value
            next_value = next_value << 1

    xor_value = next_value
    # get high nibble of xor_value
    high_nib = (xor_value & 0xf0) >> 4
    high_char_val = high_nib + 65  # 0x41
    # get low nibble of xor_value
    low_nib = xor_value & 0x0f
    low_char_val = low_nib + 65  # 0x41
    checksum = chr(high_char_val) + chr(low_char_val)
    return checksum


def ahoy2_checksum(byte_list):
    '''
    Function to create Ahoy checksums from passed in byte list to match the
    codes printed in the magazine to check each line for typed in accuracy.
    Covers Ahoy Bug Repellent version for May 1984-Apr 1987 issues.
    '''

    xor_value = 0
    char_position = 1
    carry_flag = 1
    in_quotes = False

    for char_val in byte_list:

        # set carry flag to zero for char values less than ascii value for
        # quote character since assembly code for repellent sets carry flag
        # based on cmp 0x22 (decimal 34)
        if char_val < 34:
            carry_flag = 0
        else:
            carry_flag = 1

        # Detect quote symbol in line and toggle in-quotes flag
        if char_val == 34:
            in_quotes = not in_quotes

        # Detect spaces that are outside of quotes and ignore them, else
        # execute primary checksum generation algorithm
        if char_val == 32 and in_quotes is False:
            continue
        else:
            next_value = char_val + xor_value + carry_flag

            xor_value = next_value ^ char_position

            # limit next value to fit in one byte
            next_value = next_value & 255

            char_position = char_position + 1

    # get high nibble of xor_value
    high_nib = (xor_value & 0xf0) >> 4
    high_char_val = high_nib + 65  # 0x41
    # get low nibble of xor_value
    low_nib = xor_value & 0x0f
    low_char_val = low_nib + 65  # 0x41
    checksum = chr(high_char_val) + chr(low_char_val)
    return checksum


def ahoy3_checksum(line_num, byte_list):
    '''
    Function to create Ahoy checksums from passed in line number and byte list
    to match the codes printed in the magazine to check each line for typed in
    accuracy. Covers the last Ahoy Bug Repellent version introduced in May 1987.
    '''
    
    xor_value = 0
    char_position = 0
    in_quotes = False

    line_low = line_num % 256
    line_hi = int(line_num / 256)

    byte_list = [line_low] + [line_hi] + byte_list

    # byte_list.insert(0, line_hi)
    # byte_list.insert(0, line_low)

    for char_val in byte_list:

        # Detect quote symbol in line and toggle in-quotes flag
        if char_val == 34:
            in_quotes = not in_quotes

        # Detect spaces that are outside of quotes and ignore them, else
        # execute primary checksum generation algorithm
        if char_val == 32 and in_quotes is False:
            continue
        else:
            next_value = char_val + xor_value 

            xor_value = next_value ^ char_position

            # limit next value to fit in one byte
            next_value = next_value & 255

            char_position = char_position + 1

    # get high nibble of xor_value
    high_nib = (xor_value & 0xf0) >> 4
    high_char_val = high_nib + 65  # 0x41
    # high_char_val = high_char_val & 0x0f
    # get low nibble of xor_value
    low_nib = xor_value & 0x0f
    low_char_val = low_nib + 65  # 0x41
    # low_char_val = low_char_val & 0x0f
    checksum = chr(high_char_val) + chr(low_char_val)
    return checksum


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

    print(f'\nLines: {len(ahoy_checksums)}')


def main(argv=None, width=None):

    # call function to parse command line input arguments
    args = parse_args(argv)

    # define load address from input argument
    load_addr = args.loadaddr[0]

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
        lines_list = ahoy_lines_list(lines_list, char_maps)
        line_no = split_line_num(lines_list[1])[0]
        # handle loose brace error returned from ahoy_lines_list()
        if lines_list[0] is None:
            print(f"Loose brace/bracket error in line: {line_no}\n"
                  "Special characters should be enclosed in braces/brackets.\n"
                  "Please check for unmatched single brace/bracket in above "
                  "line.")
            sys.exit(1)

    addr = int(load_addr, 16)

    out_list = []
    ahoy_checksums = []

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

        # call checksum generator function to build list of tuples
        if args.source[0] == 'ahoy1':
            ahoy_checksums.append((line_num, ahoy1_checksum(byte_list)))
        elif args.source[0] == 'ahoy2':
            ahoy_checksums.append((line_num, ahoy2_checksum(byte_list)))
        elif args.source[0] == 'ahoy3':
            ahoy_checksums.append((line_num, ahoy3_checksum(line_num, byte_list)))
        else:
            print("Magazine format not yet supported.")
            sys.exit(1)

        out_list.append(token_ln)

    out_list.append([0, 0])

    dec_list = [byte for sublist in out_list for byte in sublist]

    bin_file = args.file_in.split('.')[0] + '.prg'

    # Write binary file compatible with Commodore computers or emulators
    write_binary(bin_file, dec_list)

    print('Line Checksums:\n')
    if not width:
        width = get_terminal_size()[0]
    print_checksums(ahoy_checksums, width) #, get_terminal_size()[0])


if __name__ == '__main__':
    sys.exit(main())
