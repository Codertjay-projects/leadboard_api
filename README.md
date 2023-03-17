# leadboard_api

This project uses celery and redis

to work on it, I created the celery as a systemd which enables me start as a service on the background

The start celery on the server currently or check status we use

Check status
`sudo systemctl status celery`

Start celery

Local$: `celery -A leadboard_api worker --loglevel=info`
Prod$: `sudo systemctl start celery`

Stop celery

`sudo systemctl stop celery`

## Redis Installation:

Start$ `redis-stack-server`

https://developer.redis.com/create/homebrew/

### Maintenance Mode

To toggle between maintenance mode on and off we access the url
but you have to be a staff or a superadmin to access this

http://127.0.0.1:8001/maintenance-mode/off/
http://127.0.0.1:8001/maintenance-mode/on/

### How to work with  Gunicorn

Restart$ `sudo systemctl restart gunicorn `

Stop$ `sudo systemctl stop gunicorn `

Start `sudo systemctl start gunicorn `

### How to work with  nginx

Restart$ `sudo systemctl restart nginx `

Stop$ `sudo systemctl stop nginx `

Start `sudo systemctl start nginx `

### How to work with  Celery

Restart$ `sudo systemctl restart celery `

Stop$ `sudo systemctl stop celery `

Start `sudo systemctl start celery `

### How to work with  CeleryBeat

Restart$ `sudo systemctl restart celerybeat `

Stop$ `sudo systemctl stop celerybeat `

Start `sudo systemctl start celerybeat `


How to download from server or Upload
Download  `scp -r user@ip-address:/home/user/projects/path  location_to_save`
Upload  `scp -r  . user@ip-address:/home/user/projects/path  `