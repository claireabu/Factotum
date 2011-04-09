''' Pred Parser

'''

from string import *
import sys
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()




regex_dict = {  'Words':    re.compile('^[.,:\-_\';0-9a-zA-Z\(\)\200-\377/]+$'), 
                'Label':    re.compile('^[-_0-9a-zA-Z\']+$'),
                'Ttypespec': re.compile('^[-_0-9a-zA-Z\'\?.,;]+$'),
                'Typename':  re.compile('^[-_0-9a-zA-Z\']+$'), 
                'Phrasename': re.compile('^[-_0-9a-zA-Z\']+$'),
                'Exp':  re.compile('^[a-zA-Z]+$|^[0-9]+$'),      #numbers or strings 
                'Op':   re.compile('^([+]|-|[*]|/|%|=|!=|<=|>=|<|>|&|[|]|[||]|&&)$'), #left out # <label>, {label} 
                'Ent':  re.compile('^([-_0-9a-zA-Z]+| \D+)$'),
                'Tag':  re.compile('^[-_0-9a-zA-Z]+$'),
                'Msg':  re.compile('^([:\-_\';,.\?a-zA-Z0-9]+)$' ),
                'N':    re.compile('^[0-9]+$'),
                'TypeDefName': re.compile('^[-_0-9a-zA-Z\']+$')
              }


Repeat = ['Words', 'Msg']
Second_check = ['Typename', 'Phrasename']


              
vocab_grammar = {   'Start' : [   ['TypeDef'],
                                ['Pred']
                             ],
                    
                    'TypeDef': [    ['TypeDefName', '\[', '\]'],
                                    ['TypeDefName', '\[', 'TypeDefName', '\]']
                                ],
                    
                    
                    
                    'Pred' :  [     [':=', 'Phrase' ],
                                    ['-=', 'Phrase' ],
                                    ['~>', 'Phrase' ],
                                    ['=>>', 'Phrase' ],
                                    ['\?<', '\(', 'Cond', '\)', 'Then', ], 
                                    ['Phrase']
                                    
                                ],
                    
                    'Phrase' : [    ['Obj', 'Words', 'Phrase' ],
                                    [ '\"', 'Obj', 'Words', 'Phrase', '\"', '.' ],
                                    [ '\"', 'Obj', 'Words', 'Phrase', '\"'],
                                    [ 'Obj', 'Words'],
                                    ['\"', 'Obj', 'Words', '\"', '.'],
                                    ['\"', 'Obj', 'Words', '\"'],
                                    ['\"', 'Words', 'Phrase', '\"', '.'],
                                    ['\"', 'Words', 'Phrase', '\"'],
                                    ['\"', 'Words', '\"', '.'],
                                    ['\"', 'Words', '\"'],
                                    ['Words'] 
                                ],
                    
                    'Obj' :     [   ['<' , '>', 'Obj'],
                                    ['<', '>'],
                                    ['<' , 'Label', ':',  '>'],
                                    ['<' , ':', 'Ttypespec', '>'],
                                    ['<' , 'Label', ':', 'Ttypespec', '>'],
                                    ['<' , 'Typename', '>'],
                                    ['<' , 'Label', '=', 'Typename', '>'],
                                    ['<' , 'Phrasename', '>'],
                                    ['<' , 'Label', '=', 'Phrasename', '>']
                                    
                                    
                                ], 

                                #note: not allowing more than one operation per condition 
                    'Cond' :    [   ['Exp', 'Op', 'Exp', 'MultOp' ],
                                    ['Ent_rstr', 'Op', 'Exp', 'MultOp' ],
                                    ['Exp', 'Op', 'Ent_rstr', 'MultOp'],
                                    ['Ent_rstr', 'Op', 'Ent_rstr', 'MultOp'],
                                    ['Exp', 'Op', 'Exp'],
                                    ['Ent_rstr', 'Op', 'Exp'],
                                    ['Exp', 'Op', 'Ent_rstr'],
                                    ['Ent_rstr', 'Op', 'Ent_rstr'],
                                    ['Exp', 'BinOp', 'MultOp'],
                                    ['Ent_rstr', 'BinOp', 'MultOp'],
                                    ['Exp', 'BinOp'],           #binary op
                                    ['Ent_rstr', 'BinOp'],         #binary op
                                    ['!', 'Exp', 'MultOp'],
                                    ['!', 'Ent_rstr', 'MultOp'],
                                    ['!', 'Exp'],
                                    ['!', 'Ent_rstr']
                                ], 
                    
                    'MultOp' : [    ['Op', 'Exp', 'MultOp'],
                                    ['Op', 'Ent_rstr', 'MultOp'],
                                    ['Op', 'Exp'],
                                    ['Op', 'Ent_rstr']
                                ],


                    'BinOp' : [     ['=\[', 'N', '\]'],       #minamx [binary op)
                                    ['\[', 'N', ':', 'N', '\]']   #substring (binary op)
                                ],

                    'Ent_rstr' : [  ['\\\\', 'Tag'],
                                    ['\\\\', '\$', 'Ent'],
                                    ['\\\\', '@', 'Ent'], 
                                    ['\\\\', '\*', 'Tag' ],
                                    ['\\\\', '&', 'Ent' ],
                                    ['\\\\', '\$', 'Tag', ':', 'Label'],
                                    ['\\\\', '\*', '<', '>', 'Tag', ':', 'Label'],
                                    ['\\\\', '<', '>', 'Tag', ':', 'Label']
                                ],

                    'Then' :    [[':', 'Command', 'Opt']],
                    
                    'Command' : [   ['satisfied'],
                                    ['comment', '\"', 'Msg','\"'],
                                    ['warn', '\"', 'Msg', '\"'],
                                    ['error','\"', 'Msg', '\"'],
                                    ['abort', '\"', 'Msg', '\"'],
                                    ['skip', 'N']
                                ],
                                     
                    'Opt' :     [   ['>?'],
                                    ['Elif'],
                                    ['Else']
                                ],
                                      
                    'Else' :  [[':', 'Command', '>?']],
                                      
                    'Elif' :  [['?:', '\(', 'Cond', '\)', 'Then']] #force whitespace between expression and ()
                    
                }

