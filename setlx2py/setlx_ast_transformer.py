from setlx2py.setlx_ast import *

class AstTransformer(NodeVisitor):

    def visit_Quantor(self, n):
        n.iterators.mode = 'cartesian'
        self.generic_visit(n)

    def visit_Comprehension(self, n):
        n.iterators.mode = 'cartesian'
        self.generic_visit(n)

    def visit_For(self, n):
        n.iterators.mode = 'zip'
        self.generic_visit(n)

    def visit_FileAST(self, n):
        for i, stmt in enumerate(n.stmts):
            if isinstance(stmt, Assignment) and isinstance(stmt.right, Procedure):
                assignment = stmt
                procedure = assignment.right
                procedure.name = assignment.target.name
                n.stmts[i] = procedure
                
            self.generic_visit(n)

    
    
    