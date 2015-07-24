$(document).ready(function(){
    var crawler = $('input[name="crawler"]');
    var nutch = $('#id_crawler_1');
    var crawl_model = $('#id_crawl_model');
    var model_div = $('#div_id_crawl_model');
    var rounds_div = $('#div_id_rounds_left');
    var rounds = $('#id_rounds_left');

    var on_crawler_change = function(){
        if (nutch[0].checked){
            crawl_model.prop("disabled", true);
            rounds.prop("disabled", false);
            model_div.addClass("input-greyed-out");
            model_div.removeClass("input-available");
            rounds_div.addClass("input-available");
            rounds_div.removeClass("input-greyed-out");
        } else {
            crawl_model.prop("disabled", false);
            rounds.prop("disabled", true);
            model_div.addClass("input-available");
            model_div.removeClass("input-greyed-out");
            rounds_div.addClass("input-greyed-out");
            rounds_div.removeClass("input-available");
        }
    }

    // In case the form is reloaded with ACHE set, fire once
    on_crawler_change();

    crawler.change(on_crawler_change);

});
