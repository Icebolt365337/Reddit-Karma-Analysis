import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ast import literal_eval
from scipy.stats import gaussian_kde
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import PunktSentenceTokenizer
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import webtext
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

dir_path = os.path.dirname(os.path.realpath(__file__));
file_path_2 = str(os.path.join(dir_path, 'commentsposts.csv'));
df = pd.read_csv(file_path_2);

df['Top10 Ratio'] = df['Top10 Scores']/df['Total Karma'];
df['Top Subreddits'] = df['Top Subreddits'].apply(literal_eval);
df['Dates'] = df['Dates'].apply(literal_eval);
df['Content'] = df['Content'].apply(literal_eval);
df['Scores'] = df['Scores'].apply(literal_eval);
df['Sentiment'] = df['Sentiment'].apply(literal_eval);

def top10ToKarma(df):
    plt.scatter(np.log10(df['Total Karma']), df['Top10 Ratio'], alpha=0.02);
    plt.title('log10(Total Karma), to Top10 Ratio');
    plt.xlabel('log10(Total Karma)');
    plt.ylabel('Top10 Ratio');
    plt.ylim(0, 10);
    plt.show();

def commonSubreddits(df):
    subreddits = df[['Top Subreddits', 'Scores']].explode(['Top Subreddits', 'Scores']).groupby('Top Subreddits');
    byTotal = subreddits.sum();
    byTotal['Average Karma'] = byTotal['Scores']/subreddits.count()['Scores'];
    byTotal = byTotal.sort_values(by='Scores', ascending=False).head(10).reset_index();
    fig, axes = plt.subplots(1, 3);
    byTotal[['Top Subreddits', 'Scores']].plot.bar(ax=axes[0]);
    byTotal[['Top Subreddits', 'Average Karma']].plot.bar(ax=axes[1]);
    axes[0].set_title('Subreddits by Total Scores');
    axes[0].set_xlabel('Subreddits');
    axes[0].set_ylabel('Scores');
    axes[1].set_title('Subreddits by Average Score');
    axes[1].set_xlabel('Subreddits');
    axes[2].table(cellText=byTotal['Top Subreddits'].reset_index().values.tolist(), loc='center');
    axes[2].axis('off');
    plt.show();

def timeDensity(df):
    subreddits = pd.to_datetime(df['Dates'].explode()).value_counts().sort_index();
    subreddits = subreddits.reindex(pd.date_range(subreddits.index[0], subreddits.index[-1]), fill_value=0);
    bins = np.linspace(-1, len(subreddits), 200);
    plt.plot(bins, gaussian_kde(np.arange(len(subreddits)), bw_method=0.2, weights=subreddits)(bins), lw=2);
    plt.xticks(np.array([0,1000,2000,3000,4000,5000,6000]), np.array([subreddits.index[0].strftime('%m/%d/%y'), subreddits.index[1000].strftime('%m/%d/%y'), subreddits.index[2000].strftime('%m/%d/%y'), subreddits.index[3000].strftime('%m/%d/%y'), subreddits.index[4000].strftime('%m/%d/%y'), subreddits.index[5000].strftime('%m/%d/%y'), subreddits.index[6000].strftime('%m/%d/%y')]));
    plt.title('Submissions over time');
    plt.xlabel('Time');
    plt.ylabel('Density');
    plt.show();

def sentimentMarker(df):
    sid = SentimentIntensityAnalyzer();
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle');
    global i;
    i = 0;
    def sentimentFunc(textList):
        scores = [];
        for text in textList:
            score = sid.polarity_scores(text)['compound'];
            if score > 0.25:
                scores.append('Positive');
            elif score < -0.25:
                scores.append('Negative');
            else:
                scores.append('Neutral');
        global i;
        i += 1;
        if (i%100 == 0):
            print(str(i)+" users done");
        return scores;
    return df['Content'].apply(sentimentFunc);

def sentimentAnalysis1(df):
    df1 = df['Sentiment'];
    vals = df1.explode().value_counts();
    vals = vals.reindex(['Negative', 'Neutral', 'Positive']);
    vals.plot.barh();
    plt.title('Total submissions by Sentiment');
    plt.xlabel('# of Submissions');
    plt.show();

