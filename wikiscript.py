#!/usr/local/bin/python
# coding: utf-8

''' Wikiscript.py
@author Claire

Pulls content from wikipedia language pages with the Infobox template, 
and proceeds to parse the content 

Note, if include a file of links/already have pages with links contents, 
wikiscript should be run in the same directory.  
'''


import urllib2
import sys
from string import *
import string
import time 
import io



started = False 
Name = '' 
Native = '' 

linkList = []
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
                 'Regulated by'
                 ]

headings_off = [
                'Official language in',
                'Recognised minority language in',
                'List of language regulators',
                'Regulated by'
                ]

headings_codes = ['ISO 639-1',
                  'ISO 639-2',
                  'ISO 639-3',
                  'Linguasphere Observatory',
                  'Linguasphere'
                 ]

def writeFacts(facts):
    ''' Writes facts to a file either specified by 
    the user in input, or automatically created and called
    _wikidata.f. 
    
    It goes thru the dictionary Facts and writes each one 
    into the file. If it is the first item (@started) to be 
    written for this given subject, then the subject is 
    included followed by the fact. If it is not the first item
    then a quotation mark is inserted before the rest of the 
    entry. 
    '''
    if len(sys.argv)  >=  2: 
        filename = sys.argv[1]
    else: 
        filename = '_wikidata_.f'
    file = open(filename, 'a') 
    
    writestring = ''
    subject = Name 
    
    for k in facts.keys():
        if facts[k].__class__  == list: 
            
            for entry in facts[k]: 
                
                if entry.find('\"') != -1: 
                    if entry.count('\"') % 2 != 0: 
                        continue  
                        
                if not started:
                    global started
                    started = True
                    writestring = subject + ' ' + k + ' ' + entry #+ '\n'
                
                elif k == 'Official language in': 
                    writestring = subject  + ' ' + k + ' ' + entry
                    
                else: 
                    writestring = '\"' + ' ' + k + ' ' + entry #+ '\n'
                    
                file.write(writestring)
                file.write('\n')
            
            continue 
                
        elif not started:
            
            if facts[k].find('\"') != -1: 
                if facts[k].count('\"') % 2 != 0: 
                    continue
                
            global started
            started = True 
            if k == '<-':
                 writestring =  ':' + subject + ' ' + '<-' + ' ' + Native #+ '\n'
            elif k == 'Language family': 
                writestring =  ':' + subject + ' ' + '[' +  facts[k] + '] ' #+ '\n'
                
            else: 
                writestring =  subject + ' ' + k + ' ' + facts[k] #+ '\n'
            
        else: 
            
            if facts[k].find('\"') != -1: 
                if facts[k].count('\"') % 2 != 0: 
                    continue
                
            if k == '<-':
                 writestring =  ':' + '\"' + ' ' + '<-' + ' ' + Native #+ '\n'
            
            elif k == 'Language family': 
                writestring =  ':' + subject + ' ' + '[' +  facts[k] + '] ' #+ '\n'
            
            elif k == 'Official language in': 
                writestring = subject  + ' ' + k + ' ' + facts[k]
#                
            else:   
                writestring =  '\"' + ' ' + k + ' ' + facts[k] #+ '\n'
                
        #writestring = unicode(writestring, 'utf-8')
        file.write(writestring)
        file.write('\n')
        
        
    
    file.close()
            
    
    return 

##############################
def cleanUpFact(x, key):
    ''' Cleans up each fact, removing excess colons (:) 
    and whitespace, then getting rid of embedded citations or 
    brackets, split up string on double colons or commas
    into list. 
    
    '''
    
    z = x.strip(':')
    z = z.strip(',')
    z = z.strip()
    
    #### GET RID OF CITATIONS 
    
    l = z.find('[') 
    while l != -1: 
        r = z.find(']')
        if r != -1:
            if key != 'Pronunciation':
                sub = z[l:r+1]
                z = z.replace(sub, '')
                l = z.find('[')
            else: 
                z = z.replace('[', '')
                z = z.replace(']', '')
                z.strip()
                break
        else: 
            break 
    
    ###GET RID OF COLONS --> PUT IN TO SEP
    if z.find('::') != -1:
        z = z.replace('::::', '::')
        z = z.split('::')
        
        removeli = []
        for zi in z: 
            i = zi.find('IGNORE') 
            if i >= 0: 
                removeli.append(zi)
            else: 
                zi = zi.strip(',')
            
        if removeli != []:
            for ri in removeli: 
                z.remove(ri)
    
    
        
    ##### GET RID OF COMMAS --only if not in Total S, or there's more than one comma, and it's not
    #in between parentheses 
    removeli = []
    addon = []
            
    if key != 'Total speakers' and key != 'Total signers':    
        if z.__class__ == list: 
            for zi in z: 
                if zi.count(',') > 1 : 
                    if zi.count(')') == 0:
                        zk = zi.split(',')
                        removeli.append(zi)
                        addon.extend(zk)
                    else: 
                        if zi.find(':') == -1:
                            p1 = zi.find('(')
                            p2 = zi.find(')')
                            if p1 != -1 and p2 != -1: 
                                c = zi[p1:p2].find(',')
                                if c == -1:  
                                    zi = zi.split(',')
                    
        else: 
            if z.count(',') > 1: 
                if z.count(')') == 0: 
                    z = z.split(',')
                else: 
                    if z.find(':') == -1:
                        p1 = z.find('(')
                        p2 = z.find(')')
                        if p1 != -1 and p2 != -1: 
                            c = z[p1:p2].find(',')
                            if c == -1:  
                                z = z.split(',')
            
    if removeli != []:
        for ri in removeli: 
            z.remove(ri)
                   
    if addon != []:
        for a in addon: 
            if a == '':
                continue 
            else: 
                z.append(a)
       
                
    return z

