from io import StringIO
import pytest

from debug_tokenize.debug_tokenize import (parse_args,
                                           print_checksums,
                                           command_line_runner)


@pytest.mark.parametrize(
    "argv, arg_valid",
    [
        (['infile.ahoy'],
         ['0x0801', 'ahoy2', 'infile.ahoy']),
        (['infile.ahoy', '-s', 'ahoy1'],
         ['0x0801', 'ahoy1', 'infile.ahoy']),
        (['infile.ahoy', '-l', '0x1001'],
         ['0x1001', 'ahoy2', 'infile.ahoy']),
        (['-s', 'ahoy3', 'infile.ahoy', '-l', '0x1001'],
         ['0x1001', 'ahoy3', 'infile.ahoy']),
    ],
)
def test_parse_args(argv, arg_valid):
    """
    Unit test to check that function parse_args() yields the correct list of
    arguments for a range of different command line input combinations.
    """
    args = parse_args(argv)
    arg_list = [args.loadaddr[0], args.source[0], args.file_in]
    assert arg_list == arg_valid


@pytest.mark.parametrize(
    "ahoy_checksums, term_width, term_capture",
    [
        ([(11110, 'AP')],
         31,
         ' 11110 AP   \n\nLines: 1\n\n'),
        ([(10, 'HE'), (20, 'PH'), (30, 'IM'), (40, 'CD'), (50, 'OB'),
          (60, 'OF'), (70, 'OG'), (80, 'NI'), (90, 'DG'), (100, 'IC'),
          (64000, 'KK')],
         44,
         '    10 HE       50 OB       90 DG   \n    20 PH       60 OF      '
         '100 IC   \n    30 IM       70 OG    64000 KK   \n    40 CD       '
         '80 NI   \n\nLines: 11\n\n')
    ],
)
def test_print_checksums(capsys, ahoy_checksums, term_width, term_capture):
    """
    Unit test to check that function print_checksums() is propery creating
    lists for lines and codes to print in a matrix format.
    """
    print_checksums(ahoy_checksums, term_width)
    captured = capsys.readouterr()
    assert captured.out == term_capture


@pytest.mark.parametrize(
    "source, lines_list, term",
    [
        ('ahoy1', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\nFile '
         '"{d}/example.prg" written successfully.\n\nLine Checksums:\n\n    '
         '10 IA       20 NI   \n\nLines: 2\n\n'),

        ('ahoy2', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\nFile '
         '"{d}/example.prg" written successfully.\n\nLine Checksums:\n\n    '
         '10 EO       20 PH   \n\nLines: 2\n\n'),

        ('ahoy3', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\nFile '
         '"{d}/example.prg" written successfully.\n\nLine Checksums:\n\n    '
         '10 GC       20 PP   \n\nLines: 2\n\n'),
    ],
)
def test_command_line_runner(tmp_path, capsys, source, lines_list, term):
    """
    End to end test to check that function command_line_runner() is properly
    generating the correct output for a given command line input.
    """
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "example.ahoy"
    p.write_text(lines_list)

    term_capture = term.format(d=d)

    argv = ['-s', source, str(p)]

    command_line_runner(argv, 40)

    captured = capsys.readouterr()
    assert captured.out == term_capture


@pytest.mark.parametrize(
    "user_entry, source, lines_list, term",
    [
        ('Y\n', 'ahoy1', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'Writing binary output file "{d}/example.prg"...\n\n'
         'File "{d}/example.prg" written successfully.\n\nLine Checksums:\n\n'
         '    10 IA       20 NI   \n\nLines: 2\n\n'),

        ('y\n', 'ahoy2', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'Writing binary output file "{d}/example.prg"...\n\n'
         'File "{d}/example.prg" written successfully.\n\nLine Checksums:\n\n'
         '    10 EO       20 PH   \n\nLines: 2\n\n'),

        ('y\n', 'ahoy3', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'Writing binary output file "{d}/example.prg"...\n\n'
         'File "{d}/example.prg" written successfully.\n\nLine Checksums:\n\n'
         '    10 GC       20 PP   \n\nLines: 2\n\n'),

        ('N\n', 'ahoy1', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'File "{d}/example.prg" not overwritten.\n\nLine Checksums:\n\n'
         '    10 IA       20 NI   \n\nLines: 2\n\n'),

        ('N\n', 'ahoy2', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'File "{d}/example.prg" not overwritten.\n\nLine Checksums:\n\n'
         '    10 EO       20 PH   \n\nLines: 2\n\n'),

        ('no\n', 'ahoy3', '10 PRINT"HELLO"\n20 GOTO10',
         'Writing binary output file "{d}/example.prg"...\n\n'
         'Output file "{d}/example.prg" already exists. Overwrite? (Y = yes) '
         'File "{d}/example.prg" not overwritten.\n\nLine Checksums:\n\n'
         '    10 GC       20 PP   \n\nLines: 2\n\n'),

    ],
)
def test_command_line_runner_interactive(tmp_path, capsys, monkeypatch,
                                         user_entry, source, lines_list, term):
    """
    End to end test to check that function command_line_runner() is properly
    generating the correct output for a given command line input.
    """
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "example.ahoy"
    p.write_text(lines_list)
    o = d / "example.prg"
    o.write_text("create the file")

    term_capture = term.format(d=d)

    argv = ['-s', source, str(p)]

    monkeypatch.setattr('sys.stdin', StringIO(user_entry))
    command_line_runner(argv, 40)
    captured = capsys.readouterr()
    assert captured.out == term_capture
