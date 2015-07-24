(function(){
  $(document).ready(function(){

    var addCrawlForm = document.getElementById("addCrawlForm")

    addCrawlForm.onsubmit = function(event){
      event.preventDefault();

      var xhr = new XMLHttpRequest();

      xhr.open('POST', window.location.href + "add_crawl/", true);
      xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
      xhr.onload = function(){
        if ((xhr.status === 200) || (xhr.status === 302)){
          success = true;
        } else {
          crispyFormErrors.showFormErrors(xhr.response);
          success = false;
        }
      }

      var seeds_list = addCrawlForm.seeds_list.files[0]
      var name = addCrawlForm.name.value;
      var csrfmiddlewaretoken = addCrawlForm.csrfmiddlewaretoken.value;
      var description = addCrawlForm.description.value;
      var crawl_model = addCrawlForm.crawl_model.value;
      var rounds_left = addCrawlForm.rounds_left.value;
      var textseeds = addCrawlForm.textseeds.value;
      var submit = addCrawlForm.submit.value;
      // Safari hates addCrawlForm.crawler.value, so use a jquery selector instead.
      var crawler = $("input[name='crawler']").val();

      var formData = new FormData();

      formData.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
      formData.append("name", name);
      formData.append("description", description);
      formData.append("crawl_model", crawl_model);
      formData.append("rounds_left", rounds_left);
      formData.append("textseeds", textseeds);
      if (typeof seeds_list != 'undefined'){
        formData.append("seeds_list", seeds_list, seeds_list.name);
      }
      formData.append("crawler", crawler);
      formData.append("submit", submit);

      crispyFormErrors.clearErrors([
        "csrfmiddlewaretoken",
        "name",
        "description",
        "crawl_model",
        "rounds_left",
        "seeds_list",
        "crawler",
        "submit",
      ]);

      xhr.send(formData);
    }

  });
})();
