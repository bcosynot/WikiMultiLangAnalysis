# -*- coding: utf-8 -*-
import csv
import collections
import codecs
import pywikibot
import threading

class templateProcessingThread(threading.Thread):
    def __init__(self, threadnumber, pageslist, tempparams, templates, lang, langtemps):
        threading.Thread.__init__(self)
        self.threadnumber = threadnumber
        self.pageslist = pageslist
        self.tempparams = tempparams
        self.templates = templates
        self.lang = lang
        self.langtemps = langtemps
        
    def run(self):
        threading.Thread.run(self)
        print "Starting thread number 2.", self.threadnumber, " with " , len(self.pageslist) , " pages for " + lang
        rows = []
        i = 0
        for page in self.pageslist:
            templatesWithParams = page.templatesWithParams()
            for templatepage, parametervalues in templatesWithParams:
                template = None
                if ":" in templatepage.title():
                    template = templatepage.title().split(":")[1] 
                else:
                    template = templatepage.title()
                parameters = None
                paramvals = None
                if template.lower() in self.templates:
                    parameters = self.langtemps[self.lang.lower()][template.lower()].keys()
                    paramvals = self.langtemps[self.lang.lower()][template.lower()]
                elif "*" in self.templates:
                    parameters = self.langtemps[self.lang.lower()]["*"].keys()
                    paramvals = self.langtemps[self.lang.lower()]["*"]
                if parameters is not None and paramvals is not None:
                    for parameter in parameters:
                        values = paramvals[parameter.lower()]
                        for parametervalue in parametervalues:
                            if parametervalue.split("=")[0].lower() == parameter.lower() and parametervalue.split("=")[1].lower() in values:
                                row = [self.lang.lower(), page.title(), parametervalue.split("=")[1].lower()]
                                rows.append(row)
            i += 1
            if(i % 500 == 0):
                print i + " articles completed in thread " + self.threadnumber + " out of ", len(self.pageslist) + " for " + self.lang
                with codecs.open('./output/templates_details.csv', 'a+b', 'utf-8') as outputFile:
                    templatedetailswriter = csv.writer(outputFile)
                    print "Writing " , len(rows) , " lines in thread " + self.threadnumber
                    templatedetailswriter.writerows(rows);
                    rows = []

class langProcessingThread(threading.Thread):
    
    def __init__(self, lang, langtemps, threadnumber):
        threading.Thread.__init__(self)
        self.lang = lang
        self.langtemps = langtemps
        self.threadnumber = threadnumber
        self.threadsl=[]
        
    def run(self):
        threading.Thread.run(self)
        print "Starting thread number 1." , self.threadnumber , " for " + self.lang
        site = pywikibot.Site(self.lang, "wikipedia")
        sitesize = site.siteinfo["statistics"]["articles"]
        print "Site size: ", sitesize
        allpages = site.allpages(namespace=1)
        print "All pages generator loaded for " + self.lang
        tempparams = self.langtemps[self.lang]
        templates = tempparams.keys();
        i = 0
        threadnumberl = 0
        pageslist = []
        for page in allpages:
            i += 1
            pageslist.append(page)
            if i % 100000 == 0:
                threadnumberl += 1
                print "At ",float(float(i)*100/float(sitesize)),"% for" + self.lang
                newthread = templateProcessingThread(threadnumberl, pageslist, tempparams, templates, self.lang, self.langtemps)
                newthread.start()
                self.threadsl.append(newthread)
                pageslist = []
        print i
        print "Starting last thread"
        threadnumberl += 1
        newthread = templateProcessingThread(threadnumberl, pageslist, tempparams, templates, self.lang, self.langtemps)
        newthread.start()
        self.threadsl.append(newthread)
        print "All pages processed for "+self.lang
        # Wait for all threads to complete
        for t in self.threadsl:
            t.join()
        print "Exiting language processing thread"
                   
threads = []
with codecs.open('./input/templates.csv', 'r+b', 'utf-8') as templatesInputFile:
    treader = csv.reader(templatesInputFile)
    langtemps = collections.defaultdict(dict)
    for lang, template, parameter, value in treader:
        if lang.lower() in langtemps:
            tempParams = langtemps[lang.lower()]
        else:
            tempParams = collections.defaultdict(dict)
        if template.lower() in tempParams:
            paramvals = tempParams[template.lower()]
        else:
            paramvals = collections.defaultdict(list) 
        paramvals[parameter.lower()].append(value.lower())
        tempParams[template.lower()] = paramvals
        langtemps[lang.lower()] = tempParams

threadLock = threading.Lock()
print langtemps
i = 0
for lang in langtemps.keys():
    i+=1
    newthread = langProcessingThread(lang, langtemps, i)
    newthread.start()
    threads.append(newthread)
        
# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
        
