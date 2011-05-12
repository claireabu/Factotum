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
import string 
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
AliasestoSubj = {}
#SubjtoAliases = {}
MultiAl = []
Labels = {}

########################################################

def check_vocab():
    ''' Parses vocab using predpar over the .v passed into fcheck 
        so that we may use the output dictionary grammar to parse our facts 
    '''
    res_parseV = []
    res_parseV = predpar.parse_vocab()
    return res_parseV  

################################################

def add_predef_rules():
    
    grammar_dict['Start'] = [[':','Predefined'],
                             ['Phrase']
                             ]

    grammar_dict['Predefined'] = [['Primary Term', '<-', 'Single Alias'],
                                  ['Primary Term', '<-', 'Multi Alias '], 
                                  ['Single Alias', '->', 'Primary Term'],
                                  ['Primary Term', '[', 'Type', ']']
                                  ]
    return 

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
            if '<-' in my_fact and not '<-' in p:
                p = '<' + p
                
            marker = my_fact[0]
            if marker == ':':
                fstr = s + ' ' + p 
                facts.append([marker, fstr])
            
            else: 
                facts.append([s,p])
            
    
    return facts 
###################################################

def isDescendant(item, tmatch):
    ''' note: remember that the TypeHier maps subtype to the parent, 
    want to check if item is a descendant of tmatch 
    '''
    tmatch.strip()
    if tmatch == 'ANY': 
        return True 
    
    elif not item in TypeHier.keys(): #means you've parsed thru and made it to the root without finding a match 
        if item in AliasestoSubj.keys(): #means is an Alias
            ent = AliasestoSubj[item]
            return isDescendant(ent, tmatch)
        else: 
            return False 
    
    elif tmatch == item : 
        return True 
    
    else: 
        parent = TypeHier[item][1]
        return isDescendant(parent, tmatch)

#####################################################

def checkLabel(rule, fact, n):
     
    if rule.__class__ == list: 
        label = rule[0]
        ttype = rule[1]
        
        x = checkTtype(ttype, fact, n)
        
        if x.__class__ == string: 
            if not label in Labels: 
                i = x[1]
                x = x[0]
                #Labels[x] = label
                fact = fact[i+1:]
                return (fact, i)
        elif x: 
            #label = label[len('Label:'):]
            #label.strip()
            if not fact[n] in Labels:
                #Labels[fact[n]] = labelr
                return True 
                
        else: return False 
            
        
    else: 
        #label = rule[len('Label:')+1:]
        #label.strip()
        if not fact in Labels: 
            #Labels[fact] = label 
            return True 
            
        
    return True 

##############################################

def checkTtype(rule, fact, n):
    
    z = len('Ttype:')
    ttype = rule[z:]
    ttype.strip()
    
    if ttype == 'n': #number 
        period = False 
        if fact[n][0] == '-':
            #negative number 
            test = fact[n][1:]
        else: 
            test = fact 
        
        for e in test: 
            if e == '.' and not period: 
                period = True 
            elif not e in string.digits: 
                return False 
            else: 
                continue 
        
        return True  
  
    elif ttype == 's':  #string
        
        if fact[n] == '\"': 
            str = '\"'
            n += 1
            while fact[n] != '\"':
                str += fact[n]
                str += ' '
                if n == len(fact): 
                    return False 
                else: 
                    n += 1
            str += '\"'
            
            return (str, n)
            
        else: 
            return False #not a string 
        
        
    elif ttype == 'w':  #word
        
        for e in fact[n]:
            if e in string.letters: 
                continue 
            elif e == '\'': 
                continue 
            else: 
                return False 
        return True 
        
    elif ttype == 'o':  #object
        
        if fact[n] in TypeHier.keys():
            return True 
        else: 
            return False 
            
    else: 
        return False
    
