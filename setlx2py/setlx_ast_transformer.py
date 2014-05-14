import re

from setlx2py.setlx_ast import *
from setlx2py.setlx_parser import Parser

TAG_INTERPOLATION = "KLIENTERPOLATION"

class AstTransformer(NodeVisitor):

    def visit(self, node, parent=None):
        """ Visit a node.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent)
        
    def generic_visit(self, node, parent):
        """ Called if no explicit visitor function exists for a
        node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            self.visit(c, node)

    def visit_FileAST(self, n, p):
        for i, stmt in enumerate(n.stmts):
            if isinstance(stmt, Assignment) and isinstance(stmt.right, Procedure):
                assignment = stmt
                procedure = assignment.right
                procedure.name = assignment.target.name
                n.stmts[i] = procedure

            self.generic_visit(n, p)

    def visit_MatchCase(self, n, p):
        pattern = n.pattern
        if isinstance(pattern, List):
            lst = ExprList(list(pattern.items))
            n.pattern = Pattern(lst, None)
        self.generic_visit(n, p)

    def visit_Pattern(self, n, p):
        head = n.head
        if not isinstance(head, ExprList):
            n.head = ExprList([head])
        self.generic_visit(n, p)

    def visit_Assignment(self, n, p):
        target = n.target
        if isinstance(target, List):
            target.tags.append('bracketed')
        self.generic_visit(n, p)

    def visit_Iterator(self, n, p):
        assignable = n.assignable
        n.tags.append('bracketed')
        self.generic_visit(n, p)

    def visit_List(self, n, p):
        if isinstance(p, Iterator):
            n.tags.append('outer_list')
        elif "bracketed" in p.tags or  "outer_list" in p.tags :
            n.tags.append('bracketed')
        self.generic_visit(n, p)

    def visit_Range(self, n, p):
        if "bracketed" in p.tags:
            n.tags.append('bracketed')
        self.generic_visit(n, p)

    def visit_Interpolation(self, n, p):
        self._fill_interpolation(n)
        self.generic_visit(n, p)
            
    def _fill_interpolation(self, n):
        text = n.format_string.value
        parser = Parser()
        format_string, expressions = self._extract_interpolations(text)
        exprs = [parser.parse(expr) for expr in expressions]
        n.format_string.value = format_string
        n.expressions.exprs.extend(exprs)

    def _extract_interpolations(self, s):
        pattern = re.compile('\$([^\$]+?)\$')
        expressions =  re.findall(pattern, s)
        formatted = s
        for i in range(len(expressions)):
            formatted = re.sub(pattern, '{' + str(i) + '}', formatted, count=1)
        return formatted, expressions