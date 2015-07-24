(function(exports){

  function displayError(inputDiv, error){
    $("#div_id_" + inputDiv).addClass("has-error");
    $("#error_id_" + inputDiv).attr("hidden", false).html(error);
  }

  function removeError(inputDiv){
    $("#div_id_" + inputDiv).removeClass("has-error");
    $("#error_id_" + inputDiv).attr("hidden", true).html("");
  }

  exports.showFormErrors = function(errorResponse){
    var errorsObject = JSON.parse(errorResponse).form_errors;
    var errorsArray = Object.keys(errorsObject);
    _.each(errorsArray, function(field){
      displayError(field, errorsObject[field])
    })
  }

  exports.clearErrors = function(inputs){
    _.each(inputs, function(field){
      removeError(field);
    })
  }

})(this.crispyFormErrors = {});
