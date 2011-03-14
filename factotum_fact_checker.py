
''' FACT_CHECKER
python tool, "checking facts for vocabulary consistency"

(from paper)
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
import factotum_entities
import factotum_lex
import vocab_predicate_string_parser 
import sys 
from string import *

full_ent = factotum_entities.EntityClass()


    
####################################################

def prelim_check_facts(fact_file):
        
        ''' run buildentities over fact file
            organize by subject, have predicates for each subject 
            return this data struct organized by subjects and predicate:
                ent is a a dictionary with the subject as key and full sentence predicates
                as 
        '''
        
        full_ent.build_entities(fact_file)

        # for every subject in full_ent, want to extract subject and just predicate,
            #note: predicate is 3rd item in the 8-tuple

        ent = {}
        subj_list = full_ent.keys()

        
        for n in range(len(subj_list)):
            
            for fact_num in range(len(full_ent.entities[subj_list[n]])):
                if fact_num == 0:
                    ent[subj_list[n]] = list(full_ent.entities[subj_list[n]][fact_num][3])
                else:
                    ent[subj_list[n]].append(full_ent.entities[subj_list[n]][fact_num][3])
                                                #note, 3 is the string pred

                
        del full_ent 

        return ent 
                
        

####################################################

            
def prelim_check_vocab(vocab_file):
        ''' run parser over vocab file.
            make sure vocab rules all follow factotum format,
                 if fine: put into rule data struct, [organized by subjects/?? is that
                 even possible??] 
                 else if problem: don't include rule, warning message and put in sep list
        '''
        succ_rules = []
        fail_rules = [] 
        [succ_rules, fail_rules]  = parse_vocab(vocab_file)

       # print ("Problematic Rules") 
       # print (rules['Problematic']) #make prettier 

       # print ("Correct Rules")
       # print (rules ['Correct']) #make prettier 
                        
        return succ_rules

####################################################

def get_entity_vocab_rules(ent, rules):

        ent_rules = []
        
        for n in rules:
            if n[0] == '*':                  #if subject is unique name or matches
                ent_rules.append(n[1:])          #entity, then use rule
            elif n[0] == ent:
                ent_rules.append(n[1:])
            else:
                continue
            
        return ent_rules
            


####################################################

    
def tokenize (desired_string ):
        
        ''' go through predicate.
            sort out token by token --> put in list?.
        '''
        return desired_string.split()
        
        


####################################################

def deal_imply_rule (imply_rule, fact):

        #add to internal structure somehow
        
        pass

            
    
####################################################

def deal_gen_rule (gen_rule, fact):

        # add new rule to internal strucutre
        pass



####################################################

def deal_rule_restr (rule):
        #deal with conditionals and expressions
        pass

####################################################


def token_is_objtype (rule_token):
        '''check if rule token is <type>/object or if just normal
        '''
        if rule_token.find('<') and rule_token.find('>'):
            return True
        else:
            return False

####################################################


def assign_objType (rule_token, fact_token):
        ''' if rule token is <type>, mark in internal struct
            that the fact_token is object of this type
        '''
        pass

####################################################

    
def check_entity (ent, ent_preds, ent_rules):

        problematic_facts=[]
        fine_facts = []
        current_fact = []
        current_rule = []

        # go through facts in entity (loop)
        for n in range(len(ent_preds)):    

            # (break fact pred into tokens--> tokenize_predicate)
            current_fact = tokenize(ent_preds[n]) 
            
               # go through vocab rules (loop)
               for k in range(len(ent_rules)):
               
                   #break up rule into tokens
                   current_rule = tokenize(ent_rules[k])
                   
                   for j in range(len(current_fact)): 

                       for i in range(len(current_rule)):

                           if current_rule[i] == '~>':
                               deal_imply_rule(current_rule, current_fact)
                            elif current_rule[i] == '=>>':
                                deal_gen_rule(current_rule, current_fact)
                            elif current_rule[i] == '?<':
                                deal_rule_restr(current_rule, current_fact)
                            else: #   else: go through tokens of rule (rules starting with nothing,

                                if current_rule[i] == ':=' or '-=':
                                    current_rule[i+1]
                                    i =  i+1

                                if token_is_objtype(current_rule[i]):
                                    assign_Objtype(current_rule[i], current_fact[j])

                                #tokens all match, and at end of fact and rule
                                elif current_fact[j] == current_rule[i] and
                                        j + 1 == len(current_fact) and
                                        i + 1 == len(current_rule):
                                            fine_facts.append(current_Fact)
                                            k  = len(ent_rules) + 2     # get out of k for loop,
                                                                        # can move onto next fact
                                                 
                                                 
                                elif len(current_fact) != len(current_rule): #don't match on length
                                    i = len(current_rule) + 2 # get out of i for loop
                                                                #so can move onto next rule

                                elif current_fact[j] == current_rule[i]:
                                    #good
                                    continue #???

                                elif k+1 == len(ent_rules): # dont have match yet & at end of rules
                                        print("error with fact:" + current fact)
                                        problematic_facts.append(current_fact)

                                                                        
                                        
    return (fine_facts, problematic_facts) 

####################################################

def fcheck():  
'''
prelim_check_facts --> entities

prelim_check_vocab --> rules

loop though enities
    check_entity( entity, get_entity_specific_rules(entity, rules).
    
    
'''
    if len(sys.argv) < 3:
        sys.stderr.write("Both Fact file (.f) and Vocabulary file (.v) must be entered")
        raise SystemExit(1)
    
    factfile = open(sys.argv[1], 'r')
    vocabfile = open(sys.argv[2], 'r')

    entities = prelim_check_facts(factfile)
    rules = prelim_check_vocab(vocabfile)

    factfile.close()
    vocabfile.close()

    ent_list = list(entities)
    
    for n in ent_list:
        entity_rules = get_entity_vocab_rules(ent_list, rules)
        entity_preds = entities[ent_list]
        check_entity(ent_list, entity_preds, entity_rules)
        
     #for now checking, internal structure tbd    

    
    
    
pass

if __name__ == "main":
    fcheck()
    

