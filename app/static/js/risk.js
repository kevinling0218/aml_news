var selected_news = news;

$(function() {
    create_select_entity();
    create_monthly_sentiment_chart();
    create_positive_news();
    create_negative_news();
    create_neutral_news();
});

$( "#select_industry").change(function() {
    window.location.href = "/risk/".concat($("#select_industry").val());
});


function create_select_entity(){
    for(i = 0; i<entities.length; i++){
        var selected = '';
        if (entities[i].toLowerCase() == entity.toLowerCase()){
            selected = 'selected="selected"'
        }
        $("#select_entity").append(
            `<option ${selected} value="${entities[i]}">${entities[i]}</option>`
        );
    }

    $( "#select_entity").change(function() {
        window.location.href = "/risk/".concat(
            $("#select_industry").val()
        ).concat(
            '?entity='
        ).concat(
            $("#select_entity").val().replace(/&/g, "%26")
        );
    });
}

function create_monthly_sentiment_chart() {
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


    var emb_score = [];
    var emb_date = [];
    var emb_text = [];

    for (var i = 0; i < monthly_sentiment_emb.length; i++) {
        var this_emb = monthly_sentiment_emb[i];
        emb_score.push(this_emb.sentiment_emb);
        emb_date.push(parser(this_emb.year_month+'-15'));
        emb_text.push('Risk score: '+Math.round(this_emb.sentiment_emb)+'<br>'+this_emb.year_month)
    }

    emb_score = emb_score.map(function(x) {
        return x / d3.max([Math.abs(d3.max(emb_score)), Math.abs(d3.min(emb_score))]) * news_sentiment_score_range;
    });

    var trace2 = {
        x: emb_date,
        y: emb_score,
        text: emb_text,
        mode: 'markers+lines',
        hoverinfo: "text",
        // name: 'steepest',
        line: {color: 'rgb(104,104,104)'},
        type: 'scatter'
    };

    var data = [trace1, trace2];

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
        plot_bgcolor: '#f9f9f9',
        showlegend: false
    };


    Plotly.newPlot('monthly_sentiment_chart', data, layout);

    // Handle click event
    var sentiment_trend_chart = document.getElementById('monthly_sentiment_chart');
    sentiment_trend_chart.on('plotly_click', function(d){
        console.log(d);
    });
}

function create_positive_news(){
    $("#positive_news_list").hide();
    for (var i = 0; i < positive_news.length; i++) {
        $("#positive_news_list").append(get_news_html(positive_news[i]));
        enable_sentiment_override();

    }
    // $("#positive_news_list").slideDown(1000);

    var positive_news_count = 'No';
    if(positive_news.length > 0){
        positive_news_count = positive_news.length
    }
    $("#positive_news_count").html(positive_news_count);

    $("#positive_news_toggle").click(function(){
        if($(this).attr('status') == 'shown'){
            $("#positive_news_list").hide();
            $(this).attr('status', 'hidden');
            $(this).html('Show News')
        }else{
            $("#positive_news_list").slideDown(1000);
            $(this).attr('status', 'shown');
            $(this).html('Hide News')
        }
    })
    if(positive_news.length == 0){
        $("#positive_news_toggle").hide();
    }
}

function create_negative_news(){
    $("#negative_news_list").hide();
    for (var i = 0; i < negative_news.length; i++) {
        $("#negative_news_list").append(get_news_html(negative_news[i]));
        enable_sentiment_override();

    }
    // $("#negative_news_list").slideDown(1000);

    var negative_news_count = 'No';
    if(negative_news.length > 0){
        negative_news_count = negative_news.length
    }
    $("#negative_news_count").html(negative_news_count);

    $("#negative_news_toggle").click(function(){
        if($(this).attr('status') == 'shown'){
            $("#negative_news_list").hide();
            $(this).attr('status', 'hidden');
            $(this).html('Show News')
        }else{
            $("#negative_news_list").slideDown(1000);
            $(this).attr('status', 'shown');
            $(this).html('Hide News')
        }
    });
    if(negative_news.length == 0){
        $("#negative_news_toggle").hide();
    }
}

function create_neutral_news(){
    $("#neutral_news_list").hide();
    for (var i = 0; i < neutral_news.length; i++) {
        $("#neutral_news_list").append(get_news_html(neutral_news[i]));
        enable_sentiment_override();

    }
    // $("#neutral_news_list").slideDown(1000);

    var neutral_news_count = 'No';
    if(neutral_news.length > 0){
        neutral_news_count = neutral_news.length
    }
    $("#neutral_news_count").html(neutral_news_count);

    $("#neutral_news_toggle").click(function(){
        if($(this).attr('status') == 'shown'){
            $("#neutral_news_list").hide();
            $(this).attr('status', 'hidden');
            $(this).html('Show News')
        }else{
            $("#neutral_news_list").slideDown(1000);
            $(this).attr('status', 'shown');
            $(this).html('Hide News')
        }
    })
    if(neutral_news.length == 0){
        $("#neutral_news_toggle").hide();
    }
}