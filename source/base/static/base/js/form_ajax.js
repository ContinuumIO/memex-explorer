(function(exports){

  exports.toFormData = function(formElement){
    var objects = new FormData();
    var formData = formElement.serializeArray();
    _.each(formData, function(formObject){
      objects[formObject.name] = formObject.value;
    });
    return objects;
  }

  exports.toJson = function(formElement){
    var objects = {};
    var formData = formElement.serializeArray();
    _.each(formData, function(formObject){
      objects[formObject.name] = formObject.value;
    });
    return objects;
  }

})(this.ajaxForms = {});
