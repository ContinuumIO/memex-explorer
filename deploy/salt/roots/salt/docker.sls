docker-python-apt:
  pkg.installed:
    - name: python-apt

docker-dependencies:
  pkg.installed:
    - pkgs:
      - apt-transport-https
      - iptables
      - ca-certificates
      - lxc

docker-repo:
  pkgrepo.managed:
    - humanname: Docker repo
    - name: deb https://get.docker.com/ubuntu docker main
    - file: /etc/apt/sources.list.d/docker.list
    - keyid: d8576a8ba88d21e9
    - keyserver: keyserver.ubuntu.com
    - refresh_db: True
    - require_in:
        - pkg: lxc-docker
    - require:
      - pkg: docker-python-apt

lxc-docker:
  pkg.installed:
    - name: lxc-docker

/etc/default/docker:
  file.copy:
    - force: True
    - makedirs: True
    - source: /vagrant/deploy/docker.conf
      
docker-service:
  service.running:
    - name: docker
    - enable: True

docker-py package dependency:
  pkg.installed:
    - name: python-pip

docker-py:
  pip.installed:
    - require:
      - pkg: lxc-docker
      - pkg: python-pip
    - reload_modules: True
