# -*- coding: utf-8 -*-
import csv
import collections
import codecs
import pywikibot.pagegenerators
import threading

class categoryProcessingThread(threading.Thread):
    def __init__(self, site, lang, categorytitles):
        threading.Thread.__init__(self)
        self.site = site
        self.lang = lang
        self.categorytitles = categorytitles
        
    def run(self):
        threading.Thread.run(self)
        print "Processing language " + self.lang + " with " , len(self.categorytitles), " categories"
        sitesize = self.site.siteinfo["statistics"]["articles"]
        print "Site size: ", sitesize
        for categoryTitle in self.categorytitles:
            pagerows = []
            countrows = []
            print "Fetching details for " + categoryTitle;
            category = pywikibot.Category(self.site, categoryTitle);
            totalSize = 0;
            for pagefromcat in pywikibot.pagegenerators.CategorizedPageGenerator(category, recurse=True):
                if(pagefromcat.namespace() == 0 or pagefromcat.namespace() == 1):
                    totalSize += 1
                    pagerow = [self.lang, categoryTitle, pagefromcat.namespace(), pagefromcat.title()];
                    pagerows.append(pagerow)
            with codecs.open('./output/categories_pages.csv', 'a+b', 'utf-8') as outputfile:
                datawriter = csv.writer(outputfile)
                datawriter.writerows(pagerows)
            countrow = [self.lang, categoryTitle, totalSize]
            countrows.append(countrow)
            with codecs.open('./output/categories_counts.csv', 'a+b', 'utf-8') as outputfile:
                countswriter = csv.writer(outputfile)
                countswriter.writerows(countrows);

threads = []
d = collections.defaultdict(list)
with codecs.open('./input/categories.csv', 'r', 'utf-8') as inputFile:
    reader = csv.reader(inputFile, delimiter=",")
    for k, v in reader:
        d[k].append(v)
threadLock = threading.Lock()
for lang in d.viewkeys():
    categorytitles = d[lang];
    site = pywikibot.Site(lang, "wikipedia")
    newthread = categoryProcessingThread(site, lang, categorytitles)
    newthread.start()
    threads.append(newthread)
    
# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
