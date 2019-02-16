import pandas as pd
from selenium.webdriver import Chrome

news = pd.read_csv('./data_processed/kevin_ling_topics_with_sentiment.csv')

# print (df)
#
# def match_name(search_name, row):
#     for name in row['person'].split("|"):
#         print (name)
#         if search_name == name:
#            return "True"
#     return "False"
#
#
# df['relevance'] = df.apply(lambda row: match_name("Lisa Ling", row), axis=1)
#
# print(df)


# # Open the website
# driver = Chrome(executable_path="/Users/kevin/desktop/name/chromedriver")
#
# selected_url = 'http://www.ocbc.com'
#
# driver.get(selected_url)
#
#
# # Define and search keywords
#
# keywords= ["Personal Bankingg","Premier Bankingg"]
#
# for keyword in keywords:
#
#     if driver.find_elements_by_xpath("//*[contains(text(), '{0}')]".format(keyword)):
#         print ("True")
#     else:
#         print("false")

news['person'] = news['person'].astype(str)
def match_name(search_name, row):
    print(row['person'])
    for name in row['person'].split("|"):
        print(name)
        if search_name == name:
            return "True"
    return "False"


news['name_relevance'] = news.apply(lambda row: match_name("Kevin Ling", row), axis=1)

# Temporarily chek the file

news.to_csv("data_processed/" + "kevin_ling_testing" + "_article_sentiment_raw_temp.csv")

def search_keyword(row):
    driver = Chrome(executable_path="/Users/kevin/desktop/name/chromedriver")

    #for href in row['href']:
     #   # Open the website
     #   print (row['href'].dtypes)
     #   print (row['href'])
     #   print("The href currently under testing is:", href)

    print (row['href'])
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
news.to_csv("data_processed/" + "kevin_ling_testing" + "_article_sentiment_raw_temp_1.csv")

def final_check(row):
    if (row['keywords']=="FALSE" and row['social_media']=="FALSE" and row['name_relevance']=="FALSE"):
        return "False"
    else:
        return "True"

news['final'] = news.apply(lambda row: final_check(row), axis=1)

news.to_csv("data_processed/" + "kevin_ling_testing" + "_article_sentiment_raw_temp_2.csv")