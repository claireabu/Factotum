#!/usr/bin/python
# vi: ts=4 sw=4 et ai sm

false = 0
true  = 1
from string import *

# This module handles type information about entities

class GlobalClass:

    unique_num = 0
    current_subject = ''

#----------------------------------------------------------
 
    def __init__(self,parent=None):
        self.parent = parent
        return
        
#----------------------------------------------------------

    def unique_name( self ):
        self.unique_num += 1
        return( '$$' + ( '%08d' % self.unique_num ) )
    
#----------------------------------------------------------