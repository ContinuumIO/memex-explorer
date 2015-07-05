{# This settings makes sure that the proper settings file is copied when salt is
 run. For vagrant and EC2 deployment, the deploy_settings file must be used.
 For development on a django development server, the dev_settings.py file must
 be used. #}
/vagrant/source/memex/settings.py:
  file.copy:
    - source: /vagrant/source/memex/settings_files/deploy_settings.py
    - user: vagrant
    - force: True

LOCAL_PATH:
  file.append:
    - name: /home/vagrant/.bashrc
    - text: export PATH="/home/vagrant/miniconda/envs/memex/bin:$PATH"

local_settings_path:
   environ.setenv:
     - name: LOCAL_SETTINGS_PATH
     - value: /vagrant/source/memex/local_settings.py

migrate:
  cmd.run:
    - name: |
        /home/vagrant/miniconda/envs/memex/bin/python /vagrant/source/manage.py migrate
    - cwd: /home/vagrant
    - user: vagrant
    - require:
        - sls: conda-memex

collectstatic:
  cmd.run:
    - name: |
        echo yes | /home/vagrant/miniconda/envs/memex/bin/python /vagrant/source/manage.py collectstatic
    - cwd: /home/vagrant
    - user: vagrant
    - require:
        - sls: conda-memex

celery:
  cmd.run:
    - name: /home/vagrant/miniconda/envs/memex/bin/celery --detach --loglevel=debug --logfile=/vagrant/source/celeryd.log --workdir="/vagrant/source" -A memex worker
    - cwd: /vagrant/source
    - user: vagrant
    - env:
        - JAVA_HOME: '/usr/lib/jvm/java-7-oracle'
    - unless: "ps -p $(cat /vagrant/source/celeryd.pid)"
    - require:
        - sls: conda-memex

supervisor:
  cmd.run:
    - name: |
        source activate memex
        supervisord -c /vagrant/deploy/supervisor.conf
    - user: vagrant
    - env:
       - PATH:
           /home/vagrant/miniconda/bin:/home/ubuntu/miniconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
    - require:
        - sls: conda-memex
    - unless: pgrep --full '/vagrant/deploy/supervisor.conf'

reload-supervisor:
  cmd.run:
    - name: |
        source activate memex
        supervisorctl -c /vagrant/deploy/supervisor.conf reload
    - user: vagrant
    - env:
       - PATH:
           /home/vagrant/miniconda/bin:/home/ubuntu/miniconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
    - require:
        - sls: conda-memex

/home/vagrant/resources/configs:
  file.recurse:
    - source: salt://source/resources/configs
    - user: vagrant
    - force: True

/home/vagrant/resources/profiles:
  file.recurse:
    - source: salt://source/resources/profiles
    - user: vagrant
    - force: True
