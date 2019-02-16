var selected_news = news;

$(function() {
    create_topic_chart();
    create_sentiment_trend_chart();
});

$( "#select_industry").change(function() {
    window.location.href = "/summary/".concat($("#select_industry").val());
});

function clip(x, min, max){
    return Math.min(Math.max(x, min), max);
}

function create_topic_chart() {
    var topic_sentiment_score = [];
    var topic_score = [];
    var topic_title = [];
    var size = [];
    var topic_id = [];

    for (var i = 0; i < topics.length; i++) {
        var topic = topics[i];
        topic_sentiment_score.push(topic.topic_sentiment_score);
        topic_score.push(topic.topic_score - 0.5);
        topic_title.push(topic.topic_title);
        size.push(clip(topic.news_count_rank*1.5, 15, 45));
        topic_id.push(topic.topic_id);
    }

    var topic_sentiment_score_range = d3.max([Math.abs(d3.max(topic_sentiment_score)), Math.abs(d3.min(topic_sentiment_score))]);

    // Set minimum sentiment score (for color to be correct)
    topic_sentiment_score.push(-1);
    topic_score.push(0);
    topic_title.push("");
    size.push(0);
    topic_id.push(1000);

    // Set maximum sentiment score (for color to be correct)
    topic_sentiment_score.push(1);
    topic_score.push(0);
    topic_title.push("");
    size.push(0);
    topic_id.push(1000);

    var trace1 = {
        x: topic_score,
        y: topic_sentiment_score,
        text: topic_title,
        hoverinfo: "text",
        marker: {
            size: size,
            opacity: 0.8,
            color: topic_sentiment_score,
            colorscale: [
                ['0.0', 'rgb(240, 30, 30)'],
                ['0.4', 'rgb(231, 142, 142)'],
                ['0.5', 'rgb(255, 240, 197)'],
                ['0.6', 'rgb(212, 231, 205)'],
                ['1.0', 'rgb(30, 240, 30)']
            ]
        },
        mode: 'markers',
        type: 'scatter'
    };

    var data = [trace1];

    var layout = {
        xaxis: {
            // title: 'impact',
            range: [-0.6, 0.6],
            // autotick: false,
            // showticklabels: false,
            zeroline: true,
            zerolinecolor: '#ccc',
            showgrid: false,
            tickvals: [-0.3, 0.3],
            ticktext: ['Low Impact', 'High Impact']
        },
        yaxis: {
            // title: 'sentiment',
            range: [-topic_sentiment_score_range-0.1, topic_sentiment_score_range+0.1],
            // autotick: false,
            // showticklabels: false,
            zeroline: true,
            zerolinecolor: '#ccc',
            showgrid: false,
            tickvals: [-topic_sentiment_score_range/2, topic_sentiment_score_range/2],
            ticktext: ['Negative Sentiment', 'Positive Sentiment'],
            tickangle: 270
        },
        hovermode: 'closest',
        width: 960,
        height: 400,
        margin: {
            l: 40,
            r: 40,
            b: 40,
            t: 40,
            pad: 15
        },
        paper_bgcolor: '#f9f9f9',
        plot_bgcolor: '#f9f9f9'
    };


    Plotly.newPlot('topic_chart', data, layout);

    var topic_chart = document.getElementById('topic_chart');
    // Handle click event
    topic_chart.on('plotly_click', function(d){
        var point_number = d.points[0].pointNumber;
        var selcted_topic_id = topic_id[point_number];

        selected_news = [];
        $("#section_news").html("");
        $("#section_news").hide();
        last_timestamp = "";
        for (var i = 0; i < news.length; i++) {
            var this_news = news[i];
            if (this_news.topic_id == selcted_topic_id){
                selected_news.push(this_news);
                $("#section_news").append(get_news_html(this_news, show_timeline=true));
                enable_sentiment_override();
            }
        }
        $("#section_news").slideDown(1000);
        create_sentiment_trend_chart();
    });

    // Handle Hover event
    topic_chart.on('plotly_hover', function(d){
        var point_number = d.points[0].pointNumber;
        var selcted_topic_id = topic_id[point_number];
        $("#word_cloud img").attr("src", `../static/img/${industry}_wordcloud_topic_${selcted_topic_id}.png`);
    })
     .on('plotly_unhover', function(d){

    });
}

