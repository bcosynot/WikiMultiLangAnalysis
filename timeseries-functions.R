library(data.table);
library(forecast);
library(ggplot2);

ARTVIEW_DATADIR = 'datasets/french';
PLOT_DATADIR = '/export/scratch/WikiMultiLangAnalysis/plots/ru';

dt_replace_na = function(DT) {
  # Fast replace of NAs with 0 in a data table, courtesy of
  # http://stackoverflow.com/a/7249454
  for (j in seq_len(ncol(DT)))
    set(DT,which(is.na(DT[[j]])), j, 0);
}

ts_analyse_article = function(poparticles, pageviews) {
  ## For each article in poparticles, use redirmap to find redirects,
  ## then use pageviews to get view data, combine with redirects,
  ## then use ARIMA models to check trends.  Returns
  ## a data.table with page IDs and boolean columns for upwards and
  ## downwards trending articles.
  
  res_pageids = c();
  res_uptrends = c();
  res_downtrends = c();
  res_errors = c();
  
  ## First and last dates for which we count view data
  start_date = as.IDate('2014-09-08');
  end_date = as.IDate('2014-11-30');
  
  ## Last date we use as a basis for initial trend analysis
  last_trend_date = as.IDate('2014-11-02');
  first_view_date = as.IDate('2014-11-03');
  
  viewdates = as.IDate(
    seq.Date(first_view_date,
             end_date,
             by=1)
  );
  
  ## Table containing all dates in our date range, we'll join against
  ## this table and set any non-matches to 0.
  datetable = data.table(fulldate=as.IDate(
    seq.Date(start_date,
             end_date, by=1)
  ));
  setkey(datetable, fulldate);
  
  for(art_pageid in poparticles$pageid) {
    ## Did this article trend upwards?
    ## Did this article trend downwards?
    art_downtrend = FALSE;
    art_uptrend = FALSE;
    art_error = FALSE;
    
    #print(paste('Analysing page ID', art_pageid));
    
    views = subset(pageviews, pageid==art_pageid);
    
    #print(paste('got', length(views$views), 'rows of view data'));
    ## Limit to our date range, then aggregate over date and replace
    ## missing dates w/0 (join results in NAs that are replaced)
    views = views[as.IDate(fulldate) >= start_date & as.IDate(fulldate) <= end_date];
    #print('here');
    views = views[, list(totalhits=sum(views)), by='fulldate']
    #print('here3');
    views = views[, fulldate:=as.IDate(fulldate)];
    #print('here2');
    setkey(views, fulldate);
    views = views[datetable];
    #print('here4');
    dt_replace_na(views);
    #print('here5');
    
    ## print(paste('aggregated down to', length(views$totalhits), 'rows of view data'));
    #print('Combined view aggregates, running ARIMA models');
    
    ## Create a time series for the trend data, period is 7 days.
    view_vec = views[as.Date(fulldate) <= last_trend_date]$totalhits;
    trend_ts = ts(view_vec, frequency=7);
    ## NOTE: do not use Cond. Sum of Squares approximation
    trend_model = auto.arima(trend_ts, approximation=FALSE);
    ## For each day ...
    error = tryCatch({
      for(i in 1:length(viewdates)) {
        view_date = viewdates[i];
         print(paste("Forecasting for", view_date));
        ## Forecast the next day
        fcast = forecast(trend_model, h=1, level=c(95,99,99.7,99.9,99.99));
        ## Upper and lower bounds on the 99.7% CI (3 standard deviations)
        ubound = as.numeric(fcast$upper[,3]);
        lbound = as.numeric(fcast$lower[,3]);
        ## Actual value
        actual_views = views[as.Date(fulldate) == view_date]$totalhits;
        
        ## print(paste('ubound =', ubound, 'lbound=', lbound,
        ##            'views=', actual_views));
        
        if(actual_views > ubound) {
          art_uptrend = TRUE;
        }
        if(actual_views < lbound) {
          art_downtrend = TRUE;
        }
        ## Update the model.  This does not change the model order
        ## but updates the parameter estimates.
        ## NOTE: method set to ML so Cond. Sum of Squares is skipped
        view_vec = append(view_vec, actual_views);
        trend_model = Arima(ts(view_vec, frequency=7),
                            order=trend_model$arma[c(1,6,2)], method='ML');
      }
      FALSE;
    }, error=function(e) {
      print(paste('Error:', e));
      print('This error was ignored, moving on...');
      return(TRUE)
    });
    if(error) {
      art_error = TRUE;
    }    
    ## Add to the overall results
    res_pageids = append(res_pageids, art_pageid);
    res_uptrends = append(res_uptrends, art_uptrend);
    res_downtrends = append(res_downtrends, art_downtrend);
    res_errors = append(res_errors, art_error);
  }
  data.table(pageid=res_pageids, is_uptrend=res_uptrends,
             is_downtrend=res_downtrends, is_error=res_errors);
}

