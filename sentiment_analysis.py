#%% import
import numpy as np
import pandas as pd
import json
from selenium.webdriver import Chrome
import google.cloud.language

import os


def relevance_analysis(params, CALL_GOOGLE=False, sentiment_analysis = False):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/kevinling/desktop/name/OCBC-2c27a3cdf13f.json"

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    # Create a Language client.
    language_client = google.cloud.language.LanguageServiceClient()

    #%% Parameter
    file = params['file']

    #%% Load data
    news = pd.read_csv(f"data_processed/{file}_news_english.csv")
    news["text"] = news["full_title"].map(str) + ". " +news["abstract"].map(str)

    # For past processing, only process two rows
    news = news[:2]

    if sentiment_analysis:
        #%% Article sentiment analysis
        if CALL_GOOGLE:
            article_id = []
            sentiment_score = []
            sentiment_magnitude = []

            news.reset_index(inplace=True, drop=True)
            for index, row in news.iterrows():
                if index % 10 == 0:
                    print(f"Performing article sentiment analysis for article: {index} out of {news.shape[0]}.")
                text = row['text']
                document = google.cloud.language.types.Document(
                    content=text,
                    type=google.cloud.language.enums.Document.Type.PLAIN_TEXT)

                try:
                    response = language_client.analyze_sentiment(document=document)
                except Exception as e:
                    print(f"index {index}: {e}")
                    continue

                article_id.append(row['article_id'])
                sentiment_score.append(response.document_sentiment.score)
                sentiment_magnitude.append(response.document_sentiment.magnitude)

            article_sentiment = pd.DataFrame({
                "article_id": article_id,
                "sentiment_score": sentiment_score,
                "sentiment_magnitude": sentiment_magnitude
            }).loc[:, ["article_id",
                       "sentiment_score",
                       "sentiment_magnitude"]]

            article_sentiment.to_pickle("data_processed/"+file+"_article_sentiment_raw.pkl")

        article_sentiment = pd.read_pickle("data_processed/"+file+"_article_sentiment_raw.pkl")


        #%% Topic sentiment score
        news = news.merge(article_sentiment, on='article_id')

        topic_sentiment = news.groupby('topic_id')[['sentiment_score']]\
            .agg(np.mean)\
            .reset_index()\
            .rename(columns={'sentiment_score': 'topic_sentiment_score'})

        news = news.merge(topic_sentiment, on='topic_id')


    #%% Entity sentiment analysis
    if CALL_GOOGLE:
        article_id = []
        name = []
        type = []
        importance = []
        sentiment_score = []
        sentiment_magnitude = []

        news.reset_index(inplace=True, drop=True)
        for index, row in news.iterrows():
            if index % 10 == 0:
                print(f"Performing entity analysis for article: {index} out of {news.shape[0]}.")
            text = row['text']
            document = google.cloud.language.types.Document(
                content=text,
                type=google.cloud.language.enums.Document.Type.PLAIN_TEXT)

            try:
                response = language_client.analyze_entity_sentiment(document=document)
            except Exception as e:
                print(f"index {index}: {e}")
                continue

            for entity in response.entities:
                if entity_type[entity.type] == 'ORGANIZATION' or entity_type[entity.type] == 'PERSON':
                    article_id.append(row['article_id'])
                    name.append(entity.name)
                    type.append(entity_type[entity.type])
                    importance.append(entity.salience)
                    sentiment_score.append(entity.sentiment.score)
                    sentiment_magnitude.append(entity.sentiment.magnitude)

        entity_sentiment = pd.DataFrame({
            "article_id": article_id,
            "name": name,
            "type": type,
            "importance": importance,
            "sentiment_score": sentiment_score,
            "sentiment_magnitude": sentiment_magnitude,
        }).loc[:, ["article_id",
                   "name",
                   "type",
                   "importance",
                   "sentiment_score",
                   "sentiment_magnitude"]]

        entity_sentiment.to_pickle("data_processed/"+file+"_entity_sentiment_raw.pkl")

    entity_sentiment = pd.read_pickle("data_processed/"+file+"_entity_sentiment_raw.pkl")

    #%% entity_sentiment clean up
    top_entities = entity_sentiment.groupby('name')[['importance']].sum().sort_values('importance', ascending=False)

    # remove false entities - keep name with any uppercase letters
    def any_uppercase(s):
        return any(c.isupper() for c in s)

    entity_sentiment = entity_sentiment[entity_sentiment['name'].apply(any_uppercase)]

    # remove false entities - known dictionary
    remove_list = [
        'bank',
        'banks',
        'company',
        'companies',
        'firm',
        'committee',
        'business',
        'businesses',
        'board',
        'teams',
        'party',
        'parties',
        'subsidiary',
        'commission',
        'subsidiary bank',
        'police',
        'group',
        'customers',
        'users',
        'bankers',
        'economists'
    ]

    entity_sentiment = entity_sentiment[~ entity_sentiment['name'].str.lower().isin(remove_list)]
    entity_sentiment = entity_sentiment[~ entity_sentiment['name'].str.contains("$", regex=False)]

    # BANKING - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("OCBC"), 'name'] = 'OCBC'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Oversea-Chinese Banking Corp"), 'name'] = 'OCBC'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Oversea-Chinese Banking Corporation"), 'name'] = 'OCBC'


    entity_sentiment.loc[entity_sentiment['name'].str.contains("UOB"), 'name'] = 'UOB'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("united overseas bank"), 'name'] = 'UOB'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("DBS"), 'name'] = 'DBS'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("POSB"), 'name'] = 'POSB'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Great Eastern"), 'name'] = 'Great Eastern'
    entity_sentiment.loc[entity_sentiment['name'] == 'GE', 'name'] = 'Great Eastern'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Monetary Authority of Singapore"), 'name'] = 'MAS'

    entity_sentiment.loc[entity_sentiment['name'] == 'SGX', 'name'] = 'Singapore Exchange'


    # INSURANCE - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("AIA"), 'name'] = 'AIA'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("AXA"), 'name'] = 'AXA'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Aviva"), 'name'] = 'Aviva'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Credit Suisse"), 'name'] = 'Credit Suisse'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Prudential"), 'name'] = 'Prudential'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Munich Re"), 'name'] = 'Munich Re'

    # Real Estate - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("PropNex"), 'name'] = 'PropNex'

    # CDL - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'] == 'CDL', 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments limited"), 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments"), 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments ltd"), 'name'] = 'City Developments Limited'

    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("m&c"), 'name'] = 'Millennium & Copthorne'
    entity_sentiment.loc[entity_sentiment['name'] == 'Millennium & Copthorne Hotels', 'name'] = 'Millennium & Copthorne'

    # Frasers Centrepoint - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("frasers centrepoint"), 'name'] = 'Frasers Centrepoint'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("FCL"), 'name'] = 'Frasers Centrepoint'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("FCT"), 'name'] = 'Frasers Centrepoint'

    # Hyflux - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("hyflux"), 'name'] = 'Hyflux'

    # Pacific Andes - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("pacific andes"), 'name'] = 'Pacific Andes'

    # Julius Baer - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("julius baer"), 'name'] = 'Julius Baer'

    # Julius Baer - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("credit suisse"), 'name'] = 'Credit Suisse'

    # SMRT - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Singapore Mass Rapid Transit"), 'name'] = 'SMRT'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("SMRT"), 'name'] = 'SMRT'

    # Singtel - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("singtel"), 'name'] = 'Singtel'

    # FULLERTON - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("fullerton healthcare"), 'name'] = 'Fullerton Healthcare'


    # remove false entities
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'MRT']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'SINGAPORE - Two']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Choa Chu Kang Transport']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'AI']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Fintech']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Source']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'DPU']

    # remove false person entities
    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'United Engineers'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Noble'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'MAS'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Anyone'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'sgCarMart'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Carro'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Cognicor'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'UOB'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Mr'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("agent")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("consultant")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("engineer")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("source")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("family")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("rents")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("catalist")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("reporter")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.contains("CEO")))]


    #%% If an entity appears in organization, remove it from person
    identified_organizations = entity_sentiment.loc[entity_sentiment.type == 'ORGANIZATION', 'name'].unique()

    entity_sentiment = entity_sentiment[~((entity_sentiment.name.isin(identified_organizations)) & (entity_sentiment.type == 'PERSON'))]

    #%% Add extracted entities to news
    entity_rollup = entity_sentiment.groupby(['article_id', 'type'])['name']\
        .apply(lambda x: "%s" % '|'.join(x))\
        .unstack('type')\
        .reset_index()\
        .rename(columns={'ORGANIZATION': 'organization', 'PERSON': 'person'})

    news = news.merge(entity_rollup, how='left', on='article_id')  # Temporarily chek the file

    news.to_csv("data_processed/" + file + "_article_sentiment_raw_temp.csv")


    # %% Match the entity with the original name of search

    def match_name(search_name, row):
        for name in row['person'].split("|"):
            # print(name)
            if search_name == name:
                return "True"
        return "False"


    news['person'] = news['person'].astype(str)
    news['name_relevance'] = news.apply(lambda row: match_name(params['query'], row), axis=1)


    # %% Check whether it's customer's facebook or linkedin profile

    def check_social_media(row):
        for href in row['href']:
            if "facebook" in href:
                return "False"
            if "linkedin" in href:
                return "False"

        return "True"


    news['social_media'] = news.apply(lambda row: check_social_media(row), axis=1)


    # %% Click into the True news and check whether the keywords is in it

    def search_keyword(row):
        driver = Chrome(executable_path="/Users/kevinling/desktop/name/chromedriver")

        try:
            driver.get(row['href'])

            # Define and search keywords

            keywords = ["finance", "transaction"]

            for keyword in keywords:
                if driver.find_elements_by_xpath("//*[contains(text(), '{0}')]".format(keyword)):
                    return "True"
            return "False"
        except:
            return "True"


    news['href'] = news['href'].astype(str)
    news['keywords'] = news.apply(lambda row: search_keyword(row), axis=1)


    # Final check

    def final_check(row):
        if (row['name_relevance'] != "FALSE" and row['social_media'] != "TRUE"):
            if row['keywords'] == "True":
                return "True"
        else:
            return "False"


    news['news_final'] = news.apply(lambda row: final_check(row), axis=1)
    # Temporarily chek the file

    news.to_csv("data_processed/" + file + "_article_sentiment_raw_temp_2.csv")

    if "TRUE" in news['news_final']:
        params['news_final'] = "TRUE"
    else:
        params['news_final'] = "FALSE"

    news.to_csv("data_processed/" + file + "temp.csv")

    return params['news_final']


