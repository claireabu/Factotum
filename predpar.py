''' Pred Parser

note:
-left out items that use tag, 
-only allowing one operation per rule restriction condition (if block) 

'''

from string import *
import sys
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()

#msg
regex_msg = re.compile('^([:-_\';,.\?a-zA-Z0-9]+)$' )

#N
regex_n = re.compile('^[0-9]+$')

#exp
regex_exp = re.compile('^[a-zA-Z]+$|^[0-9]+$')      #numbers or strings 
regex_op = re.compile('^([+]|-|[*]|/|%|=|!=|<=|>=|<|>|&|[|]|[||]|&&)$') #left out # <label>, {label} 
regex_ent = re.compile('^([-_0-9a-zA-Z]+| \D+)$')          
regex_tag = re.compile('^[-_0-9a-zA-Z]+$') 

                        
#word
regex_wrds = re.compile('^[:.-_\';,0-9a-zA-Z]+$')

#objs
regex_label = re.compile('^[-_0-9a-zA-Z\']+$')
regex_ttypespec = re.compile('^[-_0-9a-zA-Z\'\?.,;]+$')     #note: left out infinity 
regex_typename = re.compile('^[-_0-9a-zA-Z\']+$')           #couldn't find def: used same as label 
regex_phrasename = re.compile('^[-_0-9a-zA-Z\']+$')         #couldn't find def: used same as label 

                               
Pred =  [   (':=', '\"', 'Phrase', '\"', '.' ),
            ('-=', '\"', 'Phrase', '\"', '.' ),
            ('~>', '\"', 'Phrase', '\"', '.'),
            ('=>>', '\"', 'Phrase', '\"', '.' ),
            #('?<', '(', 'Exp', ')', 'Then', '.'), 
            ('?<', '(', 'Cond', ')', '.'),
            ('\"', 'Phrase', '\"', '.')
        ]

  
Phrase = [  ( 'Obj', 'Words'),
            ( 'Obj', 'Words', 'Phrase' )           
        ]
    
Obj =  [('<' , '>'),
        ('<' , 'label', ':',  '>'),
        ('<' , ':', 'tokentypespec', '>'),
        ('<' , 'label', ':', 'tokentypespec', '>'),
        ('<' , 'type-name', '>'),
        ('<' , 'label', '=', 'typename', '>'),
        ('<' , 'phrase-name', '>'),
        ('<' , 'label', '=', 'phrase-name', '>')
        ]

 #note: not allowing more than one operation per condition 
Cond = [    ( 'Exp', 'Op', 'Exp' ),
            ('Ent_rstr', 'Op', 'Exp' ),
            ('Exp', 'Op', 'Ent_rstr'),
            ('Ent_rstr', 'Op', 'Ent_rstr'),
            ('Exp', 'BinOp'),           #binary op
            ('Ent_rstr', 'BinOp'),         #binary op
            ('!', 'Exp'),
            ('!', 'Ent_rstr')
        ]


BinOp = [   ('=[', 'N', ']'),       #minamx (binary op)
            ('[', 'N', ':', 'N', ']')   #substring (binary op)
        ]

Ent_rstr = [    ('\\', 'Tag'),
                ('\\', '$','Ent'),
                ('\\', '@','Ent'), 
                ('\\', '*','Tag' ),
                ('\\', '&','Ent' ),
                ('\\', '$', 'Tag', ':', 'label'),
                ('\\', '*', '<', '>', 'Tag', ':', 'label'),
                ('\\', '<', '>', 'Tag', ':', 'label')
            ]

Then = [(':', 'Command', 'Opt')],

Command = [ ('satisfied'),
            ('comment', '\"', 'Msg','\"'),
            ('warn', '\"', 'Msg', '\"'),
            ('error','\"', 'Msg', '\"'),
            ('abort', '\"', 'Msg', '\"'),
            ('skip', 'N')
            ]
                 
Opt = [  ('>?'),
         ('Elif'),
         ('Else')
      ]
                  
Else =  [':', 'Command', '>?'],
                  
