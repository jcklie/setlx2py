#------------------------------------------------------------------------------
# setlx2py: setlxc
#
# CLI for setlx2py
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from argparse import ArgumentParser

import os.path
import argparse

from setlx2py.setlx_util import compile_setlx

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file {0} does not exist!".format(arg))
    else:
        return os.path.abspath(arg)

def is_writable(parser, arg):
    try:
        with open(arg, 'w') as f:
            return os.path.abspath(arg)
    except:
        parser.error("The file {0} cannot be written!".format(arg))

def compile(inp, out):
    parser = Parser()
    transformer = AstTransformer()
    generator = Codegen()
    ast = parser.parse(source)
    transformer.visit(ast)
    compiled = generator.visit(ast)
    header =  'from setlx2py.setlx_builtin import *\n'
    compiled = header + compiled

parser = ArgumentParser(description="ikjMatrix multiplication")
parser.add_argument("-i", required=True, help="input file", metavar="FILE",
                    type=lambda x: is_valid_file(parser,x))

parser.add_argument("-o", required=True, help="output file", metavar="FILE",
                    type=lambda x: is_writable(parser,x))


args = parser.parse_args()

print(args.i)
print(args.o)

source = ""

with open(args.i, 'r') as input_file:
    source = input_file.read()

with open(args.o, 'w') as output_file:
    compiled = compile_setlx(source)
    output_file.write(compiled)
    

