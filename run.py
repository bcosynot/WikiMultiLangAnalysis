# -*- coding: utf-8 -*-
import pywikibot;
import csv;
import collections;
import codecs;
import pywikibot.pagegenerators

with codecs.open('./input/templates.csv', 'r', 'utf-8') as templatesInputFile:
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
    print langtemps
    rows = []
    for lang in langtemps.keys():
        site = pywikibot.Site(lang, "wikipedia")
        allpages = site.allpages(namespace=1, filterredir=False)
        tempparams = langtemps[lang]
        templates = tempparams.keys();
        print templates
        i = 0
        for page in allpages:
            templatesWithParams = page.templatesWithParams()
            for templatepage,parametervalues in templatesWithParams:
                template = templatepage.title().split(":")[1] 
                if template in templates:
                    parameters = langtemps[lang][template].keys()
                    for parameter in parameters:
                        values = langtemps[lang][template][parameter]
                        for parametervalue in parametervalues:
                            if parametervalue.split("=")[0] == parameter and parametervalue.split("=")[1] in values:
                                row=[lang,page.title(),parametervalue.split("=")[1]]
                                rows.append(row)
            i+=1
            if(i%100==0):
                print i
                print len(rows)
        print "All pages processed. Writing."
        print rows
        with codecs.open('./output/templates_details.csv', 'wb', 'utf-8') as outputFile:
            templatedetailswriter = csv.writer(outputFile)
            for row in rows:
                templatedetailswriter.writerow(row);
            

with codecs.open('./input/categories.csv', 'r', 'utf-8') as inputFile:
    reader = csv.reader(inputFile, delimiter=",")
    d = collections.defaultdict(list)
    for k, v in reader:
        d[k].append(v)
pagerows = []
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