Elif =  ['?:', '(', 'Cond', ')', 'Then'], #force whitespace between expression and ()
                  
                        
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
    tokens = re.compile('(:=|-=|\?<|:|;|\?:|>\?|.|\?|,|"|~>|=>>|<|>|[-_0-9a-zA-Z\']+|[+]|-|[*]|/|%|=|!=|<=|>=|=[[]|[]]|[(]|[)]|!|&|[|]|[||]|&&|[\\\\$]|[\\\\]&|[\\\\\]@|[\\\\*]|[\\\\])$')
    
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
                            exit(1)
                            
                            
                        
                else:                               #couldn't tokenize 
                    print >> sys.stderr, 'Failed to tokenize rule with predicate: %s' %(pstring,)
                    return []
    
    #print tokenList
    return tokenList
                                                    
##########################################
###########################################



def parse_pred(vrule):  
    
    l_rule = [] 
    tree = []
    
    for tuple in Pred:
        tree = []
        tree.append(['Pred', tuple])
        l_rule = vrule 
                
        for token in tuple:
            
            if token == 'Phrase':
                res_phrase = parse_phrase(l_rule)
                if res_phrase: 
                    tree.extend(res_phrase[0])
                    l_rule = res_phrase[1]
                    
                else:
                    print >> sys.stderr, 'Failed to parse Phrase'
                    return False 
            
            elif token == 'Cond':
                 res_cond = parse_cond(l_rule)
                 if res_cond:
                     tree.extend(res_cond[0])
                     l_rule = res_cond[1]
                     
                 else: 
                     print >> sys.stderr, 'Failed to parse Cond'
                     return False
                        
            elif token == 'Then':
                res_then = parse_then(l_rule)
                if res_then:
                    tree.extend(res_then[0])
                    l_rule = res_then[1]
                else:
                    print >> sys.stderr, 'Failed to parse Then phrase'
                    return False 
    
            elif token == '.' : #must be at end of tuple as well as rule
                if l_rule[0] == token and len(l_rule) == 1: #means only 1 item remains in lrule and it's the period! 
                    #success 
                                           #treeupdate? 
                    return(vrule, tree)
                else:
                    break 
                
            else: 
                if token == l_rule[0]: 
                    
                    l_rule = l_rule[1:]
                    
                       #treeupdate? 
                    continue 
                else:
                    break 
                
               
    return False 
 
 
#############################


def parse_phrase(vrule):
    
    l_rule = vrule
    res_obj = []
    res_word = []
    res_phrase = []
    tree = []
        
    for phrase_tuple in Phrase:         #go through possible phrase grammar
        
        tree = [] #automatically resets tree --- means previous tuple failed and so we need to start over 
        tree.append(['Phrase', phrase_tuple])
        l_rule = vrule                 #have to rest to beginning of rule 
        
        for token in phrase_tuple:      #go through tokens in the grammar rule
        
            if token == 'Obj':
                res_obj = parse_obj(l_rule)
                if res_obj:                 #means that obj parsed fine
                    tree.extend(res_obj[0])
                    l_rule = res_obj[1]
                else:
                    break
                
            elif token == 'Words':                  #regex match words?
                res_word = parse_words(l_rule)          #check: either return true: continue & update lrule 
                if res_word:
                    tree.extend(res_word[0])
                    l_rule = res_word[1]
                    if l_rule[0] == '<':
                        continue 
                    else: 
                        return (tree, l_rule)
                else:
                    break
            
            elif token == 'Phrase':
                res_phrase = parse_phrase(l_rule)
                if res_phrase:
                    tree.extend(res_phrase[0])
                    l_rule = res_phrase[1]
                    return (tree, l_rule)
                    
                else:
                    break
            
    return False  
    
###############################