TypeTree = {}
TypeList = []
UnclassifiedTree= {}
UnclassifiedList = []
PhraseList = []
ulen = 0 


############################################
                 
def match_regex (regex, i):
    '''
        A helper function with essentially the same functionality 
        as re.match -- just provides a more concise form of 
        confirming whether expression i matches the regular expression 
        regex
    '''

    if re.match(regex, i):
        return True
    else:
        return False
                                          
######################################################

def check_regex(item):
    '''
    This helper function checks if item is defined in the 
    regex dictionary (True), and if it isn't, we return 
    False and the parser with just do a simple symbol match 
    with item.    
    '''
    
    try:
        if regex_dict[item]:
            return True
    except KeyError: 
        return False


#########################################################

def check_repeat(item):
    '''
    This helper function checks if item is in the global 
    list Repeat (which demarcates which regex terms 
    allow multiple tokens to fulfill it). Returns True if 
    item is in list and False if it is not.  
    '''
    
    for x in Repeat:
        if item == x: 
            return True
    
    return False 

##################################################


##############################################################

def update_TypeTree(token, ruleList, tree):
    '''
    updates the global "typetree", listing each entry as 
    subtype: [T/F, head]. All items are initially are set to 
    false except ROOTs, and then will be checked later with 
    tracePath, confirming that the subtype hierarchy does indeed work
    
    '''

    if token == 'TypeDef':
        new_type = ruleList[0]
        
        if len(ruleList) == 3:  #means blank, head of tree
            
            #global TypeTree
            TypeTree[new_type] = [True, 'ROOT']
            #update typelist 
            TypeList.append(new_type)
            
        else:
            
            head = ruleList[2]
            subtype = ruleList[0]
            
            if subtype in TypeTree.keys():
                print >> sys.stderr, " \nMulti-Inheritance detected, Type \"%s\" is not included in the type tree.\n" % (subtype, )
            else: 
                TypeTree[subtype] = [False, head]
        
    return 
                        
                    
###################################################################                    


def needs_sec_check(item):
    for x in Second_check: 
        if item == x: 
            return True 
    
    return False 

#############################################################   



def check_second_check(item, instance):
    
    if item == 'Typename':
        for x in TypeList: 
            if x == instance:
                return True 
            else: 
                continue 
        
        return False   
    
    elif item == 'Phrasename':
        for p in PhraseList: 
            if p == instance: 
                return True 
    
    #print >>sys.stderr, "%s is not a defined Phrase name or Type" % (instance,)
    return False 
            


######################################################
    
def parseGrammar (rulePred, start_sym):
    ''' The main parsing function and is recursive, 
        makes a copy of the token list in rulePred (stored to local), 
        and then goes through the global vocab_grammar. 
    '''
    
    #if rulePred == []: return False 
    
    local = rulePred
    tree = [] 
    key = start_sym
    rules = []
    n = 0
    count = 0
    

        
    try:
        
        if vocab_grammar[key]:
            rules = vocab_grammar[key]
            
            for rtuple in rules:
                
                tree = []
                tree.append([key, rtuple])
                local = rulePred
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
                        
            
        
    except KeyError:
        #regex most likely could not be matched 
        return False 
    
    
