var selected_news = news;

$(function() {
    console.log('jquery is working!');

    // d3.csv("/static/data/smrt_topics_summary.csv", function(topics) {
    //   console.log(topics[0]);
    // });

    select_company_in_url();

    create_topic_chart();
    create_sentiment_trend_chart();
});

function select_company_in_url(){
    $("#select_company").val(company);
}

$( "#select_company").change(function() {
    window.location.href = "/".concat($("#select_company").val());
});


function clip(x, min, max){
    return Math.min(Math.max(x, min), max);
}

function create_topic_chart() {
    var topic_sentiment = [];
    var topic_score = [];
    var topic_title = [];
    var size = [];
    var topic_id = [];

    for (var i = 0; i < topics.length; i++) {
        var topic = topics[i];
        topic_sentiment.push(topic.topic_sentiment);
        topic_score.push(topic.topic_score);
        topic_title.push(topic.topic_title);
        size.push(clip(topic.news_count_rank*4, 15, 40));
        topic_id.push(topic.topic_id);
    }

    var trace1 = {
        x: topic_score,
        y: topic_sentiment,
        text: topic_title,
        hoverinfo: "text",
        marker: {
            size: size,
            opacity: 0.8,
            color: topic_sentiment,
            colorscale: [
                ['0.0', 'rgb(182,85,85)'],
                ['0.5', 'rgb(201,185,125)'],
                ['1.0', 'rgb(106,165,110)']
            ]
        },
        mode: 'markers',
        type: 'scatter'
    };

    var data = [trace1];

    var layout = {
        xaxis: {
            title: 'impact',
            range: [-0.1, 1.1]
        },
        yaxis: {
            title: 'sentiment',
            range: [-1.2, 1.2]
        },
        hovermode: 'closest',
        title:'Top 10 Topics',
        width: 800,
        height: 400,
        margin: {
            l: 30,
            r: 30,
            b: 30,
            t: 30,
            pad: 0
        },
        paper_bgcolor: '#fff',
        plot_bgcolor: '#fff'
    };


    Plotly.newPlot('topic_chart', data, layout);

    // Handle click event
    var topic_chart = document.getElementById('topic_chart');
    topic_chart.on('plotly_click', function(d){
        var point_number = d.points[0].pointNumber;
        var selcted_topic_id = topic_id[point_number];

        selected_news = [];
        $("#section_news").html("");
        for (var i = 0; i < news.length; i++) {
            var this_news = news[i];
            if (this_news.topic_id == selcted_topic_id){
                selected_news.push(this_news);

                $("#section_news").append(get_news_html(this_news));
            }
        }
        create_sentiment_trend_chart();
    });
}

function get_news_html(this_news){
    return [
            '<div class="news">',
                '<a target="_blank" href="'+this_news.href+'"><img src="'+this_news.thumbnail+'"></a>',
                '<div class="news_holder">',
                    '<a class="title" target="_blank" href="'+this_news.href+'">'+this_news.title+'</a>',
                    '<div class="meta">',
                        '<span class="news_media">'+this_news.media+'</span>',
                        '<span class="sep"></span>',
                        '<span class="date">'+this_news.date+'</span>',
                        '<span class="sep"></span>',
                        '<span class="sentiment">Sentiment '+this_news.article_sentiment+'</span>',
                    '</div>',
                    '<div class="abstract">'+this_news.abstract+'</div>',
                '</div>',
            '</div>'
        ].join("\n");
}

function create_sentiment_trend_chart() {
    var news_sentiment = [];
    var news_score = [];
    var news_title = [];
    var news_date = [];

    var parser = d3.timeParse("%d/%m/%y");

    for (var i = 0; i < selected_news.length; i++) {
        var this_news = selected_news[i];
        news_sentiment.push(this_news.article_sentiment);
        news_score.push(this_news.article_score);
        news_title.push(this_news.title);
        news_date.push(parser(this_news.date))
    }

    var trace1 = {
        x: news_date,
        y: news_sentiment,
        text: news_title,
        hoverinfo: "text",
        marker: {
            color: news_sentiment,
            colorscale: [
                ['0.0', 'rgb(182,85,85)'],
                ['0.5', 'rgb(201,185,125)'],
                ['1.0', 'rgb(106,165,110)']
            ],
            cauto: false,
            cmin : -1,
            cmax : 1,
            line: {
                color: news_sentiment,
                width: 1.5,
                colorscale: [
                    ['0.0', 'rgb(182,85,85)'],
                    ['0.5', 'rgb(201,185,125)'],
                    ['1.0', 'rgb(106,165,110)']
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
        // xaxis: {
        //     range:[parser("01/01/17"), parser("28/02/18")]
        // },
        yaxis: {
            title: 'sentiment',
            range: [-1.1, 1.1]
        },
        hovermode: 'closest',
        width:800,
        height: 400,
        margin: {
            l: 30,
            r: 30,
            b: 30,
            t: 30,
            pad: 0
        },
        paper_bgcolor: '#fff',
        plot_bgcolor: '#fff'
    };


    Plotly.newPlot('sentiment_trend_chart', data, layout);

    // Handle click event
    var sentiment_trend_chart = document.getElementById('sentiment_trend_chart');
    sentiment_trend_chart.on('plotly_click', function(d){
        console.log(d);
    });
}