# Dockerized App: Django + MySQL
#thanks a thanks to https://github.com/Alejandroacho/DockerizedAppTemplate for the docker template
All we be in one Docker container that will be already setted up to just start WIth ths hyper wiki=

## Requirements
  - Docker
  - Docker-Compose

## Nice to have
  - Python3
  - Django

## Nice to take a look to
- [Docker documentation.](https://docs.celeryproject.org/en/stable/index.html#)
- [Django documentation.](https://www.djangoproject.com/)
- [DjangoREST documentation.](https://www.django-rest-framework.org/)
- [Celery documentation.](https://docs.celeryproject.org/)



## Instructions

1. Go to root content folder.
2. Bring up the docker container running:  
    ```docker-compose up```

3. go to http://localhost:8000/ he rest of the documention can be found there
4. That's all!

    Django admin will be available on: [http://localhost:8000/admin](http://localhost:8000/admin)

    Django app will be available on: [http://localhost:8000/](http://localhost:8000/)

    Flower task monitor will be available on: [http://localhost:5555](http://localhost:5555)