######################################################

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
                            
                        res = parse_Facts (local[n:], token, dI)
                            
                        if res:
                            tree.extend(res[0])
                            local = res[1]
                                
                            if count == len(rtuple) and local == []:
                                 return (tree, local)
                            else: 
                                 n = 0
                        else: 
                            break
                                
                    else:        #encountered regex/terminal
                        if n < len(local):
                            if 'Type:' in token:
                                typename = token.replace('Type: ', '')
                                if isDescendant(local[n], typename):
                                    n+= 1
                                    if count == len(rtuple):
                                        return(tree, local[n:])
                                    else:
                                        continue
                                else: 
                                    break 
                                    
                            elif token.__class__ == list:
                                x = checkLabel(token, local, n)
                                if x.__class__ == tuple: 
                                    n = x[1] + 1
                                    local = local[n:]
                                    tree.append([token, x[0]])
                                elif x == True:
                                    tree.append([token, local[n]])
                                    n+= 1
                                else: 
                                    break 
                                
                                if count == len(rtuple):
                                    return(tree, local[n:])
                                else:
                                    continue
                                    
                                  
                            elif 'Label:' in token: 
                                if checkLabel(token, local, n):
                                    tree.append([token, [local[n]]])
                                    n += 1
                                    if count == len(rtuple):
                                        return(tree, local[n:])
                                    else:
                                        continue
                                else: 
                                    break 
                                    
                                
                           
                            elif 'Ttype:' in token: 
                                x = checkTtype(token, local, n)
                                if x.__class__ == tuple: 
                                    n = x[1] + 1
                                    local = local[n:]
                                    tree.append([token, x[0]])
                                elif x == True:
                                    n+= 1
                                else: 
                                    break 
                                
                                if count == len(rtuple):
                                    return(tree, local[n:])
                                else:
                                    continue
                               
                                 
                            elif re.match(token, local[n]): 
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
                        
                    res = parse_Facts(local[n:], rtuple[0], dI) 
                        
                    if res:
                        tree.extend(res[0])
                        local = res[1]
                        return(tree, local)
                    else:
                        return False
                        
                else: #not entry in dict
                        
                    if n < len(local):
                        if 'Type:' in rtuple:
                            typename = rtuple.replace('Type: ', '')
                            if isDescendant(local[n], typename):
                                n+= 1
                                return(tree, local[n:])
                        
                        elif rtuple.__class__ == list:
                                x = checkLabel(token, local, n)
                                if x.__class__ == tuple: 
                                    n = x[1]
                                    local = local[n:]
                                    tree.append([rtuple, x[0]])
                                elif x == True:
                                    n+= 1
                                else: 
                                    break 
                                
                                
                                return(tree, local[n:])
                                
                                  
                        elif 'Label:' in rtuple: 
                            if checkLabel(rtuple, local, n):
                                tree.append([rtuple, [local[n]]])
                                n += 1
                                return(tree, local[n:])
                                
                            else: 
                                break 
                        
                        elif 'Ttype:' in rtuple: 
                            x = checkTtype(rtuple, local, n)
                            if x.__class__ == tuple: 
                                n = x[1]
                                local = local[n:]
                                tree.append([rtuple, x[0]])
                            elif x == True:
                                n+= 1
                            else:
                                 break
                            return(tree, local[n:])

                        
                        elif re.match(rtuple[0], local[n]):
                            n+=1
                            return(tree, local[n:])
                                
                            
                        else:                       #only item in tuple doesn't match 
                            break                    #break out of tuple loop

    else:         
        return False    

##########################################################


def input_typedef(fact):
    
    subj = fact[0]
    if subj in TypeHier.keys():
        print >> sys.stderr, " \nMulti-Inheritance detected, Type \"%s\" is not included in the type tree.\n" % (subj, )
        return
    else: 
        head = fact[2]
        TypeHier[subj] = [False, head]
        return  
        
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

def isPredef(fact):
    
    if fact[0] == ':':
        if '->' in fact:
             return True 
        elif '<-' in fact:
             return True 
        elif ('[' in fact) and (']' in fact):
             return True 
        else: 
            fact.remove(':')
            return False 
            
       
    elif '->' in fact:
         print >> sys.stderr, '\'->\' present in fact but no predefined marker \':\',\n user is advised to add it' 
         return True 
    elif '<-' in fact: 
        print >> sys.stderr, '\'<-\' present in fact but no predefined marker \':\', user is advised to add it' 
        return True 
    elif ('[' in fact) and (']' in fact): 
        print >> sys.stderr, '\'[]\' present in fact but no predefined marker \':\', user is advised to add it' 
        return True     
    else: 
        return False 

###################################################

