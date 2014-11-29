# -*- coding: utf-8 -*-
import csv
import collections
import codecs
import pywikibot.pagegenerators
import threading

class categoryProcessingThread(threading.Thread):
    def __init__(self, site, lang, categorytitles):
        print "Processing language " + lang + " with " , len(categorytitles), " categories"
        sitesize = site.siteinfo["statistics"]["articles"]
        print "Site size: ", sitesize
        for categoryTitle in categorytitles:
            pagerows = []
            countrows = []
            print "Fetching details for " + categoryTitle;
            category = pywikibot.Category(site, categoryTitle);
            totalSize = 0;
            for pagefromcat in pywikibot.pagegenerators.CategorizedPageGenerator(category, recurse=True):
                if(pagefromcat.namespace() == 0 or pagefromcat.namespace() == 1):
                    totalSize += 1
                    row = [lang, categoryTitle, pagefromcat.namespace(), pagefromcat.title()];
                    pagerows.append(row)
            with codecs.open('./output/categories_pages.csv', 'a+b', 'utf-8') as outputfile:
                datawriter = csv.writer(outputfile)
                datawriter.writerows(pagerows)
            row = [lang, categoryTitle, totalSize]
            countrows.append(row)
            with codecs.open('./output/categories_counts.csv', 'a+b', 'utf-8') as outputfile:
                countswriter = csv.writer(outputfile)
                countswriter.writerows(countrows);

threads = []
d = collections.defaultdict(list)
with codecs.open('./input/categories.csv', 'r', 'utf-8') as inputFile:
    reader = csv.reader(inputFile, delimiter=",")
    for k, v in reader:
        d[k].append(v)
for lang in d.viewkeys():
    categorytitles = d[lang];
    site = pywikibot.Site(lang, "wikipedia")
    newthread = categoryProcessingThread(site, lang, categorytitles)
    threads.append(newthread)
    
# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
