'''
Created on May 26, 2011
takes vocabulary rules produced by mkvocab.py 
@author: Claire
'''


import string 
import sys


VDICT = {}

def getGreatest(miniD):
    ''' Finds the most common capitalization (represented by the counts stored in 
    the entry in the dictionary).  If there is only a single entry, then obviously that is
    the most common version.  However if there are versions that are tied for the most common, 
    I just use the first one encountered because there is no easy way to tell which is the best one.  
    ##NOTE : POTENTIAL PROBLEM IN ACTUAL FACTS WHEN THERE ARE MULTIPLE VERSIONS PRESENT 
    '''
    
    if len(miniD) > 1: 
        highestCount = 0
        mostCommonstr = ''
        ties = []
        versions = miniD.keys()
    
        for v in versions: 
            
            localCount = miniD[v]
            if localCount > highestCount: 
                highestCount = localCount
                mostCommonstr = v
                ties = []
            elif localCount == highestCount: 
                ties.append(mostCommonstr)
                ties.append(v)
            else: 
                continue 
            
        if ties != []: 
            mostCommonstr = ties[0]
            
    else:       #if only one entry, then don't have to worry about different versions 
        p = miniD.popitem()
        mostCommonstr = p[0]
    
    
    return  mostCommonstr
        
    

def firstPass(vocab):
    #str.lower()
    for orig in vocab: 
        vlower = orig.lower()
        if VDICT.get(vlower):
            mini = VDICT[vlower]
            if mini.get(orig):
                mini[orig] += 1
            else: 
                mini[orig] = 1
            
        else: 
            VDICT[vlower] = {orig: 1}
    
    return 

def secondPass():
    ''' Go through the built up VDICT and see which versions have the highest counts, 
    storing the one with the highest in the string 'unified' and subsequently adding it 
    to a modified vocabulary list @mvocab. However, the other versions are stored in another 
    dictionary called record.   
    '''
    mvocab = []
    record = {}
    
    for vlower in VDICT: 
        if vlower == '':
            continue
        mini = VDICT[vlower]
        unified = getGreatest(mini)
        mvocab.append(unified)
        if mini != {}:
            for v in mini: 
                if record.get(unified):
                    record[unified].append(v)
                else: 
                    record[unified] = [v]
        
    
    return mvocab, record 


def capMain():
#    ''' Argument passed through command line is the name of the vocab file, which
#    is opened, and each line is read and subsequently stored as an item in the list 
#    'vocab' in which 
#    '''
#    if len(sys.argv) < 2: 
#        sys.stderr.write("must include vocabulary (.v) file \n")
#        raise SystemExit(1)
#    else: 
#        vfileName = sys.argv[1]
    vfileName = '_wikidata_.v'
    vfile = open(vfileName, 'r')
    
    
    vocabLi = []
    rule = vfile.readline()
    
    while rule != '':
        rule = rule.strip()
        if rule != '\n' or rule != '':
            vocabLi.append(rule)
        rule = vfile.readline()
        
    vfile.close 
    
    firstPass(vocabLi)
    modVocab, recordOfVers = secondPass()
    modVocab.sort()
    
    vmodname = '_wikidata_.v'
    vmod = open(vmodname, 'w')
    
    for m in modVocab: 
        vmod.write(m) 
        vmod.write('\n')
            
    vmod.close()
    
    print 'VERSIONS of CAPITALIZATION'
    for r in recordOfVers: 
        print r
        for v in recordOfVers[r]: 
            print v
        print '\n'
#        
    return vmodname, modVocab, recordOfVers


if __name__ == "__main__":
    capMain()
    