#############################################
def tracePath(subtype):
    '''
    Traces the path of a given subtype to a root, 
    thus confirming if it is indeed linked to a properly defined root 
    '''
    path = []
    sub = subtype
    head = TypeTree[sub][1]
    
    if head == 'ROOT':
        path = [sub]
        return path 
    
    elif head in TypeTree.keys():
        
        path = tracePath(head)
        
        if path != []:
            path.append(sub)
            return path
    else: 
        return []
    
###################################################

def loopCheck():
    pass

def check_multiInher():
    pass

def reachability_types():
    pass 


def check_types():
    
    
    
    types = TypeTree.keys()
    
    for t1 in types:
        if not TypeTree[t1][0]:
            
            path = tracePath(t1)
            if path != []:
                for link in path: 
                    if TypeTree[link][0]:
                        continue 
                    else:
                        TypeTree[link][0] = True 
                        TypeList.append(link)
            else: 
                continue 
        else:
            continue 
        
    
    #if any type still has "False" entry, it means no proper
    # path was discovered to the root, thus meaning the type
    # was in some way improperly defined, and so we remove it 
    # from the tree
    for t2 in types: 
        if not TypeTree[t2][0]:
            del TypeTree[t2]
        else:
            continue 
        
    return 
        
###########################################
               
def add_new_dict(subj, parsetree, dict):
    
    count = 0
    
    try:
        if dict[subj]:
            subj_entry = dict[subj]
            for x in parsetree:
                try:
                    if subj_entry[x[0]]:
                        count = 0
                        for w in subj_entry[x[0]]:
                            count += 1
                            if w != x[1] and count == len(subj_entry[x[0]]):
                                subj_entry[x[0]].append(x[1])
                            else: 
                                continue 
                            
                except KeyError: 
                    subj_entry[x[0]] = [x[1]]
    
    except KeyError: 
        subj_entry = {}
        for item in parsetree:
            subj_entry[item[0]] = [item[1]]
            
        
        
    
    return subj_entry       

###########################################################################

def tokenize_pred_string(pstring):
    '''
    Takes in the predicate string you wish to parse through, 
    and tokenizes it using the regular expression "Tokens."
    This is to separate symbols and operators from words and names. 
    Note that the longest match is desired here and is given preference when 
    going through the string. 
    
    Any whitespace encountered in the string is thrown out, 
    and if the string is successfully transformed, the list of 
    tokens is returned; otherwise, an empty list is returned or
    the program exits. 
    '''
    testStr = ''
    longestStr = ''
    tokenList = []
    count = 0
    tokens = re.compile('(:=|-=|\?<|:|;|\?:|>\?|.|\?|,|"|~>|=>>|<|>|[-_0-9a-zA-Z\']+|[+]|-|[*]|/|%|=|!=|<=|>=|=[[]|[\\\\][[]|[[]|[]]|[(]|[)]|!|&|[|]|[||]|&&|[\\\\$]|[\\\\]&|[\\\\\]@|[\\\\*]|[\\\\]|#)$')
   
    
    for n in pstring:
        count += 1
        if re.match('\s', n):                        #throwout whitespace -- but probs mean new token 
            if longestStr != '':
                tokenList.append(longestStr)
                longestStr = ''                 #clear longest string
                testStr = ''                    #clear test string 
            
        elif re.match('#', n): #or re.match('[[]', n): 
            #if come across comment , ignore it, at the end of fact and it's allowed to be there 
            if longestStr != '': 
                tokenList.append(longestStr)
                return ( tokenList, pstring[count:] )
                            
            
        else: 
            testStr += n
            
            if testStr == '=>':
                if pstring[count] == '>' : #next item in pstring
                    continue #dont go into block 
                                    
                
            
            if re.match(tokens, testStr):           #if match regex
                longestStr = testStr                #try to get longest match,
                
                if count == len(pstring):  #have reached last element in string
                    if re.match(tokens, testStr):
                        tokenList.append(testStr)
                    else:                           #couldn't tokenize 
                        print >> sys.stderr, 'Failed to tokenize rule with predicate: %s' %(pstring,)
                        exit(1)
                
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
    return (tokenList, [])


########################################################



