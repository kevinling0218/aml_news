function enable_sentiment_override(){
    $(".sentiment_override_button").off('click', sentiment_override_button_clicked) // remove handler
              .on('click', sentiment_override_button_clicked); // add handler
}

function sentiment_override_button_clicked(){
    var button = $(this);
    var parent_sentiment_class = button.closest(".sentiment_class");

    var sentiment_text = button.html();
    parent_sentiment_class.html(sentiment_text);

    var sentiment_class = sentiment_text.replace(" ", "_").toLowerCase();
    parent_sentiment_class.removeClass("very_positive");
    parent_sentiment_class.removeClass("positive");
    parent_sentiment_class.removeClass("neutral");
    parent_sentiment_class.removeClass("negative");
    parent_sentiment_class.removeClass("very_negative");
    parent_sentiment_class.addClass(sentiment_class);

    var article_id = button.attr("article_id");
}