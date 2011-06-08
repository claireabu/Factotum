import string
import sys
'''
@author Claire 
PULLVOCAB.py pulls out 'possible vocabulary' section from results of mkvocab.py 
''''
def getVocab():

    if len(sys.argv) < 2:
        print 'NO FILE WAS PROVIDED' 
        return
    else: 
        orig_vfilename = sys.argv[1]

    
    orig_vfile = open(orig_vfilename, 'r')
    orig_vocab = orig_vfile.read()
    orig_vfile.close()

    if orig_vocab == '':
        print 'ORIG VOCAB EMPTY'
        return
    else:
        note = 'Possible Vocabulary:'
        res = orig_vocab.find(note)
        
        if res == -1:
            print 'COULDN\'T FIND NOTE'
            return
        else:
            vocab = orig_vocab[res+len(note):]
            vocab = vocab.strip()

        cleanv = open('_wikidata_.v', 'a')
        cleanv.write(vocab)
        cleanv.close()
        return



if __name__ == '__main__':
    getVocab()
    
            
    
