''' Pred Parser

note left out tag, only allowing one operation per rule restriction condition (if block) 

'''

from string import *
import sys
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()


global_item = ''



#word
regex_wrds = re.compile('(([:-_\'\";,a-zA-Z]+\s)+[:-_\'\";,a-zA-Z]+.$)')


#obj
                        #[(label, ':'),
                         #(':', token_type_specification),
                         #(label, ':', token_type_specification),
                         #(typ_name),
                         #(label, '=', typ_name),
                         #(phrase-name),
                         #(label, '=', phrase-name)],

regex_obj = re.compile()

#msg
regex_msg = re.compile('(([:-_\';,a-zA-Z0-9]+\s)+[:-_\'\";,a-zA-Z]+[.?]$)' )

#N
regex_n = re.compile('^[0-9]+$')

#exp
regex_exp = re.compile('^[a-zA-Z]+$|^[0-9]+$')      #numbers or strings 

#entity restriction
                               


    
vocab_grammar = { #'Start': ['Pred'],
                  
                  'Pred': [(':=', '\"', 'Phrase', '\"', '.' ),
                           ('-=', '\"', 'Phrase', '\"', '.' ),
                           ('~>', '\"', 'Phrase', '\"', '.'),
                           ('=>>', '\"', 'Phrase', '\"', '.' ),
                           ('?<', '(', 'Exp', ')', 'Then'), 
                           ('\"', 'Phrase', '\"', '.')],
                    
                  'Phrase': [('Obj','Words', '.'),
                             ('Obj', '.')
                             ('Obj', 'Words', 'Phrase'),
                             ],

                  'Obj':[('<' , '>'),
                         ('<' , label, ':',  '>'),
                         ('<' , ':', tokentypespec, '>'),
                         ('<' , label, ':', tokentypespec, '>'),
                         ('<' , type-name, '>'),
                         ('<' , label, '=', typename, '>'),
                         ('<' , phrase-name, '>'),
                         ('<' , label, '=', phrase-name, '>')],
                   
                
                  'Words': [regex_wrds],    #should have option to be empty 
                  
                  'Then': [':', 'Command', 'Opt'],
                  
                  'Opt':  [('>?'),
                           ('Elif'),
                           ('Else')],
                  
                  'Else': [':', 'Command', '>?'],
                  
                  'Elif': ['?:', '(', 'Exp', ')', 'Then'], #force whitespace between expression and ()
                  
                  
                  'Exp':[( regex_exp, 'Op', regex_exp ),

                         ('Ent_rstr', 'Op', regex_exp ),

                         (regex_exp, 'Op', 'Ent_rstr'),
                         
                         ('Ent_rstr', 'Op', 'Ent_rstr'),
                         
                         (regex_exp, 'BinOp'), #binary op

                         ('Ent_rstr', 'BinOp') #binary op

                         
                         #note: not allowing more than one operation per condition 

                         ],
                
                 'BinOp': [('=[', 'N', ']'),       #minamx (binary op)
                            ('[', 'N', ':', 'N', ']')],   #substring (binary op)
                  
                  'Op':[('+'),
                        ('-'),
                        ('*'),
                        ('/'),
                        ('%'),
                        ('='),
                        ('!='),
                        ('<'),
                        ('<='),
                        ('>'),
                        ('>='),
                        ('!'),
                        ('&'),
                        ('|'),
                        ('&&'),
                        ('||')
                        # <label>
                        #{label} 
                        ],
                         
                  'Command': [('satisfied'),
                              ('comment', '\"', 'Msg','\"'),
                              ('warn', '\"', 'Msg', '\"'),
                              ('error','\"', 'Msg', '\"'),
                              ('abort', '\"', 'Msg', '\"'),
                              ('skip', 'N')],

                  'Msg': [regex_msg],   #words, optional punctuation at the end 

                  'N': [regex_n],

                  'Ent_rstr': [('\\', ),
                               ('\\$', ),
                               ('\\@', ), 
                               ('\\*', ),
                               ('\\&', )]
                  }          
            
                        
