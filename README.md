# Retro Type-In Tools

## debug_tokenize
The debug_tokenize tool is a converter for Commodore BASIC programs focused on 
tokenizing magazine type-in programs popular in the mid- and late-eighties. 
Given an input text file containing BASIC source code in magazine type-in
format, it outputs two files using the basename from the input file.

As an example for an Ahoy! magazine file:

```
Input:    basename.ahoy

Output1:  basename.bas (VICE petcat-ready BASIC source code with special
characters converted to VICE petcat special character codes)

Output2:  basename.prg (tokenized file that can be run on a Commodore 
computer or on an emulator like VICE)
```

### Usage

From the directory where debug_tokenize.py exists, type:

```
python3 debug_tokenize.py [-l load_address] [-v basic_version] [-s source_format] input_file
```

```
positional arguments:
  input_file            Specify the input file name including path
                        Note:  Output files will use input file basename
                        with extensions '.pet' for petcat-ready file and
                        '.prg' for Commodore executable file format.

optional arguments:
  -h, --help            show this help message and exit
  -l load_address, --loadaddr load_address
                        Specifies the target BASIC memory address when loading:
                        - 0x0801 - C64 (default)
                        - 0x1001 - VIC20 Unexpanded
                        - 0x0401 - VIC20 +3K
                        - 0x1201 - VIC20 +8K
                        - 0x1201 - VIC20 +16
                        - 0x1201 - VIC20 +24K
  -v basic_version, --version basic_version
                        Specifies the BASIC version for use in tokenizing file.
                        - 1 - Basic v1.0  PET
                        - 2 - Basic v2.0  C64/VIC20/PET (default)
                        - 3 - Basic v3.5  C16/C116/Plus/4
                        - 4 - Basic v4.0  PET/CBM2
                        - 7 - Basic v7.0  C128
  -s source_format, --source source_format
                        Specifies the source BASIC file format:
                        pet - use standard pet control character mnemonics
                        ahoy - use Ahoy! magazine control character mnemonics (default)
```

### Using the output files

If you want to use the VICE petcat utility to tokenize the BASIC file, type:

```
petcat -w2 -o program.prg -- program.bas 
```

Generates an executable program.prg file that can be run on a Commodore 
computer or emulator.  In this example, it tokenizes for Commodore BASIC v2.

You can also use the .prg file generated directly from the tokenizer program
by running it with the following command (must have VICE installed):

```
x64sc -basicload program.prg &
```
