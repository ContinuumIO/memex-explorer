(function(){
  // $(document).ready(function(){
  //
  //   var addProjectForm = $("#addProjectForm");
  //
  //   function updateProjectList(jsonResponse){
  //     var template = _.template($("#indexProjectItem").html());
  //     $("#projectList").append(template(JSON.parse(jsonResponse)));
  //   }
  //
  //   addProjectForm.submit(function(event){
  //     event.preventDefault();
  //     var xhr = ajaxForms.xhrFactory(window.location.href + "add_project/", "addProjectForm");
  //     xhr.onreadystatechange = function(){
  //       if ((xhr.readyState == 4) && (xhr.status == 200)){
  //         console.log(xhr.response);
  //         updateProjectList(xhr.response);
  //         $("#newProjectModal").modal('hide');
  //         $("#addProjectForm")[0].reset();
  //       }
  //     }
  //
  //     var formData = ajaxForms.toFormData(addProjectForm);
  //
  //     crispyFormErrors.clearErrors(
  //       [
  //         "name",
  //       ],
  //       "addProjectForm"
  //     );
  //
  //     xhr.send(formData);
  //   });
  //
  //   $("#cancelSubmit").click(function(){
  //     crispyFormErrors.clearErrors(
  //       [
  //         "name",
  //       ],
  //       "addProjectForm"
  //     );
  //   });
  //
  // });
})();