#####################################################


def parse_mainSection(lang_str):
    '''Parses the main section of the Infobox
    '''
   
    headings = []
    pts = []
    
    for h in headings_main:
        try: 
            indx = lang_str.index(h)
            headings.append(h)
            pts.append(indx)
            
        except: 
            continue
        
    i = 0 
    facts = {}
    
    for spec in headings:  
        start = pts[i]
        if i == len(headings)-1:
            facts[spec] = lang_str[start:]
        else:
            end = pts[i+1]
            facts[spec] = lang_str[start:end]
        #some clean up 
        facts[spec] = facts[spec].replace(spec, '')
        facts[spec] = cleanUpFact(facts[spec], spec)
    
        if facts[spec] == 'see below':
            del facts[spec]
        i += 1
    
    if Native != '':
        facts['<-'] = Native
        facts['<-'] = cleanUpFact(facts['<-'], '<-')
       
    if Name.find(',') != -1: 
        names = Name.split(',')
        global Name
        Name = names[0]
        names = names[1:]
        
        if names != []:
            if '<-' in facts:
                if facts['<-'].__class__ == list:
                    facts['<-'].extend(names)
                else: 
                    aliases = [facts['<-']]
                    aliases.extend(names)
                    facts['<-'] = aliases
            else: 
                facts['<-'] = names
           
            
     
    #just grab immediate parent
    if 'Language family' in facts.keys(): 
        fams = facts['Language family']
        if fams == [] or fams == '':
            del facts['Language family']
        else:
            if fams.__class__ == list: 
               # if len(fams) > 1: 
               facts['Language family'] = fams[-2]

            elif fams.__class__ == string: 
                print 'ONE ITEM'
                #only 1 item: 
                    
    
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
        facts[title] = cleanUpFact(facts[title], title)
        i += 1
            
        
        
    writeFacts(facts)
    return

####################################################################

def parse_LanguageCodeSection(codz_str):
    ''' Parses Language Codes section of contents
    '''
    
    codz_str = codz_str.replace('Language codes', '')
    try: 
        endnote_i = codz_str.index('Note')
    except: 
        endnote_i = '' 
    
    if endnote_i !=  '':
        codz_str = codz_str[:endnote_i-1]
    pts = []
    headings = []
    
    for c in headings_codes:
        try: 
            idx = codz_str.index(c)
            headings.append(c)
            pts.append(idx)
        except:
            continue 
    
    i = 0 
    facts = {}
    
    for spec in headings: 
        
        start = pts[i]
        spec1 = 'Language codes ' + spec
        if i == len(headings) - 1:
            facts[spec1] = codz_str[start:]
            if facts[spec1] == '-':
                del facts[spec1]
        else: 
            end = pts[i+1]
            facts[spec1] = codz_str[start:end]
            
        facts[spec1] = facts[spec1].replace(spec, '')
        facts[spec1] = cleanUpFact(facts[spec1], spec1)
        i += 1
            
              
    
    if facts != {}:
        writeFacts(facts)
    return 


####################################################################

def removeTags (htmlText, count):
    ''' Removes all html tags from content so just have the info
    '''
    
    
    start = htmlText.find('<')
    
    if start == -1:
        return htmlText
    elif start != 0: 
        #pulling out name or native name 
        if count == 0: 
            global Name 
            Name = htmlText[:start]
            Name = Name.strip() 
            count += 1
            htmlText = htmlText[start:]
            start = 0 
            
        elif count == 1: 
            test = htmlText[:start]
            test = test.strip()
            if not test in headings_main: 
                global Native
                Native = test 
                count += 1
                htmlText = htmlText[start:]
                start = 0 
            else:
                count += 1
            
    end = htmlText.find('>')
    sub = htmlText[start:end+1]
    htmlText = htmlText.replace(sub, '')
    htmlText = htmlText.lstrip()
    
    return removeTags(htmlText, count)

