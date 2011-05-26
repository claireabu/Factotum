import urllib2
import sys
from string import *
import string
import time 



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
        filename = 'wikidta.f'
    file = open(filename, 'a') 
    
    writestring = ''
    subject = Name 
        
    
    for k in facts.keys():
        if facts[k].__class__  == list: 
            for entry in facts[k]: 
                
                if not started:
                    global started
                    started = True
                    writestring = subject + ' ' + k + ' ' + entry #+ '\n'
                else: 
                    writestring = '\"' + ' ' + k + ' ' + entry #+ '\n'
                    
                file.write(writestring)
                file.write('\n')
            
            continue 
                
        elif not started:
            global started
            started = True 
            if k == '->':
                 writestring =  ':' + subject + ' ' + '->' + ' ' + Native #+ '\n'
            elif k == 'Language family': 
                writestring =  ':' + subject + ' ' + '[' +  facts[k] + '] ' #+ '\n'
            else: 
                writestring =  subject + ' ' + k + ' ' + facts[k] #+ '\n'
            
        else: 
            if k == '<-':
                 writestring =  ':' + '\"' + ' ' + '<-' + ' ' + Native #+ '\n'
            
            elif k == 'Language family': 
                writestring =  ':' + '\" ' + '[' +  facts[k] + '] ' #+ '\n'
                
            else:   
                writestring =  '\"' + ' ' + k + ' ' + facts[k] #+ '\n'
        
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
            
        if removeli != []:
            for ri in removeli: 
                z.remove(ri)
    
    
        
    ##### GET RID OF COMMAS 
    addon = []
    if key == 'Total speakers' or key == 'Total Signers':
#        if z.__class__ == list: 
#            
#        else: 
        res = z.find(',')
        while res != -1:
            if z[res-1] in string.digits or z[res+1] in string.digits: 
                z = z.replace(',', '')
                res = z.find(',')
            else: 
                z = z.split(',')
                for zj in z: 
                    res = zj.find(',')
                    while res != -1:
                        if zj[res-1] in string.digits or zj[res+1] in string.digits: 
                            zj = zj.replace(',', '')
                            res = zj.find(',')
                        else: 
                            zj = zj.replace(',', '')
                            move = zj[res:]
                            addon.append(move)
                            zj = zj[:res]
                            res = zj.find(',')
                
    if addon != []:
        for a in addon: 
            z.append(a)
        cleanUpFact(z, key)
                
    return z

#####################################################


def parse_mainSection(lang_str):
    '''
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
    
    #just grab immediate parent
    if 'Language family' in facts.keys(): 
        fams = facts['Language family']
        if fams == [] or fams == '':
            del facts['Language family']
        else: 
            facts['Language family'] = fams[-2]
    
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
    if url == '':
        if len(sys.argv) < 4: 
            sys.stderr.write("please include URL")
            raise SystemExit(1)
        else: 
            url = sys.argv[3]
            htmlSource = pull_content(url)
    elif htmlSource == '':
        htmlSource = pull_content(url)

    
    versID = getID(htmlSource)
    
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
        
    perma = url.replace('wiki/', 'w/index.php?title=' )
    perma += '&oldid=' + versID
    
    return perma   



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
    Main func
    '''
    linksURL = linksToPage(sourceURL)
    
    #read page full of links 
    req = urllib2.Request(linksURL, headers={'User-Agent' : "Google Chrome"})
    conn = urllib2.urlopen(req)
    srce = conn.read()
    conn.close()

    #get in right area, from the beginning of the list
#    edgeIndic = 'View ('
#    listbeg = srce.find(edgeIndic)
#    listend = srce.rfind(edgeIndic)
#    
#    listHTML = srce[listbeg:listend]
    
    
    links = []
    moarLinks = []
    nextLink = linksURL
    
    #get the links for the first page
#    links, nextLink = go_thru_page(nextLink)
#    moarLinks.extend(links)
    
    #parse lang pages linked from page, then get next page of links 
    while nextLink != '':
        print nextLink
        links = []
        links, nextLink = go_thru_page(nextLink)
        moarLinks.extend(links)
        
#    for m in moarLinks: 
#        link_content = pull_content(m)
#        linkdict[m] = link_content
#        print m
        
    
    return moarLinks
    #langtotal = len(li_links)
    #print langtotal

    #num = len(recordoflinks)
    #print num
    #print num1
    
    #print len(recordoflinks)          
    #return recordoflinks 
    

#####################################################################

def wiki_main():
    
    if len(sys.argv)  >= 3: 
        filename = sys.argv[2]
    else: 
        filename = 'wikipedia_links.txt'
        
    file = open(filename, 'a') 
    
    
    permaLinks = []
    startURL = 'http://en.wikipedia.org/wiki/Template:Infobox_language'
    
    links = collectData(startURL)
    linksplus = []
    
    for url in links:
        htmlSoucre = ''
        htmlSource = pull_content(url)
        linksplus.append([url, htmlSource])
        time.sleep(15)
        print url 
    
    for pair in linksplus: 
        url = pair[0]
        srce = pair[1]
        
        perma= parse_wiki(url, srce)
        permaLinks.append(perma)
        
        file.write(perma)
        file.write('\n')
        
#        url = 'http://www.en.wikipedia.org/wiki/Biatah'
#        content = pull_content(url)
#        perma = parse_wiki(url, content)
        
        
    return permaLinks 





        
if __name__ == "__main__":
    wiki_main()
    #parse_wiki('','')
  
                    
