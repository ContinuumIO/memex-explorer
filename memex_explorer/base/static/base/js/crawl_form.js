var CrawlForm, crawl_form,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

CrawlForm = (function(_super) {
  var crawler, data_model, model_options, new_model_features, new_model_file, new_model_name, radio1, radio2;

  __extends(CrawlForm, _super);

  function CrawlForm() {
    return CrawlForm.__super__.constructor.apply(this, arguments);
  }

  crawler = $('#crawler');

  data_model = $('#data_model');

  new_model_file = $("#new_model_file");

  new_model_features = $("#new_model_features");

  new_model_name = $("#new_model_name");

  model_options = $('.model_options');

  radio1 = $('#radio1');

  radio2 = $('#radio2');

  CrawlForm.prototype.initialize = function() {
    return model_options.prop("disabled", true);
  };

  crawler.change(function() {
    if (crawler.val() === "ache") {
      radio1.prop("disabled", false);
      return radio2.prop("disabled", false);
    } else {
      return model_options.prop("disabled", true);
    }
  });

  radio1.change(function() {
    data_model.prop("disabled", true);
    new_model_file.prop("disabled", false);
    new_model_features.prop("disabled", false);
    return new_model_name.prop("disabled", false);
  });

  radio2.change(function() {
    data_model.prop("disabled", false);
    new_model_file.prop("disabled", true);
    new_model_features.prop("disabled", true);
    return new_model_name.prop("disabled", true);
  });

  return CrawlForm;

})(Backbone.View);

crawl_form = new CrawlForm;
