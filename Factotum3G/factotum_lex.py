#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm

false = 0
true  = 1
from string import *
import factotum_globals
g = factotum_globals.GlobalClass()

class LexException(Exception): pass

class LexFacts:

    markers = ( ':"', ':[', ':', '*', ':*', '#*', '#"', ':<', '"', '#', ' ')
    
#-------------------------------------------     
    
    def __init__(self, parent=None):
        self.parent = parent
        return
        
#-------------------------------------------    
    
    def breakup_fact( self, f ):
        # breaks up fact into marker, subject, predicate, remarks, and citations.
        # Returns 5-tuple (m,s,p,r,c)
        
        # print "fact is ", f
        m = s = p = r = c = ''
        cp = 0
        # Look for markers if none then marker will be blank
        for pm in self.markers:
            cp = len(pm)
            # print 'test >' + f[:cp] + '< against >' + pm +'<'
            if f[:cp] == pm:
                m = pm
                f = f[cp:]
                break
        
        # print 'marker is', m
            
        # if marker implies subject then fill in subject field
        mlen = len(m)
        if m == "*" or m == ':*' or m == '#*':
            s = g.unique_name()
            f = f[mlen:]
            # print "set subject to ", s
        elif m == '"' or m == ':"' or m == '#' or m == '#"' or m == ':[':
            s = g.current_subject
            f = f[mlen:]
            # print "set subject to ", s
        elif m == ':<':
            s = '\\include'
            f = f[mlen:]
            # print "set subject to ", s
        else: 
            #print 'subject left unchanged.'
            pass

        # print "fact is ", f
        # if s != '': print "subject is ", s
        f = expandtabs(f,4)

        # get citations
        # find \[ marking start of citations
        cb = rfind( f, '\\[' )
        if cb >= 0:
            c = strip(f[cb:])
            f = f[:cb]
            # print "citations are ", c

        if m == '#' or m == '#"':        
            # print 'return remark'
            return(m, g.current_subject, '', [], strip(f), c )

        # get remarks
        # find \# marking start of remarks
        rb = rfind( f, '\\#' )
        if rb >= 0:
            r = strip(f[rb+2:])   # Remove \# from the fact.
            f = strip(f[:rb])
            # print "remark is ", r

        # Get plausible subject from fact
        if s == '':
            # print "pick up subject from >" + f + "<"
            sf = split( f )
            # print `len(sf)`, `sf`
            if len(sf):
                se = len(sf[0])
                if se > 0:
                    s = f[:se]
                    f = f[se:]
                    # print "set subject to", s
            else:
                # print "Whitespace not found."
                pass
                                
        # Get plausible predicate from fact
        p = f;
        px = self.str(f) # set predicate

        if s != '':
            g.current_subject = s
        else:
            s = g.current_subject = unique_name()

        # print 'subject is', s
        # print 'predicate is', lex.unlex(px)
        return ( m, s, p, px, r, c )

#-------------------------------------------
    
    def str(self, p ):

        # Returns a list of tuples: (token, ttype).
        # ttype   indicates
        #  W      word only: letters/numbers/dash/underbar
        #  N      number only: numbers/plus/minus/period
        #  P      punctuation: single char or backslash + char
        #  "      string: can include \" characters
        #  <      an <> bracket phrase \< ... >
        #  {      a {} phrase          \{ ... }
        #  [      a [] bracket phrase (these should never occur in predicates)
        #         but they do occur in citations, so they are a part of this.
        #                                 \[ ... ]
        #  (      a parenthesized phrase  \( ... )

        # whitespace between tokens is discarded.

        # grouping token control to allow ignore grouped tokens within groups
        depth  = 0
       
        # tokens and token types allowed within the token.
        tokens = []       # contains tuples (token,token-type)
        ttype  = ' '      # blank indcates we are between tokens in white space
        token  = ''
        words   = 'a9_-'
        numbers = '9-.'

        cp = 0
        p = p.strip()
        plen = len(p)
        token_done = false
        # print 'lexing: >' + p + '< plen:', plen
        
        esym = ''
        
        while cp < plen:
            
            c = p[cp]
            try:
                n = p[cp+1]
            except:
                n = ' '
            # print 'cp =', `cp`, c + n
            dc = false
            ctype = 'x'        
            
            # Note only one token grouping is active at any one time.
            # So strings can have \<...> groupings inside them with no effect
            # likewise \<...> can have strings inside with no tokenization.

            # handle token groups: strings, angle brackets, etc.
            # depth depends on not have more than one grouping active.
            if   c == '"'  and not depth:
                depth += 1; ttype = '"'; esym = '"'        
            elif c == '\\' and n == '<' and not depth:
                depth += 1; ttype = '<'; esym = '>'; dc = true
            elif c == '\\' and n == '[' and not depth:
                depth += 1; ttype = '['; esym = ']'; dc = true
            elif c == '\\' and n == '{' and not depth:
                depth += 1; ttype = '{'; esym = '}'; dc = true
            elif c == '\\' and n == '(' and not depth:
                depth += 1; ttype = '('; esym = ')'; dc = true
            elif c == esym and depth:
                depth -= 1;
                if not depth:
                    token_done = true
                    token += c
                    cp += 1
                    ctype = 'x'
            # handle special chars: \" in strings
            elif c == '\\' and n == '"' and ttype == '"': dc = true
            # handle special chars: \c in any other context
            elif c == '\\' and not depth: token_done = true; dc = true

            # charcterize this character
            elif c in digits:     ctype = '9'
            elif c in letters:    ctype = 'a'
            elif c in whitespace: ctype = 'w'
            elif c == '+':        ctype = '+'
            elif c == '_':        ctype = '_'
            elif c == '-':        ctype = '-'
            elif c == '.':        ctype = '.'
            else: ctype = 'p'

            # print 'ctype is ', ctype, 'token:', token, 'ttype = >' + ttype + '<'

            # now decide on token type based on first char of token
            if ttype == ' ': # group tokens are started above
                             # this only handles single tokens
                if   ctype == 'w': cp += 1; token_done = true
                elif ctype == 'a': ttype = 'W'
                elif ctype == '9' or \
                     ctype == '-': ttype = 'N'
                else: # What's left should be single character tokens
                    token += c
                    cp += 1
                    if dc:
                        token += m
                        cp += 1
                    ttype = 'P'
                    ctype = 'w'
                    token_done = true

            # now decide if token has finished with a non-permissible char
            if   ttype == 'N' and ctype not in numbers: token_done = true
            elif ttype == 'W' and ctype not in words:   token_done = true
                    
            # print 'at', cp, 'ctype/ttype is >' + ctype + ttype + '<', \
            #       token_done, 'token:', token
            
            # here is where all the action is
            if token_done:
                if token:
                    tokens.append( (token,ttype) )
                token_done = false
                ttype = ' '
                token = ''
                ctype = 'x'
            else:
                # Gather characters into the token
                token += c;
                cp += 1
                if dc: 
                    token += n;
                    cp += 1
        if depth != 0:
            raise LexException( "Unbalanced grouping -- %s not found.\n in %s" %\
                   (esym,p))
        tokens.append( (token,ttype) )
        return tokens


#-------------------------------------------
    
    def __repr__(self, s):
        self.lex(s)
        return s
        
#-------------------------------------------

    def unlex(self, lex ):
        #print 'unlex of', `lex`,
        str = ''
        if len(lex) <= 1: str += lex[0][0]
        else:   
            for i in lex[:-1]:
                # i[0] is the token; i[1] is the type
                str += i[0] + ' '
            str += lex[-1][0]
        #print 'is', str
        return str

#-------------------------------------------


