#------------------------------------------------------------------------------
# setlx2py: setlx_util.py
#
# Central place for functions which are needed in at least
# two different files
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import sys
import re

from cStringIO import StringIO

from setlx2py.setlx_parser import Parser
from setlx2py.setlx_ast_transformer import AstTransformer
from setlx2py.setlx_codegen import Codegen

from setlx2py.setlx_builtin import *

parser = Parser()
transformer = AstTransformer()
generator = Codegen()

def error_msg(source, compiled=None, e=None):
    msg = 'Could not run stuff:\n'
    msg += 'Source:\n' + source + '\n'
    
    if compiled:
        msg += 'Compiled:\n' + compiled
    if e:
        msg += 'Reason:\n'
        msg += e.__class__.__name__ + '\n'
        msg += str(e) + '\n'
        msg += 'Line: ' + str(get_exception_line(e))
    return msg

def get_exception_line(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    return exc_tb.tb_lineno

def run(source, ns={}, verbose=False, print_ast=False):
    copy_globals = dict(globals())
    copy_locals = dict(locals())
#    ns.update(copy_globals)
    ast = parser.parse(source)
    transformer.visit(ast)
    
    if verbose:
        print('Source: \n' + source)

    if print_ast:
        print(ast)

    compiled = generator.visit(ast)

    header =  'from setlx2py.setlx_builtin import *\n'
    
    compiled = header + compiled
    if verbose:
        print('Compliled: \n' + compiled)

    try:
        code = compile(compiled, '<string>', 'exec')    
        exec(code, ns)
    except Exception as e:
        msg = error_msg(source, compiled, e=e)
        raise AssertionError(msg)