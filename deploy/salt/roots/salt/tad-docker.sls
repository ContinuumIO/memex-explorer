tad-pulled:
  docker.pulled:
    - name: autonlab/tad
    - image: autonlab/tad
    - tag: latest
    - require:
        - sls: docker


/home/vagrant/tad_instance/tad.cfg:
  file.copy:
    - force: True
    - makedirs: True
    - source: /vagrant/deploy/tad.cfg

/home/vagrant/tad_logs:
  file.directory:
    - user: vagrant
    - group: vagrant
    - mode: 755
    - makedirs: True

tad-running:
  cmd.run:
    - name: docker run -p 5000:5000 -d -ti --name autonlab-tad -v /home/vagrant/tad_logs:/service/tad/logs -v /home/vagrant/tad_instance:/service/tad/config:ro -v /home/vagrant/tad_instance:/service/tad/snapshot:ro  -P autonlab/tad
    - unless: docker start tad_1
    - require:
        - docker: tad-pulled
        - file: /home/vagrant/tad_instance/tad.cfg
        - file: /home/vagrant/tad_logs