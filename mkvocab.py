#!/usr/bin/python
# coding: utf-8
# vi: ts=4 sw=4 et ai sm
# mkvocab Program for reading Factotum 3G data and creating a vocabulary.
# This is the second version of the program.
# Written by Buz on 2010-11-25
# partially finished on 2010-11-26

import os, sys, time, glob
import pickle as pickle
from getopt import *
from string import *
import factotum_lex
import factotum_entities
import factotum_relations
import factotum_types
import factotum_globals

lex = factotum_lex.LexFacts()
ent = factotum_entities.EntityClass()
rel = factotum_relations.RelationsClass()
typ = factotum_types.TypesClass()
gbl = factotum_globals.GlobalClass()

true    = 1
false   = 0
debug   = false

ctagf   = false
utagf   = false

#-------------------------------------------

def usage():
    print("")
    print("mkvocab [options] file")
    print("will open file.f in the same directory as file.")
    print("If file.v is newer than file.f and then the program")
    print("issues a warning and does nothing.")
    print("")
    print("Options:")
    print("--help  Help -- provides this summary.")
    print("-h      Help -- provides this summary.")
    print("-v      Make vocabulary, default is to list vocabulary as output")
    print("-u      Vocabulary has unique names for productions")
    print("-c      Vocabulary has constructed names for productions")
    print("-q      No std-output produced.")
    return

#----------------------------------------------------------

def create_fx( ):

    return


#----------------------------------------------------------
#         Main Program
#----------------------------------------------------------


def main():
    global ctagf, utagf
    factd  = '/'
    factv  = 'photo.v'
    factf  = '_wikidata_.f'
    factfx = 'photo.fx'
        
    # Process command line options

    try:
        opts, args = getopt(sys.argv[1:], "hvVqf:v:uc",\
                ["help", "facts=", "vocab="])
    except GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if   o == "-q": verbose = false
        elif o == "-v": verbose = true
        elif o == "-V": verbose = false
        elif o == "-c": ctagf = true
        elif o == "-u": utagf = true
        elif o in ("-f", "--facts"):
            factbase = a
            if a:
                logdir = "./"
            else:
                (logdir,factn) = os.path.split(a)
                factf = factn + ".f"
                factv = factn + ".v"
                factfx = factn + ".fx"
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else: assert False, "unhandled option"

    text  = []
    stats = {}
 

    
    if os.path.exists( factd + factfx ):
        # check to see if it is newer than the input files
        # exit if it is.
        pass

    #  Pass 1 -- Read the fact file and put facts into entities directory.
    
    factfile = open( factd + factf, 'rb' ) #file( factd + factf, 'r' )
    ent.build_entities( factfile )
    factfile.close
    
    ent.show_all()
    
    # Pass 2 -- build up information about types
    typ.establish_types( ent.entities )
    print("\nTypes and their Entities\n")
    typ.show_all_entities()

    # Pass 3 -- break predicates into objects, relations, and values.

    for et in ent.entities:
        for item in ent.entities[et]:
            it = item[0]
            if it == 'F':
                rel.set_relations( item[4] )

    # Report Relation information
    
    print('\nAbstract Relations:')
    print('')
    
    rel.show()  
    
    rel.show_keys()
    
    rel.show_names()
    
    # Pass 4 -- Collapse Relations
    
    # Pass 5 -- Generate Vocabulary
    
    # print rtags
    r_tags = list(rel.rel_tags.keys())
    r_tags.sort( key=str.lower )
    
    print("\nPossible Vocabulary:\n")
    vfmt = '%-10s %s'
    
    for tn in typ.types:
        print(vfmt % (tn, "[]"))
        
    print('')
    vfmt = '%-3s %s'
    for name in r_tags:         
        vlist = rel.get_v_rule( name )  # returns ( name, [ [.vocab-rule1], [.....vocab-rule2], ...]
        # print "list of rule names:", `vlist`
        rv = vlist[1][0]
        # print "first rule:", `rv`
        if ctagf:
            print(vfmt % (vlist[0], lex.unlex(rv)))
        elif utagf:
            print(vfmt % (g.unique_name(), lex.unlex(rv)))
        else: # use * for first rule and " for subsequent ones
            print(vfmt % ("*", lex.unlex(rv)))
        for rv in vlist[1][1:]:
            print(vfmt % ('"', lex.unlex(rv)))

    return

    sys.exit(0)

if __name__ == "__main__":
    main()