def sentiment_analysis(params, CALL_GOOGLE=False):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/kevinling/desktop/name/OCBC-2c27a3cdf13f.json"

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    # Create a Language client.
    language_client = google.cloud.language.LanguageServiceClient()

    #%% Parameter
    file = params['file']

    #%% Load data
    news = pd.read_pickle(f"data_processed/{file}_topics.pkl")
    news["text"] = news["full_title"].map(str) + ". " +news["abstract"].map(str)

    #%% Article sentiment analysis
    if CALL_GOOGLE:
        article_id = []
        sentiment_score = []
        sentiment_magnitude = []

        news.reset_index(inplace=True, drop=True)
        for index, row in news.iterrows():
            if index % 10 == 0:
                print(f"Performing article sentiment analysis for article: {index} out of {news.shape[0]}.")
            text = row['text']
            document = google.cloud.language.types.Document(
                content=text,
                type=google.cloud.language.enums.Document.Type.PLAIN_TEXT)

            try:
                response = language_client.analyze_sentiment(document=document)
            except Exception as e:
                print(f"index {index}: {e}")
                continue

            article_id.append(row['article_id'])
            sentiment_score.append(response.document_sentiment.score)
            sentiment_magnitude.append(response.document_sentiment.magnitude)

        article_sentiment = pd.DataFrame({
            "article_id": article_id,
            "sentiment_score": sentiment_score,
            "sentiment_magnitude": sentiment_magnitude
        }).loc[:, ["article_id",
                   "sentiment_score",
                   "sentiment_magnitude"]]

        article_sentiment.to_pickle("data_processed/"+file+"_article_sentiment_raw.pkl")

    article_sentiment = pd.read_pickle("data_processed/"+file+"_article_sentiment_raw.pkl")


    #%% Topic sentiment score
    news = news.merge(article_sentiment, on='article_id')

    topic_sentiment = news.groupby('topic_id')[['sentiment_score']]\
        .agg(np.mean)\
        .reset_index()\
        .rename(columns={'sentiment_score': 'topic_sentiment_score'})

    news = news.merge(topic_sentiment, on='topic_id')


    #%% Entity sentiment analysis
    if CALL_GOOGLE:
        article_id = []
        name = []
        type = []
        importance = []
        sentiment_score = []
        sentiment_magnitude = []

        news.reset_index(inplace=True, drop=True)
        for index, row in news.iterrows():
            if index % 10 == 0:
                print(f"Performing entity sentiment analysis for article: {index} out of {news.shape[0]}.")
            text = row['text']
            document = google.cloud.language.types.Document(
                content=text,
                type=google.cloud.language.enums.Document.Type.PLAIN_TEXT)

            try:
                response = language_client.analyze_entity_sentiment(document=document)
            except Exception as e:
                print(f"index {index}: {e}")
                continue

            for entity in response.entities:
                if entity_type[entity.type] == 'ORGANIZATION' or entity_type[entity.type] == 'PERSON':
                    article_id.append(row['article_id'])
                    name.append(entity.name)
                    type.append(entity_type[entity.type])
                    importance.append(entity.salience)
                    sentiment_score.append(entity.sentiment.score)
                    sentiment_magnitude.append(entity.sentiment.magnitude)

        entity_sentiment = pd.DataFrame({
            "article_id": article_id,
            "name": name,
            "type": type,
            "importance": importance,
            "sentiment_score": sentiment_score,
            "sentiment_magnitude": sentiment_magnitude,
        }).loc[:, ["article_id",
                   "name",
                   "type",
                   "importance",
                   "sentiment_score",
                   "sentiment_magnitude"]]

        entity_sentiment.to_pickle("data_processed/"+file+"_entity_sentiment_raw.pkl")

    entity_sentiment = pd.read_pickle("data_processed/"+file+"_entity_sentiment_raw.pkl")

    #%% entity_sentiment clean up
    top_entities = entity_sentiment.groupby('name')[['importance']].sum().sort_values('importance', ascending=False)

    # remove false entities - keep name with any uppercase letters
    def any_uppercase(s):
        return any(c.isupper() for c in s)

    entity_sentiment = entity_sentiment[entity_sentiment['name'].apply(any_uppercase)]

    # remove false entities - known dictionary
    remove_list = [
        'bank',
        'banks',
        'company',
        'companies',
        'firm',
        'committee',
        'business',
        'businesses',
        'board',
        'teams',
        'party',
        'parties',
        'subsidiary',
        'commission',
        'subsidiary bank',
        'police',
        'group',
        'customers',
        'users',
        'bankers',
        'economists'
    ]

    entity_sentiment = entity_sentiment[~ entity_sentiment['name'].str.lower().isin(remove_list)]
    entity_sentiment = entity_sentiment[~ entity_sentiment['name'].str.contains("$", regex=False)]

    # BANKING - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("OCBC"), 'name'] = 'OCBC'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Oversea-Chinese Banking Corp"), 'name'] = 'OCBC'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Oversea-Chinese Banking Corporation"), 'name'] = 'OCBC'


    entity_sentiment.loc[entity_sentiment['name'].str.contains("UOB"), 'name'] = 'UOB'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("united overseas bank"), 'name'] = 'UOB'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("DBS"), 'name'] = 'DBS'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("POSB"), 'name'] = 'POSB'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Great Eastern"), 'name'] = 'Great Eastern'
    entity_sentiment.loc[entity_sentiment['name'] == 'GE', 'name'] = 'Great Eastern'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Monetary Authority of Singapore"), 'name'] = 'MAS'

    entity_sentiment.loc[entity_sentiment['name'] == 'SGX', 'name'] = 'Singapore Exchange'


    # INSURANCE - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("AIA"), 'name'] = 'AIA'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("AXA"), 'name'] = 'AXA'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Aviva"), 'name'] = 'Aviva'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Credit Suisse"), 'name'] = 'Credit Suisse'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Prudential"), 'name'] = 'Prudential'

    entity_sentiment.loc[entity_sentiment['name'].str.contains("Munich Re"), 'name'] = 'Munich Re'

    # Real Estate - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("PropNex"), 'name'] = 'PropNex'

    # CDL - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'] == 'CDL', 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments limited"), 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments"), 'name'] = 'City Developments Limited'
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("city developments ltd"), 'name'] = 'City Developments Limited'

    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("m&c"), 'name'] = 'Millennium & Copthorne'
    entity_sentiment.loc[entity_sentiment['name'] == 'Millennium & Copthorne Hotels', 'name'] = 'Millennium & Copthorne'

    # Frasers Centrepoint - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("frasers centrepoint"), 'name'] = 'Frasers Centrepoint'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("FCL"), 'name'] = 'Frasers Centrepoint'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("FCT"), 'name'] = 'Frasers Centrepoint'

    # Hyflux - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("hyflux"), 'name'] = 'Hyflux'

    # Pacific Andes - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("pacific andes"), 'name'] = 'Pacific Andes'

    # Julius Baer - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("julius baer"), 'name'] = 'Julius Baer'

    # Julius Baer - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("credit suisse"), 'name'] = 'Credit Suisse'

    # SMRT - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.contains("Singapore Mass Rapid Transit"), 'name'] = 'SMRT'
    entity_sentiment.loc[entity_sentiment['name'].str.contains("SMRT"), 'name'] = 'SMRT'

    # Singtel - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("singtel"), 'name'] = 'Singtel'

    # FULLERTON - unify names of known entities
    entity_sentiment.loc[entity_sentiment['name'].str.lower().str.contains("fullerton healthcare"), 'name'] = 'Fullerton Healthcare'


    # remove false entities
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'MRT']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'SINGAPORE - Two']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Choa Chu Kang Transport']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'AI']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Fintech']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'Source']
    entity_sentiment = entity_sentiment[entity_sentiment['name'] != 'DPU']

    # remove false person entities
    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'United Engineers'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Noble'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'MAS'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Anyone'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'sgCarMart'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Carro'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Cognicor'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'UOB'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'] == 'Mr'))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("agent")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("consultant")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("engineer")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("source")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("family")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("rents")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("catalist")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.lower().str.contains("reporter")))]

    entity_sentiment = entity_sentiment[~((entity_sentiment['type'] == 'PERSON') & (entity_sentiment['name'].str.contains("CEO")))]


    #%% If an entity appears in organization, remove it from person
    identified_organizations = entity_sentiment.loc[entity_sentiment.type == 'ORGANIZATION', 'name'].unique()

    entity_sentiment = entity_sentiment[~((entity_sentiment.name.isin(identified_organizations)) & (entity_sentiment.type == 'PERSON'))]

    #%% Add extracted entities to news
    entity_rollup = entity_sentiment.groupby(['article_id', 'type'])['name']\
        .apply(lambda x: "%s" % '|'.join(x))\
        .unstack('type')\
        .reset_index()\
        .rename(columns={'ORGANIZATION': 'organization', 'PERSON': 'person'})

    news = news.merge(entity_rollup, how='left', on='article_id')


    # Temporarily chek the file

    news.to_csv("data_processed/" + file + "_article_sentiment_raw_temp.csv")

    # %% Match the entity with the original name of search

    def match_name(search_name, row):
        for name in row['person'].split("|"):
            # print(name)
            if search_name == name:
                return "True"
        return "False"

    news['person'] = news['person'].astype(str)
    news['name_relevance'] = news.apply(lambda row: match_name(params['query'], row), axis=1)



    # %% Check whether it's customer's facebook or linkedin profile

    def check_social_media(row):
        for href in row['href']:
            if "facebook" in href:
                return "False"
            if "linkedin" in href:
                return "False"

        return "True"

    news['social_media'] = news.apply(lambda row: check_social_media(row), axis=1)

    # %% Click into the True news and check whether the keywords is in it

    def search_keyword(row):
        driver = Chrome(executable_path="/Users/kevinling/desktop/name/chromedriver")

        try:
            driver.get(row['href'])

            # Define and search keywords

            keywords = ["finance","transaction"]

            for keyword in keywords:
                if driver.find_elements_by_xpath("//*[contains(text(), '{0}')]".format(keyword)):
                   return "True"
            return "False"
        except:
            return "True"

    news['href'] = news['href'].astype(str)
    news['keywords'] = news.apply(lambda row: search_keyword(row), axis=1)

    # Final check

    def final_check(row):
        if (row['name_relevance'] != "FALSE" and row['social_media'] != "TRUE"):
            if row['keywords'] == "True":
                return "True"
        else:
            return "False"

    news['news_final'] = news.apply(lambda row: final_check(row), axis=1)
    # Temporarily chek the file

    news.to_csv("data_processed/" + file + "_article_sentiment_raw_temp_2.csv")

    if "TRUE" in news['news_final']:
        params['news_final'] = "TRUE"
    else:
        params['news_final'] = "FALSE"

    news.to_csv("data_processed/" + file + "temp.csv")

    return params['news_final']

    #%% Use article sentiment instead of entity sentiment
    entity_sentiment.drop(['sentiment_score', 'sentiment_magnitude'], axis=1, inplace=True)
    entity_sentiment = entity_sentiment.groupby(['article_id', 'name', 'type']).agg('mean').reset_index()
    entity_sentiment = entity_sentiment.merge(article_sentiment, on='article_id')


    #%% Nodes
    nodes = entity_sentiment.groupby(['name', 'type'])[['importance']]\
        .agg(sum)\
        .sort_values('importance', ascending=False)\
        .reset_index()
    nodes['importance'] = nodes['importance'] / max(nodes['importance'])

    # compute EMB score
    entity_sentiment.loc[:, 'sentiment_emb'] = np.nan
    entity_sentiment.loc[entity_sentiment.sentiment_score > 0.15, 'sentiment_emb'] = 1
    entity_sentiment.loc[entity_sentiment.sentiment_score < -0.15, 'sentiment_emb'] = -1

    def compute_emb(sentiment_emb):
        return np.sum(sentiment_emb) / np.size(sentiment_emb) * 100

    nodes_emb = entity_sentiment.copy().dropna().groupby('name')[['sentiment_emb']].apply(compute_emb)

    # compute monthly EMB score
    article_year_month = news.copy()[['article_id', 'date']]
    article_year_month['year_month'] = article_year_month['date'].map(lambda x: f'{x.year}-{x.month}')
    article_year_month.drop('date', axis=1, inplace=True)

    nodes_monthly_emb = entity_sentiment.copy().dropna().merge(article_year_month, on='article_id').groupby(['name', 'year_month'])[['sentiment_emb']].apply(compute_emb).reset_index()
    if len(nodes_monthly_emb)>0:
        nodes_monthly_emb['year'] = nodes_monthly_emb['year_month'].str.split("-").str[0].astype(int)
        nodes_monthly_emb['month'] = nodes_monthly_emb['year_month'].str.split("-").str[1].astype(int)
        nodes_monthly_emb = nodes_monthly_emb.sort_values(['year', 'month'])

    nodes_monthly_emb.to_csv(f"app/static/data/{file}_nodes_monthly_emb.csv", index=False, encoding="utf-8")

    nodes = nodes.merge(nodes_emb, how='left', left_on='name', right_index=True).fillna(0)

    nodes_article_id = entity_sentiment.groupby('name')['article_id'].apply(lambda x: "%s" % '|'.join(x)).reset_index()


    #%% links
    def agg_extract_links(grouped):
        grouped = grouped.drop_duplicates().sort_values('name')
        names = grouped['name']
        type = grouped['type']

        result = []
        if len(names) > 1:
            for i in range(len(names)-1):
                for j in range(i+1, len(names)):
                    link_type = "ORGANIZATION"
                    if (type.iat[i] == "PERSON") | (type.iat[j] == "PERSON"):
                        link_type = "PERSON"
                    result.append((names.iat[i], names.iat[j], 1, link_type))
        if len(result) == 0:
            result = 'no link'
        return result


    links = entity_sentiment.groupby('article_id').apply(agg_extract_links)
    links = links[links != 'no link']


    article_id = []
    source = []
    target = []
    weight = []
    link_type = []

    for index, row in links.iteritems():
        for item in row:
            article_id.append(index)
            source.append(item[0])
            target.append(item[1])
            weight.append(item[2])
            link_type.append(item[3])

    links_with_article_id = pd.DataFrame({
        "article_id": article_id,
        "source": source,
        "target": target,
        "weight": weight,
        "link_type": link_type
    }).loc[:, ["article_id",
               "source",
               "target",
               "weight",
               "link_type"]]

    links = links_with_article_id.groupby(['source', 'target', 'link_type'])['weight'].agg(sum).reset_index().sort_values('weight', ascending=False)

    links_article_id = links_with_article_id.groupby(['source', 'target', 'link_type'])['article_id'].apply(lambda x: "%s" % '|'.join(x)).reset_index()


    #%% Data Filtering - only consider links with weight >= 2 (Two entities co-appear at least twice)
    nodes_keep = links[links['weight'] >= 2]
    nodes_keep = list(nodes_keep['source'].values) + list(nodes_keep['target'].values)

    links = links[links['source'].isin(nodes_keep) & links['target'].isin(nodes_keep)]
    nodes = nodes[nodes['name'].isin(links['source'].values) | nodes['name'].isin(links['target'].values)]


    #%% save files for D3.js
    nodes.to_csv(f"app/static/data/{file}_nodes.csv", index=False, encoding="utf-8")
    links.to_csv(f"app/static/data/{file}_links.csv", index=False, encoding="utf-8")
    nodes_article_id.to_csv(f"app/static/data/{file}_nodes_article_id.csv", index=False, encoding="utf-8")
    links_article_id.to_csv(f"app/static/data/{file}_links_article_id.csv", index=False, encoding="utf-8")


    #%% save news
    news.to_csv("data_processed/" + file + "_topics_with_sentiment.csv", index=False, encoding="utf-8")
    news.to_csv(f"app/static/data/{file}_topics_with_sentiment.csv", index=False, encoding="utf-8")
    news.to_pickle(f"data_processed/{file}_topics_with_sentiment.pkl")