def parse_obj(vrule):
    '''
    go through options for Obj (global) -- 
    use regex to match label, ttypespec, phrase name and type name, 
    otherwise make sure symbols (< , >, : , =) match up
    
    if successful: returns a mini tree and where everything should be in the rule
    if no tuple returns a successful parse: return False 
    '''
    l_rule = vrule 
    n = 0
    tree = []
    
    for tuple in Obj:                       #iterate through possible tuples 
        
        #automatically resets tree --- means previous tuple failed and so we need to start over
        tree = []
        tree.append(['Obj', tuple]) 
        n = 0           #reset for every new tuple encountered 
        
        for token in tuple:                 #go through tokens in each tuple 
            
                if token == 'label':                    #match regex label
                    if match_regex (regex_label, l_rule[n]):
                        tree.append([token, l_rule[n]])
                        n += 1                              #good
                        continue                            #carry on
                    else:
                        break 
                    
                elif token == 'tokentypespec':                          #match regex tokentypespc 
                    if match_regex (regex_ttypespec, l_rule[n]):
                        tree.append([token, l_rule[n]])
                        n += 1                              #good
                        continue                            #carry on
                    else:
                        break
                    
                elif token == 'type-name':                #match regex typename
                    if match_regex (regex_typename, l_rule[n]):
                        tree.append([token, l_rule[n]])
                        n += 1                              #good
                        continue                            #carry on
                    else:
                        break
                    
                elif token == 'phrase-name':        #match regex phrase name
                    if match_regex (regex_phrasename, l_rule[n]):
                        tree.append([token, l_rule[n]])
                        n += 1                              #good
                        continue                            #carry on
                    else:
                        break
                    
                elif token == '>' and l_rule[n] == token: #have reached the end of the obj! 
                    return ([tree, l_rule[n+1:]])
                
                elif token == l_rule[n]:        #token matches l_rule 
                    #tree.append(token,n)??
                    n += 1
                    continue 
                else: 
                    break 
                    
    
    print >> sys.stderr, 'Failed to parse Object'            
    return False            #means, have gone through all tuples and not once returned successfully





    ###########################################

def parse_words(vrule):
    #go through tokens checking if word until hit period, quote, or < 
    l_rule = vrule 
    tree =[]
    min_one = False 
      
    for n in l_rule:
        
        if n == '<' or n == '\"':   
            if min_one: 
                l_rule = l_rule[l_rule.index(n):]
                return (tree, l_rule)
            else: 
                #means already obj without even one word 
                print >> sys.stderr, 'Failed to have relational tokens between objects '
                return False 
        
        elif n == '.':
            if l_rule[l_rule.index(n)+1] != '\"':
                print >> sys.stderr, 'Misplaced punctuation, (.) only allowed at the end of phrase, followed by \"'
                return False
            else: 
                tree.append(['Words', n])
                l_rule = l_rule[l_rule.index(n)+1:]
                return (tree, l_rule)
            
        elif match_regex(regex_wrds, n):
            tree.append(['Words', n])
            min_one = True 
             
        else: 
            print >> sys.stderr, '%s is not an allowed relation token' % (n, )
            return False 
   
###############################


def parse_cond(vrule):
    
    l_rule = vrule 
    tree = []
    n = 0
    cond_count = 0
    
    for tuple in Cond:
        tree = []
        tree.append(['Cond', tuple])
        l_rule = vrule
        n = 0 
        cond_count = 0
        
        for token in tuple:
            
            if token == 'Exp':
                if match_regex(regex_exp, l_rule[n]):
                    tree.append([token, l_rule[n]])
                    n += 1
                    cond_count += 1
                    
                    if cond_count == 3 and l_rule[n] == ')': #should be at end of expression 
                        return (tree, l_rule[n:])
                    else: 
                        break #fail
                     
                else:           #Expression failed to match 
                    break
                
            elif token == 'Ent_rstr':
                res_ent = parse_ent_rstr(l_rule[n:])
                if res_ent: 
                    tree.extend(res_ent[0])
                    l_rule = res_ent[1]
                    n = 0 
                    cond_count += 1
                else: 
                    break
                
                if cond_count == 3 and l_rule[n] == ')': #should be at end of expression 
                        return (tree, l_rule[n:])
                elif cond_count < 3:
                    continue 
                else:
                    break #fail
                  
                             
            elif token == 'Op':
                if match_regex(regex_op, l_rule[n]):
                    tree.append([token, l_rule[n]])
                    n += 1
                    cond_count += 1
                else:
                    break 
                
            elif token == 'BinOp':
                res_binop = parse_binop(l_rule[n:])
                
                if res_binop: 
                    tree.extend(res_binop[0])
                    l_rule = res_binop[1]
                    n = 0 
                    
                    if l_rule[n] == ')':        #next item should be ), indicating end of expr 
                        return(tree, l_rule[n:])
                    else:
                        break  
                else: 
                    break 
            elif token == l_rule[n]:
                n += 1
                cond_count += 2     #can have only 1 element after it 
                continue 
            else:
                break 
    return False 
    

            
