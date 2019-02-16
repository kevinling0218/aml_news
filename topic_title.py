#%% import
import pandas as pd
import json


def topic_title(params):
    #%% Load data
    file = params['file']
    news = pd.read_pickle(f"data_processed/{file}_topics_with_sentiment.pkl")

    if 'topic_title' in news.columns:
        news.drop(columns='topic_title', inplace=True)

    #%% Find cluster center
    if False:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import utility.string_clean as string_clean
        from nltk.tokenize import word_tokenize
        import numpy as np

        news["clustering_text"] = news["full_title"].map(str) + ". " + news["abstract"].map(str)

        # Remove numbers
        # news['clustering_text'] = news['clustering_text'].apply(string_clean.remove_numbers)

        # Remove punctuations
        news['clustering_text'] = news['clustering_text'].apply(string_clean.remvoe_punctuation)

        # Remove single character
        # news['clustering_text'] = news['clustering_text'].apply(string_clean.remove_single_character)

        def tokenize(s): return " ".join(word_tokenize(s))

        news['clustering_text'] = news['clustering_text'].apply(tokenize)

        tfidf = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 3)).fit_transform(
            news['clustering_text'].values.astype('U'))

        news.drop(columns='clustering_text', inplace=True)
        # cosine similarity
        similarity = tfidf * tfidf.T

        distance = 1 - similarity.todense()

        def get_cluster_center(news, topic_id, distance):
            indexes = news[news.topic_id == topic_id].index
            within_cluster_distance = distance[np.ix_(indexes, indexes)]
            return news.loc[indexes[np.argmin(np.sum(within_cluster_distance, axis=0))], 'title']

        topic_ids = news.topic_id.drop_duplicates()
        cluster_center = [(topic_id, get_cluster_center(news, topic_id, distance)) for topic_id in topic_ids]
        topic_title = pd.DataFrame(cluster_center, columns=['topic_id', 'topic_title'])

        news = news.merge(topic_title, on='topic_id')

    #%% Find most important news for each topic
    most_important_news = news.groupby('topic_id')['article_score'].rank(ascending=False, method='first').reset_index()
    most_important_news = most_important_news.loc[most_important_news['article_score'] == 1, 'index']
    most_important_news = news.loc[most_important_news, ['topic_id', 'title']].rename(columns={'title': 'topic_title'})

    news = news.merge(most_important_news, on='topic_id')

    news.to_csv("data_processed/"+file+"_topics_with_sentiment.csv", index=False, encoding="utf-8")
    news.to_csv(f"app/static/data/{file}_topics_with_sentiment.csv", index=False, encoding="utf-8")
    news.to_pickle(f"data_processed/{file}_topics_with_sentiment.pkl")
