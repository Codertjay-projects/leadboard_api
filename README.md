# leadboard_api

This project uses celery and redis

to work on it, I created the celery as a systemd which enables me start as a service on the background

The start celery on the server currently or check status we use

Check status
`sudo systemctl status leadboard_api_celery`

Start celery

Local$: `celery -A leadboard_api worker --loglevel=info`
Prod$: `sudo systemctl start leadboard_api_celery`

Stop celery

`sudo systemctl stop leadboard_api_celery`

## Redis Installation:

Start$ `redis-stack-server`

https://developer.redis.com/create/homebrew/

### Maintenance Mode

To toggle between maintenance mode on and off we access the url
but you have to be a staff or a superadmin to access this

http://127.0.0.1:8001/maintenance-mode/off/
http://127.0.0.1:8001/maintenance-mode/on/