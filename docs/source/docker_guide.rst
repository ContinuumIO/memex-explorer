#############################################
Docker Container Services
#############################################

Memex Explorer currently supports the following external services in Docker containers:

- Tika
- Elasticsearch
- Kibana

The current design of Memex Explorer associates a unique Docker container containing each service for each project.  We use the following definitions for the rest of this guide:

Project: A Memex Explorer project.  One instance of Memex Explorer may have multiple projects, and they may be created via the web interface
Service: An application stack that provides a single service.  Tika, Elasticsearch, and Kibana are all examples of this.
Container: A specific Docker container associated with a project that is responsible for a service.

==============================================
Details of the Launch Process
==============================================


1. Container objects are instantiated in a celery task that is launched by a post-save signal.
2. A ``docker-compose.yml`` describing the containers is dynamically generated, then launched via ``docker-compose up``.
3. A nginx configuration file for publicly exposing each service is dynamically generated, then nginx is restarted.

==============================================
Integrating Additional Services
==============================================


To integrate a service, you need:

1. A Docker image containing your service
2. A description of your service as it would be input in docker-compose YAML format

You can read more about `docker-compose <https://docs.docker.com/compose/yml/>`_ at the Docker website.

For now, all services are hardcoded in :py:mod:`base.management.commands.create_apps_Tika_ES_Kibana`.  There are examples of using App, AppPort, AppLink, and VolumeMount functionality to describe a service's requirements.  If your service requires other functionality, please raise an issue on the GitHub repository. 

If you are interested in contributing a Docker Containerized service, create a branch implementing the service and start a Pull Request.
