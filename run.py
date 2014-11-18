# -*- coding: utf-8 -*-
import pywikibot;

def getCategoryTitlesForLang(lang):
    if(lang == "tr"):
        return  {u"Kategori:SM-Sınıf maddeler", u"Kategori:SL-Sınıf maddeler",
                  u"Kategori:A-Sınıf maddeler", u"Kategori:KM-Sınıf maddeler",
                  u"Kategori:B-Sınıf maddeler", u"Kategori:C-Sınıf maddeler",
                  u"Kategori:Başlangıç-Sınıf maddeler", u"Kategori:Taslak-Sınıf maddeler"};
                  
    if(lang == "zh"):
        prefix = "Category:";
        return {prefix+"特色级条目",prefix+"甲级条目",prefix+"优良级条目",
                prefix+"乙级条目",prefix+"丙级条目",prefix+"初级条目",
                prefix+"小作品级条目",prefix+"特色列表级条目",prefix+"列表级条目"};

def run():
    lang = "zh";
    site = pywikibot.Site(lang, "wikipedia");
    categoryTitles = getCategoryTitlesForLang(lang);
    for categoryTitle in categoryTitles: 
        category = pywikibot.Category(site, categoryTitle);
        print category;
        #for article in category.articles():
        #    print article;
        print "Category size: " , category.categoryinfo.get("size");
        print "Number of subcats: " , category.categoryinfo.get("subcats");
        print "Loading subcat data...";
        totalSize = 0;
        # print len(category.subcategories);
        for subcat in category.subcategories(True):
            # print subcat;
            totalSize = totalSize + subcat.categoryinfo.get("size");
        print "Total size: " , totalSize;

run();