def check_predef(f):
    '''
    grammar_dict['Predefined'] = [['Primary Term', '<-', 'Single Alias'],
                                  ['Primary Term', '<-', 'Multi Alias '], 
                                  ['Single Alias', '->', 'Primary Term'],
                                  ['Primary Term', '[', 'Type', ']']
                                  ]
    Type definitions are added to the type hierarchy and then checked for completeness.  
    Aliases are added to the two dictionaries, Aliases to Subj (mapping the alias to it's primary term) 
    and Subj to Aliases where the Subject/Primary term is mapped to all it's aliases.  It is important to note
    that while one entitiy (primaryterm) may have multiple aliases, a single alias may refer to only one entity. 
    '''
    
    predefs = grammar_dict['Predefined']
    
    for rule in predefs: 
        symb = rule[1]
        
        if symb in f: 
            i = f.index(symb)
            
            if symb == '[':
                input_typedef(f)
                break 
            
            elif 'Alias' in rule[0]:
                l  = f[:i][0]
                r = f[i+1:][0]
                AliasestoSubj[l] = r
                break
             
            elif 'Alias' in rule[2]:
                
                l  = f[:i][0]
                r = f[i+1:]
                if len(r) > 1 and  not 'Multi' in rule[2]:
                    continue
                elif len(r) > 1: 
                    r = ' '.join(r)
                    r = r.replace('.', '')
                    r = r.strip()
                    MultiAl.append(r)
                else: 
                    r = r[0]
                    r = r.replace('.', '')
                    r = r.strip()
                    
                AliasestoSubj[r] = l     
               
                break
        else: 
            continue 
    
    return

###################################################### 
def first_pass(facts):
    '''
    The first pass pulls out predefined rules which contain information that will
    be needed before compleely going thru all facts.  Predefined rules include type definitions,
    as well as aliases, and so if a rule is of the predefined form, isPredef(fact) will return true, 
    and then the fact is  analyzed using the function CHECK_PREDEF(fact)    
    '''
    remFacts = []
    failed = []
    tokens = re.compile('(<-|->|:=|-=|\?<|:|;|\?:|>\?|.|\?|,|"|~>|=>>|<|>|[-_0-9a-zA-Z\']+|[+]|-|[*]|/|%|=|!=|<=|>=|=[[]|[\\\\][[]|[[]|[]]|[(]|[)]|!|&|[|]|[||]|&&|[\\\\$]|[\\\\]&|[\\\\\]@|[\\\\*]|[\\\\]|#)$')
    
    for f in facts: 
        
        f[1] = f[1].strip()
        f[1] = f[1].strip('.')
        f[1] = f[1].strip()
        
        subject = f[0]
        f, cit =  predpar.tokenize_pred_string(f[1], tokens)
        f.insert(0, subject)   
            
        if f == []:                              #failed to tokenize 
            failed.append(f)
                            
        #check if type def, check if predef --> only deal with those in first pass
        if isPredef(f):
            if ':' in f: 
                f.remove(':')
            check_predef(f)    
        else: 
            remFacts.append(f)
            continue 
    
    no_path = fcheck_types() 
    for n in no_path: 
        del TypeHier[n]
    
    remFacts1 = []
    
    for r in remFacts: 
        
        for a in MultiAl:
            a2 = a.split()
            if a2[0] in r: 
                i = r.index(a2[0])
                
                for il in range(len(a2)): 
                    if r[i+il] == a2[il]:
                        if il + 1 == len(a2):
                            r[i] = a
                            beg = r[:i+1]
                            after = r[i+il+1:]
                            r = beg + after  
                    else: 
                        break
                    
                
            else: 
                continue 
        remFacts1.append(r)
    
        
    return  remFacts1, failed #so when parsing thru rules, don't go thru the type definition again 
 
     
################################################
def print_grammardict():
      ##########PRINTING VOCAB DICTIONARY PRODUCED 
    for x in grammar_dict:
        print x + ":"
        print x.__class__
        for y in grammar_dict[x]:
            print  y + ":"
            for z in grammar_dict[x][y]:
                print  z 
        print '\n' 
    
########################################################################

def print_endFacts(parsed, failed):
    ##########PRINT STATMENTS 
    for n in parsed:
        print '\n'
        for i in n:
           print i
          
        
        
           
           
        
    print failed
    pass

####################################
    
def fact_checker():
    ''' 'main' function of this module. 
    '''
    vrules = []
    vfail = []
    global grammar_dict 
    grammar_dict = {}
    vdict = {}
    global TypeHier
    TypeHier = {}
    
    parsed_facts = []
    failed_facts = []
    facts2 = []
    
    
    vrules, vfail, vdict, TypeHier, grammar_dict  = check_vocab()
    
    #print_grammardict()
    
    add_predef_rules()
    facts = go_thru_factFile()
    
    facts2, failed_facts = first_pass(facts) #goes thru and analyzes predefined rules 
    
    for f2 in facts2:
        global depth
        depth = 0 
        factParse = parse_Facts(f2, 'Start', grammar_dict)
        if factParse: 
            parsed_facts.append([f2, factParse])
        else: 
            failed_facts.append(f2)
     
    print_endFacts(parsed_facts, failed_facts)
    
    return [parsed_facts, failed_facts] 



if __name__ == '__main__':
    fact_checker()


