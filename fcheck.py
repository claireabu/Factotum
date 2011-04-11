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
     other tools. 

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

def check_vocab():
    res_parseV = []
    res_parseV = predpar.parse_vocab()
    return res_parseV  

def go_thru_factFile():
    '''
    Opens up the given file,  reads in line by line, and
    uses factotum lexer to go thru and find the subject and predicates
    '''
    #if len(sys.argv) < 3: 
     #   sys.stderr.write("must include fact (.f) file \n")
      #  raise SystemExit(1)

    
    #factfile = open(sys.argv[2], 'r')
    
    factfile = open('lingdata.f', 'r')
    
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

def parse_Facts(fact, start_sym, dI):
    ''' The main parsing function and is recursive, 
        makes a copy of the token list in rulePred (stored to local), 
        and then goes through the global vocab_grammar. 
    '''
    
    #if rulePred == []: return False 
    
    local = fact
    tree = [] 
    key = start_sym
    n = 0
    count = 0
    

        
    if key in dI.keys(): 
        rules = dI[key] 
        
        if rules.__class__ == dict:  #means at very top level, and have subject 
            parse_Facts(fact, 'Start', dI[key])
            
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
                        
                        try: 
                            if vocab_grammar[token]: 
                                res = parseGrammar (local[n:], token)
                                if res: 
                                    
                                    if PassedThru == 0: 
                                        x = update_TypeTree(token, local, TypeTree)
                                    
                                    tree.extend(res[0])
                                    local = res[1]
                                                            
                                    if count == len(rtuple):
                                        return (tree, local)
                                    else: 
                                        n = 0
                                else: 
                                    break
                                
                        except KeyError:        #encountered regex/terminal
                            
                            if n < len(local):
                                
                                if check_regex(token):
                                    pattern = regex_dict[token]
                                    
                                    if match_regex(pattern, local[n]):
                                        
                                        if PassedThru > 0:
                                            if needs_sec_check(token):
                                                if not check_second_check(token, local[n]):
                                                    break
                                            
                                        if check_repeat(token):
                                            re = []
                                            
                                            if n < len(local)-1:
                                                
                                                while (match_regex(pattern, local[n])):
                                                    re.append(local[n])
                                                    if n < len(local)-1:
                                                        n += 1
                                                    else: 
                                                        break
                                                    
                                                tree.append([token, re])
                                                
                                                if count == len(rtuple) :
                                                    return(tree, local[n:])
                                                else: 
                                                    continue
                                        else: #not in repeat
                                            
                                            tree.append([token, local[n]])
                                            n += 1
                                            
                                            if count == len(rtuple) :
                                                return(tree, local[n:])
                                            else: 
                                                continue
                                    else:
                                        break    

                                else:   #not in the regex list, just a symbol match 
                                    
                                    if match_regex(token, local[n]): 
                                        n+=1
                                        
                                        if count == len(rtuple):
                                            return(tree, local[n:])
                                        else:
                                            continue
                                    
                                    else:
                                        break          
                            else:                       #no tokens don't match in tuple
                                 break                   #break out of token loop, continue to next tuple
          
                else: ####Only one item-- don't want to iterate thru the string 
                    try:
                        if vocab_grammar[rtuple[0]] :
                            res = parseGrammar(local[n:], rtuple[0])
                            if res:
                                
                                if PassedThru == 0: 
                                    x = update_TypeTree(rtuple[0], local, TypeTree)
                                                        
                                tree.extend(res[0])
                                local = res[1]
                                return(tree, local)
                        else:
                            return False
                        
                    except KeyError:
                        
                        if n < len(local):
                            
                            if check_regex(rtuple[0]):
                                pattern = regex_dict[rtuple[0]]
                                
                                if match_regex(pattern, local[n]):
                                    
                                    if PassedThru > 0: 
                                        if needs_sec_check(rtuple[0]):
                                            if not check_second_check(rtuple[0], local[n]):
                                                break #failed to be a phrasename or type name 
                                            
                                    if check_repeat(rtuple[0]):
                                        re = []
                                        
                                        if n < len(local)-1:
                                            while (match_regex(pattern, local[n])):
                                                re.append(local[n])
                                                if n < len(local)-1:
                                                    n += 1
                                                else:
                                                    break
                                            
                                            tree.append([rtuple[0], re])
                                            return(tree, local[n:])
                                       
                                    else: #not in repeat
                                        tree.append([rtuple[0], local[n]])
                                        n += 1
                                        return(tree, local[n:])
                                    
                                        
                                    
                            else:   #not in the regex list, just a symbol match
                                
                                if match_regex(rtuple[0], local[n]):
                                    n+=1
                                    return(tree, local[n:])
                                
                            
                        else:                       #only item in tuple doesn't match 
                            break                    #break out of tuple loop
                        
            
        
    else:         
        return False    

def fact_checker():
    
    #get .v file  --> vocab 
    #run predpar over .v file, 
        #get dictionary 
        #use that as grammar
    vrules = []
    vfail = []
    global grammar_dict 
    grammar_dict = {}
    global TypeHier
    TypeHier = {}
    vrules, vfail, grammar_dict, TypeHier  = check_vocab()
        
    #get .f file  --> facts
        #line by line get facts like in predpar 
        #compare against grammar like in predpar 
        
    facts = go_thru_factFile()
    
    parsed_facts = []
    failed_facts = []
    
    
    
     
        
    #go thru facts 
    #parse each one according to grammar generated by vocabulary 
    for f in facts: 
        
        subject = f[0]
        pred, cit =  predpar.tokenize_pred_string(f[1])
        #print [f[0]] + pred
        parse_facts(pred, subject, grammar_dict)
        
    
    
    
    return 



if __name__ == '__main__':
    fact_checker()