#############################################
                 
def match_regex (regex, i):

    if re.match(regex, i):
        return True
    else:
        return False
                                          
##########################################
def tokenize_pred_string(pstring):
    
    testStr = ''
    longestStr = ''
    tokenList = []
    count = 0
    tokens = re.compile('(:=|-=|\?<|:|;|\?:|>\?|.|\?|,|"|~>|=>>|<|>|[-_0-9a-zA-Z]+|[+]|-|[*]|/|%|=|!=|<=|>=|=[[]|[]]|[(]|[)]|!|&|[|]|[||]|&&|[\\\\$]|[\\\\]&|[\\\\\]@|[\\\\*][\\\\])$')
    
    for n in pstring:
        count += 1
        if n == " ":                        #throwout whitespace -- but probs mean new token 
            tokenList.append(longestStr)
            longestStr = ''                 #clear longest string
            testStr = ''                    #clear test string 
        else: 
            testStr += n
        
            if re.match(tokens, testStr):           #if match regex
                longestStr = testStr                #try to get longest match,
            else:                                   #if no match with addt'l char
                if longestStr != '':                #means have gone too far 
                    tokenList.append(longestStr)
                    if re.match(tokens, n):
                        longestStr = n                    #reset longest 
                    else: 
                        longestStr = ''
                        
                    testStr = n                         #rest test to curr val
                    
                    if count == len(pstring):  #have reached last element in string
                        if re.match(tokens, testStr):
                            tokenList.append(testStr)
                        else:                           #couldn't tokenize 
                            print >> sys.stderr, 'Failed to tokenize rule with predicate: %s' %(pstring,)
                            return []
                            
                            
                        
                else:                               #couldn't tokenize 
                    print >> sys.stderr, 'Failed to tokenize rule with predicate: %s' %(pstring,)
                    return []
    
    #print tokenList
    return tokenList
                                                    
##########################################
'''return (parse tree so far, count update)
'''

