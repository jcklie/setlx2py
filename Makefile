parser:
	python -i -c "from setlx2py.setlx_parser import Parser; parser = Parser()"

ast:
	python -c "from astgen.ast_gen import ASTCodeGenerator; \
	ast_gen = ASTCodeGenerator('setlx2py/setlx_ast.cfg'); \
	ast_gen.generate(open('setlx2py/setlx_ast.py', 'w'))"

test:
	nosetests
