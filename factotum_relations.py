#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm

false = 0
true  = 1
from string import *
import factotum_lex
import factotum_entities
import factotum_globals
lex = factotum_lex.LexFacts()
e   = factotum_entities.EntityClass()
g   = factotum_globals.GlobalClass()

# This module handles information collected as entities.
# In particular it registers aliases and 

class RelationsClass:


    relations = {}    # info about predicate relations syntax and semantics
                      # Dict of relations where each is a list of tuples"
                      # The key is always an unique_name and the contents
                      # are always a unique parse pattern.
                      # The common_name may not be unique if several parse
                      # patterns represent the same relation.
                      # ( common_name, [( repr, type )...]
                      # The list always starts with the tuple ( '<>', 'E' )
                      # which represents the subject entity.
                      # The type info is currently limited to:
                      #      E: An entity
                      #      V: A value
                      #      R: A relation literal token
                      # Additional ones need to be added:
                      #      S: A subject
                      #      P: A sub-rule predicate part

    # Two dictionarys that 'organize' the relations dictionary in different ways

    rel_keys = {}     # The key is a summary of the keywords in the relaion
                      # The value is a list of relation names that might parse
                      # the relation. This is used to check input to find a
                      # matching relation.  Partial keys could be used as well.

    rel_tags = {}     # The relation patterns that impliment this relation
                      # So the key 'died' could point a several relations that
                      #        specify that.
                      # Likewise the key 'dead' could point to the same relations.
    #
    #
    #                          Dictionary: Relations
    # Dictionary
    #  rel_keys                           name     syntax pattern
    # 'death :' +------> $$0027:( 'dead', [ (,), (,) ... ] )
    #               |
    #               +------> $$0032:( 'dead', [ (,), (,) ... ] )
    #               |
    #               +------> $$0007:( 'dead', [ (,), (,) ... ] )
    #               |
    #               +------> $$0095:( 'dead', [ (,), (,) ... ] )
    #
    # 'birth :' +------> $$0023:( 'alive',[ (,), (,) ... ] )
    #              |
    #              +------> $$0065:( 'c1',   [ (,), (,) ... ] )
    #
    # In addition there also might be an entry that looked like this:
    #
    # 'birth'   +------> $$0023:( 'alive',[ (,), (,) ... ] )
    #              |
    #              +------> $$0065:( 'c1',   [ (,), (,) ... ] )
    #
    #=================================================================
    #
    # Dictionary
    #  rel_tags                          name      syntax pattern
    # 'death'   +------> $$0108:( 'death', [ (,), (,) ... ] )
    #           |
    #           +------> $$0055:( 'x1',    [ (,), (,) ... ] )
    #           |
    #           +------> $$0007:( 'death', [ (,), (,) ... ] )  # not a mistake
    #           |
    #           +------> $$0195:( 'death', [ (,), (,) ... ] )
    #
    # 'birth:'  +------> $$0023:( 'alive', [ (,), (,) ... ] )  # This is not a
    #           |                                              # mistake either
    #           +------> $$0065:( 'c1',    [ (,), (,) ... ] )  # in fact all
    #                                                          # rel_tags look
    #           like their corresponding rel_keys when mkvocab finishes its work.
    #           However when a user starts editing his vocabulary he can group
    #           diverse syntax patterns under the same name.  At that point all
    #           bets are off.  In fact the rel_tag dictionary may well get more
    #           complicated.

    # Sorry about all the comments but this is pretty complicated and I just want to# be able to understand it when I get back to it in a couple of years.
    
#----------------------------------------------------------
 
    def __init__(self,parent=None):
        self.parent = parent
        return

