#%% import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nltk.stem import PorterStemmer

from wordcloud import WordCloud, STOPWORDS
import utility.string_clean as string_clean

import json

def word_cloud(params):
    file = params['file']

    #%% Load data
    news = pd.read_pickle("data_processed/"+file+"_topics.pkl")

    #%% Clean text
    # Remove numbers
    news['full_title'] = news['full_title'].apply(string_clean.remove_numbers)

    # Remove punctuations
    news['full_title'] = news['full_title'].apply(string_clean.remvoe_punctuation)

    # Remove single character
    news['full_title'] = news['full_title'].apply(string_clean.remove_single_character)

    # Stemming
    ps = PorterStemmer()
    # news['full_title'] = news['full_title'].apply(ps.stem)

    #%% Word Cloud
    wordcloud = WordCloud(width=600,
                          height=600,
                          stopwords=STOPWORDS,
                          background_color='white').generate(' '.join(news['full_title']))

    # fig = plt.figure(figsize=(4, 4))
    # plt.imshow(wordcloud)
    # plt.axis('off')
    # plt.show()
    # fig.savefig("data_processed/"+file+"_wordcloud.png")

    def save_image(data, filename):
        sizes = np.shape(data)
        fig = plt.figure()
        fig.set_size_inches(1. * sizes[0] / sizes[1], 1, forward = False)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(data)
        plt.savefig(filename, dpi=sizes[0], cmap='hot')
        plt.close()

    # save_image(wordcloud, "data_processed/"+file+"_wordcloud.png")
    save_image(wordcloud, f"app/static/img/{file}_wordcloud.png")


    #%% Word Cloud for each topic
    all_topic_id = list(set(news['topic_id'].values))

    for topic_id in all_topic_id:
        topic_news = news.copy()
        topic_news = topic_news[topic_news['topic_id'] == topic_id]

        wordcloud = WordCloud(width=600,
                              height=600,
                              stopwords=STOPWORDS,
                              background_color='white').generate(' '.join(topic_news['full_title']))

        save_image(wordcloud, f"app/static/img/{file}_wordcloud_topic_{topic_id}.png")
