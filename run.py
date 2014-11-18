# -*- coding: utf-8 -*-
import pywikibot;
import csv;
import collections;

def run():
    reader = csv.reader(open('categories.csv', 'r'))
    d = collections.defaultdict(list);
    for k, v in reader:
        d[k].append(v)
    for lang in d.viewkeys():
        categoryTitles = d[lang];
        site = pywikibot.Site(lang, "wikipedia");
        for categoryTitle in categoryTitles: 
            category = pywikibot.Category(site, categoryTitle);
            print category;
            print "Category size: " , category.categoryinfo.get("size");
            print "Number of subcats: " , category.categoryinfo.get("subcats");
            print "Loading subcat data...";
            totalSize = 0;
            for subcat in category.subcategories(True):
                totalSize = totalSize + subcat.categoryinfo.get("size");
            print "Total size: " , totalSize;

run();

