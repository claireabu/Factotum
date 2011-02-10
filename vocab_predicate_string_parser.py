'''
Created on Jan 22, 2011

There was initally confusion on my part about 
what this parser should do.  For a while,  I believed 
that I would have to parse the different vocabulary 
facts (rules) entirely, and pull apart the 
different predicates.  However I soon realized/ was 
informed that the already present parser would do this, 
and all I had to parse was the string.  But the work 
I did do on the predicate parser is in the vocab_parser
file.  

Though I tried to look through factotum_lex to see 
how this indeed happens, I am still not entirely sure 
since after converting to Python3, errors with unicode persist. 

So here I take in the "string"  part of the predicate of a 
vocabulary rule and split it into the tokens, and label objects. 

@author: Claire
'''

from string import *


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


def split_up(self, stringObj):
    '''
    Split up the string to check if there are any labels
    or entities present. 
    
    '''
    res = stringObj.split()
    for ele in res:
        if ele[0]=="<":
            w = checkLabel(ele)
            if not w:
                print('error in label')
                return
    return
            
        
    

def check_Label(self, possile_Label):
    '''
    Checks to make sure label follows the correct format 
    between < > 
    '''
    pass

    
        

if __name__ == "__main__":
    pass 
    
        

        