#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm

false = 0
true  = 1
from string import *
import factotum_lex
import factotum_globals
lex = factotum_lex.LexFacts()
g   = factotum_globals.GlobalClass()

# This module handles information collected as entities.
# In particular it registers aliases and 

class EntityClass:
    

    entities = {} # Dict of entitites where each is a list of 8-tuples:
                  #  [ ( info-type, subject, predicate, parsed-predicate, remarks, cits )... ]
                  #  The info-types are:
                  #      T: Type
                  #      A: Alias
                  #      a: Reverse Alias
                  #      R: Remark
                  #      C: Citation information about Entities
                  #      F: A Fact about the other entities
                  
                  #  The subject is a string representing an entity name, entities is indexed by this name
                  #  The predicate is the relation-object-value part of the fact
                  #  The parsed-predicate is the predicate lexed and broken into a list of tokens
                  #  The remarks are comments about this particular predicate.
                  #  The cits are the citation string from the fact.
                  
#----------------------------------------------------------
 
    def __init__(self,parent=None):
        self.parent = parent
        return
        

#----------------------------------------------------------


    #----------------------------------------------------------
    #   Create Entity facts
    #----------------------------------------------------------

    def alias( self, m, s, a, px, r, c):
        if not s: s = g.current_subject
        if not a: print("error in " + s + ": alias empty.")
        if a not in self.entities:
            self.entities[a] = []
            self.entities[a].append(['A', m,  a, s, [], r, c])
        if s not in self.entities:
            self.entities[s] = []
            self.entities[s].append(['a', '', s, a, [], r, c])
        return

    #----------------------------------------------------------

    def cits( self, m, s, p, px, r, c):
        if not s: s = g.current_subject
        if s not in self.entities:
            self.entities[s] = [] 
        self.entities[s].append(["C", m, s, '', [], r, c])
        return

    #----------------------------------------------------------

    def remarks( self, m, s, p, px, r, c):
        if not s: s = g.current_subject
        if s not in self.entities:
            self.entities[s] = [] 
        self.entities[s].append(["R", m, s, p, [], r, c])
        return
        
    #----------------------------------------------------------

    def predicate( self, m, s, p, px, r, c):
        if not s: s = g.current_subject
        if s not in self.entities:
            self.entities[s] = [] 
        px = lex.str( p )
        self.entities[s].append(["F", m, s, p, px, r, c])
        return

    #----------------------------------------------------------

    def type( self, m, s, t, px, r, c):
        if not s: s = g.current_subject
        if s not in self.entities:
            self.entities[s] = []
        self.entities[s].append(["T", m, s, t, [], r, c])
        return
        
    #----------------------------------------------------------   
    
    def build_entities( self, factf ):
        # Pass 1 -- Do names: pickup entity names and aliases.
        # Build up Entity data base, from users fact file.
        # Users fact file never read again after this.
        a = m = s = p = r = c = ' '
        px = []  # This is the start of predicate pre-lexed in (token,type) tuples
        

        g.current_subject = g.unique_name()   # create a current subject
       
        next_line = ''
        next_line = factf.readline()         # set up first line.
        # print '1st line >' + next_line + '<'
        # print 'subject is:', g.current_subject
    
        while len(next_line) > 0:
            afact = next_line[:-1]
            next_line = ''
            next_line = factf.readline()
                           
            # Group together continuation lines.
                       
            while (len(next_line) > 0) and (next_line[0] == '-'):
                afact += '\n' + next_line[1:-1]
                next_line = ''
                next_line = factf.readline()
                continue

            # print 'working on >' + afact + '<'
            if strip( afact ) == "": continue

            (m,s,p,px,r,c) = lex.breakup_fact( afact )
            p = strip(p)

            # Fix subject and get rid of \< > subjects
            if s[0:2] == "\<":       # then a multi-word subject
                se = find( p, '>' )  # look for end of subject
                if se > 0:           # End of subject found; adjust predicate
                    a = s[2:] + ' ' + p[:se-1]
                    p = strip( p[se:] )
                    # px = lex_string( px )
                    s = self.unique_name()
                    e.alias( m, s, a, [], [], r, c )
                else:
                    s = s[2:]

            if m == '#' or m == '#"':   # Then it is a remark
                self.remarks( m, s, p, px, r, c )
                continue

            elif m ==  ':<':       # Then it is an include
                # do the include thing
                continue

            elif m[0] == ':':
                # process the alias
                if p[:2] == '<-':    # normal alias definition
                    a = strip( p[2:] )
                    self.alias( m, s, a, '', [], r, c )
                elif p[:2] == '->':  # reverse alias definition
                    a = s
                    s = strip( p[2:] )
                    self.alias( m, a, s, [], r, c )
                elif p[:1] == '[':   # type association
                    te = find( p, ']' ) # end of type name
                    if te > 0:
                        t = strip(p[1:te])
                    else:
                        print('Warning: Type has no ending ]\nin ', p)
                        t = strip(p[1:])
                    # print "Enter type", t
                    self.type( m, s, t, [], r, c )
                elif m == ":[":       # entity citations
                    ec = rfind( p, ']' )
                    if ec > 0: p = p[0:ec]
                    self.cits( m, s, '', [], r, p )
                continue

            else:
                self.predicate( m, s, p, px, r, c )       

        return

    #----------------------------------------------------------
    
    def entity( self, e ):
        if e in self.entities:
            return self.entities(e)
        else:
            return none
            
     #----------------------------------------------------------

    def keys( self ):
        kys = list(self.entities.keys())
        return kys
        
    #----------------------------------------------------------

    def show( self, etag, dent1=4, dent2=4 ):
        
        indent1 = dent1 * " "
        indent2 = indent1 + dent2 * " " 
        
        if etag not in self.entities:
            print('No entity named:', etag)
            return
            
        print(indent1+etag)
        for i in self.entities[etag]:
            it = i[0]
            if   it == 'T': print(indent2+"Type is", i[3], i[5])
            elif it == 'R': print(indent2+"#", i[5])
            elif it == 'A': print(indent2+"Alias for", i[3], i[5])
            elif it == 'a': print(indent2+"Alias for", i[3], i[5])
            elif it == 'C': print(indent2+"Citations", i[6])
            elif it == 'F':
                if i[5]:    print(indent2, i[3], '#', i[5])
                else:       print(indent2, i[3])
            else:           print(indent2, repr(i))
        print('')
        
            
        
     #----------------------------------------------------------

    def show_all( self ):
        e_tags = list(self.entities.keys())
        e_tags.sort(key=str.lower)    
        print( '\nEntities are:' )
        for et in e_tags:
            self.show( et )
        
            
            