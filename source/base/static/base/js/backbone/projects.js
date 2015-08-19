(function(exports){

  var Project = Backbone.Model.extend({
    urlRoot: "/api/projects/",
    defaults: {
      name: "",
      description: "",
      url: "",
      slug: "",
    },
  });


  var ProjectCollection = Backbone.Collection.extend({
    url: "/api/projects/",
    model: Project,
  });


  var AddProjectView = Backbone.View.extend({
    el: "#addProjectContainer",
    template: _.template($("#addProjectTemplate").html()),
    initialize: function(collection){
      this.collection = collection;
      _.bindAll(this, 'render');
      console.log("Initialized.");
      this.render()
    },
    render: function(){
      console.log("Rendering.");
      this.$el.html(this.template());
    },
    addProject: function(event){
      console.log("Submitting");
      event.preventDefault();
      var formObjects = ajaxForms.toJson($("#addProjectForm"));
      var newProject = new Project(formObjects);
      window.newProject = newProject;
      this.collection.add(newProject);
      newProject.save({}, {
        success: function(data){
          console.log(data);
        },
        error: function(data){
          console.log(data);
        },
      });
    },
    events: {
      "submit #addProjectForm": "addProject",
    }
  });


  var ProjectView = Backbone.View.extend({
    el: "#projects",
    template: _.template($("#indexProjectItem").html()),
    initialize: function(model){
      this.model = model;
      _.bindAll(this, 'render');
      var that = this;
      this.render();
    },
    render: function(){
      this.$el.append(this.template(this.model.toJSON()));
    },
  });


  var ProjectCollectionView = Backbone.View.extend({
    initialize: function(collection){
      this.collection = collection;
      window.collection = collection;
      _.bindAll(this, 'render');
      var that = this;
      this.collection.fetch({
        success: function(){
          that.render();
        }
      });
    },
    render: function(){
      this.collection.each(function(project){
        var projectView = new ProjectView(project);
      });
    },
  });


  var ProjectRouter = Backbone.Router.extend({
    routes: {
      "": "index",
    },
    index: function(){
      var projectCollection = new ProjectCollection();
      var collectionView = new ProjectCollectionView(projectCollection);
      var addProjectView = new AddProjectView(collection);
    },
  });


  $(document).ready(function(){
    var appRouter = new ProjectRouter();
    Backbone.history.start();
  });

})(this.projects = {});
