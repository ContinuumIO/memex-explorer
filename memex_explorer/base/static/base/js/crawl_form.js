$(document).ready(function(){
    var crawler = $("[name='crawler']");
    var crawl_model = $('#id_crawl_model');

    crawl_model.prop("disabled", true);

    crawler.change(function(){
        console.log("Crawler has changed!");
        if (crawler.val() === "nutch"){
            crawl_model.prop("disabled", true);
        } else {
            crawl_model.prop("disabled", false);
        }
    });
});
