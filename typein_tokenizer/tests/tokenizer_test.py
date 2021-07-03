from typein_tokenizer.tokenizer import parse_args
from typein_tokenizer.tokenizer import read_file
from typein_tokenizer.tokenizer import ahoy_lines_list
from typein_tokenizer.tokenizer import split_line_num
import pytest

def test_parse_args():
    '''
    Unit test to check that function parse_args() yields the correct list of
    arguments for a range of different command line input combinations.
    '''

    argv = [
        ['infile.bas'],
        ['infile.bas', '-s', 'pet'],
        ['infile.bas', '-v', '7'],
        ['infile.bas', '-l', '0x1001'],
        ['-v', '4', 'infile.bas', '-s', 'ahoy', '-l', '0x1001'],
    ]
            
    arg_valid = [
        ['0x0801', '2', 'ahoy', 'infile.bas'],
        ['0x0801', '2', 'pet', 'infile.bas'],
        ['0x0801', '7', 'ahoy', 'infile.bas'],
        ['0x1001', '2', 'ahoy', 'infile.bas'],
        ['0x1001', '4', 'ahoy', 'infile.bas'],
    ]
  
    for i in range(len(argv)):
        args = parse_args(argv[i])
        arg_list = [args.loadaddr[0], args.version[0], args.source[0],
        args.file_in]
        assert arg_list == arg_valid[i]

@pytest.fixture
def infile_data():
    try:
        infile = read_file('test_infile.txt')
    except:
        infile = read_file('tests/test_infile.txt')
    return infile

def test_read_file(infile_data):
    '''
    Unit test to check that function read_file() is properly reading data from a
    file source.
    '''
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
    '''
    Unit test to check that function ahoy_lines_list() replaces ahoy special 
    character codes with petcat special character codes in each line of the
    program.  Also checks for loose braces and prompt an error message and 
    program exit.
    '''
    assert ahoy_lines_list(lines_list) == new_lines

@pytest.mark.parametrize(
    "line, sp_line",
    [
        ('10 print"hello!"', (10, 'print"hello!"')),
        ('20   goto10', (20, 'goto10')),
        ('30{wh}val = 3.2*num', (30, '{wh}val = 3.2*num')),
    ],
)

def test_split_line_num(line, sp_line):
    '''
    Unit test to check that function split_line_num() is properly splitting each
    line into tuples consisting of line number(int) and remaining line text(str).
    '''
    assert split_line_num(line) == (sp_line)
    
