import pytest
from typein_tokenizer.tokenizer import parse_args, \
                                       read_file, \
                                       ahoy_lines_list, \
                                       split_line_num, \
                                       scan, \
                                       scan_manager

@pytest.mark.parametrize(
    "argv, arg_valid",
    [
        (['infile.bas'],
        ['0x0801', '2', 'ahoy', 'infile.bas']),
        (['infile.bas', '-s', 'pet'],
        ['0x0801', '2', 'pet', 'infile.bas']),
        (['infile.bas', '-v', '7'],
        ['0x0801', '7', 'ahoy', 'infile.bas']),
        (['infile.bas', '-l', '0x1001'],
        ['0x1001', '2', 'ahoy', 'infile.bas']),
        (['-v', '4', 'infile.bas', '-s', 'ahoy', '-l', '0x1001'],
        ['0x1001', '4', 'ahoy', 'infile.bas']),
    ],
)

def test_parse_args(argv, arg_valid):
    """
    Unit test to check that function parse_args() yields the correct list of
    arguments for a range of different command line input combinations.
    """

    args = parse_args(argv)
    arg_list = [args.loadaddr[0], args.version[0],
                args.source[0], args.file_in]
    assert arg_list == arg_valid

@pytest.fixture
def infile_data():
    try:
        infile = read_file('test_infile.txt')
    except:
        infile = read_file('tests/test_infile.txt')
    return infile

def test_read_file(infile_data):
    """
    Unit test to check that function read_file() is properly reading data from a
    file source.
    """
    assert infile_data == ['10 print"hello!"', '20 goto10']

@pytest.mark.parametrize(
    "lines_list, new_lines",
    [
        (['10 print"hi"', '20 goto10'], ['10 print"hi"', '20 goto10']),
        (['10 print"hello"', '20 {goto10'], (None, '20 {goto10')),
        (['{WH}CY}', '10 print"hello"'], (None, '{WH}CY}')),
        (['{WH}{CY}', '{RV}'], ['{wht}{cyn}', '{rvon}']),
        (['{WH}{CD}{RV}{HM}{RD}{CR}{GN}{BL}{OR}{F1}{F2}'],
         ['{wht}{down}{rvon}{home}{red}{rght}{grn}{blu}{orng}{f1}{f2}']),
        (['{F3}{F4}{F5}{F6}{F7}{F8}{BK}{CU}{RO}'],
         ['{f3}{f4}{f5}{f6}{f7}{f8}{blk}{up}{rvof}']),
        (['{SC}{IN}{BR}{LR}{G1}{G2}{LG}{LB}{G3}'],
         ['{clr}{inst}{brn}{lred}{gry1}{gry2}{lgrn}{lblu}{gry3}']),
        (['{PU}{CL}{YL}{CY}{SS}'],
         ['{pur}{left}{yel}{cyn}{$a0}']),
    ],
)

def test_ahoy_lines_list(lines_list, new_lines):
    """
    Unit test to check that function ahoy_lines_list() replaces ahoy special 
    character codes with petcat special character codes in each line of the
    program.  Also checks for loose braces and prompt an error message and 
    program exit.
    """
    assert ahoy_lines_list(lines_list) == new_lines

@pytest.mark.parametrize(
    "line, split_line",
    [
        ('10 print"hello!"', (10, 'print"hello!"')),
        ('20   goto10', (20, 'goto10')),
        ('30{wh}val = 3.2*num', (30, '{wh}val = 3.2*num')),
    ],
)

def test_split_line_num(line, split_line):
    """
    Unit test to check that function split_line_num() is properly splitting each
    line into tuples consisting of line number(int) and remaining line text(str).
    """
    assert split_line_num(line) == (split_line)
    
# TODO: Write test for write_binary() function
# def test_write_binary():
''' Example code:

    def writetoafile(fname):
        with open(fname, 'w') as fp:
            fp.write('Hello\n')
    
    def test_writetofile(tmpdir):
        file = tmpdir.join('output.txt')
        writetoafile(file.strpath)  # or use str(file)
        assert file.read() == 'Hello\n'
'''

'''
def test_write_binary(tmpdir):
    file = tmpdir.join('output.prg')
    write_binary(  )
    assert file.read() == '321136'
'''

@pytest.mark.parametrize(
    "ln, bytes",
    [
        ('rem lawn', [143, 32, 76, 65, 87, 78, 0]),
        ('goto110', [137, 49, 49, 48, 0]),
        ('printtab(10);sc$', [153, 163, 49, 48, 41, 59, 83, 67, 36, 0]),
        ('printtab(16)"{lgrn}{down}l',
         [153, 163, 49, 54, 41, 34, 153, 17, 76, 0]),
        ('data15,103,255,169', 
         [131, 49, 53, 44, 49, 48, 51, 44, 50, 53, 53, 44, 49, 54, 57, 0]),
    ],
)

def test_scan_manager(ln, bytes):
    """
    Unit test to check that function scan_manager() is properly managing the
    conversion of a line of text to a list of tokenized bytes in decimal form.
    """

    assert scan_manager(ln) == bytes

@pytest.mark.parametrize(
    "ln, tokenize, byte, remaining_line",
    [
        (' space test', False, 32, 'space test'),
        ('goto11', True, 137, '11'),
        ('goto11', False, 71, 'oto11'),
        ('rem start mower', True, 143, ' start mower'),
        (' start mower', False, 32, 'start mower'),
        ('{wht}"tab(32)', True, 5, '"tab(32)'),
    ],
)

def test_scan(ln, tokenize, byte, remaining_line):
    """
    Unit test to check that function scan() is properly converting the start
    of each passed in line to a tokenized byte for BASIC keywords, petcat
    special characters, and alphanumeric characters.
    """
    
    assert scan(ln, tokenize) == (byte, remaining_line)

