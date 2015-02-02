$( document ).ready(function() {


  $('#playButton').on('click', function() {

    $( '#status' ).text( "Starting..." );
    this.disabled = true;
    $('#stopButton').removeAttr("disabled");

    $.ajax({
      type: "POST",
      data: {"action": "start"},
      success: function(response) {
        console.log(response);
        if (response.state != "Error") $( '#status' ).text(response.state);
        else console.log(response)},
      failure: function() {
          $( '#status' ).text( "Error (could not start crawl)" );
      }
    });
});

});