#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# setlx2py/setlx_ast.cfg
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
# ** ** *** ** **
#
# AST Node classes.
#
# Copyright (C) 2008-2013, Eli Bendersky
#               2013,      Jan-Christoph Klie 
# License: BSD
#-----------------------------------------------------------------


import sys


class Node(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def __str__(self):
        return self.show()

    def __repr__(self):
        return str(self.to_tuples())

    def to_tuples(self):
        result = [self.__class__.__name__]

        attr_list = [getattr(self, n) for n in self.attr_names]
        result.extend(attr_list)

        for (child_name, child) in self.children():
            result.append( child.to_tuples() )
        return tuple(result)

    def show(self,
             buf=None,
             offset=0,
             attrnames=False,
             nodenames=False,
             showcoord=False,
             _my_node_name=None):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.

            buf:
                Open IO buffer into which the Node is printed.
                If it is None or let empty, instead a string
                is returned

            offset:
                Initial offset (amount of leading spaces)

            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.

            nodenames:
                True if you want to see the actual node names
                within their parents.

            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        s = ''
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            s += lead + self.__class__.__name__+ ' <' + _my_node_name + '>: '
        else:
            s += lead + self.__class__.__name__+ ': '

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            s += attrstr

        if showcoord: s += ' (at %s)' % self.coord
        s += '\n'

        for (child_name, child) in self.children():
            s += child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)

        if buf is None: return s
        else: buf.write(s)