function create_sentiment_trend_chart() {
    var news_sentiment = [];
    var news_score = [];
    var news_title = [];
    var news_date = [];

    var parser = d3.timeParse("%Y-%m-%d");

    for (var i = 0; i < selected_news.length; i++) {
        var this_news = selected_news[i];
        news_sentiment.push(this_news.sentiment_score);
        news_score.push(this_news.article_score);
        news_title.push(this_news.title);
        news_date.push(parser(this_news.date))
    }

    var news_sentiment_score_range = d3.max([Math.abs(d3.max(news_sentiment)), Math.abs(d3.min(news_sentiment))]);

    var news_date_min = d3.min(news_date);
    var news_date_max = d3.max(news_date);
    // Set minimum sentiment score (for color to be correct)
    news_sentiment.push(-1);
    news_score.push(0);
    news_title.push("");
    news_date.push(parser("1000-01-01"));

    // Set maximum sentiment score (for color to be correct)
    news_sentiment.push(1);
    news_score.push(0);
    news_title.push("");
    news_date.push(parser("3000-01-01"));

    var trace1 = {
        x: news_date,
        y: news_sentiment,
        text: news_title,
        hoverinfo: "text+x",
        marker: {
            color: news_sentiment,
            colorscale: [
                ['0.0', 'rgb(240, 30, 30)'],
                ['0.4', 'rgb(231, 142, 142)'],
                ['0.5', 'rgb(255, 240, 197)'],
                ['0.6', 'rgb(212, 231, 205)'],
                ['1.0', 'rgb(30, 240, 30)']
            ],
            cauto: false,
            cmin : -1,
            cmax : 1,
            line: {
                color: news_sentiment,
                width: 1.5,
                colorscale: [
                    ['0.0', 'rgb(240, 30, 30)'],
                    ['0.4', 'rgb(231, 142, 142)'],
                    ['0.5', 'rgb(255, 240, 197)'],
                    ['0.6', 'rgb(212, 231, 205)'],
                    ['1.0', 'rgb(30, 240, 30)']
                ],
                cauto: false,
                cmin : -1,
                cmax : 1
            }
        },
        // mode: 'markers',
        type: 'bar'
    };

    var data = [trace1];

    var layout = {
        xaxis: {
            range:[news_date_min, news_date_max]
        },
        yaxis: {
            // title: 'sentiment',
            range: [-news_sentiment_score_range-0.1, news_sentiment_score_range+0.1],
            // autotick: false,
            // showticklabels: false,
            showgrid: false,
            tickvals: [-news_sentiment_score_range/2, news_sentiment_score_range/2],
            ticktext: ['Negative Sentiment', 'Positive Sentiment'],
            tickangle: 270
        },
        hovermode: 'closest',
        width:960,
        height: 400,
        margin: {
            l: 40,
            r: 40,
            b: 50,
            t: 40,
            pad: 15
        },
        paper_bgcolor: '#f9f9f9',
        plot_bgcolor: '#f9f9f9'
    };


    Plotly.newPlot('sentiment_trend_chart', data, layout);

    // Handle click event
    var sentiment_trend_chart = document.getElementById('sentiment_trend_chart');
    sentiment_trend_chart.on('plotly_click', function(d){
        console.log(d);
    });
}


$("#reset_button").click(function(){
    selected_news = news;
    create_topic_chart();
    create_sentiment_trend_chart();
    $("#section_news").html("");
    $("#word_cloud img").attr("src", `../static/img/${industry}_wordcloud.png`);
});