make_viewplots = function(dataset, pageviews) {
  ## For each article in the dataset (as identified by its pageid)
  ## make a time series plot for the 28-day period in our analysis.
  
  ## First and last dates which we will plot, as well as date where we'll add a vertical line
  start_date = as.IDate('2014-09-08');
  trend_start_date = as.IDate('2014-11-02');
  end_date = as.IDate('2014-11-30');
  
  ## Table containing all dates in our date range, we'll join against
  ## this table and set any non-matches to 0.
  datetable = data.table(fulldate=as.IDate(
    seq.Date(start_date,
             end_date, by=1)
  ));
  setkey(datetable, fulldate);
  
  for(art_pageid in dataset$pageid) {
    #print(paste('Analysing page ID', art_pageid));
    
      
    views = subset(pageviews, pageid==art_pageid);
    
    ## print(paste('got', length(views$views), 'rows of view data'));
    ## Limit to our date range, then aggregate over date and replace
    ## missing dates w/0 (join results in NAs that are replaced)
    views = views[as.IDate(fulldate) >= start_date & as.IDate(fulldate) <= end_date];
    views = views[, list(totalhits=sum(views)), by='fulldate']
    views = views[, fulldate:=as.IDate(fulldate)];
    setkey(views, fulldate);
    views = views[datetable];
    dt_replace_na(views);
    
    viewplot = ggplot(views, aes(fulldate, totalhits)) + geom_line() + ggtitle(paste('Views for page', art_pageid)) + xlab('') + ylab('Daily views') + geom_vline(xintercept=as.numeric(views$fulldate[57]), linetype=2, colour='red')
    plot_filename = paste0(PLOT_DATADIR, '/viewplot-page-', art_pageid, '.pdf');
    ggsave(filename=plot_filename, plot=viewplot, units='in', width=8.8, height=4.8);
  }
}
print("Reading data");
allviews5rows =  read.table('/scratch/chork/morten/2015-multilingual-popqual/datasets/cleaned-pageview-counts-pt.txt',  header = TRUE, nrows=5);
classes = sapply(allviews5rows , class);
classes;
allviews = data.table(read.table('/scratch/chork/morten/2015-multilingual-popqual/datasets/cleaned-pageview-counts-pt.txt', header = TRUE, colClasses=classes));
#allviews;
nrow(allviews);
allviews[,cumviews := views];
allviews[,views := c(0L, diff(cumviews)), by='pageid'];
allviews[as.Date(fulldate) == as.IDate('2014-09-08'), views := cumviews];
#allviews;
print("Creating subset"); 
shouldbe_FAs = subset(allviews, category=="FA");
shouldbe_FAs;
## Verify classifier performance
## 1: pick 150 articles at random
testset = shouldbe_FAs[sample(.N, 150)];
## 2: analyse all of them
testset.trends = ts_analyse_article(testset, allviews);
## 3: do we have 100 articles that didn't fail?
length(testset.trends$pageid[testset.trends$is_error == FALSE]);
## Yes, so pick 100 of them
testset.trends = testset.trends[is_error == FALSE][sample(.N, 100)];

## Re-run analysis after changing to 99.7% confidence interval
testset.trends = ts_analyse_article(testset.trends, allviews);

#print("making plots");
#make_viewplots(testset.trends, allviews);

## I've now coded the 100 randomly drawn pages.
testset.human = data.table(read.table('/export/scratch/WikiMultiLangAnalysis/french-timeseries-testsets.txt', header=TRUE));
setkey(testset.trends, pageid);
setkey(testset.human, pageid);

testset.full = testset.human[testset.trends];
## True positives
length(testset.full[really_trending == TRUE & is_uptrend == TRUE]$pageid);
## True negatives
length(testset.full[really_trending == FALSE & is_uptrend == FALSE]$pageid);
## False positives
length(testset.full[really_trending == FALSE & is_uptrend == TRUE]$pageid);
## False negatives
length(testset.full[really_trending == TRUE & is_uptrend == FALSE]$pageid);