class NodeVisitor(object):
    """ A base NodeVisitor class for visiting c_ast nodes.
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these
        methods.

        For example:

        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []

            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes
        encountered below the given node. To use it:

        cv = ConstantVisitor()
        cv.visit(node)

        Notes:

        *   generic_visit() will be called for AST nodes for which
            no visit_XXX method was defined.
        *   The children of nodes for which a visit_XXX was
            defined will not be visited - if you need this, call
            generic_visit() on the node.
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """
    def visit(self, node):
        """ Visit a node.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a
            node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            self.visit(c)


class As (Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Assert(Node):
    def __init__(self, cond, expr, coord=None):
        self.cond = cond
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()

class ArgumentList (Node):
    def __init__(self, arguments, coord=None):
        self.arguments = arguments
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.arguments or []):
            nodelist.append(("arguments[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Assignment(Node):
    def __init__(self, op, target, right, coord=None):
        self.op = op
        self.target = target
        self.right = right
        self.coord = coord

    def children(self):
        nodelist = []
        if self.target is not None: nodelist.append(("target", self.target))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    attr_names = ('op',)

class AttributeRef (Node):
    def __init__(self, obj, field, coord=None):
        self.obj = obj
        self.field = field
        self.coord = coord

    def children(self):
        nodelist = []
        if self.obj is not None: nodelist.append(("obj", self.obj))
        if self.field is not None: nodelist.append(("field", self.field))
        return tuple(nodelist)

    attr_names = ()

class BinaryOp(Node):
    def __init__(self, op, left, right, coord=None):
        self.op = op
        self.left = left
        self.right = right
        self.coord = coord

    def children(self):
        nodelist = []
        if self.left is not None: nodelist.append(("left", self.left))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    attr_names = ('op',)

class Backtrack(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class Block(Node):
    def __init__(self, stmts, coord=None):
        self.stmts = stmts
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Break(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class CachedProcedure(Node):
    def __init__(self, params, body, coord=None):
        self.params = params
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.params is not None: nodelist.append(("params", self.params))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

class Call (Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.args is not None: nodelist.append(("args", self.args))
        return tuple(nodelist)

    attr_names = ()

class Case(Node):
    def __init__(self, cond, block, coord=None):
        self.cond = cond
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    attr_names = ()

class CaseList (Node):
    def __init__(self, cases, coord=None):
        self.cases = cases
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.cases or []):
            nodelist.append(("cases[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Class(Node):
    def __init__(self, name, params, block, static, coord=None):
        self.name = name
        self.params = params
        self.block = block
        self.static = static
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.params is not None: nodelist.append(("params", self.params))
        if self.block is not None: nodelist.append(("block", self.block))
        if self.static is not None: nodelist.append(("static", self.static))
        return tuple(nodelist)

    attr_names = ()

class Comprehension (Node):
    def __init__(self, klass, expr, iterators, cond, coord=None):
        self.klass = klass
        self.expr = expr
        self.iterators = iterators
        self.cond = cond
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        if self.iterators is not None: nodelist.append(("iterators", self.iterators))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        return tuple(nodelist)

    attr_names = ('klass',)

class Continue(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class Constant(Node):
    def __init__(self, klass, value, coord=None):
        self.klass = klass
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('klass','value',)

class Default(Node):
    def __init__(self, block, coord=None):
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    attr_names = ()

class DoWhile(Node):
    def __init__(self, cond, body, coord=None):
        self.cond = cond
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

class Exit(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    attr_names = ()

class ExprList(Node):
    def __init__(self, exprs, coord=None):
        self.exprs = exprs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.exprs or []):
            nodelist.append(("exprs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class FileAST(Node):
    def __init__(self, stmts, coord=None):
        self.stmts = stmts
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.stmts or []):
            nodelist.append(("stmts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class For(Node):
    def __init__(self, iterator_chain, body, coord=None):
        self.iterator_chain = iterator_chain
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.iterator_chain is not None: nodelist.append(("iterator_chain", self.iterator_chain))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

class If(Node):
    def __init__(self, cond, iftrue, iffalse, coord=None):
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.iftrue is not None: nodelist.append(("iftrue", self.iftrue))
        if self.iffalse is not None: nodelist.append(("iffalse", self.iffalse))
        return tuple(nodelist)

    attr_names = ()

class Iterator(Node):
    def __init__(self, assignable, expression, coord=None):
        self.assignable = assignable
        self.expression = expression
        self.coord = coord

    def children(self):
        nodelist = []
        if self.assignable is not None: nodelist.append(("assignable", self.assignable))
        if self.expression is not None: nodelist.append(("expression", self.expression))
        return tuple(nodelist)

    attr_names = ()

class IteratorChain(Node):
    def __init__(self, iterators, coord=None):
        self.iterators = iterators
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.iterators or []):
            nodelist.append(("iterators[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Lambda(Node):
    def __init__(self, params, body, coord=None):
        self.params = params
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.params is not None: nodelist.append(("params", self.params))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

class List(Node):
    def __init__(self, items, coord=None):
        self.items = items
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.items or []):
            nodelist.append(("items[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Match(Node):
    def __init__(self, matchee, case_list, default, coord=None):
        self.matchee = matchee
        self.case_list = case_list
        self.default = default
        self.coord = coord

    def children(self):
        nodelist = []
        if self.matchee is not None: nodelist.append(("matchee", self.matchee))
        if self.case_list is not None: nodelist.append(("case_list", self.case_list))
        if self.default is not None: nodelist.append(("default", self.default))
        return tuple(nodelist)

    attr_names = ()

class MatchCase(Node):
    def __init__(self, expr, cond, block, coord=None):
        self.expr = expr
        self.cond = cond
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    attr_names = ()

class Param (Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)

class ParamList (Node):
    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Pattern(Node):
    def __init__(self, left, right, coord=None):
        self.left = left
        self.right = right
        self.coord = coord

    def children(self):
        nodelist = []
        if self.left is not None: nodelist.append(("left", self.left))
        if self.right is not None: nodelist.append(("right", self.right))
        return tuple(nodelist)

    attr_names = ()

class Procedure(Node):
    def __init__(self, params, body, coord=None):
        self.params = params
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.params is not None: nodelist.append(("params", self.params))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

class Quantor(Node):
    def __init__(self, name, lhs, cond, coord=None):
        self.name = name
        self.lhs = lhs
        self.cond = cond
        self.coord = coord

    def children(self):
        nodelist = []
        if self.lhs is not None: nodelist.append(("lhs", self.lhs))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        return tuple(nodelist)

    attr_names = ('name',)

class Range (Node):
    def __init__(self, klass, lower, upper, step, coord=None):
        self.klass = klass
        self.lower = lower
        self.upper = upper
        self.step = step
        self.coord = coord

    def children(self):
        nodelist = []
        if self.lower is not None: nodelist.append(("lower", self.lower))
        if self.upper is not None: nodelist.append(("upper", self.upper))
        if self.step is not None: nodelist.append(("step", self.step))
        return tuple(nodelist)

    attr_names = ('klass',)

class Regex (Node):
    def __init__(self, expr, as_expr, cond, block, coord=None):
        self.expr = expr
        self.as_expr = as_expr
        self.cond = cond
        self.block = block
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        if self.as_expr is not None: nodelist.append(("as_expr", self.as_expr))
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.block is not None: nodelist.append(("block", self.block))
        return tuple(nodelist)

    attr_names = ()

class Return (Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ()

class Scan(Node):
    def __init__(self, expr, using, regex_list, default, coord=None):
        self.expr = expr
        self.using = using
        self.regex_list = regex_list
        self.default = default
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        if self.using is not None: nodelist.append(("using", self.using))
        if self.regex_list is not None: nodelist.append(("regex_list", self.regex_list))
        if self.default is not None: nodelist.append(("default", self.default))
        return tuple(nodelist)

    attr_names = ()

class Set(Node):
    def __init__(self, items, coord=None):
        self.items = items
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.items or []):
            nodelist.append(("items[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Slice (Node):
    def __init__(self, obj, lower, upper, coord=None):
        self.obj = obj
        self.lower = lower
        self.upper = upper
        self.coord = coord

    def children(self):
        nodelist = []
        if self.obj is not None: nodelist.append(("obj", self.obj))
        if self.lower is not None: nodelist.append(("lower", self.lower))
        if self.upper is not None: nodelist.append(("upper", self.upper))
        return tuple(nodelist)

    attr_names = ()

class Subscription(Node):
    def __init__(self, obj, subscript, coord=None):
        self.obj = obj
        self.subscript = subscript
        self.coord = coord

    def children(self):
        nodelist = []
        if self.obj is not None: nodelist.append(("obj", self.obj))
        if self.subscript is not None: nodelist.append(("subscript", self.subscript))
        return tuple(nodelist)

    attr_names = ()

class Switch (Node):
    def __init__(self, case_list, default, coord=None):
        self.case_list = case_list
        self.default = default
        self.coord = coord

    def children(self):
        nodelist = []
        if self.case_list is not None: nodelist.append(("case_list", self.case_list))
        if self.default is not None: nodelist.append(("default", self.default))
        return tuple(nodelist)

    attr_names = ()

class TargetList (Node):
    def __init__(self, targets, coord=None):
        self.targets = targets
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.targets or []):
            nodelist.append(("targets[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Term(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        if self.args is not None: nodelist.append(("args", self.args))
        return tuple(nodelist)

    attr_names = ('name',)

class UnaryOp(Node):
    def __init__(self, op, expr, coord=None):
        self.op = op
        self.expr = expr
        self.coord = coord

    def children(self):
        nodelist = []
        if self.expr is not None: nodelist.append(("expr", self.expr))
        return tuple(nodelist)

    attr_names = ('op',)

class Identifier(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)

class While(Node):
    def __init__(self, cond, body, coord=None):
        self.cond = cond
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.cond is not None: nodelist.append(("cond", self.cond))
        if self.body is not None: nodelist.append(("body", self.body))
        return tuple(nodelist)

    attr_names = ()

