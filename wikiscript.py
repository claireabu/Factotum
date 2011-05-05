import urllib2
import sys
from string import *


Subject = ""
maxlenHeading = 8 
#rank? #extinction?
headings_main = ['Pronunciation', 
                 'Created by', 
                 'Spoken in' , 
                 'Signed in',
                 'Date founded',
                 'Setting and usage' , 
                 'Region', 
                 'Extinct language',
                 'Language extinction',
                 'Total speakers',
                 'Total signers' , 
                 'List of languages by number of native speakers',
                 'Ranking',
                 'Category (purpose)',
                 'Language family', 
                 'Standard forms',
                 'Dialects',
                 'Writing system',
                 'Category (sources)',
                 'List of language regulators',
                 'Regulated by', 
                 'Native-name'
                 ]

headings_off = [
                'Official language in',
                'Recognised minority language in',
                'List of language regulators',
                'Regulated by'
                ]

headings_codes = ['Language codes',
                  'ISO 639-1',
                  'ISO 639-2',
                  'ISO 639-3',
                  'Linguasphere Observatory',
                  'Linguasphere'
                 ]

def writeFacts(facts):
    #file = sys.argv[2]
    pass

##############################
def cleanUpFact(x):
    z = x.strip(':')
    z = z.strip()
    
    if z.find('::') != -1:
        z = z.replace('::::', '::')
        z = z.split('::')
        
    return z

####################################################################
def parse_mainSection(lang_str):
    
    pull_part = lang_str.split(' ',1)
    lang_name = pull_part[0]
    rem = pull_part[1]
    
    Subject = lang_name 
    headings = []
    pts = []
    
    for h in headings_main:
        try: 
            indx = rem.index(h)
            headings.append(h)
            pts.append(indx)
            
        except: 
            if h == 'Native-name':
                headings.insert(0,h)
                pts.insert(0,0)
            else: 
                continue
    i = 0 
    facts = {}
     
    for spec in headings:  
        start = pts[i]
        if i == len(headings)-1:
            facts[spec] = rem[start:]
        else:
            end = pts[i+1]
            facts[spec] = rem[start:end]
        #some clean up 
        facts[spec] = facts[spec].replace(spec, '')
        facts[spec] = cleanUpFact(facts[spec])
    
        if facts[spec] == 'see below':
            del facts[spec]
        i += 1
        
    writeFacts(facts)
    
    return 

####################################################################

def parse_OfficialStatusSection(off_str):
    '''own section, don't have to worry where starting'''

    off_str = off_str.replace('Official status', '')
    pts = []
    headings = []
    
    for o in headings_off:
        try: 
            indx = off_str.index(o)
            headings.append(o)
            pts.append(indx)
        except: 
            continue
    
    i = 0 
    facts = {}
    for title in headings: 
        start = pts[i]
        
        if i == len(headings) - 1: 
            facts[title] = off_str[start:]
        else: 
            end = pts[i+1]
            facts[title] = off_str[start:end]
        
        facts[title] = facts[title].replace(title, '')
        facts[title] = cleanUpFact(facts[title])
        i += 1
            
        
        
    writeFacts(facts)
    return

####################################################################

def parse_LanguageCodeSection(off_str):
    #writeFacts(facts)
    pass


####################################################################

def removeTags (htmlText):
    start = htmlText.find('<')
    if start == -1:
        return htmlText
    
    end = htmlText.find('>')
    sub = htmlText[start:end+1]
    htmlText = htmlText.replace(sub, '')
    
    return removeTags(htmlText)

####################################################################

def cleanUp(htmlTxt):
    #htmlTxt = htmlTxt.replace('&#160;&#160;', 'IGNORE') #refers to a map we don't have access to
    htmlTxt = htmlTxt.replace('&#160;', ' ')
    htmlTxt = htmlTxt.replace('\n\n\n', ' ') #get rid of excess newlines
    htmlTxt = htmlTxt.replace('\n', '::') ##issues where names get confused, white space was fine when they were on separate lines but that is no longer the case
    htmlTxt = htmlTxt.replace('  ', ' ')
    htmlTxt = htmlTxt.strip(':')
    return htmlTxt

####################################################################

def splitSections(htmlT):
    
    langHead = ""
    officialStatus =""
    langCodes = ""
    
    index_langHead = 0 #name of lang starts at 0 in fact
    index_officialStatus = htmlT.find('Official status')
    index_langCodes = htmlT.find('Language codes')

    if index_officialStatus == -1:
        if index_langCodes == -1:   #only 1 section, the first one with the name 
            langHead = htmlT
        else:                       #no Official Status, but Language Codes Section is present 
            langHead = htmlT[index_langHead:index_langCodes]
            langCodes = htmlT[index_langCodes:]
            
    else:
        
        langHead = htmlT[index_langHead:index_officialStatus]
        
        if index_langCodes == -1:
            officialStatus = htmlT[index_officialStatus:]    
        else: 
            officialStatus = htmlT[index_officialStatus:index_langCodes]
            langCodes = htmlT[index_langCodes:]

    
    
    return (langHead, officialStatus, langCodes)
    


def parse_wiki():
   #if len(sys.argv) < 2: 
    #    sys.stderr.write("no URL was provided ")
     #   raise SystemExit(1)

    #url = sys.argv[1]
    #file 
    url = "http://www.en.wikipedia.org/wiki/French_language"
    req = urllib2.Request(url, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    htmlSource = conn.read()
    conn.close()
    
    start = htmlSource.find('<table class=\"infobox\" style=\"width: 22em; text-align: left; font-size: 88%; line-height: 1.5em\">' ) 
    infobox = htmlSource[start:]
    end = infobox.find('</table>')
    infobox = infobox[:end]
    infobox = removeTags(infobox)
    infobox = cleanUp(infobox)
    
    
    head, official, codes = splitSections(infobox)
    
    parse_mainSection(head)
    
    if official != "":
         parse_OfficialStatusSection(official)
        
    if codes != "":
        parse_LanguageCodeSection(codes) 
        
       
    
    


if __name__ == "__main__":
    parse_wiki()

                    
