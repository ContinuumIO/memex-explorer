var tad = tad || {};

(function(){

  function tadUpdate(){
    return $.ajax({
      type: "POST",
      data: {
        "get": "data",
      },
      success: function(response){
        $("#tadResponse").html(response)
      },
      error: function(response){
        $("#tadResponse").html(response)
      },
    });
  }

  $(document).ready(function(){
    $("#tadUpdate").click(function(){
      tadUpdate();
      setInterval(function(){
        tadUpdate();
      }, 5000);
    });
  });

})();
