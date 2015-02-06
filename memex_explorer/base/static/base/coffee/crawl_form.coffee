class CrawlForm extends Backbone.View

    crawler = $ '#crawler'
    data_model = $ '#data_model'
    new_model_file = $ "#new_model_file"
    new_model_features = $ "#new_model_features"
    new_model_name = $ "#new_model_name"
    model_options = $ '.model_options'
    radio1 = $ '#radio1'
    radio2 = $ '#radio2'
    

    initialize: ->
        model_options.prop "disabled", true
        
    crawler.change ->
        if crawler.val() == "ache"
            radio1.prop "disabled", false
            radio2.prop "disabled", false
        else
            model_options.prop "disabled", true

    radio1.change ->
        data_model.prop "disabled", true
        new_model_file.prop "disabled", false
        new_model_features.prop "disabled", false
        new_model_name.prop "disabled", false

    radio2.change ->
        data_model.prop "disabled", false
        new_model_file.prop "disabled", true
        new_model_features.prop "disabled", true
        new_model_name.prop "disabled", true

crawl_form = new CrawlForm
