import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
from datetime import datetime
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
from sklearn.model_selection import train_test_split
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import mean_squared_error


dir_path = os.path.dirname(os.path.realpath(__file__));
file_path_1 = str(os.path.join(dir_path, 'data.csv'));
df1 = pd.read_csv(file_path_1);
file_path_2 = str(os.path.join(dir_path, 'commentsposts.csv'));
df = pd.read_csv(file_path_2);
#bools = df['Total Karma'] < 100000
#df = df[bools]

df['Creation'] = 2025-df1['Creation'].astype(int);
df['Top Subreddits'] = df['Top Subreddits'].apply(literal_eval);
df['Dates'] = df['Dates'].apply(literal_eval);
df['Content'] = df['Content'].apply(literal_eval);
df['Sentiment'] = df['Sentiment'].apply(literal_eval);
df['Scores'] = df['Scores'].apply(literal_eval);

sentimentTopic = df['Sentiment'].apply(lambda x: pd.Series(x).value_counts()).fillna(0).astype(int);

def removeDay(ls):
    monthls = [];
    for date in ls:
        comps = date.split('/');
        monthls.append(comps[0]+'/'+comps[2]);
    return monthls;

df['Dates'] = df['Dates'].apply(removeDay);

def sentimentSubreddit(df):
    df1 = df[['Top Subreddits', 'Sentiment']].explode(['Top Subreddits', 'Sentiment']);
    def aggFunc(df):
        neutCount = posCount = negCount = 0;
        splitCount = df.value_counts();
        if 'Neutral' in splitCount.index:
            neutCount = splitCount['Neutral'];
        if 'Positive' in splitCount.index:
            posCount = splitCount['Positive'];
        if 'Negative' in splitCount.index:
            negCount = splitCount['Negative'];
        return pd.DataFrame({'Neutral': [neutCount], 'Positive': [posCount], 'Negative':[negCount]});
    sentimentTopic = df1.groupby('Top Subreddits').apply(aggFunc, include_groups=False);
    sentimentTopic = sentimentTopic.droplevel(level=1);
    return sentimentTopic;

sentSub = sentimentSubreddit(df).astype(int);

def userSubSent(ls):
    i = 0;
    subDict = {};
    subLs = ls['Top Subreddits'];
    sentLs = ls['Sentiment'];
    subDict['SubSentAvg'] = 0;
    subDict['SubTotAvg'] = 0;
    for sub, sent in zip(subLs, sentLs):
        i += 1;
        subDict['SubSentAvg'] += sentSub.loc[sub, sent];
        subDict['SubTotAvg'] += sentSub.loc[sub].sum();
    if (i == 0):
        i = 1;
    subDict['SubSentAvg'] /= i;
    subDict['SubTotAvg'] /= i;
    return pd.Series(subDict);

dateSub = pd.pivot_table(df[['Dates', 'Sentiment', 'Scores']].explode(['Dates', 'Sentiment', 'Scores']), values = 'Scores', index = 'Dates', columns = ['Sentiment'], aggfunc = 'count').fillna(0).astype(int);

def userDates(ls):
    i = 0;
    dateDict = {};
    dateLs = ls['Dates'];
    sentLs = ls['Sentiment'];
    dateDict['dateSentAvg'] = 0;
    dateDict['dateTotAvg'] = 0;
    for date, sent in zip(dateLs, sentLs):
        i += 1;
        dateDict['dateSentAvg'] += dateSub.loc[date, sent];
        dateDict['dateTotAvg'] += dateSub.loc[date].sum();
    if (i == 0):
        i = 1;
    dateDict['dateSentAvg'] /= i;
    dateDict['dateTotAvg'] /= i;
    return pd.Series(dateDict);

scoreSentSub = pd.pivot_table(df[['Top Subreddits', 'Sentiment', 'Scores']].explode(['Top Subreddits', 'Sentiment', 'Scores']), values = 'Scores', index = 'Top Subreddits', columns = ['Sentiment'], aggfunc = 'mean').fillna(0);

def scoreSent(ls):
    i = 0;
    dict = {};
    subLs = ls['Top Subreddits'];
    sentLs = ls['Sentiment'];
    dict['scoreSentAvg'] = 0;
    for sub, sent in zip(subLs, sentLs):
        i += 1;
        dict['scoreSentAvg'] += scoreSentSub.loc[sub, sent];
    if (i == 0):
        i = 1;
    dict['scoreSentAvg'] /= i;
    return pd.Series(dict);

sentSubData = df[['Top Subreddits', 'Sentiment']].apply(userSubSent, axis=1).fillna(0);
dateData = df[['Dates', 'Sentiment']].apply(userDates, axis=1).fillna(0);
scoreData = df[['Top Subreddits', 'Sentiment']].apply(scoreSent, axis=1).fillna(0);
dfProc = pd.concat([df, dateData, sentSubData, scoreData], axis=1).drop(columns=['Username', 'Unnamed: 0', 'Comment Karma', 'Post Karma', 'Total Karma', 'Scores', 'Top10 Ratio', 'Top Subreddits', 'Sentiment', 'Content', 'Dates']);
dfProc = (dfProc-dfProc.mean())/dfProc.std();

#Linear Regression
#errs_df = pd.DataFrame();
#for d in range(1, 8):
#    pl = make_pipeline(PolynomialFeatures(d), LinearRegression(fit_intercept=False));
#    errs = cross_val_score(pl, dfProc, df['Total Karma'], 
#                           cv=KFold(5, shuffle=True), scoring='neg_root_mean_squared_error');
#    errs_df[f'Deg {d}'] = -errs;
#    print('Degree '+str(d)+' done');
#errs_df.index = [f'Fold {i}' for i in range(1, 6)];
#errs_df.index.name = 'Validation Fold';
#print(errs_df.mean());
#print(df['Total Karma'].mean());

#Decision Tree Regression
#dt_regressor = DecisionTreeRegressor()
#param_grid = {
    #'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
    #'max_depth':[5,10,15,20, None]
#}
#grid_search = GridSearchCV(estimator=dt_regressor, scoring='neg_root_mean_squared_error',
#                           param_grid=param_grid, cv=5)
#grid_search.fit(dfProc, df['Total Karma'])
#print(f"Best parameters: {grid_search.best_params_}")
#print(grid_search.best_score_)
#print(grid_search.best_estimator_.tree_)

#Gaussian Regression - needed more memory than my computer could handle
#kernel = DotProduct() + WhiteKernel()
#gpr = GaussianProcessRegressor(kernel=kernel).fit(dfProc, df['Total Karma'])
#print(gpr.score(dfProc, df['Total Karma']))

for i in range(1,101):
    knn_regressor = KNeighborsRegressor(n_neighbors=i) #best is 43, r^2=0.26 (0-1.0)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(knn_regressor, dfProc, df['Total Karma'], cv=kf, scoring='r2')
    print(f"{i} Average R² score across all folds: {np.mean(scores):.2f}")