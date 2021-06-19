from typein_tokenizer.tokenizer import parse_args
import pytest

def test_parse_args():
    argv = [
            ['infile.bas', 'outfile.prg'],
            ['infile.bas', 'outfile.prg', '-s', 'pet'],
            ['infile.bas', 'outfile.prg', '-v', '7'],
            ['infile.bas', 'outfile.prg', '-l', '0x1001'],
            ['-v', '4', 'infile.bas', 'outfile.prg', '-s', 'ahoy', '-l', '0x1001']
           ]
            
    arg_valid = [
                 ['0x0801', '2', 'ahoy', 'infile.bas', 'outfile.prg'],
                 ['0x0801', '2', 'pet', 'infile.bas', 'outfile.prg'],
                 ['0x0801', '7', 'ahoy', 'infile.bas', 'outfile.prg'],
                 ['0x1001', '2', 'ahoy', 'infile.bas', 'outfile.prg'],
                 ['0x1001', '4', 'ahoy', 'infile.bas', 'outfile.prg']
                ]
  
    for i in range(len(argv)):
        args = parse_args(argv[i])
        arg_list = [args.loadaddr[0], args.version[0], args.source[0], args.file_in, args.file_out]
        assert arg_list == arg_valid[i]

