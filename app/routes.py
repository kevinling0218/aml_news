import json

import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, request, jsonify

app = Flask(__name__)

"""
 |--------------------------------------------------------------------------
 | news page
 |--------------------------------------------------------------------------
"""
def ajax_get_industry_news(industry, first_item_index, items_per_page):
    data_path = './static/data/' + industry + '_topics_with_sentiment.csv'
    # news = pd.read_csv('app/static/data/smrt_topics.csv', encoding="utf-8")
    news = pd.read_csv(data_path)
    news = news.sort_values('date', ascending=False)

    news = news.replace(np.nan, '', regex=True)

    if first_item_index > news.shape[0]:
        no_more_data = 1
        news = "no more news"
    else:
        no_more_data = 0
        news = news.iloc[first_item_index:first_item_index+items_per_page]
        news = news.to_dict(orient='records')
        news = json.dumps(news)

    data = {'news': news, 'no_more_data': no_more_data}
    return data


@app.route('/')
def index():
    return redirect("/news/banking")


@app.route('/news/<industry>', methods=['GET'])
def news(industry):
    data = {'industry': industry}
    return render_template("news.html", data=data)


@app.route('/ajax_post_news', methods=['POST'])
def ajax_post_news():
    industry = request.json['industry']
    first_item_index = request.json['first_item_index']
    items_per_page = request.json['items_per_page']

    data = ajax_get_industry_news(industry, first_item_index, items_per_page)
    return jsonify(data)


"""
 |--------------------------------------------------------------------------
 | summary page
 |--------------------------------------------------------------------------
"""
def summary_get_industry_data(industry):
    data_path = f'./static/data/{industry}_topics_with_sentiment.csv'
    # news = pd.read_csv('app/static/data/banking_topics_with_sentiment.csv', encoding="utf-8")
    news = pd.read_csv(data_path)
    news = news.sort_values('date', ascending=False)

    # give sentiment some non-zero value in order to show on bar chat
    news.loc[news.sentiment_score == 0, 'sentiment_score'] = 0.05

    topic_news_count = news.groupby('topic_id')[['article_id']].agg('count').rename(columns={'article_id': 'news_count'}).reset_index()

    topics = news[['topic_id', 'topic_title', 'topic_sentiment_score', 'topic_score']]\
        .drop_duplicates()\
        .merge(topic_news_count, on='topic_id')\
        .sort_values('news_count', ascending=True)

    topics['topic_score'] = topics['topic_score'] / np.max(topics['topic_score'])  # normalize to 0-1 range

    if len(topics[topics['topic_score'] > 0.5]) <= (0.15 * len(topics)):
        topics['topic_score'] = np.sqrt(topics['topic_score'])  # make the difference not as big

    topics.insert(0, 'news_count_rank', range(1, 1 + len(topics)))

    news = news.to_dict(orient='records')
    news = json.dumps(news, indent=2)

    topics = topics.to_dict(orient='records')
    topics = json.dumps(topics, indent=2)

    data = {'news': news, 'topics': topics, 'industry': industry}
    return data

@app.route('/summary/<industry>', methods=['GET'])
def summary(industry):
    data = summary_get_industry_data(industry)
    return render_template("summary.html", data=data)


"""
 |--------------------------------------------------------------------------
 | network page
 |--------------------------------------------------------------------------
"""
def network_get_industry_data(industry):
    nodes = pd.read_csv(f'./static/data/{industry}_nodes.csv')
    links = pd.read_csv(f'./static/data/{industry}_links.csv')

    nodes = json.dumps(nodes.to_dict(orient='records'))
    links = json.dumps(links.to_dict(orient='records'))

    data = {
        'nodes': nodes,
        'links': links,
        'industry': industry}
    return data


def ajax_get_news_node(industry, name):
    nodes_article_id = pd.read_csv(f'./static/data/{industry}_nodes_article_id.csv')
    news = pd.read_csv(f'./static/data/{industry}_topics_with_sentiment.csv')
    # nodes_article_id = pd.read_csv('app/static/data/banking_nodes_article_id.csv', encoding="utf-8")
    # news = pd.read_csv('app/static/data/banking_topics_with_sentiment.csv', encoding="utf-8")

    article_id = nodes_article_id.loc[nodes_article_id['name'] == name, 'article_id'].values[0].split("|")

    news['article_id'] = news['article_id'].astype(str)
    news = news[news['article_id'].isin(article_id)]

    news = news.replace(np.nan, '', regex=True)\
        .sort_values('date', ascending=False)

    news = news.to_dict(orient='records')
    news = json.dumps(news)

    data = {'news': news}
    return data


def ajax_get_news_link(industry, source, target):
    links_article_id = pd.read_csv(f'./static/data/{industry}_links_article_id.csv')
    news = pd.read_csv(f'./static/data/{industry}_topics_with_sentiment.csv')
    # links_article_id = pd.read_csv('app/static/data/banking_links_article_id.csv', encoding="utf-8")
    # news = pd.read_csv('app/static/data/banking_topics_with_sentiment.csv', encoding="utf-8")

    article_id = links_article_id.loc[(links_article_id['source'] == source) & (links_article_id['target'] == target), 'article_id'].values[0].split("|")

    news['article_id'] = news['article_id'].astype(str)
    news = news[news['article_id'].isin(article_id)]

    news = news.replace(np.nan, '', regex=True) \
        .sort_values('date', ascending=False)

    news = news.to_dict(orient='records')
    news = json.dumps(news)

    data = {'news': news}
    return data


