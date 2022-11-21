# Swarm Service Reloader

Simple reloading script reading some remote url content and comparing it with last stored value.
If content is different, reloads desired services with pulling "latest" image version before.

## Install

`pip install -r requirements.txt`

## Run

`SWARM_SERVICE_RELOADER_WATCHED_URL=https://some/remote/url SWARM_SERVICE_RELOADER_TARGET_SERVICES=some_service_name_1,some_service_name_2 python reload.py`
