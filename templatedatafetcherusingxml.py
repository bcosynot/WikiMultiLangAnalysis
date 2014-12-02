# -*- coding: utf-8 -*-
import csv
import collections
import codecs
import threading
from bz2 import BZ2File
from wmf import dump
import mwparserfromhell

class langProcessingThread(threading.Thread):
    
    def __init__(self, lang, tempparams, threadnumber, filepath):
        threading.Thread.__init__(self)
        self.lang = lang
        self.tempparams = tempparams
        self.threadnumber = threadnumber
        self.filepath = filepath
        self.threadsl = []
        
    def writeoutput(self, rows, lang):
        with codecs.open('./output/templates_details.csv', 'a+b', 'utf-8') as outputFile:
            templatedetailswriter = csv.writer(outputFile)
            print "Writing" , len(rows) , "lines for " + self.lang
            templatedetailswriter.writerows(rows);
            
    def run(self):
        threading.Thread.run(self)
        print "Starting thread number", self.threadnumber , "for " + self.lang
        file = BZ2File(self.filepath)
        dumpiterator = dump.Iterator(file)
        templates = self.tempparams.keys()
        rows = []
        i = 0
        talkpages = 0
        totalrows = 0
        for page in dumpiterator.readPages():
            if page.getNamespace() == 1:
                talkpages += 1
                for revision in page.readRevisions():
                    text = mwparserfromhell.parse(revision.getText())
                    pagetemplates = text.filter_templates()
                    for pagetemplate in pagetemplates:
                        parameters = None
                        paramvals = None
                        if pagetemplate.name.lower() in templates:
                            parameters = self.tempparams[pagetemplate.name.lower()].keys()
                            paramvals = self.tempparams[pagetemplate.name.lower()]
                        elif '*' in templates:
                            parameters = self.tempparams["*"].keys()
                            paramvals = self.tempparams["*"]
                        if parameters is not None and paramvals is not None:
                            for pagetemplateparameter in pagetemplate.params:
                                if pagetemplateparameter.name.lower() in parameters:
                                    #print pagetemplates
                                    #print pagetemplate.name.lower()
                                    #print pagetemplate
                                    #print pagetemplateparameter
                                    #print parameters
                                    #print paramvals
                                    if pagetemplate.has(pagetemplateparameter.name, True):
                                        #print pagetemplate.get(pagetemplateparameter.name).value.lower()
                                        #print paramvals[pagetemplateparameter.name.lower()]
                                        if pagetemplate.get(pagetemplateparameter.name).value.lower() in paramvals[pagetemplateparameter.name.lower()]:
                                            row = [self.lang, page.getTitle(), page.getId(), pagetemplate.get(pagetemplateparameter.name).value.lower()]
                                            rows.append(row)
                                            totalrows += 1
            i += 1
            if(i % 50000 == 0):
                print i, "pages (", talkpages, "talk pages) for " + self.lang + " with", totalrows, "added."
                if  len(rows) > 1000:
                    self.writeoutput(rows, lang)
                    rows = []
                    
        self.writeoutput(rows, lang)
                    
threads = []
filesuffix = 'wiki-latest-pages-meta-current.xml.bz2'
fileprefix = './input/'
with codecs.open('./input/templates.csv', 'r+b', 'utf-8') as templatesInputFile:
    treader = csv.reader(templatesInputFile)
    langtemps = collections.defaultdict(dict)
    for lang, template, parameter, value in treader:
        if unicode(lang.lower()) in langtemps:
            tempParams = langtemps[unicode(lang.lower())]
        else:
            tempParams = collections.defaultdict(dict)
        if unicode(template.lower()) in tempParams:
            paramvals = tempParams[unicode(template.lower())]
        else:
            paramvals = collections.defaultdict(list) 
        paramvals[unicode(parameter.lower())].append(unicode(value.lower()))
        tempParams[unicode(template.lower())] = paramvals
        langtemps[unicode(lang.lower())] = tempParams

threadLock = threading.Lock()
print langtemps
i = 0
for lang in langtemps.keys():
    i += 1
    filepath = fileprefix + lang + filesuffix
    newthread = langProcessingThread(lang, langtemps[lang], i, filepath)
    newthread.start()
    threads.append(newthread)
        
# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
        
