#%% import
import pandas as pd
from langdetect import detect


def get_full_title(row):
    title = row['title']
    if title.endswith('...'):
        href = row['href']
        if href.endswith('/'):
            href = href[:-1]
        href = href.split('/')[-1].lower().replace('-', ' ')
        href_words = href.split(' ')
        title_words = title.lower().split(' ')

        if (len(title_words) - len([i for i in title_words if i in href_words]) < 3) | (len([i for i in title_words if i in href_words]) / len(title_words) > 0.5):
            title = href
    return title


def detect_language(x):
    try:
        return detect(x)
    except:
        return 'null'

def clean_news(params):
    file = params['file']
    try:
        news = pd.read_csv("data_processed/" + file + "_news.csv", encoding="utf-8")
    except:
        print(f"{file}_news.csv does not exist!")
        return

    #%% Remove non-English articles
    news['language'] = news['title'].apply(detect_language)
    news = news.loc[news['language'] == 'en']

    if len(news) > 0:
        #%% Get full title
        news['full_title'] = news.apply(get_full_title, axis=1)

        #%% Clean text
        news['media'].fillna("", inplace=True)

        # news = news.loc[~news['title'].str.contains("profit")]

        news = news.loc[news['media'] != "The Motley Fool Singapore"]
        # news = news.loc[news['media'] != "finews.asia"]
        news = news.loc[news['media'] != "Red Sports"]
        news = news.loc[~news['title'].str.contains("Broker's take")]
        news = news.loc[~news['title'].str.contains("Stocks to watch")]
        news = news.loc[~news['title'].str.contains("inflation")]

        news = news.loc[~news['title'].str.contains("ST Run")]
        news = news.loc[~news['title'].str.contains("AOTY HK series")]
        news = news.loc[~news['title'].str.contains("Brokers' Call")]
        news = news.loc[~news['title'].str.contains("Winners and photos")]
        news = news.loc[~news['title'].str.contains("Daily Markets Briefing")]

        if file == "ocbc":
            news = news.loc[~news['title'].str.contains("Internet scam")]
            news = news.loc[~news['title'].str.contains("love scam")]
            news = news.loc[news['title'] != 'DBS CEO signals bank may be past worst of energy-loan issues']

        news.to_csv("data_processed/"+file+"_news_english.csv", index=False, encoding="utf-8")
