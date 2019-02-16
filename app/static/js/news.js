$( "#select_industry").change(function() {
    window.location.href = "/news/".concat($("#select_industry").val());
});

$(function() {
    enable_utility_auto_load();
    append_data()
});

/*
 |--------------------------------------------------------------------------
 | scroll down auto load
 |--------------------------------------------------------------------------
 */
var utility_auto_load_paras = {
    first_item_index    : 0,
    items_per_page      : 10,
    no_more_data        : false,
    distance_to_bottom  : 150,
    loading             : false
};

function enable_utility_auto_load() {
    $(window).scroll(function () {
        //when scroll to bottom, auto load more items
        var distance_to_bottom = $(document).height() - ($(window).scrollTop() + $(window).height());
        if (distance_to_bottom < utility_auto_load_paras.distance_to_bottom) {
            if (!utility_auto_load_paras.loading && !utility_auto_load_paras.no_more_data) {
                append_data();
            }
        }
    });
}

function append_data() {
    utility_auto_load_paras.loading = true; //imply that we're loading

    var first_item_index = utility_auto_load_paras.first_item_index;
    var items_per_page = utility_auto_load_paras.items_per_page;

    // append data for each item
    $.ajax({
        url: '/ajax_post_news',
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({
            'industry':industry,
            'first_item_index':first_item_index,
            'items_per_page': items_per_page
        }),
        type: 'POST',
        success: function(response) {
            var news = JSON.parse(response['news']);
            if(response['no_more_data'] == 1){
                utility_auto_load_paras.no_more_data = true;
            }else{
                for (var i = 0; i < news.length; i++) {
                    var this_news = news[i];
                    $("#section_news").append(get_news_html(this_news, show_timeline=true));
                    enable_sentiment_override();
                }
            }
            first_item_index =  first_item_index + items_per_page;
            utility_auto_load_paras.first_item_index = first_item_index;
            utility_auto_load_paras.loading = false; //imply that we've finished loading
            }
    });
}

