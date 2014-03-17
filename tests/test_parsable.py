from nose.tools import with_setup

import types

def create_function(name, args):
    def y(): pass
    
    y_code = types.CodeType(args, \
                            y.func_code.co_nlocals, \
                            y.func_code.co_stacksize, \
                            y.func_code.co_flags, \
                            y.func_code.co_code, \
                            y.func_code.co_consts, \
                            y.func_code.co_names, \
                            y.func_code.co_varnames, \
                            y.func_code.co_filename, \
                            name, \
                            y.func_code.co_firstlineno, \
                            y.func_code.co_lnotab)
    
    return types.FunctionType(y_code, y.func_globals, name)


def setup():
    myfunc = create_function('myfunc', 3)

@with_setup(setup)    
def test_dummy(): pass


