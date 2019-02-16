var last_timestamp;

function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;

    // usage example:
    // var a = ['a', 1, 'a', 2, '1'];
    // var unique = a.filter( onlyUnique ); // returns ['a', 1, 2, '1']
}

function get_news_html(this_news, show_timeline=false){
    var sentiment_score = this_news.sentiment_score;
    var sentiment_class, sentiment_label;
    if(sentiment_score > 0.55){
        sentiment_class = 'very_positive';
        sentiment_label = 'Very Positive'
    }else if(sentiment_score > 0.15){
        sentiment_class = 'positive';
        sentiment_label = 'Positive'
    }else if(sentiment_score > -0.15){
        sentiment_class = 'neutral';
        sentiment_label = 'Neutral'
    }else if(sentiment_score > -0.55){
        sentiment_class = 'negative';
        sentiment_label = 'Negative'
    }else{
        sentiment_class = 'very_negative';
        sentiment_label = 'Very Negative'
    }

    var organizations_html = "";
    var organizations = this_news.organization;
    if(organizations.length > 0) {
        organizations = organizations.split('|').filter(onlyUnique);
        organizations_html = `Identified organizations:`;
        organizations.forEach(function (element) {
            organizations_html = `${organizations_html}<li>${element}</li>`;
        });
    }

    var person_html = "";
    var person = this_news.person;
    if(person.length > 0) {
        person = person.split("|").filter(onlyUnique);
        person_html = `Identified person:`;
        person.forEach(function (element) {
            person_html = `${person_html}<li>${element}</li>`;
        });
    }

    var thumbnail = String(this_news.thumbnail);
    if (thumbnail == "" || thumbnail=="NaN"){
        thumbnail = "/static/img/default_news_thumbnail.png";
    }

    var timeline_html = "";
    if (show_timeline){
        var this_timestamp_html = "";
        var this_timestamp = this_news.date.split("-", 2).join("-");  // get year-month
        if (this_timestamp != last_timestamp){
            this_timestamp_html = `<div class="timestamp">${this_timestamp}</div>`;
            last_timestamp = this_timestamp;
        }
        timeline_html = [
            `<div class="timeline"></div>`,
            `${this_timestamp_html}`,
        ].join("\n");
    }
    return [
            `<article class="news">`,
                `${timeline_html}`,
                `<div class="news_wrap">`,
                    `<div class="news_left_wrap">`,
                        `<a target="_blank" href="${this_news.href}"><img src="${thumbnail}"></a>`,
                        `<div class="news_holder">`,
                            `<a class="title" target="_blank" href="${this_news.href}">${this_news.title}</a>`,
                            `<div class="meta">`,
                                `<span class="news_media">${this_news.media}</span>`,
                                `<span class="sep"></span>`,
                                `<span class="date">${this_news.date}</span>`,
                            `</div>`,
                            `<div class="abstract">${this_news.abstract}</div>`,
                        `</div>`,
                    `</div>`,
                    `<div class="news_right_wrap">`,
                        `<div class="news_sentiment">`,
                            `Sentiment`,
                            `<span class="sentiment_class ${sentiment_class}">${sentiment_label}`,
                                `<div class="sentiment_override_wrap">`,
                                    `Sentiment override: <br/>`,
                                    `<div class="sentiment_override_button very_positive" article_id="${this_news.article_id}">Very Positive</div><br/>`,
                                    `<div class="sentiment_override_button positive" article_id="${this_news.article_id}">Positive</div><br/>`,
                                    `<div class="sentiment_override_button neutral" article_id="${this_news.article_id}">Neutral</div><br/>`,
                                    `<div class="sentiment_override_button negative" article_id="${this_news.article_id}">Negative</div><br/>`,
                                    `<div class="sentiment_override_button very_negative" article_id="${this_news.article_id}">Very Negative</div>`,
                                `</div>`,
                            `</span>`,
                        `</div>`,
                        `<div class="sentiment_score">${sentiment_score}</div>`,
                        `<div class="news_organizations">${organizations_html}</div>`,
                        `<div class="news_person">${person_html}</div>`,
                    `</div>`,
                    `<div class="clear_both"></div>`,
                `</div>`,
            `</article>`
        ].join("\n");
}