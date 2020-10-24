# NearBY-API #

**Django Rest API for the Authentication. [Nearby Mobile Application](https://github.com/PushpanshuRanjanSingh/NearBY) is using it.**

Install Requirements

```python
pip3 install -r requirements.txt
```

## Some sort of problem during hosting it on [Heroku](https://dashboard.heroku.com/) ##

> **Problem Number - 1** 
```sh
 !     Error while running '$ python manage.py collectstatic --noinput'.
       See traceback above for details.
       You may need to update application code to resolve this error.
       Or, you can disable collectstatic for this application:
          $ heroku config:set DISABLE_COLLECTSTATIC=1
       https://devcenter.heroku.com/articles/django-assets
 !     Push rejected, failed to compile Python app.
 !     Push failed
```

**Solution**

Django won’t automatically create the target directory (STATIC_ROOT) that collectstatic uses, if it isn’t available. You may need to create this directory in your codebase, so it will be available when collectstatic is run. Git does not support empty file directories, so you will have to create a file inside that directory as well. So this is a file to complete rule.

Add this Line into settings.py > MIDDLEWARE
```python
'whitenoise.middleware.WhiteNoiseMiddleware',
```

Add this Line into settings.py (Buttom Line)
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Heroku Doesn't have Static File. So we need to create static folder inside your project folder. make sure that folder have atleast one file
<center>
<img src="https://i.loli.net/2020/10/10/H9RXfUITdiNnKVP.png" alt="Directory Structure" style="width:10%;" />
</center>



> **Problem Number - 2**

<center>
<p float="left">
<img src="https://i.loli.net/2020/10/10/ED13MzOkCLwqsHY.png" alt="Error on Terminal" width="50%" />
<img src="https://i.loli.net/2020/10/10/X3k4L9jShw8MQup.png" alt="Error on Web" width="33%" />
</p>
</center>

**Solution**

We don't have http server to run this instance so we need gunicorn.
> Add Procfile at root && write the below code

```r
release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input
# wsgi from settings.py
web: gunicorn nearbyauth.wsgi
```


## Deployement on AWS EC2 ##

Step : 1

change allowed host in settings.py

```py
ALLOWED_HOSTS = ['*']
```

Step : 2

```sh
# update machine
sudo apt-get update
sudo apt-get upgrade -y

# configuration for project
sudo apt-get install python3-pip
sudo apt-get install python3-venv

# create virtual enviroment and activate it
python3 -m venv env
source env/bin/activate
```

Step : 3

install all dependencies of your project

```sh
git clone <https://github.com/PushpanshuRanjanSingh/Nearby-Auth.git>
cd Nearby-Auth
python -m pip install -r requirements.txt
```

Step : 4

```sh
pip install gunicorn
sudo apt-get install -y nginx
# edit inbound in aws : add http:80  source=> anywhere
```

Step : 5

test your project that it works or not
```sh
# you can check your wsgi 
$ cat settings.py | grep wsgi
# output : WSGI_APPLICATION = 'NearBYAuth.wsgi.application'
gunicorn --bind 0.0.0.0:8000 NearBYAuth.wsgi:application
# check your aws ip in browser along with port : http://111.11.11.111:8000
```

Step : 6

Configure Supervisor

```sh
$ cd /etc/supervisor/conf.d
$ sudo nano gunicorn.conf

# write in conf file according to you path & name
[program:gunicorn]
directory=/home/ubuntu/Nearby-Auth
command=/home/ubuntu/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/Nearby-Auth/app.sock NearBYAuth.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/gunicorn.err.log
stdout_logfile=/var/log/gunicorn/gunicorn.out.log

[group:guni]
programs:gunicorn

$ mkdir /var/log/gunicorn
$ sudo supervisorctl reread
$ sudo supervisorctl update
# checkout gunicorn is running or not
$ sudo supervisorctl status
```

Step : 7

configure nginx configuration
```sh
cd /etc/nginx/sites-available
sudo touch django.conf
```

Write this code to django.conf

```sh
server{
      listen 80;
      server_name ec2-15-206-117-147.ap-south-1.compute.amazonaws.com 15.206.117.147;
      location / {
            include proxy_params;
            proxy_pass http://unix:/home/ubuntu/Nearby-Auth/app.sock;
      }
}

```

Check & Test

```sh
sudo nginx -t
#output
#nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
#nginx: configuration file /etc/nginx/nginx.conf test is successful
```
Now enable it

```sh
sudo ln django.conf /etc/nginx/sites-enabled/
```

> Note : You may get error: 
could not build server_names_hash, you should increase server_names_hash_bucket_size: 64
so ..

```sh
sudo nano /etc/nginx/nginx.conf
#change this line
server_names_hash_bucket_size 512;
sudo service nginx restart
```