####################################################################

def cleanUp(htmlTxt):
    htmlTxt = htmlTxt.replace('&#160;&#160;', 'IGNORE') #refers to a map we don't have access to
    htmlTxt = htmlTxt.replace('&#160;', ' ')
    htmlTxt = htmlTxt.replace('\n\n\n', ' ') #get rid of excess newlines
    htmlTxt = htmlTxt.replace('\n', '::') ##issues where names get confused, white space was fine when they were on separate lines but that is no longer the case
    htmlTxt = htmlTxt.replace('  ', ' ')
    htmlTxt = htmlTxt.strip(':')
    return htmlTxt

####################################################################

def splitSections(htmlT):
    ''' splits Infobox into sections according to the headings 
    '''
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
    
###################################################
def getID(srce):
    ''' Gets the version number of the page accessed
    '''
    idx = srce.find('oldid')
    id = srce[idx:]
    idx = id.find('\"')
    id = id[:idx]
    
    id = id.replace('oldid=', '')
    id.strip()
    return id
#################################
def pull_content(url):
    
    req = urllib2.Request(url, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    htmlSource = conn.read()
    conn.close()

    return htmlSource 


###################################################

def parse_wiki(url, htmlSource):
    ''' goes through a given url, grabs the html source, 
    isolates the section that contains the Infobox information, 
    pulls that apart into the designated 2 or 3 sections and 
    transforms into facts that may be written to the file. 
    Returns the version number of the page accessed. 
    
    Note: if using this function without collect data, you may 
    input a url using the first commented part below. 
    '''
#    if url == '':
#        if len(sys.argv) < 4: 
#            sys.stderr.write("please include URL")
#            raise SystemExit(1)
#        else: 
#            url = sys.argv[3]
#            htmlSource = pull_content(url)
#    elif htmlSource == '':
#        htmlSource = pull_content(url)

    
    
    
    start = htmlSource.find('<table class=\"infobox\" style=\"width: 22em; text-align: left; font-size: 88%; line-height: 1.5em\">' ) 
    infobox = htmlSource[start:]        
    end = infobox.find('</table>')
    infobox = infobox[:end]
    infobox = removeTags(infobox, 0)
    infobox = cleanUp(infobox)
    
    head, official, codes = splitSections(infobox)
    
    parse_mainSection(head)
    
    if official != "":
        parse_OfficialStatusSection(official)
        
    if codes != "":
        parse_LanguageCodeSection(codes)
        
    global started 
    started = False  
    
    global Name 
    Name = ''
    global Native
    Native = ''
        
    

########################################
def getPerma(url, srce):
    ''' Grabs version id of the page and 
        hashes together what would be the archive/permalink 
        to the accessed page     
    '''
    
    versID = getID(srce)
    perma = url.replace('wiki/', 'w/index.php?title=' )
    perma += '&oldid=' + versID
    
    return perma, versID   
    

##################################

def grabLinks(block):
    ''' goes through page of links and grabs one by one, 
    ignoring cases where a colon is present.  
    '''
    lbeg = -1
    lend = -1 
    link = ''
    llist = []
    lbeg = block.find('/wiki/')
    
    if lbeg == -1:
        return  llist
    else: 
        
        block = block[lbeg:]
        lend = block.find('\"')
        
        if lend == -1:
            return []
        
        link = block[:lend]
        if link.find(':') != -1: 
            link = ''
        else: 
            link = 'http://www.en.wikipedia.org' + link 
            
            
    block = block[lend:]
    res = grabLinks(block)
    
    if link != '':
        if res != []:
            llist.append(link)
            llist.extend(res)
        else:
            llist.append(link)
    else: 
        if res != []: 
            llist.extend(res)
    
    return llist

#############################################################

def getNextPage(html):
    ''' Gets link for the next page listing links of languages
    '''
    edgeIndic = 'View ('
    listbeg = html.find(edgeIndic)
    
    newlink = html[listbeg:]
    marker = newlink.find('|')
    newlink = newlink[marker+1:]
    
    newlink = newlink.strip()
    if newlink.find('next') == -1: 
        print html
        return ''
    elif newlink.find('next') == 0:   #no more pages
        return ''

    s = newlink.find('\"')
    nextl = newlink[s+1:]
    e = nextl.find('\"')
    nextl = nextl[:e]
    nextl = nextl.replace('amp;', '')
    nextl = 'http://www.en.wikipedia.org' + nextl
   
    return nextl 

#######################################

def go_thru_page(linksURL):
    '''
    Go thru one of the pages with the list of links, 
    pull all the links from the given page using grabLinks func,
    and grab the link for the next page and return a list of the 
    links and the next url. 
    '''
    req = urllib2.Request(linksURL, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    listHTML = conn.read()
    conn.close()
    
    nextURL = getNextPage(listHTML)
    
    start = listHTML.find('mw-whatlinkshere-list')
    listHTML = listHTML[start:]
    end = listHTML.find('View (')
    listHTML = listHTML[:end]
    
    linklist = []
    linklist = grabLinks(listHTML)

    return (linklist, nextURL)
    
#########################################################

def linksToPage(sourceURL):
    '''
    Input is the URL for the Template:Infobox, and pulls the link 
    that will take us to the list of all pages that link(use) this 
    given Infobox 
    '''
    req = urllib2.Request(sourceURL, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    srce = conn.read()
    conn.close()
    
    i = srce.find('whatlinkshere')
    srce = srce[i:]
    
    j = srce.find('<a href=\"')
    srce = srce[j:]
    
    k = srce.find('>')
    srce = srce[:k]
    
    j = len('<a href=\"')
    srce = srce[j:]
    
    q = srce.find('"')
    srce = srce[:q]
    
    linktolinks = 'http://www.en.wikipedia.org' + srce
    return linktolinks

#########################################################################

def collectData(sourceURL):
    '''
    Main func for collecting all the links 
    '''
    linksURL = linksToPage(sourceURL)
    
    #read page full of links 
    req = urllib2.Request(linksURL, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    srce = conn.read()
    conn.close()    
    
    links = []
    moarLinks = []
    nextLink = linksURL
    
    #parse lang pages linked from page, then get next page of links 
    while nextLink != '':
        print nextLink
        links = []
        links, nextLink = go_thru_page(nextLink)
        moarLinks.extend(links)
        
    
    return moarLinks

    

#####################################################################

def wiki_main():
    ''' Main function of script, pulls content/links if necessary, 
    and then parses the content 
    '''
    
    if len(sys.argv)  >= 3: 
        filename = sys.argv[2]
    else: 
        filename = 'wikipedia_links.txt'
    
    try: 
        permafile = open(filename) 
    except:
        permafile = open(filename, 'a')
        permafile.close()
        permafile = open(filename, 'r')

    succ = []
    permas = permafile.readlines()
    permafile.close()
    #if file is empty (eg NO LINKS ARE FOUND YET) 
    #otherwise, if a file of links is found: go through that 
    if permas == []: 
        permafile = open(filename, 'a') 
        
        startURL = 'http://en.wikipedia.org/wiki/Template:Infobox_language'
    
        links = collectData(startURL)
    
        for url in links:
            htmlSoucre = ''
            htmlSource = pull_content(url)
        
            ###WRITE ALL PERMA LINKS TO A FILE 
            perma, OID = getPerma(url, htmlSource)
            permafile.write(perma)
            permafile.write('\n')
            permas.append(perma)
        
            #WRITE CONTENT TO FILE, WITH PERMA LINK AS FILE NAME 
            x = perma.find('=')
            contentfilename = perma[x+1:]
            
            try:  #try to open file, if it exists, then it will open
                contentfile = open(contentfilename, 'r') 
                contentfile.close()
            except: #if it can't open, then we create it, and write to it 
                contentfile = open(contentfilename, 'a')
                contentfile.write(htmlSource)
                contentfile.close()
    
        permafile.close()
    failed = []
    for url in permas:
        
        srcetitle = url.strip()
        i = srcetitle.find('=') 
        if i != -1: 
            srcetitle = srcetitle[i+1:]
        else: 
            continue
            
        try:  #CHECK FOR FILE WITH HTMLSOURCE FOR LINK
            srce = open('/Users/Claire/SchoolStuff/UCLA/CS199/Factotum 3G 2/LangHTMLSources/' + srcetitle, 'r')
            htmlsrce = srce.read()
            srce.close()
            
            parse_wiki(url, htmlsrce)
            
            succ.append(url)
            print >> sys.stderr, url
            
        except: 
            try: #IF NO FILE, PULL CONTENT FROM LINK 
                htmlSoucre = ''
                htmlSource = pull_content(url)
                parse_wiki(url, htmlsrce)
            
                succ.append(url)
                print >> sys.stderr, url
                
            except:#CAN"T USE SOURCE FOR SOME REASON 
                err = 'Link ' + url + ' failed to parse'
                failed.append(err)
                continue
            
        
        
    for f in failed:             
        print >> sys.stderr, f
        
    return succ 


        
if __name__ == "__main__":
    wiki_main()
    #parse_wiki('','')
  
                    
