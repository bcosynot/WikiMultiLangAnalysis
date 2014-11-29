# -*- coding: utf-8 -*-
import csv
import collections
import codecs
import pywikibot
import threading

class templateProcessingThread(threading.Thread):
    def __init__(self, threadnumber, pageslist, tempparams, templates):
        print "Starting thread number ", threadnumber, " with " , len(pageslist) , " pages"
        rows = []
        i = 0
        for page in pageslist:
            templatesWithParams = page.templatesWithParams()
            for templatepage, parametervalues in templatesWithParams:
                if ":" in templatepage.title():
                    template = templatepage.title().split(":")[1] 
                    if template in templates:
                        parameters = langtemps[lang][template].keys()
                        for parameter in parameters:
                            values = langtemps[lang][template][parameter]
                            for parametervalue in parametervalues:
                                if parametervalue.split("=")[0] == parameter and parametervalue.split("=")[1] in values:
                                    row = [lang, page.title(), parametervalue.split("=")[1]]
                                    rows.append(row)
            i += 1
            if(i % 500 == 0):
                print i + " articles completed in thread " + threadnumber + " out of ", len(pageslist)
                with codecs.open('./output/templates_details.csv', 'a+b', 'utf-8') as outputFile:
                    templatedetailswriter = csv.writer(outputFile)
                    print "Writing " , len(rows) , " lines in thread " + threadnumber
                    templatedetailswriter.writerows(rows);
                    rows = []
                    
threads = []
with codecs.open('./input/templates.csv', 'r+b', 'utf-8') as templatesInputFile:
    treader = csv.reader(templatesInputFile, delimiter=",")
    langtemps = collections.defaultdict(dict)
    for lang, template, parameter, value in treader:
        if lang in langtemps:
            tempParams = langtemps[lang]
        else:
            tempParams = collections.defaultdict(dict)
        if template in tempParams:
            paramvals = tempParams[template]
        else:
            paramvals = collections.defaultdict(list) 
        paramvals[parameter].append(value)
        tempParams[template] = paramvals
        langtemps[lang] = tempParams
    for lang in langtemps.keys():
        site = pywikibot.Site(lang, "wikipedia")
        sitesize = site.siteinfo["statistics"]["articles"]
        print "Site size: ", sitesize
        allpages = site.allpages(namespace=1)
        tempparams = langtemps[lang]
        templates = tempparams.keys();
        i = 0
        threadnumber = 0
        pageslist = []
        for page in allpages:
            i += 1
            pageslist.append(page)
            if i % 10000 == 0:
                threadnumber += 1
                newthread = templateProcessingThread(threadnumber, pageslist, tempparams, templates)
                threads.append(newthread)
                pageslist = []
        print i
        print "Starting last thread"
        threadnumber += 1
        newthread = templateProcessingThread(threadnumber, pageslist, tempparams, templates)
        threads.append(newthread)
        print "All pages processed."
        
# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
        
