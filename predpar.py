''' Pred Parser

'''

from string import *
import sys
import re
import factotum_lex
import factotum_globals

lex = factotum_lex.LexFacts()
g = factotum_globals.GlobalClass()



#word
Words = re.compile('^[.,:\-_\';0-9a-zA-Z\(\)\200-\377/]+$')
EndPhrase = re.compile('[."]')

#objs
Label = re.compile('^[-_0-9a-zA-Z\']+$')
Ttypespec = re.compile('^[-_0-9a-zA-Z\'\?.,;]+$')     #note: left out infinity 
Typename = re.compile('^[-_0-9a-zA-Z\']+$')           #couldn't find def: used same as label 
Phrasename = re.compile('^[-_0-9a-zA-Z\']+$')         #couldn't find def: used same as label

#exp
Exp = re.compile('^[a-zA-Z]+$|^[0-9]+$')      #numbers or strings 
Op = re.compile('^([+]|-|[*]|/|%|=|!=|<=|>=|<|>|&|[|]|[||]|&&)$') #left out # <label>, {label} 
Ent = re.compile('^([-_0-9a-zA-Z]+| \D+)$')          
Tag = re.compile('^[-_0-9a-zA-Z]+$') 

#msg
Msg = re.compile('^([:\-_\';,.\?a-zA-Z0-9]+)$' )

#N
N = re.compile('^[0-9]+$')

Repeat = [Words, Msg]

              
vocab_grammar = { 'Start' : ['Pred'],
                 
                 'Pred' :  [       
                                    (':=', 'Phrase' ),
                                    ('-=', 'Phrase' ),
                                    ('~>', 'Phrase' ),
                                    ('=>>', 'Phrase' ),
                                    ('\?<', '\(', 'Cond', '\)', 'Then', ), 
                                    ( 'Phrase')
                                    
                                ],
                    
                    'Phrase' : [    ( 'Obj', Words, 'Phrase' ),
                                    ( '\"', 'Obj', Words, 'Phrase', '\"', '.' ),
                                    ( 'Obj', Words),
                                    ('\"', 'Obj', Words, '\"', '.')
                                    
                                              
                                ],
                    
                    
    
                    'Obj' :     [   ('<' , '>', 'Obj'),
                                    ('<', '>'),
                                    ('<' , Label, ':',  '>'),
                                    ('<' , ':', Ttypespec, '>'),
                                    ('<' , Label, ':', Ttypespec, '>'),
                                    ('<' , Typename, '>'),
                                    ('<' , Label, '=', Typename, '>'),
                                    ('<' , Phrasename, '>'),
                                    ('<' , Label, '=', Phrasename, '>')
                                ], 

                                #note: not allowing more than one operation per condition 
                    'Cond' :    [   (Exp, Op, Exp ),
                                    ('Ent_rstr', Op, Exp ),
                                    (Exp, Op, 'Ent_rstr'),
                                    ('Ent_rstr', Op, 'Ent_rstr'),
                                    (Exp, 'BinOp'),           #binary op
                                    ('Ent_rstr', 'BinOp'),         #binary op
                                    ('!', Exp),
                                    ('!', 'Ent_rstr')
                                ], 


                    'BinOp' : [     ('=\[', N, '\]'),       #minamx (binary op)
                                    ('\[', N, ':', N, '\]')   #substring (binary op)
                                ],

                    'Ent_rstr' : [  ('\\\\', Tag),
                                    ('\\\\', '\$', Ent),
                                    ('\\\\', '@', Ent), 
                                    ('\\\\', '\*', Tag ),
                                    ('\\\\', '&', Ent ),
                                    ('\\\\', '\$', Tag, ':', Label),
                                    ('\\\\', '\*', '<', '>', Tag, ':', Label),
                                    ('\\\\', '<', '>', Tag, ':', Label)
                                ],

                    'Then' :    [(':', 'Command', 'Opt')],
                    
                    'Command' : [   ('satisfied'),
                                    ('comment', '\"', Msg,'\"'),
                                    ('warn', '\"', Msg, '\"'),
                                    ('error','\"', Msg, '\"'),
                                    ('abort', '\"', Msg, '\"'),
                                    ('skip', N)
                                ],
                                     
                    'Opt' :     [   ('>?'),
                                    ('Elif'),
                                    ('Else')
                                ],
                                      
                    'Else' :  [':', 'Command', '>?'],
                                      
                    'Elif' :  ['?:', '\(', 'Cond', '\)', 'Then'] #force whitespace between expression and ()
                    
                }