@app.route('/network/<industry>', methods=['GET'])
def network(industry):
    data = network_get_industry_data(industry)
    return render_template("network.html", data=data)


@app.route('/ajax_click_node', methods=['POST'])
def ajax_click_node():
    industry = request.json['industry']
    name = request.json['name']

    data = ajax_get_news_node(industry, name)
    return jsonify(data)

@app.route('/ajax_click_link', methods=['POST'])
def ajax_click_link():
    industry = request.json['industry']
    source = request.json['source']
    target = request.json['target']

    data = ajax_get_news_link(industry, source, target)
    return jsonify(data)


"""
 |--------------------------------------------------------------------------
 | risk page
 |--------------------------------------------------------------------------
"""
def risk_get_industry_data(industry, entity):
    nodes = pd.read_csv(f'./static/data/{industry}_nodes.csv')
    nodes = nodes[nodes.type == 'ORGANIZATION']
    nodes_article_id = pd.read_csv(f'./static/data/{industry}_nodes_article_id.csv')
    news = pd.read_csv(f'./static/data/{industry}_topics_with_sentiment.csv')
    nodes_monthly_emb = pd.read_csv(f'./static/data/{industry}_nodes_monthly_emb.csv')

    # nodes = pd.read_csv('app/static/data/credit_suisse_nodes.csv', encoding="utf-8")
    # nodes_article_id = pd.read_csv('app/static/data/credit_suisse_nodes_article_id.csv', encoding="utf-8")
    # news = pd.read_csv('app/static/data/credit_suisse_topics_with_sentiment.csv', encoding="utf-8")

    # give sentiment some non-zero value in order to show on bar chat
    news.loc[news.sentiment_score == 0, 'sentiment_score'] = 0.05

    # if entity is not set or not match, show the most important entity by default
    if (all(nodes['name'].str.lower() != entity.lower())) & (entity == "not_set"):
        entity = nodes.iloc[0, 0]

    # find news of this entity
    article_id = nodes_article_id.loc[nodes_article_id['name'].str.lower() == entity.lower(), 'article_id'].values[0].split("|")

    news['article_id'] = news['article_id'].astype(str)
    news = news[news['article_id'].isin(article_id)]

    news = news.replace(np.nan, '', regex=True) \
        .sort_values('date', ascending=False)

    # find sentiment_emb score of this entity
    sentiment_emb = nodes.loc[nodes.name.str.lower() == entity.lower(), 'sentiment_emb'].values[0]
    sentiment_emb = int(np.round(sentiment_emb))
    sentiment_emb_class = 'neutral'
    if sentiment_emb > 50:
        sentiment_emb_class = 'very_positive'
    elif sentiment_emb > 15:
        sentiment_emb_class = 'positive'
    elif sentiment_emb > -15:
        sentiment_emb_class = 'neutral'
    elif sentiment_emb > -50:
        sentiment_emb_class = 'negative'
    else:
        sentiment_emb_class = 'very_negative'

    # get sentiment_monthly_emb score of this entity
    nodes_monthly_emb = nodes_monthly_emb.loc[nodes_monthly_emb['name'].str.lower() == entity.lower()]

    # find top positive, negative and neutral news
    positive_news = news.copy()
    positive_news = positive_news[positive_news['sentiment_score'] > 0.15].sort_values('sentiment_score', ascending=False)

    negative_news = news.copy()
    negative_news = negative_news[negative_news['sentiment_score'] <= -0.15].sort_values('sentiment_score', ascending=True)

    neutral_news = news.copy()
    neutral_news = neutral_news[(neutral_news['sentiment_score'] > -0.15) & (neutral_news['sentiment_score'] <= 0.15)].sort_values('sentiment_score', ascending=False)

    # find all important entities
    nodes = nodes.sort_values('name')
    nodes = nodes[~nodes['name'].str.contains("'")]

    entities = '|'.join(list(nodes['name'].values))

    # prepare output
    news = json.dumps(news.to_dict(orient='records'))
    positive_news = json.dumps(positive_news.to_dict(orient='records'))
    negative_news = json.dumps(negative_news.to_dict(orient='records'))
    neutral_news = json.dumps(neutral_news.to_dict(orient='records'))
    nodes_monthly_emb = json.dumps(nodes_monthly_emb.to_dict(orient='records'))

    data = {
        'entities': entities,
        'entity': entity,
        'news': news,
        'sentiment_emb': sentiment_emb,
        'sentiment_emb_class': sentiment_emb_class,
        'monthly_sentiment_emb': nodes_monthly_emb,
        'positive_news': positive_news,
        'negative_news': negative_news,
        'neutral_news': neutral_news,
        'industry': industry}
    return data

@app.route('/risk/<industry>', methods=['GET'])
def risk(industry):
    entity = request.args.get('entity', 'not_set')
    data = risk_get_industry_data(industry, entity)
    return render_template("risk.html", data=data)

if __name__ == '__main__':
    app.run(debug=True)