def go_thru_file():
    '''
    Opens up the given file,  reads in line by line, and
    uses factotum lexer to go thru and find the subject and predicates
    '''
    #if len(sys.argv) < 2: 
     #   sys.stderr.write("must include vocabulary (.v) file \n")
      #  raise SystemExit(1)

    
    #vocabfile = open(sys.argv[1], 'r')
    
    vocabfile = open('test.v', 'r')
    
    facts = []
    line = ''
    line = vocabfile.readline()
    m = s = p =  r = c = ''
    px = []
    
    #sampled from factotum_entities 
    #READ IN LINES 
    
    while(len(line) > 0):
        my_fact = line[:-1]
        line = ''
        line = vocabfile.readline()
        
        while(len(line) > 0) and (line[0] == '-'):
            my_fact += '\n' + line[1:-1]
            line = ''
            line = vocabfile.readline()
            continue
        
        if my_fact != '':
            (m,s,p,px,r,c) = lex.breakup_fact(my_fact)
        
            p = p.strip() # get rid of whitespace
            facts.append([s,p])
    
    return facts

###############################################################

def firstPass(facts):
    
    #GO THROUGH RULES AND PARSE THEM 
    parsed = []
    failed = []
    
    global PassedThru 
    PassedThru = 0 
    
    for rule in facts:
        
        if rule[1] == '':           #skip any blank lines in vocab file 
            continue

        #TOKENIZE THE RULE
        (rule_pred, c) = tokenize_pred_string(rule[1])
        
        if rule_pred == []:         #if fails to tokenize, put in failed rules
            failed.append(rule)
            continue 
        
        #PARSE RULE
        if rule_pred[0] != '[': #all rules except type defs
            rule_parse =  parseGrammar(rule_pred, 'Start')
        else:                   #TypeDefs don't have subject in front, so diff handle
            rule_pred.insert(0, rule[0])
            rule_parse = parseGrammar(rule_pred, 'Start')
            
      
        #RESULT OF PARSE
        if rule_parse:                   #if true, means parsed successfully 
            parsed.append([rule[0], rule[1], rule_pred])
            if rule_pred[0] == '-=':                        #updating phrase list 
                PhraseList.append(rule[0])
        else:
            failed.append(rule)
    
    
    return [parsed, failed]
   
#########################################################

def second_pass():
    
    
    pass 


#############################################################

def parse_vocab():
    
    '''
    This is the acting main function of the parser, it reads in a given 
    vocabulary file (exits if not included), then extracts rules/facts from 
    the file using the method which I found in factotum_entities.py. Next, 
    using factotum_lex, I pull out the subject and predicate from each line, 
    and store them in a list of facts -- of the form (subj, pred).  
    
    After all this pre-processing, I have a for loop which  iterates through all 
    these pairs, tokenizes the predicate using  TOKENIZE_PRED_STRING, (note: 
    if it fails to do so properly, the rule is added to a list of failed facts), 
    and then feed the resulting list of tokens to PARSE_GRAMMAR.  If PARSE GRAMMAR 
    succeeds, I put the original rule, followed by it's parse tree into a list of 
    successfully parsed rules, otherwise, the rule gets aded to the list of failed facts. 
    
    '''
    facts = go_thru_file()
    
    rule_pred = ''
    parsed_rules = []
    failed_rules = []
    entries = []
    new_dict = {}
    second_parsed_rules = []
    
    #GO THROUGH RULES AND PARSE THEM 
    (parsed_rules, failed_rules) = firstPass(facts)
    
    #checktype tree
    check_types()
    
    
    for r in parsed_rules: 
    
        global PassedThru
        PassedThru = 1 
        second_pass = parseGrammar(r[2], 'Start') #r2 s rulepred 
        
        if second_pass: 
            second_parsed_rules.append([r[0], r[1], second_pass[0]])
            entries.extend(second_pass[0])
            new_entry = add_new_dict(r[0], second_pass[0], new_dict)
            new_dict[r[0]] = new_entry
        else: 
            failed_rules.append([r[0],r[1]])
        
        
       
    for n in second_parsed_rules:
        for i in range(len(n)):
            if i == 2:
                for z in n[i]:
                   print z
            else:
                print n[i]
        print '\n'
        
    print failed_rules
  
    #for x in new_dict:
     #   print x + ":"
      #  print x.__class__
       # for y in new_dict[x]:
        #    print "\t" + y + ":"
            
            #print y.__class__
             
    for x in TypeTree: 
        print x + ":"
        print TypeTree[x]
            
        
    return(parsed_rules, failed_rules, new_dict, TypeTree)

#########################################################


if __name__ == "__main__":
    parse_vocab()
    
                      
