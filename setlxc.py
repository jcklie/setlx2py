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

from setlx2py.setlx_util import log_ast, HEADER
from setlx2py.setlx_parser import Parser
from setlx2py.setlx_ast_transformer import AstTransformer
from setlx2py.setlx_codegen import Codegen
from setlx2py.setlx_ast import Call

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file {0} does not exist!".format(arg))
    else:
        return os.path.abspath(arg)

def is_writable(parser, arg):
    try:
        with open(arg, 'w') as _:
            return os.path.abspath(arg)
    except:
        parser.error("The file {0} cannot be written!".format(arg))
        
def build_argparser():
    argparser = ArgumentParser(description="ikjMatrix multiplication")
    argparser.add_argument("-i", required=True, help="input file", metavar="FILE",
                        type=lambda x: is_valid_file(argparser,x))
    
    argparser.add_argument("-o", required=True, help="output file", metavar="FILE",
                        type=lambda x: is_writable(argparser,x))
    
    argparser.add_argument("-v", required=False, help="verbosity", action="store_true")
    return argparser

if  __name__ == '__main__':    
    args = build_argparser().parse_args()
    
    source = ""
    
    with open(args.i, 'r') as input_file:
        source = input_file.read()    
    
    parser = Parser()
    ast = parser.parse(source)
    
    if args.v: log_ast(ast)
        
    # Load files
    # We just search for calls to the 'load' function
        
    to_replace = {} # Stores which Call nodes to replace with AST from loaded file
    for i, stmt in enumerate(ast.stmts):
        if isinstance(stmt, Call) and stmt.name.name == 'load':
            path = stmt.args.arguments[0].value
            to_replace[i] = path
    
    # Second loop as you do not want to alter a list you are iterating on            
    for i, path in to_replace.items():        
        with open(path, 'r') as f:
            source = f.read()
            parser = Parser()
            transformer = AstTransformer()
            loaded_ast = parser.parse(source)
            ast.stmts = ast.stmts[:i] + loaded_ast.stmts + ast.stmts[i+1:]
        
    # Transform
    transformer = AstTransformer()   
    transformer.visit(ast)
        
    # Generate code    
    generator = Codegen() 
    compiled = generator.visit(ast)
    compiled = HEADER + compiled    
        
    with open(args.o, 'w') as output_file:    
        output_file.write(compiled)