def sentimentAnalysis2(df):
    df1 = df[['Sentiment', 'Scores']];
    sentimentKarma = df1.explode(['Sentiment', 'Scores']);
    sentimentKarma = sentimentKarma.groupby('Sentiment').mean();
    sentimentKarma.plot.barh();
    plt.title('Average Score by Sentiment');
    plt.xlabel('Average Score');
    plt.show();

def sentimentAnalysis3(df):
    df1 = df[['Top Subreddits', 'Sentiment', 'Dates', 'Scores']];
    def aggFunc(df):
        neutCount = posCount = negCount = 0;
        neutAvg = posAvg = negAvg = 0;
        splitCount = df[['Sentiment', 'Dates']].groupby('Sentiment')['Dates'].count();
        splitKarma = df[['Sentiment', 'Scores']].groupby('Sentiment')['Scores'].mean();
        if 'Neutral' in splitCount.index:
            neutCount = splitCount.loc['Neutral'];
        if 'Positive' in splitCount.index:
            posCount = splitCount.loc['Positive'];
        if 'Negative' in splitCount.index:
            negCount = splitCount.loc['Negative'];
        if 'Neutral' in splitKarma.index:
            neutAvg = splitKarma.loc['Neutral'];
        if 'Positive' in splitKarma.index:
            posAvg = splitKarma.loc['Positive'];
        if 'Negative' in splitKarma.index:
            negAvg = splitKarma.loc['Negative'];
        return pd.DataFrame({'Total Count':[df.shape[0]], 'Neutral Count': [neutCount], 'Positive Count': [posCount], 'Negative Count':[negCount], 'Neutral Karma':[neutAvg], 'Positive Karma':[posAvg], 'Negative Karma': [negAvg]});
    df1 = df1.explode(['Top Subreddits', 'Sentiment', 'Dates', 'Scores']);
    sentimentTopic = df1.groupby('Top Subreddits').apply(aggFunc, include_groups=False).sort_values('Total Count', ascending=False).head(10);
    sentimentTopic = sentimentTopic.droplevel(level=1).sort_values('Total Count').drop('Total Count', axis=1);
    fig, axes = plt.subplots(2,1);
    sentimentTopic[['Neutral Count', 'Positive Count', 'Negative Count']].plot.barh(ax=axes[0]);
    axes[0].set_title('Number of Submissions by Sentiment');
    axes[0].set_xlabel('');
    axes[0].set_ylabel('Subreddits');
    sentimentTopic[['Neutral Karma', 'Positive Karma', 'Negative Karma']].plot.barh(ax=axes[1]);
    axes[1].set_title('Average Score per Submission by Sentiment');
    axes[1].set_xlabel('Score');
    axes[1].set_ylabel('Subreddits');
    plt.show();

def sentimentTimeDensity(df):
    dateSub = df[['Dates', 'Sentiment', 'Scores']].explode(['Dates', 'Sentiment', 'Scores']);
    dateSub = pd.pivot_table(dateSub, values = 'Scores', index = 'Dates', columns = ['Sentiment'], aggfunc = 'count').fillna(0).astype(int);
    dateSub.index = pd.to_datetime(dateSub.index, format="%m/%d/%y");
    dateSub = dateSub.reindex(pd.date_range(dateSub.index[0], dateSub.index[-1]), fill_value=0);
    bins = np.linspace(-1, dateSub.shape[0], 200);
    fig, ax = plt.subplots(figsize=(12, 4))
    for column, color in zip(dateSub.columns, plt.cm.Set2.colors):
        kde = gaussian_kde(np.arange(dateSub.shape[0]), bw_method=0.2, weights=dateSub[column])
        ax.plot(bins, kde(bins), lw=2, color=color, label=column)
        ax.fill_between(bins, kde(bins), color=color, alpha=0.2)
        ax.set_xlim(bins[0], bins[-1])
    plt.title('Submissions (by Sentiment) over time');
    plt.xticks(np.array([0,1000,2000,3000,4000]), np.array([dateSub.index[0].strftime('%m/%d/%y'), dateSub.index[1000].strftime('%m/%d/%y'), dateSub.index[2000].strftime('%m/%d/%y'), dateSub.index[3000].strftime('%m/%d/%y'), dateSub.index[4000].strftime('%m/%d/%y')]));
    plt.ylabel('Density');
    plt.legend();
    plt.show();

sentimentAnalysis1(df);