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
        self.cur_indent = 0
        self.indent = ' ' * 4

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        fun = getattr(self, method, self.generic_visit)(node)
        return fun

    def generic_visit(self, node):
       if node is None:
           return ''
       else:
           try:
               return ''.join(self.visit(c) for c in node.children())
           except AttributeError, e:
               msg = 'Cannot visit : \n'
               msg += str(node) + '\n'
               msg += 'Reason: ' + str(e)
               raise Exception(msg)

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
        lhs = self.visit(n.target)
        rhs = self.visit(n.right)
        return s.format(lhs, op, rhs)

    def visit_Constant(self, n):
        # Types which do not need special treatment;
        # they can be generated without any problem
        simple_constants = [
            'int',
            'bool',
        ]
        
        if n.klass == 'string': 
            return "'" + str(n.value) + "'"
        elif n.klass == 'literal':
            return "'" + str(n.value) + "'"
        elif n.klass in simple_constants:
            return str(n.value)
        else:
            msg = 'Invalid constant: {0}'.format(n)
            raise Exception(msg)

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

    def visit_If(self, n):
        s  = 'if {0}:'
        s += '\n'
        s += '{1}'        

        cond = self.visit(n.cond)
        if_body = self._generate_stmt(n.iftrue, add_indent=True)

        if n.iffalse:
            if isinstance(n.iffalse, If):
                else_body = self._generate_stmt(n.iffalse, add_indent=False)
                s += 'el'
                s += '{2}'
            else:
                else_body = self._generate_stmt(n.iffalse, add_indent=True)
                s += self._make_indent() + 'else:\n{2}'
        else:
            else_body = ''

        return s.format(cond, if_body, else_body)

    def visit_Block(self, n):
        s = ''
        self._indent()
        
        if n.stmts:
            s += ''.join(self._generate_stmt(stmt) for stmt in n.stmts)
        else:
            s += self._make_indent() + 'pass\n'

        self._unindent()

        return s

    #
    # Helper functions
    #

    # Indent

    def _indent(self):
        self.cur_indent += 1

    def _unindent(self):
        self.cur_indent -= 1

    def _make_indent(self):
        return self.indent * self.cur_indent

    def _generate_stmt(self, n, add_indent=False):
        """ Generation from a statement node. This method exists as a wrapper
        for individual visit_* methods to handle different treatment of
        some statements in this context.
        """
        typ = type(n)
        if add_indent: self._indent()
        indent = self._make_indent()
        if add_indent: self._unindent()

        # These can also appear in an expression context so no semicolon
        # is added to them automatically
        simple_stmts = [
            Assignment, UnaryOp, BinaryOp, Call, Subscription,
            AttributeRef, Constant, Identifier
        ]
        
        if typ in simple_stmts:
            return indent + self.visit(n) + '\n'
        elif typ in (Block,):
            # No extra indentation required before the opening brace of a
            # block - because it consists of multiple lines it has to
            # compute its own indentation.
            return self.visit(n)
        else:
            return indent + self.visit(n) + '\n'
            
    # Parenthesize

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

    