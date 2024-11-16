import os
import re
import argparse
import sys
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME

from bython import VERSION_NUMBER

def ends_in_py(word):
    """
    Returns True if word ends in .py, else False

    Args:
        word (str): Filename to check

    Returns:
        boolean: Whether 'word' ends with 'py' or not
    """
    return word.endswith(".py")

def change_file_name(name, outputname=None):
    """
    Changes *.py filenames to *.by filenames. If filename does not end in .py, 
    it adds .by to the end.

    Args:
        name (str): Filename to edit
        outputname (str): Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.by at the end (unless 'outputname' is
        specified, then that is returned).
    """
    if outputname is not None:
        return outputname

    return name[:-3] + ".by" if ends_in_py(name) else name + ".by"

def translate_dictionary(definition_string):
    """
    Translate one specific dictionary definition from using {} to using dict()

    Args:
        definition_string (str): A string with a dictionary definition (including '=' beforehand)

    Returns:
        str: An equivalent definition (including '='), but using the
        dict()-constructor instead of { and }
    """
    definition_string = re.sub(r"\s*=\s*", "", definition_string)
    definition_string = re.sub(r"[{}]", "", definition_string)
    definition_string = re.sub(r"\s*\n\s*", "", definition_string)

    pairs = re.split(r"\s*,\s*", definition_string)

    result_inner = ", ".join(f"({key.strip()}, {value.strip()})" for pair in pairs if pair.strip() for key, value in [re.split(r"\s*:\s*", pair)])

    return f"= dict([{result_inner}])" if result_inner else "= dict()"

def pre_reverse_parse(infile_string):
    """
    Perform some necessary changes to the file before reverse parsing can ensue.
    This include changing dict definitions to include 

    Args:
        infile_string (str):    A string containing the whole python source

    Returns:
        str: The source with changes to dictionary definitions
    """
    dictionaries = re.findall(r"=\s*{\s*(?:.+\s*:\s*.+(?:\s*,\s*)?)*\s*}", infile_string)

    for dictionary in dictionaries:
        infile_string = re.sub(dictionary, translate_dictionary(dictionary), infile_string)

    return infile_string

def reverse_parse(filename, outputname):
    """
    Changes a Python file to a Bython file

    All semantically significant whitespace resulting in a change
    in indentation levels will have a matching opening or closing
    curly-brace.

    Args:
        filename (str):     Path of file to parse
        outputname (str):   Path of destination file
    """
    infile = open(filename, "rb")
    inlines = infile.readlines()

    for index, line in enumerate(inlines):
        inlines[index] = line.decode("utf-8")
        inlines[index] = inlines[index].rstrip()

    infile.seek(0)
    tokens = list(tokenize(infile.readline))
    infile.close()

    indent_tracker = []

    indent_levels = []
    position = 0
    line_of_last_name_token = 0
    max_indent = 0

    for token in tokens:
        current_line = token.start[0]
        if ((token.exact_type == NAME) and line_of_last_name_token != current_line):
            line_of_last_name_token = current_line
            position = token.start[1]

        if (token.exact_type == INDENT):
            indent_levels.append(position)
            indent_tracker.append((INDENT,current_line,position))

        if (token.exact_type == DEDENT):
            indent_tracker.append((DEDENT,current_line,indent_levels.pop()))

        if (len(indent_levels) > max_indent):
            max_indent = len(indent_levels)

    extra = 0

    for indent in indent_tracker:
        token = indent[0]
        index = indent[1]
        position = indent[2]

        inlines.insert(
            index + extra - 1,
            " " * position + ("}","{")[token==INDENT]
        )

        extra += 1

    outfile = open(outputname, "w")

    entire_file = "\n".join(inlines)

    entire_file = re.sub(r"\s*:", "", entire_file)

    entire_file = re.sub(r"((?:\s*#\s*.*\n?)*)?\n\s*{", r" {\1", entire_file)

    for i in range(max_indent):
        entire_file = re.sub(r"(\n+)([ \t]*})(\n)", r"\3\2\1", entire_file)

    print(entire_file, file=outfile)

def main():
    """
    Translate python to bython

    Command line utility and Python module for translating python code
    to bython code, adding curly braces at semantically significant
    indentations.
    """ 
    argparser = argparse.ArgumentParser("py2by",
        description="py2by translates python to bython",
        formatter_class=argparse.RawTextHelpFormatter
    )
    argparser.add_argument("-v", "--version", 
        action="version",
        version=f"py2by is a part of Bython v{VERSION_NUMBER}\nMathias Lohne and Tristan Pepin 2017")
    argparser.add_argument("-o", "--output",
        type=str, 
        help="specify name of output file",
        nargs=1)
    argparser.add_argument("input", type=str,
        help="python file to translate",
        nargs=1)

    cmd_args = argparser.parse_args()

    try:
        outputname = cmd_args.output[0] if cmd_args.output else change_file_name(cmd_args.input[0])

        with open(cmd_args.input[0], "r") as infile:
            infile_string = infile.read()

        pre_parsed = pre_reverse_parse(infile_string)
        temp_filename = f"{cmd_args.input[0]}.py2bytemp"
        
        with open(temp_filename, "w") as tempoutfile:
            tempoutfile.write(pre_parsed)

        reverse_parse(temp_filename, outputname)

        os.remove(temp_filename)

    except FileNotFoundError:
        print(f"No file named {cmd_args.input[0]}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()