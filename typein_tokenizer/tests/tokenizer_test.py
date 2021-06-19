from typein_tokenizer.tokenizer import parse_args
import pytest

def test_parse_args1():
    argv = ['infile.bas', 'outfile.prg']
    args = parse_args(argv)
    arg_list = [args.loadaddr[0], args.version[0], args.source[0], args.file_in, args.file_out]
    assert arg_list == ['0x0801', '2', 'ahoy', 'infile.bas', 'outfile.prg']
'''
def test_main_argparse2(capsys):
    main(['-s', 'pet', 'infile.bas', 'outfile.prg'])
    out_raw, err = capsys.readouterr()
    out = out_raw.split("\n")[:-1]
    assert out == ['0x0801', '2', 'pet', 'infile.bas', 'outfile.prg']
    assert err == ''

def test_main_argparse3(capsys):
    main(['-v', '7', 'infile.bas', 'outfile.prg'])
    out_raw, err = capsys.readouterr()
    out = out_raw.split("\n")[:-1]
    assert out == ['0x0801', '7', 'ahoy', 'infile.bas', 'outfile.prg']

def test_main_argparse4(capsys):
    main(['-l', '0x1001', 'infile.bas', 'outfile.prg'])
    out_raw, err = capsys.readouterr()
    out = out_raw.split("\n")[:-1]
    assert out == ['0x1001', '2', 'ahoy', 'infile.bas', 'outfile.prg']
'''

