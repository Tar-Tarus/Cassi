from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

class SIXParser(HTMLParser):
    """ PARSER for the ESMA LIBRARY to Search for Drafts of Technical Standards """
    def __init__(self):
        HTMLParser.__init__(self)
        self.inside_a = False
        self.flag_title = False
        self.title_container_class = "esma_library-title"
        self.title_collection = list()
        self.link_collection = list()
        self.iterator = 0
        print "\nINITIALIZED PARSER\n"

    def handle_starttag(self, tag, attrs):
        if(tag=="td"):
            for attr in attrs:
                if self.title_container_class in attr:
                    self.flag_title = True
        elif(tag=="a" and  self.flag_title):
            self.inside_a = True
            for attr in attrs:
                self.link_collection.append(attr[1])
                self.flag_title = False

    def handle_endtag(self, tag):
#        print "End tag :", tag
        print ""

    def handle_data(self, data):
        if(self.inside_a):
            self.title_collection.append(data)
            self.iterator += 1
            self.inside_a = False
