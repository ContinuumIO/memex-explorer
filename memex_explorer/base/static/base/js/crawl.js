$( document ).ready(function() {


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



  setInterval(function(){
    $.ajax({
      type: "POST",
      data: {"action": "status"},
      success: function(response){
        $( '#status' ).text(response.status);
        $( '#stats-pages' ).text(response.pages_crawled);
        $( '#stats-harvest' ).text(response.harvest_rate);
        if (response.status == "stopped") {
          $('#stopButton').attr("disabled", true);
        }
      }
    });
  }, 5000);

});