############################

def parse_binop(vrule):
    l_rule = vrule 
    tree = []
    i = 0
    
    for tuple in BinOp:
        tree = []
        tree.append(['Binop', tuple])
        l_rule = vrule 
        i = 0
        
        for token in tuple: 
            
            if token == 'N':
                if match_regex(regex_n, l_rule[i] ):
                    tree.append([token, l_rule[i]])
                    i += 1
                    continue
                else: 
                    break 
                
            elif token == ']' and token == l_rule[i]: #have reached end of binop! 
                return(tree, l_rule[i+1:])
            
            elif token == l_rule[i]:
                i+=1
                continue 
            else:
                break 
        

    return False   
        
    

###############################


def parse_ent_rstr(vrule):
    l_rule = vrule
    tree = []
    n = 0
    count = 0
    
    for tuple in Ent_rstr:
        tree = []
        tree.append(['Ent_rstr', tuple])
        l_rule = vrule
        n = 0
        count = 0
        
        for token in tuple:
            
            count += 1
            
            if token == 'Tag':
                if match_regex(regex_tag, l_rule[n]):
                    tree.append([token, l_rule[n]])
                    n+=1  
                else:
                    break 
                
            elif token == 'Ent':
                if match_regex(regex_ent, l_rule[n]):
                    tree.append([token, l_rule[n]])
                    n+=1
                else:
                    break 
                
            elif token == 'label':
                if match_regex(regex_label, l_rule[n]):
                    tree.append([token, l_rule[n]])
                    n += 1
                else:
                    break 
                
            else:
                if token == l_rule[n]:
                    n+=1
                else:
                    break 
                
            if count == len(tuple):
                
                return (tree, l_rule[n:])
            
            
                
    return False

###########################


def parse_then(vrule):
    '''
    Then = [(':', 'Command', 'Opt')],
    '''
    l_rule = vrule
    tree = []
    n = 0
    
    for tuple in Then:
        tree.append(['Then', tuple ] ) 
        
        for token in tuple:
            
            if token == 'Command':
                res_c = parse_commad(l_rule[n:])
                if res_c:
                    tree.extend(res_c[0])
                    l_rule = res_c[1]
                    n = 0 
                else:
                    break
            
            elif token == 'Opt': 
                 res_opt = parse_opt(l_rule[n:])
                 if res_opt:
                     tree.extend(res_opt[0])
                     l_rule = res_opt[1]
                     n = 0
                     return (tree, l_rule)
                 else: 
                     break 
                 
            elif token == l_rule[n]: 
                n += 1
                continue 
            
            else:
                break 
    
    return False
###############################


