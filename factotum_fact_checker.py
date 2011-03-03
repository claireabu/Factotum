
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
import sys 
from string import *

full_ent = factotum_entities.EntityClass()

# take in vocab file
# take in fact file


    
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
                
        #PROBLEM: need to remove comments?

####################################################

            
    def prelim_check_vocab(vocab_file):
        ''' run parser over vocab file.
            make sure vocab rules all follow factotum format,
                 if fine: put into rule data struct, organized by subjecs
                 else if problem: don't include rule, warning message and put in sep list
        '''

        
        pass

####################################################


    def tokenize_predicate (entity_pred):
        
        ''' go through predicate.
            sort out token by token --> put in list?.
        '''
        
        pass

####################################################


    def get_entity_vocab_rules (ent, rules):
        ''' go through vocab rules, and get rules
            that pertain only to requested entity
        '''

        pass  

####################################################

    
    def check_imply_rule (rule_pred):
        '''take in rule prediate for the entity in question,
           check if contains ~> 
        '''
        for x in range(len(rule_pred)):
            if rule_pred[x] == '~':
                if rule_pred[x+1] == '>':
                    return True
        return False

####################################################

    def deal_imply_rule (imply_rule, fact, fact_db):
        
        pass

####################################################

    def check_generate_rule (rule_pred):
        '''take in rule predicate for the entity in question,
           check if it begins with =>>
        '''
        for x in range(len(rule_pred)):
            if rule_pred[x] == '=':
                if rule_pred[x+1] == '>' and rule_pred[x+2] == '>':
                    return True

        return False
                    
            
    
####################################################

    def deal_gen_rule (gen_rule, fact):
        pass

####################################################

    def check_rule_restr (rule_pred):
        ''' take in rule predicate for entity in question,
            check if it begins with ?<
        '''
        for x in range(len(rule_pred)):
            if rule_pred[x] == '?':
                if rule_pred[x+1] == '<':
                    return True
        return False    


####################################################

    def deal_rule_restr (rule):
        pass

####################################################


    def token_is_type (rule_token):
        '''check if rule token is <type> or if just normal
        '''
        pass

####################################################


    def assign_objType (rule_token, fact_token):
        ''' if rule token is <type>, mark in internal struct
            that the fact_token is object of this type
        '''
        pass

####################################################

    
    def check_entity (ent, ent_preds, ent_rules):

        
        ''' go through facts in entity (loop)
                (break fact pred into tokens--> tokenize_predicate) 

                go through vocab rules (loop)       
                    
                    match rule
            
                        if check_imply_rule: deal_imply_rule
                
                        elif check_gen_rule: deal_generate_rule
                
                        elif check_rule_restr: deal_rule_restr
                
                        else: loop through tokens of rule (rules starting with nothing, :=, -=):

                                -->#make sure num of tokens in rule & fact match, and if
                                don't then problem

                                
                                loop through tokens of fact: 
                                                                
                                if rule token_is_type: assignObjType, goto next token (both)
                                
                                elif rule_token matches fact_token: good!, add to internal struct

                                else: goto next rule 

                                #if run out of rules before fact is added to internals struct,
                                # (e.g. no match), then put fact in "bad facts" category 
                                 


        '''


       
        
        pass

####################################################

def fcheck():  
'''
prelim_check_facts --> entities

prelim_check_vocab --> rules

loop though enities
    check_entity( entity, get_entity_specific_rules(entity, rules).
    
    
'''
    if len(sys.argv) != 2:
        sys.stderr.write("Both Fact file (.f) and Vocabulary file (.v) must be entered")
        raise SystemExit(1)
    
    factfile = open(sys.argv[1], 'r')
    vocabfile = open(sys.argv[2], 'r')

    entities = prelim_check_facts(factfile)
    rules = prelim_check_vocab(vocabfile)

    factfile.close()
    vocabfile.close()

    ent_list = list(entities)
    
    for n in range(len(entity_list)):
        entity_rules = get_entity_vocab_rules(ent_list[n], rules)
        entity_preds = entities[ent_list[n]]
        check_entity(entity_list[n], entity_preds, entity_rules)
        
     #for now checking, internal structure tbd    

    
    
    
pass

if __name__ == "main":
    fcheck()
    

