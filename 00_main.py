#%% import library
import pandas as pd
import time
import random
from selenium.webdriver import Chrome
import importlib


#%% import workflow
import sibs_watchlist; importlib.reload(sibs_watchlist)
import ename; importlib.reload(ename)
import scrape_news; importlib.reload(scrape_news)
import clean_news; importlib.reload(clean_news)
import text_clustering; importlib.reload(text_clustering)
import word_cloud; importlib.reload(word_cloud)
import sentiment_analysis; importlib.reload(sentiment_analysis)
import topic_title; importlib.reload(topic_title)
import final_check; importlib.reload(final_check)

#%% Set parameters
params = pd.read_csv('params.csv')
# indexes = range(186, 192)
indexes = [0,1]
CALL_GOOGLE = True
num_pages = 1
strings = ["crime+OR+investigate+OR+conviction+OR+sentenced", "crime+OR+investigate+OR+conviction+OR+laundering"]


#%% Step 1: Sibs_watchlist
for i, index in enumerate(indexes):
    print(f"Performing SiBs Watchlist check for index: {index}")
    params.loc[index, 'sibs_final'] = sibs_watchlist.sibs_watchlist(params.loc[index].to_dict())
    # print ("The params after Sibs_watchlist is:", params.T)

#%% Step 2: E_name/BAE checklist

for i, index in enumerate(indexes):
    print (f"Performing E_name check for index :{index}")
    params.loc[index, "ename_final"] = ename.ename_result(params.loc[index].to_dict(), factor_number = 1)

#%% Step 3: scrape news
for i, index in enumerate(indexes):
    if i > 0:
        time.sleep(15 + random.randint(1, 10001) / 1000 + 60 * (random.randint(1, 21) <= 1))
    else:
        driver = Chrome(executable_path="/Users/kevinling/desktop/name/chromedriver")
    print(f"scrape news for index: {index}")
    scrape_news.scrape_news(params.loc[index].to_dict(), driver, strings, num_pages)


#%% Step 4: clean news
for i, index in enumerate(indexes):
    print(f"clean news for index: {index}")
    clean_news.clean_news(params.loc[index].to_dict())

# #%% Step 3: text clustering
# for i, index in enumerate(indexes):
#     print(f"text clustering for index: {index}")
#     text_clustering.text_clustering(params.loc[index].to_dict())

# #%% Step 4: word_cloud
# for i, index in enumerate(indexes):
#     print(f"generate word cloud for index: {index}")
#     word_cloud.word_cloud(params.loc[index].to_dict())

#%% Step 5: Google news_analysis
for i, index in enumerate(indexes):
    print(f"news analysis for index: {index}")
    params['news_final'] = sentiment_analysis.relevance_analysis(params.loc[index].to_dict(), CALL_GOOGLE=True, sentiment_analysis=False)
    print(params.loc[index].to_dict())

#%% Step 6: topic_title
# for i, index in enumerate(indexes):
#     print(f"generate topic title for index: {index}")
#     topic_title.topic_title(params.loc[index].to_dict())

#%% Step 6: Print the final result
for i, index in enumerate(indexes):
    params = final_check.final_check(params)
    print(params.loc[index].to_dict())

params.to_csv('params_temp.csv')
