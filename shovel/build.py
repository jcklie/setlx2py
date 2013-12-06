from shovel import task

@task
def ast():
    from astgen.ast_gen import ASTCodeGenerator
    print("""
   ___                                   _               _     ___   _____ 
  / __|  ___   _ _    ___   _ _   __ _  | |_   ___      /_\   / __| |_   _|
 | (_ | / -_) | ' \  / -_) | '_| / _` | |  _| / -_)    / _ \  \__ \   | |  
  \___| \___| |_||_| \___| |_|   \__,_|  \__| \___|   /_/ \_\ |___/   |_|  
""")                                                                           
    ast_gen = ASTCodeGenerator('setlx2py/setlx_ast.cfg')
    ast_gen.generate(open('setlx2py/setlx_ast.py', 'w'))
