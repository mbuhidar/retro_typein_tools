from typein_tokenizer.tokenizer import main
# from typeintokenizer import tokenizer
import pytest

def test_main_argparse1(capsys):
    main(['infile.bas', 'outfile.prg'])
    out_raw, err = capsys.readouterr()
    out = out_raw.split("\n")[:-1]
    assert out == ['0x0801', '2', 'ahoy', 'infile.bas', 'outfile.prg']
    assert err == ''

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
