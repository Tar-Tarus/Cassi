import os
import json
import pprint
import sys
from subprocess import call
from subprocess import check_output

from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import requests

from SIXParser import SIXParser
from config import *
from cog_config import *


def fetchESMAPage(url):
    print "\nFetching ESMA Library Page to collect CP\n"
    try:
        r = requests.get(url)
        return r.text
    except:
        print "An error occured and the ESMA Library Page could not be fetched"


def parseESMAPage(htmlText):
    parser = SIXParser()
    parser.feed(htmlText)
    return parser.link_collection, parser.title_collection


def link_title_cleanup(links, titles):
    cleanLinks = links
    cleanTitles = titles
    iterator = 0

    for title in titles:
        if("Draft technical" in title ):
            #print "Good DOC\n"
            print ""
        else:
            #print "Bad DOC\n"
            del cleanTitles[iterator]
            del cleanLinks[iterator]
            iterator += 1
    return cleanLinks, cleanTitles


def downloadPDFs(links, titles):
    iterator = 0

    for link in links:
        if (titles[iterator]+".pdf" not in os.listdir("./pdf")):
            with open(os.path.join("./pdf",titles[iterator]+'.pdf'), 'wb') as f:
                response = requests.get(link)
                f.write(response.content)
        else:
            print ""
        iterator += 1


def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

def find_between_r(s, first, last):
    try:
        start = s.rindex(first)
        end = s.rindex(last, start)
        return s[start:end]
    except ValueError:
        return ""


if __name__ == "__main__":
    print "\nSTART DRAFT COLLECTION\n"
    print search_url
    
    print("\nStart ESMA Page Fetch?\n")
    pageHtml = fetchESMAPage(search_url)
    #print pageHtml
    
    print("\nStart ESMA Page Parsing?\n")
    links, titles = parseESMAPage(pageHtml)
    #print links, titles
    
    print("\nStart Links and Title Cleanup?\n")
    cleanLinks, cleanTitles = link_title_cleanup(links, titles)
    #print cleanLinks, cleanTitles
    assert(len(cleanLinks) == len(cleanTitles))
    
    print("\nStart Download of PDF Documents?\n")
    downloadPDFs(cleanLinks, cleanTitles)
    iterator = 0
    for f in  os.listdir(("./pdf")):
        #print str(iterator)+"- "+f
        iterator += 1
    file_index = raw_input("\nWhich file do you wish to analyze? (Enter Number)\n")
    file_name = "./pdf/"+os.listdir(("./pdf"))[int(file_index)]
    print("\nStart Conversion of PDF to text\n")
    #pdfText = convert(file_name)
    if (file_name[6:]+".conv" not in os.listdir("./pdf")):
        pdfText = check_output(["pdf2txt.py", file_name])
        f = open(file_name+".conv", 'w')
        f.write(pdfText)
        print "CONVERTED"
    else:
        f = open(file_name+".conv", 'r')
        pdfText = f.read()
        print "Fetched existing version"

    f.close()
     
    cleanPDFText = pdfText[pdfText.index("Table of Contents"):]
    tableOfContents = cleanPDFText[:cleanPDFText.index("Annex")].split("\n\n")
    cleanPDFText = cleanPDFText[cleanPDFText.index("Executive Summary"):]
    draftTitles = list()
    draftEnds = list()
    iterator = 0
    for title in tableOfContents:
        if ("Draft technical standards" in title):
            name = title
            draftTitles.append(name)
            try:
                stop = tableOfContents[iterator+2].split(' ..')
                draftEnds.append(tableOfContents[iterator+2].split(' ..')[0])
            except:
                print "Reached end of ToC"
        iterator +=1
    print("Fetched draft titles")
    print("Fetch Technical Standards Draft")
    
    draftText = list()
    iterator = 0
    for title in draftTitles:
        if (iterator == 0):
            payload = {"documents":[]}
            title = title.split(' ..')[0]
            draft = find_between_r(cleanPDFText, title, draftEnds[iterator])
            f = open("./drafts/"+title.replace(".", "-")+".txt", 'w')
            f.write(draft)
            payload["documents"].append({
                "language":"en",
                "id":str(iterator),
                "text": draft
                })
            #print ("Size of Payload First"+str(sys.getsizeof(payload)))
            #print ("Size of draft First"+str(sys.getsizeof(draft)))
            if (sys.getsizeof(draft) > 5000):
                print("Text too long")
                for size_iterator in range(sys.getsizeof(draft)/5000):
                    if((size_iterator+1)*5000> sys.getsizeof(draft)):
                        text = draft[(size_iterator-1)*5000:]
                    else:
                        text = draft[(size_iterator)*5000:(size_iterator+1)*5000]
                    payload["documents"].append({
                        "language":"en",
                        "id":str(100+size_iterator),
                        "text":text
                        })
            else:   
                #draftText.append(draft)"""
                payload["documents"].append({
                    "language":"en",
                    "id":str(iterator),
                    "text": draft
                    })
            iterator += 1

    #headers["Content-Length"] = (sys.getsizeof(payload))
  #  raw_input(payload)
#   raw_input(headers)
    payload_json = json.dumps(payload, encoding='latin1')
    print "PAYLOAD SIZE "+str(sys.getsizeof(payload_json))
    pprint.PrettyPrinter().pprint(payload)
    response = requests.post(post_url_keyPhrases, data = payload_json, headers = headers)
    print "Response Code OUTSIDE\n"
    print str(response.status_code)
    print "\n\n"
    for pack in response.content[0]:
        pprint.PrettyPrinter().pprint(response.content)
