#------------------------------------------------------------------------------
# setlx2py: setlx_lexer.py
#
# Lexer class: lexer for the setlx language
#
# Copyright (C) 2013, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from ply import lex
from ply.lex import TOKEN

class SyntaxError (Exception):
    def __init__(self, msg, LEXER, src, lineno=None, lexpos=None):
        if lineno is None:
            lineno = LEXER.lexer.lineno
        if lexpos is None:
            lexpos = LEXER.lexer.lexpos
        msg += " at %d column %d: %r" % (
            lineno, lexpos - LEXER.line_head_pos, src)
        Exception.__init__(self, msg)

class Lexer():

    def __init__(self):
        self.line_head_pos = 0

    def build(self, **kwargs):
        """ Builds the lexer from the specification. Must be
            called after the lexer object is created.

            This method exists separately, because the PLY
            manual warns against calling lex.lex inside
            __init__
        """
        self.lexer = lex.lex(object=self, **kwargs)

    def input(self, text):
        """ Sets the input for the lexer
        """
        self.lexer.input(text)  
    
    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    t_ignore = ' \t\r\f\v' # Whitespace skipped
    t_ignore_comment = r'\#.*' # Ignore comments

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
        self.line_head_pos = t.lexpos + 1

    def t_error(self, t):
        s = t.value[0]
        raise SyntaxError("bad character", self, t.value[0])

    ##
    ## Regexes for use in tokens
    ##

    decimal_constant = '[+-]?(?<!\.)\b[0-9]+\b(?!\.[0-9])'

    ##
    ## List of tokens recognized by the lexer
    ##
 
    keywords = {
        
    }
    
    tokens = [
        # Constants

        'INT_CONST_DEC', 
            
        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE'
    ] + list(keywords.values())           

    ##
    ## Rules for the normal state
    ##

    t_PLUS          = r'\+'
    t_MINUS         = r'\-'
    t_DIVIDE        = r'\\'
    t_TIMES         = r'\*'    

    @TOKEN(decimal_constant)
    def t_INT_CONST_DEC(self, t):
        return t
