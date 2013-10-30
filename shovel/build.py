from shovel import task

@task
def ast():
    from astgen.ast_gen import ASTCodeGenerator
    ast_gen = ASTCodeGenerator('setlx2py/setlx_ast.cfg')
    ast_gen.generate(open('setlx2py/setlx_ast.py', 'w'))
