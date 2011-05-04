import urllib2
import sys
from string import *




def parse_LanguageSection():
    pass

####################################################################

def parse_OfficialStatusSection():
    pass

####################################################################

def parse_LanguageCodeSection():
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
    htmlTxt = htmlTxt.replace('&#160;&#160;', 'IGNORE') #refers to a map we don't have access to
    htmlTxt = htmlTxt.replace('&#160;', ' ')
    htmlTxt = htmlTxt.replace('\n\n\n', ' ') #get rid of excess newlines
    htmlTxt = htmlTxt.replace('\n', ' ')
    htmlTxt = htmlTxt.replace('  ', ' ')
    htmlTxt = htmlTxt.strip()
    return htmlTxt

####################################################################

def splitSections(htmlT):
    
    langHead = ""
    officialStatus =""
    langCodes = ""
    
    index_langHead = 0 #name of lang starts at 0 in fact
    index_officialStatus = htmlT.find('Official Status')
    index_langCodes = htmlT.find('Language Codes')

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
   #if len(sys.argv) < 1: 
    #    sys.stderr.write("no URL was provided ")
     #   raise SystemExit(1)

    #url = sys.argv[1]
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
    
    #head = ""
    #official = ""
    #codes = ""
    
    head, official, codes = splitSections(infobox)
    
    print infobox
    print head
    print official
    print codes 
    



if __name__ == "__main__":
    parse_wiki()

                    
