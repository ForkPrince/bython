import re
import os
from tokenize import tokenize, tok_name, INDENT, DEDENT, NAME
from tokenize import open as topen;
"""
Python module for converting bython code to python code.
"""

def _ends_in_by(word):
    """
    Returns True if word ends in .by, else False

    Args:
        word (str):     Filename to check

    Returns:
        boolean: Whether 'word' ends with 'by' or not
    """
    return word[-3:] == ".by"


def _change_file_name(name, outputname=None):
    """
    Changes *.by filenames to *.py filenames. If filename does not end in .by, 
    it adds .py to the end.

    Args:
        name (str):         Filename to edit
        outputname (str):   Optional. Overrides result of function.

    Returns:
        str: Resulting filename with *.py at the end (unless 'outputname' is
        specified, then that is returned).
    """

    # If outputname is specified, return that
    if outputname is not None:
        return outputname

    # Otherwise, create a new name
    if _ends_in_by(name):
        return name[:-3] + ".py"

    else:
        return name + ".py"


def parse_imports(filename):
    """
    Reads the file, and scans for imports. Returns all the assumed filename
    of all the imported modules (ie, module name appended with ".by")

    Args:
        filename (str):     Path to file

    Returns:
        list of str: All imported modules, suffixed with '.by'. Ie, the name
        the imported files must have if they are bython files.
    """
    infile = open(filename, 'r')
    infile_str = ""

    for line in infile:
        infile_str += line


    imports = re.findall(r"(?<=import\s)[\w.]+(?=;|\s|$)", infile_str)
    imports2 = re.findall(r"(?<=from\s)[\w.]+(?=\s+import)", infile_str)

    imports_with_suffixes = [im + ".by" for im in imports + imports2]

    return imports_with_suffixes


def parse_file(infilepath, outfilepath, add_true_line,  utputname=None, change_imports=None):
    """
    Converts a bython file to a python file and writes it to disk.

    Args:
        filename (str):             Path to the bython file you want to parse.
        add_true_line (boolean):    Whether to add a line at the top of the
                                    file, adding support for C-style true/false
                                    in addition to capitalized True/False.
        filename_prefix (str):      Prefix to resulting file name (if -c or -k
                                    is not present, then the files are prefixed
                                    with a '.').
        outputname (str):           Optional. Override name of output file. If
                                    omitted it defaults to substituting '.by' to
                                    '.py'    
        change_imports (dict):      Names of imported bython modules, and their 
                                    python alternative.
    """

   #filename = os.path.basename(filepath)
   #filedir = os.path.dirname(filepath)

    infile = open(infilepath, 'r')
    outfile = open(outfilepath, 'w')

    indentation_level = 0
    indentation_sign = "    "
    current_line = ""

    if add_true_line:
        outfile.write("true=True; false=False; null=None\n")
    
    tokenfile = open(infilepath, 'rb')
    tokens = list(tokenize(tokenfile.readline))
    tokens.pop(0)
    
    for i, j in enumerate(tokens):
        #print(j)
        #write line with indentation
        
        if j.string == "{":
            indentation_level += 1
            current_line += ":"
        elif j.string == "}":
            indentation_level -= 1

        #check for && and replace with and
        elif j.string == "&" and tokens[i+1].string == "&":
            current_line += " and "
        elif j.string == "&" and tokens[i-1].string == "&":
            pass
        
        #check for || and replace with or
        elif j.string == "|" and tokens[i+1].string == "|":
            current_line += " or "
        elif j.string == "|" and tokens[i-1].string == "|":
            pass

        else:
            current_line += j.string


        #adds a space after NAME tokens, so def main doesnt become defmain
        if j.type == 1:
            current_line += " "
        #on a newline, write the current line and restart
        if j.string == "\n":
            outfile.write(current_line)
            current_line = indentation_level * indentation_sign

    infile.close()
    outfile.close()
    # Add 'pass' where there is only a {}. 
    # 
    # DEPRECATED FOR NOW. This way of doing
    # it is causing a lot of problems with {} in comments. The feature is removed
    # until I find another way to do it. 
    
    # infile_str_raw = re.sub(r"{[\s\n\r]*}", "{\npass\n}", infile_str_raw)
    


""" Complete garbage, exists solely for reference from now on
    # Fix indentation
    infile_str_indented = ""
    for line in infile_str_raw.split("\n"):
        # Search for comments, and remove for now. Re-add them before writing to
        # result string
        m = re.search(r"[ \t]*(#.*$)", line)

        # Make sure # sign is not inside quotations. Delete match object if it is
        if m is not None:
            m2 = re.search(r"[\"'].*#.*[\"']", m.group(0))
            if m2 is not None:
                m = None

        if m is not None:
            add_comment = m.group(0)
            line = re.sub(r"[ \t]*(#.*$)", "", line)
        else:
            add_comment = ""

        # skip empty lines:
        if line.strip() in ('\n', '\r\n', ''):
            infile_str_indented += indentation_level*indentation_sign + add_comment.lstrip() + "\n"
            continue

        # remove existing whitespace:
        line = line.lstrip()
        
        # Check for reduced indent level
        for i, j in enumerate(list(line)):
            if (j == "}"):
                brace_inside_string = False
                for k in string_regex.finditer(line): #check if curly brace is inside string
                    if (k.span()[0] < i and i < k.span()[1]):
                        brace_inside_string = True
                if (not brace_inside_string):
                    indentation_level -= 1

        # Add indentation
        for i in range(indentation_level):
            line = indentation_sign + line

        # Check for increased indentation
        for i, j in enumerate(list(line)):
            if j == "{":
                brace_inside_string = False
                for k in string_regex.finditer(line): #check if curly brace is inside string
                    if (k.span()[0] < i and i < k.span()[1]):
                        brace_inside_string = True
                if (not brace_inside_string):
                    indentation_level += 1

        # Replace { with : and remove }
        line = re.sub(r"[\t ]*{[ \t]*", ":", line)
        line = re.sub(r"}[ \t]*", "", line)
        line = re.sub(r"\n:", ":", line)

        infile_str_indented += line + add_comment + "\n"


    # Support for extra, non-brace related stuff
    infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
    infile_str_indented = re.sub(r";\n", "\n", infile_str_indented)

    # Change imported names if necessary
    if change_imports is not None:
        for module in change_imports:
            infile_str_indented = re.sub("(?<=import\\s){}".format(module), "{} as {}".format(change_imports[module], module), infile_str_indented)
            infile_str_indented = re.sub("(?<=from\\s){}(?=\\s+import)".format(module), change_imports[module], infile_str_indented)

    outfile.write(infile_str_indented)

    infile.close()
    outfile.close()"""
