# -*- coding: utf-8 -*-
import pywikibot;
import csv;
import collections;
import codecs;

with codecs.open('./input/categories.csv', 'r', 'utf-8') as inputFile:
    reader = csv.reader(inputFile, delimiter=",")
    d = collections.defaultdict(list)
    for k, v in reader:
        d[k].append(v)
with codecs.open('./output/categories_counts.csv', 'wb', 'utf-8') as outputFile:
    countswriter = csv.writer(outputFile)
    for lang in d.viewkeys():
        categoryTitles = d[lang];
        site = pywikibot.Site(lang, "wikipedia");
        print "Processing language: " + lang;
        for categoryTitle in categoryTitles:
            print "Fetching details for " + categoryTitle;
            category = pywikibot.Category(site, categoryTitle);
            totalSize = 0;
            for subcat in category.subcategories(True):
                totalSize = totalSize + subcat.categoryinfo.get("size");
            row = [lang, categoryTitle, category.categoryinfo.get("subcats"), totalSize];
            countswriter.writerow(row);            