def command(vrule):
    '''
    Command': [                ('satisfied'),
                              ('comment', '\"', 'Msg','\"'),
                              ('warn', '\"', 'Msg', '\"'),
                              ('error','\"', 'Msg', '\"'),
                              ('abort', '\"', 'Msg', '\"'),
                              ('skip', 'N')],
    '''
    
    l_rule = vrule
    tree = []
    n = 0
    quote_encountered = False
    
    for tuple in Command:
        tree = []
        tree.append(['Command', tuple])
        l_rule = v_rule 
        n = 0 
        
        for token in tuple: 
            
            if token == 'Msg':
                res_msg = parse_msg(l_rule[n:])
                if res_msg: 
                    tree.extend(res_msg[0])
                    l_rule = res_msg[1]
                    n = 0
                else:
                    break 
                   
            elif token == 'N':
                
                if match_regex(regex_n, l_rule[n]):
                    tree.append(['N', l_rule[n]])
                    return(tree, l_rule)
                else:
                    break 
                
            
            elif l_rule[n] == token: 
                
                n += 1
                
                if token == '"':
                    if quote_encountered:
                        return (tree, l_rule[n+1:])
                    else:
                        quote_encountered = True
                        
                elif token == 'satisfied':
                    return (tree, l_rule[n+1:])
                
                else: 
                    continue 
                
            else:
                print >> sys.stderr, 'Failed to match Command: %s' %(l_rule[n], )
                break
                
                
             
    
    return False 
    
###############################


def parse_msg(vrule):
    
    l_rule = vrule 
    tree =[]
    min_one = False
    
    for n in l_rule:
        
        if n == '\"':
            if min_one:
                l_rule = l_rule[l_rule.index(n):]
                return (tree, l_rule)
            else:
                print >> sys.stderr, "Please include a message with command \n"
                break 
        
        elif match_regex(regex_msg, n):
            tree.append(['Msg', n])
            min_one = True 
            continue 
        
        else:
            print >> sys.stderr, "Message failed to follow standard format \n"
            break 
            
    
    
    return False 
###############################

def parse_opt(vrule ):
    '''
    Opt = [  ('>?'),
         ('Elif'),
         ('Else')]

    '''
    l_rule = vrule
    tree = []
    
    for tuple in Opt:
        tree = []
        tree.append(['Opt', tuple])
        l_rule = vrule
        
        for token in tuple:
            
            if token == 'Elif':
                res_elif = parse_elif_st(l_rule)
                if res_elif:
                    tree.extend(res_elif[0])
                    l_rule = res_elif[1]
                    return (tree, l_rule)
                else:
                    break
            
            elif token == 'Else':
                res_else = parse_else_st(l_rule)
                if res_else:
                    tree.extend(res_else[0])
                    l_rule = res_else[1]
                    return (tree, l_rule)
            
            elif l_rule[0] == token: #>?'
                    return (tree, l_rule[1:])
            
            else: 
                break
            
    return False 

###############################

def parse_elif_st(vrule):
    '''
    Elif =  ['?:', '(', 'Cond', ')', 'Then']
    '''
    l_rule = vrule
    tree = []
    tree.append(['Elif', tuple(Elif)])
    
    for token in Elif: 
        
        if token == 'Cond':
            res_cond = parse_cond(l_rule)
            if res_cond: 
                tree.extend(res_cond[0])
                l_rule = res_cond[1]
                continue 
            else:
                break 
                
        elif token == 'Then':
            res_then = parse_then(l_rule)
            if res_then:
                tree.extend(res_then[0])
                l_rule = res_then[1]
                return (tree, l_rule  )
            else: 
                
                break 
            
        elif l_rule[0] == token:
            l_rule = l_rule[1:]
            continue 
        
        else: 
            break 

    return False 


###############################
def parse_else_st():
    '''
    Else =  [':', 'Command', '>?'],
    '''
    l_rule = vrule
    tree = []
    tree.append(['Else', tuple(Else)])
    
    for token in Else: 
        
        if token == 'Command':
            res_cmd = command(l_rule)
            if res_cmd: 
                tree.extend(res_cond[0])
                l_rule = res_cond[1]
                continue 
            else:
                break 
            
        elif l_rule[0] == token:
            l_rule = l_rule[1:]
            
            if token == '>?':
                return (tree, l_rule)
            
            continue 
        
        else: 
            break 

    return False 


###############################

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
    #parse_vocab()
    rule_pred = tokenize_pred_string('?< ( !\NP-Complete ).')
    res = parse_pred(rule_pred)
    if not res:
        
        print ('False')
    else:
        for n in res[1]:
            print n 
            print ('\n')
     
    
                      
