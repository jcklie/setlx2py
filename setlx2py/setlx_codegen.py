#------------------------------------------------------------------------------
# setlx2py: setlx_codegen.py
#
# Code generator for the setlx2py AST
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

import re

from setlx2py.setlx_ast import *

class Codegen(object):

    def __init__(self):
        self.cur_indent = 0
        self.func_count = 0
        self.indent = ' ' * 4
        self.last_visited = ''

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        fun = getattr(self, method, self.generic_visit)(node)
        self.last_visited = method
        return fun

    def generic_visit(self, node):
       if node is None:
           return ''
       else:
           try:
               return ''.join(self.visit(c) for c in node.children())
           except AttributeError as e:
               msg = 'Cannot visit : \n'
               msg += str(node) + '\n'
               msg += 'Reason: ' + str(e) + '\n'
               msg += 'Last: ' + self.last_visited + '\n'
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

        s = '{0} {1} {2}'
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
            return "r'" + str(n.value) + "'"
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

        op_to_function = {
            '=>'   : 'implies',
            '<==>' : 'equivalent',
            '<!=>' : 'antivalent',
            '><'   : 'cartesian',
            '**'   : 'pow',
        }

        if n.op in bool_op_simple:
            op = bool_op_simple[n.op]
        elif n.op in op_to_function:
            op = op_to_function[n.op]
            s = '{1}({0},{2})'
        else:
            op = n.op
        
        return s.format(lval_str, op, rval_str)

    def visit_UnaryOp(self, n):
        op = n.op
        operand = self._parenthesize_unless_simple(n.expr)

        op_to_function = {
            'fac' : 'factorial',
            '#'   : 'len',
            '+/'  : 'sum',
            '*/'  : 'product',
        }
        if n.op in op_to_function:
            op = op_to_function[n.op]
            s = op + '({0})'
        else:
            s = op + ' {0}'

        return s.format(operand)

    def visit_Set(self, n):
        items = ','.join(self.visit(x) for x in n.items)
        return 'Set([{0}])'.format(items)

    def visit_List(self, n):
        items = ','.join(self.visit(x) for x in n.items)
        return '[{0}]'.format(items)

    def visit_Subscription(self, n):
        s = '{0}[{1} - 1]'
        obj = self._parenthesize_unless_simple(n.obj)
        subscript =  self.visit(n.subscript)
        return s.format(obj, subscript)

    def visit_Slice(self, n):
        obj = self._parenthesize_unless_simple(n.obj)
        lower = self._parenthesize_unless_simple(n.lower)
        upper = self._parenthesize_unless_simple(n.upper)

        if lower:
            lower = '(' + lower + ' - 1)'

        s = '{0}[{1}: {2}]'
        return s.format(obj, lower, upper) 

    def visit_Range(self, n):
        collection = self._get_collection_name(n.klass)
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

    def visit_Comprehension(self, n):
        collection = self._get_collection_name(n.klass)

        expr = self.visit(n.expr)
        iterators = self.visit(n.iterators)
        cond = self._parenthesize_unless_simple(n.cond)

        if cond:
            s = '{0}([{1} for {2} if {3}])'
        else:
            s = '{0}([{1} for {2}] )'
        return s.format(collection, expr, iterators, cond)
        
    def visit_If(self, n):
        s  = 'if {0}:'
        s += '\n'
        s += '{1}'        

        cond = self.visit(n.cond)
        if_body = self._generate_stmt(n.iftrue, add_indent=True)

        if n.iffalse:
            if isinstance(n.iffalse, If):
                else_body = self._generate_stmt(n.iffalse, add_indent=False).lstrip(self.indent)
                s += self._make_indent() + 'el'
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

    def visit_For(self, n):
        s = 'for {0}:'
        s += '\n'
        s += '{1}'
        iterators = self.visit(n.iterators)
        body = self._generate_stmt(n.body, add_indent=True)
        return s.format(iterators, body)

    def visit_Iterator(self, n):
        lhs = self.visit(n.assignable)
        rhs = self.visit(n.expression)
        return '{0} in {1}'.format(lhs, rhs)

    def visit_IteratorChain(self, n):
        assert n.mode in ['zip', 'cartesian'], 'Invalid mode for iterator chain : ' + n.mode
        targets = ', '.join(self.visit(itr.assignable) for itr in n.iterators)
        iterables = ', '.join(self.visit(itr.expression) for itr in n.iterators)
        return '{0} in {1}({2})'.format(targets, n.mode, iterables)

    def visit_Quantor(self, n):
        s = '{0}({1} for {2})'        
        iterators = self.visit(n.iterators)
        cond = self.visit(n.cond)
        return s.format(n.name, cond, iterators)

    def visit_Procedure(self, n):
        s = 'def {0}({1}):\n'
        s += '{2}'

        if n.clazz == 'cached':
            s = '@memoized' + '\n' + s
        params = self.visit(n.params)
        body = self.visit(n.body)
        return s.format(n.name, params, body)

    def visit_ParamList(self, n):
        return ', '.join(self.visit(param) for param in n.params)

    def visit_Param(self, n):
        return n.name

    def visit_Return(self, n):
        s = 'return'
        if n.expr: s += ' ' + self.visit(n.expr)
        return s

    def visit_ArgumentList(self, n):
        return ', '.join(self.visit(arg) for arg in n.arguments)

    def visit_Call(self, n):
        fref = self._parenthesize_unless_simple(n.name)
        return fref + '(' + self.visit(n.args) + ')'

    def visit_Lambda(self, n):
        s = 'lambda {0}: {1}'
        params = self.visit(n.params)
        body = self.visit(n.body)
        return s.format(params, body)

    def visit_Switch(self, n):
        cases = self.visit(n.case_list)
        if n.default:
            default = self.visit(n.default)
            cases += default
        return cases

    def visit_CaseList(self, n):
        s = ''.join(self.visit(case) for case in n.cases)
        return s.replace(self._make_indent() + 'el', '', 1)

    def visit_ExprList(self, n):
        s = ', '.join(self.visit(expr) for expr in n.exprs)
        return s

    def visit_Case(self, n):
        s = self._make_indent()
        s += 'elif {0}:'
        s += '\n'
        s += '{1}'        

        cond = self.visit(n.cond)
        body = self._generate_stmt(n.body, add_indent=True)

        return s.format(cond, body)

    def visit_Default(self, n):
        s = self._make_indent()
        s += 'else:\n'
        s += '{0}'        

        body = self._generate_stmt(n.body, add_indent=True)
        return s.format(body)

    def visit_Match(self, n):
        s = '_matchee = {0}\n'
        s += self._make_indent() + '{1}'
        matchee = self.visit(n.matchee)
        matches = self.visit(n.case_list)
        if n.default:
            default = self.visit(n.default)
            matches += default
        return s.format(matchee, matches)

    def visit_Pattern(self, n):
        s = '{0}, {1}'
        head = self.visit(n.head)
        tail = self.visit(n.tail)
        return s.format(head, tail)

    def visit_MatchCase(self, n):
        s = self._make_indent()
        s += 'elif matches(Pattern({0}, {1}), _matchee):\n'

        pattern = self.visit(n.pattern)
        cond = self.visit(n.cond)
        body = self._generate_stmt(n.body, add_indent=True)
        
        if isinstance(n.pattern, Pattern):
            headcount = len(n.pattern.head.exprs)
            has_tail = n.pattern.tail is not None

            if headcount > 0:
                self._indent()
                binding = self._make_indent() + '{2} = bind(Pattern({0}, {1}), _matchee)\n'
                s += binding
                self._unindent()

        else:
            head = pattern
            tail = None
        s += '{3}'        

        return s.format(headcount, has_tail, pattern, body)
        
    #
    # Helper functions
    #

    def _get_collection_name(self, clazz):
        if clazz == 'set':
            return 'Set'
        elif clazz == 'list':
            return 'list'
        else:
            msg = 'Invalid collection name: {0}'.format(clazz)
            raise Exception(msg)

    def _string_interpolate(self, s):
        pattern = re.compile('\$.*?\$')
        
        
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
            Identifier,
            List,
            Set
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

    