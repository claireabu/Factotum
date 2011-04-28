'''

@author: Claire

1.   The markers, subject, predicate, and citation are lexically
     recognized for all the facts.
     
2.   The resulting data is sorted by subject name, gathering all
     common subjects together.
     
3.   The vocabulary file is parsed and an executable form of the rules
     produced. Unrecognizable facts (rules>?) are printed.
     
4.   The entity sorted facts are brought in entity by entity and checked
     for syntactic correctness against the vocabulary. This identifies
     relations and objects. An internal structure is created for each
     entity. For each entity "implied" facts are generated and added to
     the internal structure.
     
5.   For each entity, the entity is checked for conditions in the types
     associated with the entity.
     
6.   Upon completion of processing all the facts, there exists internally,
     a representation of all the facts...this allows for much deeper and
     specific entity checking. So at this point the entities are checked
     against the constraintss on each type to which they belong. User
     defined comments, errors, and warnings are generated.
     
7.   The internal structure is written out to a file which will be used by
     other tools. [??]

'''

import predpar
import sys 
from string import *
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()

grammar_dict = {}
TypeHier = {}
PhraseList  = []
depth = 0
depthLim = 100 

########################################################

def check_vocab():
    ''' Parses vocab using predpar over the .v passed into fcheck 
        so that we may use the output dictionary grammar to parse our facts 
    '''
    res_parseV = []
    res_parseV = predpar.parse_vocab()
    return res_parseV  

#############################################################

def go_thru_factFile():
    '''
    Opens up the given file,  reads in line by line, and
    uses factotum lexer to go thru and find the subject and predicates
    (nearly identical to go_thru_file used in predpar.py) 
    '''
    #if len(sys.argv) < 3: 
     #   sys.stderr.write("must include fact (.f) file \n")
      #  raise SystemExit(1)

    
    #factfile = open(sys.argv[2], 'r')
    
    factfile = open('test.f', 'r')
    
    facts = []
    line = ''
    line = factfile.readline()
    m = s = p =  r = c = ''
    px = []
    
    #sampled from factotum_entities 
    #READ IN LINES 
    
    while(len(line) > 0):
        my_fact = line[:-1]
        line = ''
        line = factfile.readline()
        
        while(len(line) > 0) and (line[0] == '-'):
            my_fact += '\n' + line[1:-1]
            line = ''
            line = factfile.readline()
            continue
        
        if my_fact != '':
            (m,s,p,px,r,c) = lex.breakup_fact(my_fact)
        
            p = p.strip() # get rid of whitespace
            facts.append([s,p])
    
    return facts 
###################################################



def isDescendant(item, tmatch):
    ''' note: remember that the TypeHier maps subtype to the parent, 
    want to check if item is a descendant of tmatch 
    '''
    
    if tmatch == 'ANY': 
        return True 
    
    elif not item in TypeHier.keys(): #means you've parsed thru and made it to the root without finding a match 
        return False 
    
    elif tmatch == item : 
        return True 
    
    else: 
        parent = TypeHier[item][1]
        return isDescendant(parent, tmatch)

#####################################################


def parse_Facts(fact, start_sym, dI):
    ''' The main parsing function and is recursive, 
        nearly identical to parseGrammar in predpar, 
        except that at top level when we first encounter the subject, 
        we must dive into that dictionary immediately and call the parse_Facts
        function on that dictionary. 
    '''
    
    #if rulePred == []: return False 
    global depth

    if depth == depthLim:
        print >> sys.stderr, 'Warning: Have exceeded depth limit, grammar is most likely Left Recursive\n Program now exiting'
        exit(1) 
    else: 
        global depth
        depth += 1
        
        
    local = fact
    tree = [] 
    key = start_sym
    n = 0
    count = 0
    

        
    if key in dI.keys(): 
        rules = dI[key] 
        
        if rules.__class__ == dict:  #means at very top level, and have subject--> need to call subject dictionary 
            res = parse_Facts(fact, 'Start', dI[key])
            if res:
                return res 
            else: 
                return False 
            
        else: 
            
                         
            
            for rtuple in rules:
                tree = []
                tree.append([key, rtuple])
                local = fact
                n = 0
                count = 0
            
                if  len(rtuple) > 1 and rtuple.__class__ == list:   #multiple options in grammar rule 
                    
                    for token in rtuple:
                        count += 1
                        
                        if token in dI.keys():
                            
                            res = parse_Facts (local[n:], token)
                            
                            if res:
                                tree.extend(res[0])
                                local = res[1]
                                
                                if count == len(rtuple):
                                    return (tree, local)
                                else: 
                                    n = 0
                            else: 
                                break
                                
                        else:        #encountered regex/terminal
                            
                            if n < len(local):
                                if key == 'Typename':
                                    if isDescendant(local[n], token):
                                        n+= 1
                                        return(tree, local[n:])
                                    
                                elif match_regex(token, local[n]): 
                                    n+=1
                                        
                                    if count == len(rtuple):
                                        return(tree, local[n:])
                                    else:
                                        continue
                                    
                                else:
                                    break          
                           
                else: ####Only one item-- don't want to iterate thru the string 
                    
                    if rtuple[0] in dI.keys():
                        #need to check also if type of phrasename
                        
                        res = parse_Facts(local[n:], rtuple[0])
                        
                        if res:
                            tree.extend(res[0])
                            local = res[1]
                            return(tree, local)
                        else:
                            return False
                        
                    else: #not entry in dict
                        
                         
                        
                        if n < len(local):
                            if key == 'Typename':
                                if isDescendant(local[n], rtuple[0]):
                                    n+= 1
                                    return(tree, local[n:])
                            
                            elif match_regex(rtuple[0], local[n]):
                                n+=1
                                return(tree, local[n:])
                                
                            
                            else:                       #only item in tuple doesn't match 
                                break                    #break out of tuple loop

    else:         
        return False    

