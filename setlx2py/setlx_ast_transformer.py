from setlx2py.setlx_ast import *

class AstTransformer(NodeVisitor):

    def visit_FileAST(self, n):
        for i, stmt in enumerate(n.stmts):
            if isinstance(stmt, Assignment) and isinstance(stmt.right, Procedure):
                assignment = stmt
                procedure = assignment.right
                procedure.name = assignment.target.name
                n.stmts[i] = procedure
                
            self.generic_visit(n)

    def visit_MatchCase(self, n):
        pattern = n.pattern
        if isinstance(pattern, List):
            lst = ExprList(list(pattern.items))
            n.pattern = Pattern(lst, None)
        self.generic_visit(n)

    def visit_Pattern(self, n):
        head = n.head
        if not isinstance(head, ExprList):
            n.head = ExprList([head])
        self.generic_visit(n)

    def visit_Assignment(self, n):
        target = n.target
        if isinstance(target, List):
            target.tags.append('bracketed')
        self.generic_visit(n)

    def visit_Iterator(self, n):
        assignable = n.assignable
        if isinstance(assignable, List):
            assignable.tags.append('bracketed')
        self.generic_visit(n)
            
            