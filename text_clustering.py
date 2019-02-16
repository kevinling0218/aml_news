#%% import
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from string import punctuation
from sklearn.preprocessing import MinMaxScaler
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')

from sklearn.cluster import DBSCAN

import utility.string_clean as string_clean
import importlib
importlib.reload(string_clean)


def text_clustering(params):
    #%% Load data
    file = params['file']

    if not pd.isnull(params['micro_files']):
        micro_files = params['micro_files'].split("|")
        news_original = pd.DataFrame()
        for micro_file in micro_files:
            try:
                news_original = pd.concat([news_original, pd.read_csv("data_processed/"+micro_file+"_news_english.csv", encoding="utf-8")], axis=0)
            except:
                print(f"{micro_file}_news_english.csv does not exist!")
                continue
    else:
        news_original = pd.read_csv("data_processed/"+file+"_news_english.csv", encoding="utf-8")

    #%% Combine duplicate news
    news_original = news_original.sort_values('search_rank').groupby('href').head(1)

    #%% Clean text
    news = news_original.copy()
    news["clustering_text"] = news["full_title"].map(str) + ". " +news["abstract"].map(str)

    # Remove numbers
    # news['clustering_text'] = news['clustering_text'].apply(string_clean.remove_numbers)

    # Remove punctuations
    news['clustering_text'] = news['clustering_text'].apply(string_clean.remvoe_punctuation)

    # Remove single character
    # news['clustering_text'] = news['clustering_text'].apply(string_clean.remove_single_character)

    # Stemming
    ps = PorterStemmer()
    # news['clustering_text'] = news['clustering_text'].apply(ps.stem)

    def tokenize(s): return " ".join(word_tokenize(s))
    news['clustering_text'] = news['clustering_text'].apply(tokenize)

    #%% TF-IDF
    tfidf = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 3)).fit_transform(news['clustering_text'].values.astype('U'))

    # cosine similarity
    similarity = tfidf * tfidf.T

    distance = 1-similarity.todense()

    #%% DBSCAN
    db = DBSCAN(eps=0.85, min_samples=2, metric='precomputed').fit(distance)

    #get labels
    labels = db.labels_

    #get number of clusters
    no_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print('No of clusters:', no_clusters)

    #%% Rank topics
    # assign cluster labels
    news = news_original.copy()
    news['topic_id'] = labels

    # for standalone articles, assign negative cluster labels
    outlier = news['topic_id'] == -1
    labels_outlier = news.loc[outlier, 'article_id']\
        .reset_index()\
        .drop('index', axis=1)\
        .reset_index()\
        .rename(columns={'index': 'topic_id_outlier'})
    labels_outlier['topic_id_outlier'] = -1*(labels_outlier['topic_id_outlier'] + 1)

    news = news.merge(labels_outlier, how='left', on='article_id')
    outlier = news['topic_id'] == -1
    news.loc[outlier, 'topic_id'] = news.loc[outlier, 'topic_id_outlier']
    news.drop(['topic_id_outlier'], axis=1, inplace=True)

    # compute article score
    news['search_rank_score'] = 10/(9+news['search_rank'])
    news['related_article_count_score'] = news['related_article_count'] / max(news['related_article_count'])
    news['related_article_count_score'].fillna(0, inplace=True)
    news['article_score'] = news['search_rank_score'] + 0.5*news['related_article_count_score']

    # compute topic score
    # topic_score = sum of(top three article scores)
    news['article_score'] = pd.to_numeric(news['article_score'])
    topic_score = news.groupby('topic_id')['article_score']\
        .apply(lambda grp: grp.nlargest(3).sum())\
        .reset_index()\
        .rename(columns={'article_score': 'topic_score'})

    news = news.merge(topic_score, on='topic_id')

    # rank topics
    news = news.sort_values(['topic_score', 'article_score'], ascending=[False, False]) \
               .loc[:, ['topic_id',
                        'article_id',
                        'date',
                        'title',
                        'full_title',
                        'media',
                        'language',
                        'topic_score',
                        'article_score',
                        'href',
                        'thumbnail',
                        'abstract']]

    news['topic_id'] = news['topic_id'].astype(int)
    news['date'] = pd.to_datetime(news['date'])

    # pick top 30 topics
    top_topic_id = news['topic_id'].unique()[:30]
    news = news[news['topic_id'].isin(top_topic_id)]

    #%% For each cluster, find cluster center
    def get_cluster_center(news, topic_id, distance):
        indexes = news[news.topic_id == topic_id].index
        within_cluster_distance = distance[np.ix_(indexes, indexes)]
        return news.loc[indexes[np.argmin(np.sum(within_cluster_distance, axis=0))], 'title']

    topic_ids = news.topic_id.drop_duplicates()
    cluster_center = [(topic_id, get_cluster_center(news, topic_id, distance)) for topic_id in topic_ids]
    topic_title = pd.DataFrame(cluster_center, columns=['topic_id', 'topic_title'])

    news = news.merge(topic_title, on='topic_id')


    #%% temp
    # a = news.loc[news['topic_id'] == 2].copy()
    # a["clustering_text"] = a["title"].map(str) + ". " +a["abstract"].map(str)
    # text = a['clustering_text'].str.cat(sep=' \n')
    # text_file = open("news_cluster.txt", "w", encoding="utf-8")
    # text_file.write(text)
    # text_file.close()
    #%% temp end

    # scale scores
    news['topic_score'] = (news['topic_score'] - min(news['topic_score'])) / (max(news['topic_score']) - min(news['topic_score']))
    news['article_score'] = (news['article_score'] - min(news['article_score'])) / (max(news['article_score']) - min(news['article_score']))

    news.to_csv("data_processed/"+file+"_topics.csv", index=False, encoding="utf-8")
    news.to_pickle("data_processed/"+file+"_topics.pkl")