##########################################################


def pull_typedefs(subj, pred):
    
    if pred[0] == '[':
        
        if subj in TypeHier.keys():
            print >> sys.stderr, " \nMulti-Inheritance detected, Type \"%s\" is not included in the type tree.\n" % (subj, )
        
        else: 
            head = pred[1]
            TypeHier[subj] = [False, head]
            return  True
        
    else: 
        return False
    
################################################################

#############################################
def f_tracePath(subtype, mini):
    '''
    Traces the path of a given subtype to a root, 
    thus confirming if it is indeed linked to a properly defined root, 
    also has an internal check for LOOPS, using the mini dictionary d, to keep 
    track of items already detected in the path and returns false (blank path []) indicating so 
    '''
    path = []
    sub = subtype
    head = TypeHier[sub][1]
    d = mini
    
    if sub in d.keys():
        print >> sys.stderr, "Loop detected"
        return [] #loop 
    
    elif head == 'ROOT':
        path = [sub]
        return path 
    
    elif head in TypeHier.keys():
        d[sub] = ''
        path = f_tracePath(head, d)
        
        if path == []:
            return []
        else: 
            path.append(sub)
            return path
            
    else: 
        return []
    

#################################################

def fcheck_types():
   
    delList = []
    types = TypeHier.keys()
    
    for t1 in types:
        looptest = {}
        if not TypeHier[t1][0]:
            path = f_tracePath(t1, looptest)
            if path != []:
                for link in path: 
                    if TypeHier[link][0]:
                        continue 
                    else:
                        TypeHier[link][0] = True 
            else: 
                continue 
        else:
            continue 
        
    
    #if any type still has "False" entry, it means no proper
    # path was discovered to the root, thus meaning the type
    # was in some way improperly defined, and so we remove it 
    # from the tree
    for t2 in types: 
        if not TypeHier[t2][0]:
            del TypeHier[t2]
            delList.append(t2)
        else:
            continue 
        
    
        
        
    return delList

#####################################################

   
def first_pass(facts):
    
    nonTDefs = []
    failed = []
    
    for f in facts: 
        subject = f[0]
        pred, cit =  predpar.tokenize_pred_string(f[1])
        
        if pred == []:                              #failed to tokenize 
            failed.append(f)
            
        elif not pull_typedefs(subject, pred):
            nonTDefs.append(f) #new list of facts, already added types to type tree, but take out of fact list
        else: 
            continue 
    
    
    
    no_path = fcheck_types()
    
    return  nonTDefs, failed #so when parsing thru rules, don't go thru the type definition again 
     
        

########################################################################
    
    
def fact_checker():
    
    
    vrules = []
    vfail = []
    global grammar_dict 
    grammar_dict = {}
    
    global TypeHier
    TypeHier = {}
    
    
    vrules, vfail, grammar_dict, TypeHier  = check_vocab()
     ##########PRINTING VOCAB DICTIONARY PRODUCED 
    #for x in grammar_dict:
     #   print x + ":"
      #  print x.__class__
       # for y in grammar_dict[x]:
        #    print  y + ":"
         #   for z in grammar_dict[x][y]:
          #      print  z 
        #print '\n' 
    
    #check left recursion 
        
    facts = go_thru_factFile()
    
    parsed_facts = []
    failed_facts = []
    facts2 = []
    

    #go thru facts 
    #parse each one according to grammar generated by vocabulary 
    facts2, failed_facts = first_pass(facts)
    
    for f2 in facts2:
        
        subject = f2[0]
        pred = f2[1]
        
        factParse = parse_Facts(pred, subject, grammar_dict)
        
        if factParse: 
            parsed_facts.append(f2[0], pred, factParse[0])
        else: 
            failed_facts.append(f2)
     
    
    
    
    ##########PRINT STATMENTS 
    for n in parsed_facts:
        for i in range(len(n)):
            if i == 2:
                for z in n[i]:
                    print z
            else:
                print n[i]
            print '\n'
        
    print failed_facts
    
    return [parsed_facts, failed_facts] 



if __name__ == '__main__':
    fact_checker()


