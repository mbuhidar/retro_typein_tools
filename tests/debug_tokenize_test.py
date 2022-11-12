from io import StringIO
import pytest

from debug_tokenize.debug_tokenize import (parse_args,
                                           read_file,
                                           check_line_number_seq,
                                           ahoy_lines_list,
                                           split_line_num,
                                           _scan,
                                           scan_manager,
                                           write_binary,
                                           ahoy1_checksum,
                                           ahoy2_checksum,
                                           ahoy3_checksum,
                                           print_checksums,
                                           confirm_overwrite,
                                           write_checksums,
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


@pytest.fixture
def infile_data():
    try:
        infile = read_file('trial_infile.txt')
    except OSError:
        infile = read_file('tests/trial_infile.txt')
    return infile


def test_read_file(infile_data):
    """
    Unit test to check that function read_file() is properly reading data from
    a file source.
    """
    assert infile_data == ['10 print"hello!"', '20 goto10']


@pytest.mark.parametrize(
    "lines_list, term_capture",
    [
        (["10 OK", "20 OK", "30 OK", "40 OK"],
         ""
         ),
        (["10 OK", "20 OK"],
         ""
         ),
        (["10 OK"],
         ""
         ),
    ],
)
def test_check_line_number_seq_ok(capsys, lines_list, term_capture):
    """
    Unit test to check that function check_line_number_seq() is propery
    identifying cases where lines have the correct line number sequencing.
    """
    check_line_number_seq(lines_list)
    capture = capsys.readouterr()
    assert capture.out == term_capture


@pytest.mark.parametrize(
    "lines_list, term_capture",
    [
        (["10 OK", "20 OK", "5 OFF", "40 OK"],
         "Entry error after line 20 - lines should be in "
         "sequential order.  Exiting.\n"
         ),
        (["10 OK", "200 OFF", "30 OK", "40 OK"],
         "Entry error after line 200 - lines should be in "
         "sequential order.  Exiting.\n"
         ),
        (["10 OK", "200 OFF", "3 OFF", "40 OK"],
         "Entry error after line 200 - lines should be in "
         "sequential order.  Exiting.\n"
         ),
        (["100 OFF", "20 OK", "30 OK", "40 OK"],
         "Entry error after line 100 - lines should be in "
         "sequential order.  Exiting.\n"
         ),
        (["10 OK", "OFF", "30 OK", "40 OK"],
         "Entry error after line 10 - each line should start with a line "
         "number.  Exiting.\n"
         ),
        (["OFF", "20OK", "30 ON", "40 OK"],
         "Entry error after line 0 - each line should start with a line "
         "number.  Exiting.\n"
         ),
        (["20OK", "ON"],
         "Entry error after line 20 - each line should start with a line "
         "number.  Exiting.\n"
         ),
        (["20 OK", "10 ON"],
         "Entry error after line 20 - lines should be in "
         "sequential order.  Exiting.\n"
         ),
    ],
)
def test_check_line_number_seq_bad(capsys, lines_list, term_capture):
    """
    Unit test to check that function check_line_number_seq() is propery
    identifying cases where lines either don't start with an integer line
    number or have line numbers out of sequence.
    """
    with pytest.raises(SystemExit):
        check_line_number_seq(lines_list)
    capture = capsys.readouterr()
    assert capture.out == term_capture


@pytest.mark.parametrize(
    "lines_list, new_lines",
    [
        (['10 print"hi"', '20 goto10'], ['10 print"hi"', '20 goto10']),
        (['10 print"hello"', '20 {goto10'], (None, '20 {goto10')),
        (['{WH}CY}', '10 print"hello"'], (None, '{WH}CY}')),
        (['{WH{CY}', '10 print"hello"'], (None, '{WH{CY}')),
        (['{WH}{CY}', '{RV}'], ['{wht}{cyn}', '{rvon}']),
        (['{WH}{CD}{RV}{HM}{RD}{CR}{GN}{BL}{OR}{F1}{F2}'],
         ['{wht}{down}{rvon}{home}{red}{rght}{grn}{blu}{orng}{f1}{f2}']),
        (['{F3}{F4}{F5}{F6}{F7}{F8}{BK}{CU}{RO}'],
         ['{f3}{f4}{f5}{f6}{f7}{f8}{blk}{up}{rvof}']),
        (['{SC}{IN}{BR}{LR}{G1}{G2}{LG}{LB}{G3}'],
         ['{clr}{inst}{brn}{lred}{gry1}{gry2}{lgrn}{lblu}{gry3}']),
        (['{PU}{CL}{YL}{CY}{SS}'],
         ['{pur}{left}{yel}{cyn}{sspc}']),
        (['[CLEAR][INSERT][BROWN][LTRED][GRAY1][GRAY2][LTGREEN][LTBLUE]'],
         ['{clr}{inst}{brn}{lred}{gry1}{gry2}{lgrn}{lblu}']),
        (['[PURPLE][LEFT][YELLOW][CYAN][SS]'],
         ['{pur}{left}{yel}{cyn}{sspc}']),
        (['[2 "[PURPLE]"][LEFT][YELLOW][CYAN][SS]'],
         ['{pur}{pur}{left}{yel}{cyn}{sspc}']),
        (['print"{4"{cd}"}{cy}";:printtab(8)"press trigger"'],
         ['print"{down}{down}{down}{down}{cyn}";:printtab(8)"press trigger"']),
        (['print"[4"[cd]"][cy]";:printtab(8)"press trigger"'],
         ['print"{down}{down}{down}{down}{cyn}";:printtab(8)"press trigger"']),
        (['print"[4" "][cy]";:printtab(8)"press trigger"'],
         ['print"    {cyn}";:printtab(8)"press trigger"']),
        (['print"[4"*"][5"4"][BR]"'],
         ['print"****44444{brn}"']),
        (['print"4"*"][5"4"][BR]"'],
         (None, 'print"4"*"}{5"4"}{BR}"')),
        (['print"[4"*"[5"4"][BR]"'],
         (None, 'print"{4"*"{5"4"}{BR}"')),
        (['print"[4 " "][cy]";:printtab(8)"press trigger"'],
         ['print"    {cyn}";:printtab(8)"press trigger"']),
        (['print"[4 "*"][5 "4"][BR]"'],
         ['print"****44444{brn}"']),
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
    Unit test to check that function split_line_num() is properly splitting
    each line into tuples consisting of line number(int) and remaining line
    text(str).
    """
    assert split_line_num(line) == (split_line)


def test_write_binary(tmpdir):
    """
    Unit test to check that function write_binary() is properly writing a list
    of decimals to a binary file.
    """
    file = tmpdir.join('output.prg')
    # For reference, the ahoy input for the byte list below is:
    # 10 print"hello"
    # 20 goto10
    write_binary(file, [1, 8, 16, 8, 10, 0, 153, 40, 34,
                        72, 69, 76, 76, 79, 34, 41, 0,
                        24, 8, 20, 0, 137, 49, 48, 0, 0, 0])
    with open(file, 'rb') as f:
        contents = f.read()

    assert contents == b'\x01\x08\x10\x08\n\x00\x99("HELLO")\
\x00\x18\x08\x14\x00\x8910\x00\x00\x00'


@pytest.mark.parametrize(
    "user_entry, return_value",
    [
        ('y\n', True),
        ('Y\n', True),
        ('n\n', False),
        ('nope\n', False),
        ('\n', False),
    ],
)
def test_confirm_overwrite(capsys, monkeypatch, user_entry, return_value):
    """
    Unit test to check that function confirm_overwrite() is properly handling
    user input properly.
    """
    monkeypatch.setattr('sys.stdin', StringIO(user_entry))
    overwrite = confirm_overwrite('test_file.prg')
    out, err = capsys.readouterr()
    assert overwrite == return_value
    assert out == 'Output file "test_file.prg" already exists. ' \
                  'Overwrite? (Y = yes) '
    assert err == ''


@pytest.mark.parametrize(
    "ln, bytestr",
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
def test_scan_manager(ln, bytestr):
    """
    Unit test to check that function scan_manager() is properly managing the
    conversion of a line of text to a list of tokenized bytes in decimal form.
    """
    assert scan_manager(ln) == bytestr


@pytest.mark.parametrize(
    "ln, tokenize, byte, remaining_line",
    [
        (' space test', False, 32, 'space test'),
        ('goto11', True, 137, '11'),
        ('goto11', False, 71, 'oto11'),
        ('rem start mower', True, 143, ' start mower'),
        (' start mower', False, 32, 'start mower'),
        ('{wht}"tab(32)', True, 5, '"tab(32)'),
        ('{c g} test commodore-g', True, 165, ' test commodore-g'),
        ('{s ep}start mower', True, 169, 'start mower'),
    ],
)
def test__scan(ln, tokenize, byte, remaining_line):
    """
    Unit test to check that function _scan() is properly converting the start
    of each passed in line to a tokenized byte for BASIC keywords, petcat
    special characters, and alphanumeric characters.
    """
    assert _scan(ln, tokenize) == (byte, remaining_line)


@pytest.mark.parametrize(
    "byte_list, checksum",
    [
        # '10 GZ'
        ([71, 90, 0], 'KA'),
        # '30 G Z'
        ([71, 32, 90, 0], 'KA'),
        # '40 PRINT"HELLO WORLD"
        ([153, 34, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 34, 0], 'OI'),
        # '50 PRINT "HELLO WORLD"
        ([153, 32, 34, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 34, 0],
         'OI'),
        # '60 AA1'
        ([65, 65, 49, 0], 'NM'),
        # '70 AA2'
        ([65, 65, 50, 0], 'OA'),
        # '80 "G"
        ([34, 71, 34, 0], 'OA'),
        # '10 PRINT"HI W"
        ([153, 34, 72, 73, 32, 87, 34, 0], 'NA'),
    ],
)
def test_ahoy1_checksum(byte_list, checksum):
    """
    Unit test to check that function ahoy1_checksum() is properly calculating
    and returning the proper ahoy checksum code.
    """
    assert ahoy1_checksum(byte_list) == checksum


@pytest.mark.parametrize(
    "byte_list, checksum",
    [
        # '10 GZ'
        ([71, 90, 0], 'KF'),
        # '30 G Z'
        ([71, 32, 90, 0], 'KF'),
        # '40 PRINT"HELLO WORLD"
        ([153, 34, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 34, 0], 'PE'),
        # '50 PRINT "HELLO WORLD"
        ([153, 32, 34, 72, 69, 76, 76, 79, 32, 87, 79, 82, 76, 68, 34, 0],
         'PE'),
        # '60 AA1'
        ([65, 65, 49, 0], 'LO'),
        # '70 AA2'
        ([65, 65, 50, 0], 'LN'),
        # '80 "G"
        ([34, 71, 34, 0], 'IM'),
        # '10 PRINT"HI W"
        ([153, 34, 72, 73, 32, 87, 34, 0], 'PN'),
        # '11006 printtab(12)"{down}mike buhidar jr."'
        ([153, 163, 49, 50, 41, 34, 17, 77, 73, 75, 69, 32, 66, 85, 72, 73,\
          68, 65, 82, 32, 74, 82, 46, 34, 0], 'EI'),
        # add AA is IE; BB is IE; CC is II; DD is II
    ],
)
def test_ahoy2_checksum(byte_list, checksum):
    """
    Unit test to check that function ahoy2_checksum() is properly calculating
    and returning the proper ahoy checksum code.
    """
    assert ahoy2_checksum(byte_list) == checksum


@pytest.mark.parametrize(
    "line_num, byte_list, checksum",
    [
        # '25 GOSUB325'
        (25, [141, 51, 50, 53, 0], 'EH'),
        # '256 GOSUB325'
        (256, [141, 51, 50, 53, 0], 'CP'),
        # '23456 GOSUB325'
        (23456, [141, 51, 50, 53, 0], 'BN'),
        # '30 GOSUB425'
        (30, [141, 52, 50, 53, 0], 'EP'),
        # '485 RETURN'
        (485, [142, 0], 'HE'),
        # '20 PRINT"[8"[DOWN]"]"TAB(7)"PLEASE WAIT[4"."]READING DATA"'
        (20, [153, 34, 17, 17, 17, 17, 17, 17, 17, 17, 34, 163, 55, 41, 34, 80,
              76, 69, 65, 83, 69, 32, 87, 65, 73, 84, 46, 46, 46, 46, 82, 69,
              65, 68, 73, 78, 71, 32, 68, 65, 84, 65, 34, 0], 'LE'),
    ],
)
def test_ahoy3_checksum(line_num, byte_list, checksum):
    """
    Unit test to check that function ahoy3_checksum() is properly calculating
    and returning the proper ahoy checksum code.
    """
    assert ahoy3_checksum(line_num, byte_list) == checksum


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
    "ahoy_checksums, file_contents",
    [
        ([(11110, 'AP')],
         '11110 AP\n\nLines: 1\n'),
        ([(10, 'HE'), (20, 'PH'), (30, 'IM'), (40, 'CD'), (50, 'OB'),
          (60, 'OF'), (70, 'OG'), (80, 'NI'), (90, 'DG'), (100, 'IC'),
          (64000, 'KK')],
         '10 HE\n20 PH\n30 IM\n40 CD\n50 OB\n60 OF\n70 OG\n80 NI\n90 DG\n'
         '100 IC\n64000 KK\n\nLines: 11\n')
    ],
)
def test_write_checksums(tmpdir, ahoy_checksums, file_contents):
    """
    Unit test to check that function write_checksums() is properly writing a
    lines and checksums to a file.
    """
    file = tmpdir.join('output.chk')

    write_checksums(file, ahoy_checksums)
    with open(file, 'r') as f:
        contents = f.read()

    assert contents == file_contents


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
