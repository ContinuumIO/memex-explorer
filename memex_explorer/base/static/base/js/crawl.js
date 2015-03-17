$( document ).ready(function() {

  $( document ).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
  });

  $('#playButton').on('click', function() {

    $( '#status' ).text( "starting" );
    this.disabled = true;
    $('#stopButton').removeAttr("disabled");

    $.ajax({
      type: "POST",
      data: {"action": "start"},
      success: function(response) {
        console.log(response);
        if (response.status != "error") $( '#status' ).text(response.status);
        else console.log(response)},
          failure: function() {
            $( '#status' ).text( "Error (could not start crawl)" );
          }
    });
  });



  $('#stopButton').on('click', function() {

    $( '#status' ).text( "stopping" );
    this.disabled = true;

    $.ajax({
      type: "POST",
      data: {"action": "stop"},
      success: function(response) {
        console.log(response);
        if (response.status != "error") $( '#status' ).text(response.status);
        else console.log(response)},
          failure: function() {
            $( '#status' ).text( "Error (could not stop crawl)" );
          }
        });
  });


  $('#restartButton').on('click', function() {

    $( '#status' ).text( "restarting" );
    this.disabled = true;

    $.ajax({
      type: "POST",
      data: {"action": "start"},
      success: function(response) {
        console.log(response);
        if (response.status != "error") $( '#status' ).text(response.status);
        else console.log(response)},
          failure: function() {
            $( '#status' ).text( "Error (could not restart crawl)" );
          }
        });
  });

  setInterval(function(){
    $.ajax({
      type: "POST",
      data: {"action": "status"},
      success: function(response){
        $( '#status' ).text(response.status);
        $( '#stats-pages' ).text(response.pages_crawled);
        if ('harvest_rate' in response) {
          $( '#stats-harvest' ).text(response.harvest_rate);
          if (response.harvest_rate > 0) {
            $('#getSeeds').removeAttr("disabled");
          }
        }
        if (response.status == "stopped") {
          $('#stopButton').attr("disabled", true);
          $('#restartButton').removeAttr("disabled");
        } else if (response.status == "running") {
          $('#stopButton').removeAttr("disabled");
        }
      }
    });
  }, 5000);

    $("#gotoSolr").on('click', function(){
        if (window.location.port){
            solr_url = "http://" + window.location.hostname + ":8983/solr/#"
        }else{
            solr_url = "http://" + window.location.host + ":8983/solr/#"
        }
        window.open(solr_url, '_blank');
    });

});

