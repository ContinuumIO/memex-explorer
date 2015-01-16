$( document ).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    $('#reload').on('click', function(){
        location.reload(true);
    });

    var ME = ME || {};
    ME.polling = true;

    var show_error = function(){
            ME.polling = false;
            // alert("Error: could not start crawl.")
            $( '#status' ).text( "Error (could not start crawl)" );
    }

    $('#playButton').on('click', function() {

        $( '#status' ).text( "Starting..." );

        this.disabled = true;
        $('#stopButton').removeAttr("disabled");

        $.ajax({
          type: "POST",
            url: document.URL + "/run",
          success: function(retval) {
            if (retval == "Error") show_error();
            else $( '#status' ).text(retval);
          },
          failure: function() {
            show_error();
          }
        });
    });

    $('#stopButton').on('click', function(){
        $( '#status' ).text( "Stopping..." );
        this.disabled = true;
        $.ajax({
          type: "POST",
            url: document.URL + "/stop",
          success: function(retval) {
            if (retval == "Error") show_error();
            else $( '#status' ).text(retval);
          },
          failure: function() {
            show_error();
          }
        });
        $.ajax({ type: "GET", url: document.URL + "/stats",
          success: function(data) {
                console.log("stats-data" + data);
                if (data.nutch) {
                  $.ajax({
                    type: "POST",
                    url: document.URL + "/update_stats",
                    contentType: 'application/json',
                    data: JSON.stringify({crawled: data.num_crawled, crawler: 'nutch'}),
                  });
                } else {
                  $.ajax({
                    type: "POST",
                    url: document.URL + "/update_stats",
                    contentType: 'application/json',
                    data: JSON.stringify({crawled: data.num_crawled, harvest: data.harvest_rate, crawler:'ache'}),
                  });
                }
            },
          failure: function() {
            $( '#stats-data' ).html('<h4>(Statistics are not yet available for this crawl.)</h4>');
          }
        });
    });

    (function pollStatus() {

      // If polling has been turned off, break the loop
      if (!ME.polling) return;

        $.ajax({
            url: document.URL + "/status",
            type: "GET",
            success: function(data) { $('#status').text( data ) },
            complete: setTimeout(pollStatus, 5000),
            timeout: 2000
        });
    })();

    $('#imageDump').on('click', function(){
        $.ajax({
          type: "POST",
          url: document.URL + "/dump",
          success: console.log("crawlImagesDumped")
        }).done(function() {
          window.location.href = document.URL
        });
    }); 

    function statsPoll(){ 
          $.ajax({ type: "GET", url: document.URL + "/stats",
          success: function(data) {
                console.log("stats-data" + data);
                if (data.nutch) {
                  $( '#stats-data' ).html(
                      '<div class="col-sm-12"><table class="table table-striped"><tr><th>Site(s) crawled</th></tr><tr><td>' 
                      + data.num_crawled 
                      + '</td></tr></table>'
                    );
                } else {
                  $( '#stats-data' ).html(
                      '<div class="col-sm-12"><table class="table table-striped"><tr><th>Harvest Rate</th><th>Site(s) crawled</th></tr><tr><td>' 
                      + data.harvest_rate 
                      + '</td><td>' 
                      + data.num_crawled 
                      +'</td></tr></table></div>'
                    );
                }
            },
          failure: function() {
                  $( '#stats-data' ).html('<h4>(Statistics are not yet available for this crawl.)</h4>');
          }
        })
    }

    var statsInterval = setInterval(function(){statsPoll()}, 10000);
});

