#%% import
import pandas as pd
from pyquery import PyQuery as pq
from selenium.webdriver import Chrome
import time
import calendar
import random


def parse_html(html):
    if (html("#topstuff").text().find("No results") > -1) | (html("#topstuff").text().find("did not match any news results") > -1):  # if no result found
        return (True, pd.DataFrame())

    articles = html("div.g")

    title = []
    href = []
    media = []
    date = []
    abstract = []
    related_article_count = []

    for i in range(articles.length):
        article = articles.eq(i)
        title.append(article("h3").text())
        href.append(article("h3 a").attr("href"))
        media.append(article("div.slp")("span").eq(0).text())
        date.append(article("span.st")("span.f").text())
        abstract.append(article("span.st").text())
        related_article_count.append(article("div.card-section a").length)

    try:
        if (articles.length == 1) & (date[0] == ""):
            date[0] = article(".st")("span.f").text().split("-")[0].strip()
            abstract[0] = article(".st").text()
    except:
        pass

    news = pd.DataFrame(
        {
            "title": title,
            "media": media,
            "date": date,
            "abstract": abstract,
            "href": href,
            "related_article_count": related_article_count
        }, columns=[
            "date",
            "title",
            "media",
            "href",
            "abstract",
            "related_article_count"
        ]) \
        .reset_index().rename(columns={'index': 'search_rank'})

    news['search_rank'] = news['search_rank']+1

    return (False, news)


def scrape_news_for_individual(query, driver, string):

    news = pd.DataFrame()

    url = f"https://www.google.com.sg/search?q={query}+AND+%28{string}%29&tbs=cdr:1"

    try_again = True

    while try_again:

        print("trying again")

        driver.get(url)
        html = pq(driver.find_element_by_tag_name('body').get_attribute("outerHTML"))

        (is_no_result, parsed_html) = parse_html(html)

        if is_no_result:
            print("No search result")
            try_again = False
        elif parsed_html.empty:
            variable = input('Do Google verification and press any key to continue.')
        else:
            try_again = False

    news = news.append(parsed_html)

    time.sleep(15 + random.randint(1, 10001) / 1000 + 60 * (random.randint(1, 21) <= 1))

    return news

def scrape_news_for_individual_with_dates(query, start, end, driver,string):
    '''If there is a requirement for searching news with specific time period'''

    # Scrape top 100 news for each month
    start_year, start_month = start
    end_year, end_month = end

    print (start_year,start_month, end_year,end_month)

    news = pd.DataFrame()

    for year in range(start_year, end_year+1):

        print(year)

        if year < end_year:

            print("year < end_year")

            last_month = 12
        else:
            last_month = end_month

        if year == start_year:

            print("year == end_year")

            first_month = start_month
        else:
            first_month = 1

        for month in range(first_month, last_month+1):

            print (month)

            last_day_of_month = calendar.monthrange(year, month)[1]

            month_first_date = "/".join([str(month), "1", str(year)])
            month_last_date = "/".join([str(month), str(last_day_of_month), str(year)])

            url = f"https://www.google.com.sg/search?q={query}+AND+%28{string}%29&tbs=cdr:1, cd_min:{month_first_date}, cd_max:{month_last_date}"

            # url = f"https://www.google.com/search?q={query}&num=100&safe=off&tbs=cdr:1,cd_min:{month_first_date},cd_max:{month_last_date}&tbm=nws&source=lnt&biw=1440&bih=692&dpr=2"

            try_again = True

            while try_again:

                print("trying again")

                driver.get(url)
                html = pq(driver.find_element_by_tag_name('body').get_attribute("outerHTML"))

                (is_no_result, parsed_html) = parse_html(html)

                if is_no_result:
                    print("No search result")
                    try_again = False
                elif parsed_html.empty:
                    variable = input('Do Google verification and press any key to continue.')
                else:
                    try_again = False

            news = news.append(parsed_html)

            time.sleep(15 + random.randint(1, 10001) / 1000 + 60 * (random.randint(1, 21) <= 1))

    return news



def scrape_news(params, driver, strings, num_pages=1):

    # The query we put in will be all customer name and joint by OR
    # For example, if the name is "Kevin | Adrian", the output will be "Kevin OR Adrian"

    all_names = params['name'].split('|')
    query = ""
    for name in all_names:
        query = query + name + " OR "
    query = query[:-3]

    file = params['file']

    search_result_list = []

    for string in strings:

        if params['start']:
            start = params['start'].split("-")
            start = [int(i) for i in start]
            end = params['end'].split("-")
            end = [int(i) for i in end]

            search_result = scrape_news_for_individual_with_dates(query, start, end, driver,string)

        else:
            search_result = scrape_news_for_individual(query, driver, string)

        search_result_list.append(search_result)

        news = pd.concat(search_result_list)

    if len(news) > 0:

        # Add a running number as article_id
        news = news.reset_index().drop(['index'], axis=1).reset_index().rename(columns={'index': 'article_id'})

        # params = json.load(open('params.json'))
        # file = params['file']
        # news = pd.read_csv("data_processed/"+file+"_news.csv", encoding="utf-8")

        news['article_id'] = file + '_' + news['article_id'].astype(str).str.zfill(5)
        news.to_csv("data_processed/"+file+"_news.csv", index=False, encoding="utf-8")











