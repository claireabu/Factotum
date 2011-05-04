import urllib2
import sys
from string import *


def removeTags (htmlText):
    
    
    start = htmlText.find('<')
    if start == -1:
        htmlText = htmlText.replace('&#160;', '')
        htmlText = htmlText.replace('\n\n\n', '') #get rid of excess newlines
        return htmlText
    
    end = htmlText.find('>')
    sub = htmlText[start:end+1]
    htmlText = htmlText.replace(sub, '')
    
    return removeTags(htmlText)
    


def parse_wiki():
    if len(sys.argv) < 1: 
        sys.stderr.write("no URL was provided ")
        raise SystemExit(1)

    
    url = sys.argv[1]
    #url = "http://www.en.wikipedia.org/wiki/French_language"
    req = urllib2.Request(url, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    htmlSource = conn.read()
    conn.close()
    #print conn.read()
    start = htmlSource.find('<table class=\"infobox\" style=\"width: 22em; text-align: left; font-size: 88%; line-height: 1.5em\">' ) 
    infobox = htmlSource[start:]
    end = infobox.find('</table>')
    infobox = infobox[:end]
    infobox = removeTags(infobox)
    print infobox
    



if __name__ == "__main__":
    parse_wiki()

                    
