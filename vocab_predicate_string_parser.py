'''
Created on Jan 22, 2011

There was initially confusion on my part about 
what this parser should do.  For a while,  I believed 
that I would have to parse the different vocabulary 
facts (rules) entirely, and pull apart the 
different predicates.

However I soon realized/ was 
informed that the already present parser would do this, 
and all I had to parse was the string.  But some of the remnants
of my work remain commented below

Though I tried to look through factotum_lex/entities to see 
how this indeed happens.

So here I take in the "string"  part of the predicate of a 
vocabulary rule and check the objects to make sure they are
of the correct format.

if more functionality is needed, it is quite feasible

@author: Claire
'''

from string import *
import sys
import factotum_lex

lex = factotum_lex.LexFacts()


labels = {'term': ['< >', 
                   '< label: >', 
                   '<: ttype_spec >', 
                   '< label: ttype_spec>'],
           'type': ['< type_name>',
                    '< label = type_name>'],
            'phrase': ['< phrase_name>',
                       '< label = phrase_name>'
                       ]
            }


#######################################################

def check_object( possile_obj):
    '''
    #--> if come across a label, make sure it's the correct format! 
    #Checks to make sure label follows the correct format 
    #between < > : retruns index of closing bracket
    
    '''

    #we already know starts with '<' since that's how we got in the function,
    #   so we can throw it away for now

    possible_label = possible_obj[1:]
    
    for n in range(len(possible_obj)):


        #
        # term <>
        #
        if possible_obj[n] == '>' and possible_obj[n+1] == ' ':       
            return n    #returns index of closing angle bracket


       

        elif i = possible_obj.index(':'):
            #
            # term  <:token-type-specification>
            #
            if possible_obj[n] == ':':
                possible_obj = possible_obj[n+1:]

                while possible_obj[n] != '>':
                    if possible_obj[n] in lowercase:
                        n = n+1
                    elif possible_obj[n] in uppercase:
                        n = n+1
                    elif possible_obj[n] in punctuation:
                        n = n+1
                    elif possible_obj[n] == '_':
                        n = n+1
                    elif possible_obj[n] == '-':
                        n = n+1
                    elif possible_obj[n] == '`':
                        n = n+1
                    elif possible_obj[n] in digits:
                        n = n+1
                    #elif possible_obj[n] in escaped symbol ??
                    #elif possible_obj[n] in infinity ??
                
                    else:
                        return -1 #fail if token type spec wrong

                    continue

                return n
            
            #
            # term <label:>
            #
            elif possible_obj[i+1] == '>':

                w = n

                while w < i:
                    if possible_obj[w] != ' ':
                        w = w + 1
                    else: #fail, whitespace in label
                        return -1
                    continue

                #otherwise, fine

                n = i + 1
                return n 
                    
            
            #
            # term <label: token-type-spec>
            #
            else:
                
                x = n
                
                while x < i:
                    if possible_obj[x] != ' ':
                        x = x+ 1
                    else: #fail, whitespace in label
                        return -1
                    continue

                # move past parentheses now 
                possible_obj = possible_obj[i+1:]
                n = i + 1

                
                while possible_obj[n] != '>':
                    if possible_obj[n] in lowercase:
                        n = n+1
                    elif possible_obj[n] in uppercase:
                        n = n+1
                    elif possible_obj[n] in punctuation:
                        n = n+1
                    elif possible_obj[n] == '_':
                        n = n+1
                    elif possible_obj[n] == '-':
                        n = n+1
                    elif possible_obj[n] == '`':
                        n = n+1
                    elif possible_obj[n] in digits:
                        n = n+1
                    #elif possible_obj[n] in escaped symbol ??
                    #elif possible_obj[n] in infinity ??
                
                    else:
                        return -1 #fail if token type spec wrong

                    continue

                return n

                
                
        #
        # type/ phrase <label = type-name> or < label = phrase-name> 
        #
        #

        elif i = possible_obj.index('='):

            k = possible_obj[n:i]
            k = k.strip() #make sure no whitespace on ends, can detect in middle 

            for z in range(len(k)):
                if k[z] == ' ':
                    return -1
                #else continue

            n = i+1
            
            possible_obj = possible_obj.lstrip()
            
            while possible_obj[n] != '>':
                
                if possible_obj[n] == ' ': #if whitespace, over
                    return -1
                else:
                    n = n+1


            if possible_obj[n] == '>':
                return n 
            
                
                
                
                
        # type/phrase <type-name> or <phrase-name> 
        #
        #

        else:
            possible_obj = possible_obj.lstrip()
            
            while possible_obj[n] != '>':

                if possible_obj[n] == ' ': #if whitespace, over
                    return -1
                else:
                    n = n+ 1


            if possible_obj[n] == '>':
                return n

            
    return -1 

###########################################################

def check_rule(rule, success, problems):

    pred = rule[1]
    
    n = 0
       #adjusting starting position
    
    if pred[0] == ':' or '-' or '~':     #eg if it starts with:
        pred = pred[2:]                         # :=, -=, ~>,

    if pred[0] == '=':                  #or =>>
        pred = pred[3:]

    imply_count = 0
    
    while n < len(pred):

        if pred[n] == '<':          #some sort of label is involved
            indx = check_object(pred)
            if indx == -1: # bad
                problems.append(rule)
                return
            else:
                pred = pred[indx+1:]                #adjust 
        
            
        elif pred[n] == '~' :#encountered tag imply, can only happen once
            if imply_count == 1:
                #bad
                problems.append(rule)
                return
            else: #things are good
                pred= pred[n+2:]
                imply_count =  1
        
        
        pred = pred.strip()
        n = n + 1
        continue


    success.append(rule)
    return 
                        
        
        
        

        
    


