#------------------------------------------------------------------------------
# setlx2py: setlx_codegen.py
#
# Code generator for the setlx2py AST
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from setlx2py.setlx_ast import *

class Codegen(object):

    def __init__(self):
        self.output = ''
        self.ident_level = 0

    def _make_indent(self):
        return ' ' * self.indent_level

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        fun = getattr(self, method, self.generic_visit)(node)
        return fun

    def generic_visit(self, node):
       if node is None:
           return ''
       else:
           return ''.join(self.visit(c) for c in node.children())

    ## Visit functions

    def visit_Identifier(self, n):
        return n.name

    def visit_FileAST(self, n):
        s = ''
        for stmt in n.stmts:
            s += self.visit(stmt) + '\n'
        return s

    def visit_Assignment(self, n):
        s = '{0} {1} {2}'
        op = n.op if n.op != ':=' else '='
        return s.format(self.visit(n.target), op, self.visit(n.right))

    def visit_Constant(self, n):
        return str(n.value)

    def visit_BinaryOp(self, n):
        lval_str = self._parenthesize_unless_simple(n.left)
        rval_str = self._parenthesize_unless_simple(n.right)

        s = '{0} {1} {2}'

        bool_op_simple = {
            '&&' : 'and',
            '||' : 'or',
        }

        bool_op_complex = {
            '=>'   : 'implies',
            '<==>' : 'equivalent',
            '<!=>' : 'antivalent',
        }

        if n.op in bool_op_simple:
            op = bool_op_simple[n.op]
        elif n.op in bool_op_complex:
            op = bool_op_complex[n.op]
            s = '{1}({0},{2})'
        else:
            op = n.op
        
        return s.format(lval_str, op, rval_str)

    def visit_Set(self, n):
        items = ','.join(self.visit(x) for x in n.items)
        return 'frozenset([{0}])'.format(items)

    def visit_List(self, n):
        items = ','.join(self.visit(x) for x in n.items)
        return '[{0}]'.format(items)

    def visit_Range(self, n):
        if n.klass == 'set':
            collection = 'frozenset'
        elif n.klass == 'list':
            collection = 'list'
        else:
            msg = 'Invalid range: {0}'.format(n.klass)
            raise Exception(msg)
            
        lower = self._parenthesize_unless_simple(n.a)
        middle = self._parenthesize_unless_simple(n.b)
        upper = self._parenthesize_unless_simple(n.c)

        if middle:
            s = '{0}(range({1},{2}, {3}))'
            step = '{0} - {1}'.format(middle, lower)
        else:
            s = '{0}(range({1},{2} + 1, {3}))'
            step = '1'
        
        return s.format(collection, lower, upper, step)
        
    def visit_UnaryOp(self, n):
        op = n.op
        operand = self._parenthesize_unless_simple(n.expr)
        if op == 'fac':
            s = 'factorial({0})'

        else:
            s = op + ' {0}'

        return s.format(operand)

    # Helper functions

    def _is_simple_node(self, n):
        """ Returns True for nodes that are "simple" - i.e. nodes that always
            have higher precedence than operators.
        """
        simple_nodes = (
            Constant,
            Identifier
        )
        return isinstance(n, simple_nodes) or n is None

    def _parenthesize_if(self, n, condition):
        s = self.visit(n)
        return '(' + s + ')' if condition(n) else s

    def _parenthesize_unless_simple(self, n):
        """ Common use case for _parenthesize_if """
        return self._parenthesize_if(n, lambda d: not self._is_simple_node(d))

    def _parenthesize_if_simple(self, n):
        """ Common use case for _parenthesize_if """
        return self._parenthesize_if(n, self._is_simple_node)
        