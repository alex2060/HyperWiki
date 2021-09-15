# Dockerized App: Django + MySQL + Celery + RabbitMQ + Flower
* * *
The goal of this project is to enable an easy-to-use and implement template in order to start developing a web app as quickly and conveniently as possible.

The environment we are looking to build is one that uses Django as a python framework for web development with MySQL as a database. Also will be setted up the DjangoRESTFramework to build an API if needed; Celery with RabbitMQ for managing asynchronous tasks, and Flower for monitoring those tasks.

All we be in one Docker container that will be already setted up to just start coding the project.

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
- [RabbitMQ documentation.](https://www.rabbitmq.com/)
- [Flower documentation.](https://flower.readthedocs.io/en/latest/)

## Before starting
Feel free to set your environment variables as you want on ```env.env``` file.

You can change the container name by changing the main folder name.

You can change project name to your actual app name, just take in mind that you will need to change folders name, docker-compose.yml content, Dockerfile content and some django settings in order to the container work correctly.

## Instructions

1. Go to root content folder.
2. Bring up the docker container running:  
    ```docker-compose up```
     
4. That's all!

    Django admin will be available on: [http://localhost:8000/admin](http://localhost:8000/admin)

    Django app will be available on: [http://localhost:8000/](http://localhost:8000/)

    Flower task monitor will be available on: [http://localhost:5555](http://localhost:5555)

## Observations

To actual interact with django admin for the first time, you will need to run:

    python3 manage.py migrate
    python3 manage.py createsuperuser
     
And create your super user.

You can create and app ([app vs project](https://docs.djangoproject.com/en/3.2/intro/tutorial01/#creating-the-polls-app)) running:

    python3 manage.py startapp app-name
        

## Interaction
You can see docker logs just running ```docker-compose up```, but this will attach the console directly to the container process so if you close it, you will set down the docker container too. To avoid this you can run the container detached to console running:
  
    docker-compose up -d

To see container logs run:
  
    docker-compose logs -f

To access container shell to interact directly with django run:

    docker-compose exec app /bin/bash

To access MySQL database run:

    docker-compose exec database -uuser -ppassword```


# Use custom django user model
* * *
Following steps from [Django documentation to use custom user.](https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#substituting-a-custom-user-model) 

## Before starting
It's highly recommended doing this reinterpretation of Use model at the very beginning of the project. Take in mind this requires a reinterpretation of the User model, so if you already have run migrations, you will need to make an empty apply of the migration; this means that you will lose the database data, so it's recommendable to make a backup before do that if there are valuable data on databases.

## Step-by-step
This example will be for an User model with email (as identifier) and name as parameters.

1. Create the users app running:

        python3 manage.py startapp users

2. Add ```users``` to installed apps section in project settings (```App/settings.py```) file, and in the same file add: 
              
        AUTH_USER_MODEL = 'users.User'

3. The file ```models.py``` must look like this:

    ``` python
    from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
    from django.contrib.auth.models import PermissionsMixin
    from django.db import models
    from django.utils.http import urlquote
    from django.utils.translation import ugettext_lazy as _


    class CustomUserManager(BaseUserManager):
        """
        Custom user model manager where email is the identifier for authentication instead of usernames.
        """
        def create_user(self, email, password, name, **extra_fields):
            """
            Creates and saves a User with the given email and password.
            """
            if not email:
                raise ValueError('The given email must be set')
            email = self.normalize_email(email)
            user = self.model(email=email,
                              name=fname,
                              **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

        def create_superuser(self, email, name, password, **extra_fields):
            """
            Create and save a SuperUser with the given email and password.
            Function needed to run <createsuperuser> django command.
            """
            user = self.model(email=email,
                            name=name,
                            **extra_fields)
            user.set_password(password)
            user.is_admin = True
            user.save(using=self._db)
            return user


    class User(AbstractBaseUser, PermissionsMixin):
        username = None # <--- Here disables a field from AbstractBaseUser
        email = models.EmailField('Email address',
                                    unique = True,
                                    error_messages = {
                                        'unique': 'This email already exists.'
                                    })
        name = models.CharField('First name',
                                    blank = False,
                                    max_length = 50)
        is_admin = models.BooleanField('Admin status',
                                        default = False)
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = ['name']

        objects = CustomUserManager()

        def __str__(self):
            return self.email

        def has_perm(self, perm, obj=None):
            return self.is_admin

        @property
        def is_staff(self):
            "Is the user a member of staff?"
            # Simplest possible answer: All admins are staff
            return self.is_admin
    ```

4. Enter the container shell to interact directly with django and run:

    ``` 
    python3 manage.py makemigrations
    ```  
     
5. Now you will now have to apply the migrations running:

    ``` 
    python3 manage.py migrate
    ``` 
    
    If you have had applied migrations before, you may get an error like this: 
    
        django.db.migrations.exceptions.InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency users.0001_initial on database 'default'.
    
    To fix that, you may apply the migration with ```'django.contrib.admin'``` removed from 'installed apps' property on settings django file, and also removing admin's url on urls django file. After the migration, you can recover admin's lines and continue developing as well.

6. And a custom user model is done!

# Versions
* * *
Versions that will use the project. Take in mind that python sub versions may change because it will depend on the one used on [python dockerhub image.](https://hub.docker.com/_/python), it will be the same with [RabbitMQ](https://hub.docker.com/_/rabbitmq), and [MySQL](https://hub.docker.com/_/mysql). Even so, the python version in docker container (reviewed on 2021/09/05) is ```3.9.7```.

* Docker compose schema version:  3.8
* Python image:  3
* RabbitMQ image: 3
* MySQL image:  5.6
* Django version:  3.2.6
* DjangoRESTFramework version:  3.12.4
* Celery version:  5.1.2
