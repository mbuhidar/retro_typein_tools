from typein_tokenizer.tokenizer import parse_args
from typein_tokenizer.tokenizer import read_file
from typein_tokenizer.tokenizer import split_line_num
import pytest

def test_parse_args():
    argv = [
            ['infile.bas'],
            ['infile.bas', '-s', 'pet'],
            ['infile.bas', '-v', '7'],
            ['infile.bas', '-l', '0x1001'],
            ['-v', '4', 'infile.bas', '-s', 'ahoy', '-l', '0x1001']
           ]
            
    arg_valid = [
                 ['0x0801', '2', 'ahoy', 'infile.bas'],
                 ['0x0801', '2', 'pet', 'infile.bas'],
                 ['0x0801', '7', 'ahoy', 'infile.bas'],
                 ['0x1001', '2', 'ahoy', 'infile.bas'],
                 ['0x1001', '4', 'ahoy', 'infile.bas']
                ]
  
    for i in range(len(argv)):
        args = parse_args(argv[i])
        arg_list = [args.loadaddr[0], args.version[0], args.source[0],
        args.file_in]
        assert arg_list == arg_valid[i]

def test_read_file():
    filename = 'test_infile.txt'
    assert read_file(filename) == ['10 print"hello!"', '20 goto10']

def test_split_line_num():
    assert split_line_num('10 print"hello!"') == (10, 'print"hello!"')
    assert split_line_num('20   goto10') == (20, 'goto10')