############################################
                 
def match_regex (regex, i):
    '''
        A helper function with essentially the same functionality 
        as re.match -- just provides a more concise form
    '''

    if re.match(regex, i):
        return True
    else:
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
                
                if  len(rtuple) > 1 and rtuple.__class__ == tuple:   #multiple options in grammar rule 
                    
                    for token in rtuple:
                        count += 1
                        
                        try: 
                            if vocab_grammar[token]: 
                                res = parseGrammar (local[n:], token)
                                if res: 
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
                                if  match_regex(token, local[n]):
                                    #add to tree?
                                        n += 1
                                        
                                        for item in Repeat: 
                                            if token == item: 
                                                if n < len(local)-1:
                                                    while (match_regex(token, local[n])):
                                                        if n < len(local)-1:
                                                            n += 1
                                                        else: 
                                                            break
                                                    break
                                                else:
                                                    return(tree, local[n:])
                                            
                                        if count == len(rtuple) :
                                            return(tree, local[n:])
                                         
                                          
                                        else: 
                                            continue 
                                    
                                else:                       #no tokens don't match in tuple
                                    break                   #break out of token loop, continue to next tuple
                            else:
                                break
                        
                            
                            
                else: ####Only one item-- don't want to iterate thru the string 
                    try:
                        if vocab_grammar[rtuple]:
                            res = parseGrammar(local[n:], rtuple)
                            if res:
                                tree.extend(res[0])
                                local = res[1]
                                return(tree, local)
                        else:
                            return False
                        
                    except KeyError:
                        
                        if n < len(local):
                            if  match_regex(rtuple, local[n]):       
                                #add to tree?
                                n += 1
                                
                                for item in Repeat:
                                    if rtuple == item:
                                        if n < len(local)-1:
                                            while (match_regex(rtuple, local[n])):
                                                if n < len(local)-1:
                                                    n += 1
                                                else:
                                                    break
                                            break
                                        
                                        
                                return(tree, local[n:]) 
                            
                            else:                       #only item in tuple doesn't match 
                                continue                    #break out of tuple loop
                        
            
        
    except KeyError:
        #regex most likely could not be matched 
        return False 
    
    
#############################################
               


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
            
        elif re.match('#', n) or re.match('[[]', n): 
            #if come across comment or citation, ignore it, at the end of fact and it's allowed to be there 
            if longestStr != '': 
                tokenList.append(longestStr)
                return( tokenList, pstring[count:] )
                
            
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

    if len(sys.argv) < 2: 
        sys.stderr.write("must include vocabulary (.v) file \n")
        raise SystemExit(1)

    
    vocabfile = open(sys.argv[1], 'r')
    
    #vocabfile = open('res_lingdata.v', 'r')
    
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

        (m,s,p,px,r,c) = lex.breakup_fact(my_fact)
        
        p = p.strip() # get rid of whitespace
        facts.append([s,p])
    
    rule_pred = ''
    parsed_rules = []
    failed_rules = []
    
    #GO THROUGH RULES AND PARSE THEM 
    
    for rule in facts:
        
        if rule[1] == '':           #skip any blank lines in vocab file 
            continue
        
        (rule_pred, c) = tokenize_pred_string(rule[1])
        
        if rule_pred == []:
            failed_rules.append(rule)
            continue 
        
        rule_parse =  parseGrammar(rule_pred, 'Start')
        
        if rule_parse:                   #if true, means parsed successfully 
            parsed_rules.append([rule[0], rule[1], rule_parse[0]])
        else:
            failed_rules.append(rule)
        
    for n in parsed_rules:
        for i in range(len(n)):
            if i == 2:
                for z in n[i]:
                    print z
            else:
                print n[i]
        print '\n'
        
    print failed_rules
        
    return(parsed_rules, failed_rules)

#########################################################


if __name__ == "__main__":
    parse_vocab()
    
                      
