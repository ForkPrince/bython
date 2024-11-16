import re
import os
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME
from tokenize import open as topen

"""Python module for converting bython code to python code."""

def ends_in_by(word):
    """
    Returns True if word ends in .by, else False

    Args:
        word (str): Filename to check

    Returns:
        bool: Whether 'word' ends with 'by' or not
    """
    return word.endswith(".by")

def change_file_name(name, outputname=None):
    """
    Changes *.by filenames to *.py filenames. If filename does not end in .by, 
    it adds .py to the end.

    Args:
        name (str): Filename to edit
        outputname (str): Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.py at the end (unless 'outputname' is
        specified, then that is returned).
    """
    if outputname is not None:
        return outputname

    return name[:-3] + ".py" if ends_in_by(name) else name + ".py"

def parse_imports(filename):
    """
    Reads the file, and scans for imports. Returns all the assumed filename
    of all the imported modules (ie, module name appended with ".by")

    Args:
        filename (str): Path to file

    Returns:
        list of str: All imported modules, suffixed with '.by'. Ie, the name
        the imported files must have if they are bython files.
    """
    with open(filename, "r") as infile:
        infile_str = infile.read()

    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    return [f"{im}.by" for im in imports + imports2]

def parse_file(infilepath, outfilepath, add_true_line, outputname=None, change_imports=None):
    """
    Converts a bython file to a python file and writes it to disk.

    Args:
        infilepath (str): Path to the bython file you want to parse.
        outfilepath (str): Path to the output Python file.
        add_true_line (bool): Whether to add a line at the top of the file, adding support for C-style true/false in addition to capitalized True/False.
        outputname (str): Optional. Override name of output file. If omitted it defaults to substituting '.by' to '.py'
        change_imports (dict): Names of imported bython modules, and their python alternative.
    """
    with open(infilepath, "r") as infile, open(outfilepath, "w") as outfile:
        if add_true_line:
            outfile.write("true=True; false=False; null=None\n")

        indentation_level = 0
        indentation_sign = "    "
        current_line = ""

        with open(infilepath, "rb") as tokenfile:
            tokens = list(tokenize(tokenfile.readline))
        tokens.pop(0)

        inside_fstring = False
        inside_dict = False

        for i, token in enumerate(tokens):
            if token.type == 61:  # STRING_START
                inside_fstring = True
            elif token.type == 63:  # STRING_END
                inside_fstring = False

            if token.string == "=" and tokens[i+1].string == "{":
                inside_dict = True
            if inside_dict and tokens[i-1].string == "}":
                inside_dict = False

            if inside_fstring or inside_dict:
                current_line += token.string
                continue

            if token.string == "{":
                indentation_level += 1
                current_line += ":"
            elif token.string == "}":
                indentation_level -= 1
                outfile.write(current_line + "\n")
                current_line = indentation_level * indentation_sign
            elif token.string == "&" and tokens[i+1].string == "&":
                current_line += " and "
            elif token.string == "&" and tokens[i-1].string == "&":
                continue
            elif token.string == "|" and tokens[i+1].string == "|":
                current_line += " or "
            elif token.string == "|" and tokens[i-1].string == "|":
                continue
            else:
                current_line += token.string

            if token.type == NAME:
                current_line += " "

            if token.string == "\n":
                outfile.write(current_line)
                current_line = indentation_level * indentation_sign