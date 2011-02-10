'''
Created on Jan 22, 2011

@author: Claire
'''

class VocabRules:
    '''
    classdocs
    '''
    #need to get grammar rules into a dictionary
    v_rules = {"start": [("y","x"),
                         ("w","x"), 
                         ("l", "y", "r"), 
                         ("p", "n"), 
                         ("y", "i", "x"), 
                         ("g") 
                         ("f","z","t")],
             "y":["", "tag"],
             "x": ["string"],
             "w": ["-=", ":="],
             "l": [ "[" ],
             "r": [ "]" ],
             "p": ["%"],
             "n": ["", "#"],
             "i": ["~>"],
             "g": ["->>"],
             "f": ["?<"],
             }
    
    def __parseIfBlock__(self, eles):
        return
        
        
    def __parseRule__ (self, starting_rule, all, tokens):
        
        count = 0
        res = ""
        
        for t in tokens:
            for nonterm in starting_rule:
                for term in all[nonterm]:
                    count = count + 1
                    if term == t:
                        break #how to represent parse?
                    elif count == len(all[nonterm]):
                        return [] #false
                    # if have reached end of nonterminal poss, and no match -- fail
                
                    
                    
             
            
          
    
    def __dealWithEmptyString__(self, nonterm, rule):
        #basically pass to parse rule a starting rule without the first nonterm (empty)
        #and also pass a different one with it in it
        return 
        
    #parse rule
    #if rule doesnt parse, should call check vocab again, but this time remove
    #the rule you have already tried from the dictionary of all_rules
    def __checkVocab__(self, tokens, all_rules):
        #take in whatever lexer outputs -- stream? lines? of tokens
        #take in first token
        #iterate thru start rules
        
        if tokens[0] == all_rules["f"]:     #check if it's an if block, have a diff function to deal
            parseIfBlock(tokens) 
        else:  
            start_rules = all_rules["start"]
            
            for rule in start_rules:  #rule is a tuple in the list of start rules
                
                for nonterm in rule: #each item in the rule tuple 
                                            
                        for term in all_rules[ nonterm ]: #look up nonterm in dictionary
                            
                            if term == "": #check if can go to empty string 
                                dealWithEmptyString(nonterm, rule )
                                
                            elif term == tokens[0]: 
                                if parseRule(rule) 
                                    return parseRule(rule, tokens)
                                else:
                                    start_rules.remove(rule)
                                    break
                            else: 
                                #have reached END of that non-terminal and no match, get rid of rule
                        
                                 
                            
                
                         
                                    
                                    
                                        
                            
                            
                                
                            
                                
                            #first try without the empty (eg non-empty option)
                   
                #then try with empty (aka go to next symbol in that start rule) 
                    
            
                    #if that rule can go to empty, first try wihtout empty
                    #if match then continue through token list
                    #else try with empty
                    #else go to next start rule
            
            #if matches: 
                #if goes to if-then block: go to specified function for if-then
                #match-- break out of this block 
            #if doesnt match
                #if no more start rules -- send error message
                #else go to next start rule 
        
            
                            
    
             
             
             

    def __init__(selfparams,tokens):
        '''
        Constructor
        '''
        checkVocab(tokens, v_rules)
        

if __name__ == "__main__":
    
        

        