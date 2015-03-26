$( document ).ready(function() {

  $( document ).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
  });

  $("#dumpImages").attr("disabled", true);

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


$('#forceStop').click(function(){
    swal({
        title: "Are you sure?",
        text: "Forcing a nutch crawl to stop may result in corrupted crawl data.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: '#DD6B55',
        confirmButtonText: 'Yes!',
        cancelButtonText: "No, cancel!",
        closeOnConfirm: false,
        closeOnCancel: false
    },
    function(isConfirm){
        if (isConfirm){
            swal("Success", "", "success");
            $('#forceStop').attr("disabled", true);
            $('#stopButton').attr("disabled", true);
            $.ajax({
                type: "POST",
                data: {"action": "force_stop"},
                success: function(response) {
                    console.log(response);
                    if (response.status != "error") $( '#status' ).text(response.status);
                    else console.log(response)},
                    failure: function() {
                        $( '#status' ).text( "Error (could not stop crawl)" );
                    }
            });
        } else {
            swal("Cancelled", "", "error");
        }
    })
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
          $('#dumpImages').removeAttr("disabled");
        } else if (response.status == "running") {
          $('#stopButton').removeAttr("disabled");
        }
      }
    });
  }, 5000);

    $("#gotoSolr").on('click', function(){
        solr_url = "http://" + window.location.hostname + ":8983/solr/#"
        window.open(solr_url, '_blank');
    });

    $("#dumpImages").on('click', function(){
        $("#nutchButtons").append('<i id="imageSpinner" class="fa fa-refresh fa-spin" style="font-size:20;"></i>')
        $.ajax({
            type: "POST",
            data: {"action": "dump"},
            success: function(response) {
                sweetAlert("Success", "Images have been successfully dumped!", "success");
                $("#imageSpinner").remove()
            },
            failure: function() {
                sweetAlert("Error", "Image dump has failed.", "error");
                $("#imageSpinner").remove()
            }
        });
    });

});