def parse_grammar (rule, start_sym, cnt):

    try:                                        
        sym_rules = []
        sym_rules = vocab_grammar[start_sym]            #start with sym: look up in grammar dict

        tree = []

                                 
        vrule = rule[1].split()                            #split rule into tokens along whitespace
        if not cnt == 0:
            vrule = vrule[cnt:]                           #update where are in rule
        
        #pass_count = 0
        count = 0
        
        max_count = len(vrule)
        
        for sym_tuple in sym_rules:                      #loop through tuples:get tuple in list of rules
                                        
            tree.append((start_sym, sym_tuple))
            
            if isinstance(sym_tuple[0], str) :
                
                for item in sym_tuple:                       #loop thru items in tuple: get item in tuple
                    try:
                        if vocab_grammar[item]:             # if item is an entry in dict: #eg Nonterminal
    
                            res = parse_grammar(rule, item, count)       #if returns true:
                                                                          #goto next item in tuple, else goto next tuple
                            #make sure res good
                            if res[1] == -1:                #means tuple failed
                                tree.remove(tree[-1])       #remove latest keyword/tuple pair --> this tuple failed
                                break                       #break out of items loop, tuple loop continues 
                                            
                            elif res[1] > count:          #if count returned by parse grammar greater than actual count
                                count = res[1] - 1           #means that func call got further in vrule than current count,
                                vrule = vrule[count:]        #should update rule and count
                                tree.extend(res[0])          #update tree
                                            
                            
                    except KeyError:                                #if not entry, Must be Terminal (since exception raised)
    
                        if not isinstance(item, str):               #means that have come across regex!
                            
                            if match_regex(item, vrule[count]): #matched regex 
                                
                                tree.append((start_sym, sym_tuple))
                                count = count + 1
    
                                if sym_tuple.index(item) == len(sym_tuple) - 1: #at end of tuple, done, can return 
                                    return (tree, count)
                                else:                   #still more items in tuple to go! 
                                    continue 
                            else:                               #fail means that regex failed -- failed tuple!
                                tree.remove(tree[-1])
                                break
                                
                                                                           #check if item(token) in tuple matches with
                        elif count < max_count and vrule[count] == item :     #token in vrule : yes:
    
                            tree.append((start_sym, sym_tuple))             #add to parse tree
                            
                            count = count + 1
    
                            if sym_tuple.index(item) == len(sym_tuple) - 1:         #if end of tuple (pred): DONE
                                                                                     #return parse tree text + count
                                return (tree, count) 
    
                            else:                                               #else: GOOD so far,  #still more items to go:
                                continue                                           #goto next item in tuple:
    
                        elif not count <  max_count:                        #have reached end of vrule before proper end:
                                                                        #problems
                            print >> sys.stderr, "Error -- reached end of vrule" 
                            
                            return([], -1)
                             
    
                        else:                                   #if no match and no more tuples:
                            break                                   #break out of items loop, sym_rules will exit on own
                                                                #else no match, but more tuples left to explore:
                                                                   #break out of items loop -- sym_rules will continue
                                                                #note: count is valid-- havent reached end of vrule yet
    
            else:  #means have encountered regex 
                
                if match_regex(item, vrule[count]): #matched regex 
                    tree.append((start_sym, sym_tuple))
                    count = count + 1
                    
                    if sym_tuple.index(item) == len(sym_tuple) - 1: #at end of tuple, done, can return 
                         return (tree, count)
                    else:                   #still more items in tuple to go!
                          continue
                else:                               #fail means that regex failed -- failed tuple!
                    tree.remove(tree[-1])
                    continue 
                
                
            print >> sys.stderr,"Stopped parsing after encountering %s" % (start_sym,)
    
            return (tree,-1)       #means failed  

    except TypeError: 
        
        if match_regex(sym_tuple[0], vrule[count]): #matched regex 
                    tree.append((start_sym, sym_tuple))
                    count = count + 1
                    
                    if sym_tuple.index(item) == len(sym_tuple) - 1: #at end of tuple, done, can return 
                         return (tree, count)
                    else:                   #still more items in tuple to go!
                        
                          sym_rules = sym_rules[:-1]
                          
                          return parse_vocab(rule, sym_rules[start_sym], count)
        else:                               #fail means that regex failed -- failed tuple!
            tree.remove(tree[-1])  
                                                  
    except KeyError:                                #start sym is not in dict for some reason

        print >> sys.stderr,"%s not present in grammar" % (start_sym,)
        
        return ([], -1)     #means failed 
    
        
                        
    # except TypeError: 
                            
     

                  
                    
#############################################################


def parse_vocab():
    
    '''#take in vocab file
       #read line by line (one rule per line)
    '''

    if len(sys.argv) < 2: 
        sys.stderr.write("must include vocabulary (.v) file \n")
        raise SystemExit(1)

    
    vocabfile = open(sys.argv[1], 'r')
    
    #vocabfile = open('test.v', 'r')
    facts = []
    line = ''
    line = vocabfile.readline()
    m = s = p =  r = c = ''
    px = []
    
    #sampled from factotum_entities 

    while(len(line) > 0):
        my_fact = line[:-1]
        line = ''
        line = vocabfile.readline()
        
        while(len(line) > 0) and (line[0] == '-'):
            my_fact += '\n' + line[1:-1]
            line = ''
            line = vocabfile.readline()
            continue

        (m,s,p,px,r,c) = lex.breakup_fact(my_fact)
        
        p = p.strip() # get rid of whitespace
        facts.append([s,p])
    
    rule_pred = ''
    parseTrees = []
    failed_rules = []
    
    for rule in facts:
        rule_pred = tokenize_pred_string(rule[1])
        rule_parse =  parse_grammar(rule_pred, 'Pred', 0)
        if rule_parse != []:                        #if parse didn't fail, add to list of accepted parse trees
            parseTrees.append(rule, rule_parse)
        else: 
            failed_rules.append(rule)
            
        
    
    print parseTrees 
    print failed_rules
    return parseTrees 

#########################################################


if __name__ == "__main__":
    parse_vocab()
    
                      