#----------------------------------------------------------
 
    def enter_syntax( self, vtag, vlist ):
        # print "Enter Syntax:", k, `v`
        
        # Loop to find an exact matching relation
        n = 0
        found = false

        if vtag in self.rel_keys:
            for r in self.rel_keys[vtag]: # We are looking for an exact relation match
                if vlist == self.relations[r][1]:
                    found = true
                    return
            
        # if found, r is the basic relation name it will be a unique name
        # and we can forget it since it is already a recorded relation.
        # So at this point we have a new vtag, vlist pattern

        cname = replace( vtag, ' ', '')

        # create the low-level relation vocabulary
        
        s = g.unique_name()
        self.relations[s] = ( cname, vlist )

        # Enter the key in rel_keys as a pattern or alternative pattern:
        # ... exact matches disappered in the search loop.

        if vtag not in self.rel_keys:
            self.rel_keys[vtag] = []
        self.rel_keys[vtag].append(s)
            
        # Enter the cname in rel_tags as a relation:
        # this will alias together patterns with the same key words
        # and different patterns of entities and values.
        
        if cname not in self.rel_tags:
            self.rel_tags[cname] = []
        self.rel_tags[cname].append(s)

        return

    

    #----------------------------------------------------------

    def set_relations( self, px ):

        # set relations takes a parsed predicate
        # It attempts to separate elements of the predicate into
        # relation-words, entity-references, and values.
        # Without clues as to what strings are values this is highly error prone
        # The user can clue in the program as to what is a value by using \( ... )
        # The program will try to fix up results later.
            
        vlist = []
        iw = 0
        tlist = len(px)
        # print 'starting with:', `px`
        vlist.append( ('<>','E') )  # put in subject Entity
        while iw < tlist:
            w, t = px[iw]
            wt = w
            found = false
            if  t == 'W':
                nwds = 1
                while true:
                    # print 'is %s an entity name?' % wt,                                
                    if wt in e.entities: # Eliminate known entity references
                        vlist.append( ['<>', 'E'] )
                        found = true
                        iw += nwds
                        # print '  yes!'
                        break                
                    # print '   no!'                
                    # This loop tests an enlarging sequence of up to 3 words
                    # as an entity name.  It terminates when it encounters
                    # a non word, or the end of the predicate
                    if nwds > 3 or (iw+nwds) >= tlist-1: break                
                    nxt, t = px[iw+nwds]                
                    if t != 'W': break
                    # Enlarge the potential entity name.
                    wt += ' ' + nxt
                    # print 'next test is', wt
                    nwds += 1
                    
                if not found:
                    vlist.append( [w, 'R'] )
         
            else:
                vt = 'X'
                if   t == 'P': vt = 'R'
                elif t == 'W': vt = 'R'
                elif t == 'N': vt = 'V'
                elif t == '{': vt = 'V'
                elif t == '[': vt = 'C'
                elif t == '(': vt = 'V'
                elif t == '<': vt = 'E'
                elif t == '"': vt = 'V'
                elif t == 'w': vt = ' '
                
                if   vt == ' ': pass
                elif vt == 'R': vlist.append( ( w,   vt ) )
                elif vt == 'V': vlist.append( ( '()',vt ) )
                elif vt == 'C': vlist.append( ( w,   vt ) )
                elif vt == 'E': vlist.append( ( '<>',vt ) )
                else :
                    if w: vlist.append( ('!'+w+'!',vt) )
            # Advance through the entire predicate building up vlist
            iw += 1
                                                   
        vtag = lex.unlex( vlist )
        vtag = replace( vtag, '<>', ' ' )
        vtag = replace( vtag, '()', ' ' )
        vtag_list = split(vtag)
        vtag = join(vtag_list)
        # print "vtag is", vtag
        self.enter_syntax( vtag, vlist )
            
        return
        
#-----------------------------------------------------------------------------------------------------
        
    def get_v_rule( self, name ):
    # Return a tuple with a name and a list of vocabulary rules associated with name 
        # print name, self.relations[self.rel_tags[name][0]]
        if name not in self.rel_tags:
            return None
        vtlist = self.rel_tags[name]
        # print "vocab tag list:", `vtlist`
        vlist = (name,[])
        for vt in vtlist:
            vlist[1].append( self.relations[vt][1] )
        # print "vocab list:", `vlist`
        return vlist

#-----------------------------------------------------------------------------------------------------

    def show( self ):
    # Display information about general relations

        r_tags = self.relations.keys()
        r_tags.sort()
        
        print "\nRelations Table:"
        print ''
        for rt in r_tags:
            if len( self.relations[rt][1] ) > 5:
                print "   ", rt, self.relations[rt][0], lex.unlex(self.relations[rt][1][:5]), "..."
            else:
                print "   ", rt, self.relations[rt][0], lex.unlex(self.relations[rt][1])
        return
       
#-----------------------------------------------------------------------------------------------------

    def show_keys( self ):  # Display information about keys to find a relation
    
        r_keys = self.rel_keys.keys()
        r_keys.sort()
        print "\nRelation Key Table:"
        print ''
        
        for rk in r_keys:
            label = rk
            for i in self.rel_keys[rk]:
                x, rv = self.relations[i]       
                if len(label) > 15:
                    print "    " + label, "-->"
                    print "        " + lex.unlex(rv)
                else:
                    print "    %-15s" % (label,),
                    print "-->", lex.unlex(rv)
                label = ""
        return
        
#-----------------------------------------------------------------------------------------------------        
        
    def show_names( self ):  # Display information about keys to find a relation   
        r_tags = self.rel_tags.keys()
        r_tags.sort(key=str.lower)
        
        print "\nRelation Tag Table:"
        print ''
        for rtg in r_tags:
            rn, rv = self.relations[ self.rel_tags[rtg][0] ]
            if len(rn) > 15:
                print "    " + rn, "-->"
                print "        " + lex.unlex(rv)
            else:
                print "    %-15s" % (rn,),
                print "-->", lex.unlex(rv)
        return

#-------------------------------------------