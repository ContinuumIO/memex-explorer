[![Build Status](https://travis-ci.org/memex-explorer/memex-explorer.svg?branch=master)](https://travis-ci.org/memex-explorer/memex-explorer)
[![Coverage Status](https://coveralls.io/repos/ContinuumIO/memex-explorer/badge.svg?branch=memex-django)](https://coveralls.io/r/ContinuumIO/memex-explorer?branch=memex-django)

# memex-explorer
Memex explorer application written in Django 1.7
* To setup the environment, do the following:
```
$ wget http://bit.ly/miniconda
$ bash miniconda
```
Then, navigate to the repository root and run these commands:
```
$ conda env update
$ source activate memex
```
* Before you create the database, you need to copy one of the settings files that you need to use. There are two settings files, one for development and one for deployment. Do the following:
```
$ cd source
$ cp memex/settings_files/dev_settings.py memex/settings.py
(or)
$ cp memex/settings_files/deploy_settings.py memex/settings.py
```
* To setup the application, after creating the `memex` environment, run these commands in the `source` folder. This will create the database for the application using the migration scripts provided in the source code:
```
$ python manage.py migrate
```
* Then, in the same folder run this command to launch the application as a local server:
```
$ python manage.py runserver
```
* To set up superuser access to the administrative panel, run this command and provide a username, email, and password:
```
$ python manage.py createsuperuser
```
* To access the administration panel navigate to http://localhost:8000/admin after running `python manage.py runserver`. Here you will be able to view and make manual changes to the database.
* To run the tests, run the command:
```
$ py.test
```

# Starting Celery
* Memex Explorer relies on both redis and Celery to manage tasks. To start the celery worker, run these two commands from the source directory:
```
$ redis-server
$ celery -A memex worker -l info
```

# Installing Compass
If you need to make changes to the .scss stylesheets, [Compass](http://compass-style.org/) is a useful tool. The following are instructions on how to install compass without using `sudo`.
* For mac users, add this line to your `~/.bash_profile`:
```
export PATH=/Users/<username>/.gem/ruby/<ruby version>/bin:$PATH
```
Then run `$ gem install compass --user-install`. This will install Compass on your system.
* To make changes to the stylesheets, do:
```
$ cd ../
$ compass watch
```