#############################################################


def parse_vocab():
    
    '''#take in vocab file
       #read line by line (one rule per line)
       
    '''
    if len(sys.argv) < 2:
        sys.stderr.write("must include vocabulary (.v) file")
        raise SystemExit(1)

    
    vocabfile = open(sys.argv[1], 'r')

    facts = []
    line = ''
    line = vocabfile.readline()

    #sampled from factotum_entities 

    while(len(line) > 0):
        my_fact = line[:-1]
        line = ''
        line = vocabfile.readline()

        while(len(line) > 0) and (next_line[0] == '-'):
            my_fact += '\n' + line[1:-1]
            line = ''
            line = vocabfile.readline()
            continue

        if my_fact.strip(my_fact) == "": continue
        ##not sure excatly why this is there

        (m,s,p,px,r,c) = lex.breakup_fact(my_fact)

        p = p.strip() # get rid of whitespace

        facts.append([s,p])


    correct_rules = []
    problematic_rules = []
    
    for n in range(len(facts)):
        check_rule(facts[n], correct_rules, problematic_rules)

        

     

if __name__ == "__main__":
    parse_vocab() 
    
    






'''             




#########################################################

def split_up(stringObj):
    '''
    #Split up the string to check if there are any labels
    #or entities present. 
    
    '''
    res = stringObj.split()
    for ele in res:
        if ele[0]=="<":
            w = checkLabel(ele)
            if not w:
                print('error in label')
                return
    return
            
        
'


#########################################################

    



def label_type_bool (label):
    pass
'


#########################################################


def check_type_tree (rule):
        '''# if come across a vocab rule that defines
            #a type tree, take care of it here.
        '''
        pass



#########################################################


def check_condition_expression (restr_rule_cond):
    ''' #if come across a fact restriction rule,
        #check the condition/expression here
    '''

    cond = restr_rule_cond.split()

    if cond[0] == '(' and cond[len(cond)-1] == ')':     #if expression has to have parentheses


    
        if cond[1].__class__ == str:

            if check_string_ops(cond[2]):
                

            if check_entity_restr(cond[1]):


                   #if nothing after operation:
                                        #bad return False.
                
                    

        if cond[1].__class__ == int:
                
                for x in range(len(operations_arith)):
                    #check for arith ops + range test

        
                


            
          
               
    ]
            
            
    #check if label is a type
    #check if label matches one anything
    #check if expression begins with (




    #check ends in ) 
    


    pass
 
    


#########################################################


    


def check_string_ops (op_in_question):

    if op_in_question == '=':
        return True

    elif op_in_question == '!=':
        return True

    elif op_in_question == '<':
        return True

    elif op_in_question == '<=':
        return True

    elif op_in_question == '>':
        return True

    elif op_in_question == '>=':
        return True

    elif op_in_question[0] == '[': #substring
        if op_in_question[1].__class__ == str:
            if op_in_question[2] == ':':
                if op_in_question[3].__class__ == int or int(op_in_question[3]):
                    if op_in_question[4]== ']':
                        return True    
                
    
    else
        return False

    return False 
    


#########################################################    

        

def check_arith_ops (op_in_question):

    if op_in_question == '+':
        return True

    elif op_in_question == '-':
        return True

    elif op_in_question == '*':
        return True

    elif op_in_question == '/':
        return True

    elif op_in_question == '%':
        return True

    elif op_in_question == '=':
        return True

    elif op_in_question == '!=':
        return True

    elif op_in_question == '<':
        return True

    elif op_in_question == '<=':
        return True

    elif op_in_question == '>':
        return True

    elif op_in_question == '>=':
        return True


    elif op_in_question[0] == '=':                  #  #'=[min, max]'
        if op_in_question[1]== '[':
            
            if op_in_question.index(','):
                indx = op_in_question.index(',')
                
                if op_in_question[2:indx].__class__  == int or int(op_in_question[2:indx]):
                    
                    if op_in_question.index(']'):
                        end = op_in_question.index(']')
                        
                        if op_in_question[indx+1:end].__class__ == int or int(op_in_question[indx+1:end]):
                            
                            if op_in_question[indx+1:end] > op_in_question[2:indx]:
                                
                                return True    
                
    
    else
        return False

    return False 
    


#########################################################
    

def check_entity_restr (ent_rst):
    ''' #in restr rule, check to see if entitiy reference present
       # in expression
    '''
    if ent_rst.find('\\$'

'


#########################################################


def check_commands (restr_rule_cmd):
    '''# in restr rule, checks to make sur it's a
       # valid command format
    '''

    # split command by whitespace once: get the command and then
    #   the possible message 
    
    command = restr_rule_cmd.split(' ', 1)
    
    if command[0] == 'satisfied':
        return True
    
    elif command[0] == 'comment' and command[1].__class__ == str:
        return True
        
    elif command[0] == 'warn' and command[1].__class__ == str:
        return True
    
    elif command[0] == 'error' and command[1].__class__ == str:
        return True
    
    elif command[0] == 'abort' and command[1].__class__ == str:
        return True 
    
    elif command[0] == 'skip' and command[1].__class__ == int:
        return True 
             
      
    else:
        return False

'


#########################################################


def check_fact_restr( rule):
    '''# if come across a rule that's a fact restriction (eg if/else block),
        #take care of it here
    '''
    pass 
'


#########################################################


def parse_vocab():
    '''#take in vocab file
       #read line by line (one rule per line)
       
    '''
    pass
        

if __name__ == "__main__":
    pass 
    
        
'''
        
