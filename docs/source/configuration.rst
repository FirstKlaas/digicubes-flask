Configuration
=============

Environment Variables
---------------------
Many of the aspects can be configured by setting environment variables.
If it exists, DigiCubes will import environment variables from and ``.env``
file.

Main configuration file
~~~~~~~~~~~~~~~~~~~~~~~

The main configuration file looks is a yaml file

.. code-block:: yaml

    # The secret used to secure your session
    # Make sure not to expose this secret to
    # other people. And keep a copy somewhere.
    secret: "djsjah67sh7/&)788hxcbxsh"

    # Are new users automatically verified when
    # they register?
    auto_verify: false

Configuring the emailserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:DC_SMTP_HOST: The name or IP of the smtp server. If the variable is set,
    DigiCubes will try to configure email support. In this case the
    following variables have to be set correctly. If this variable is not
    set, email support is disabled.
:DC_SMTP_PORT: The smtp port. If not configured, the default 465 is used.
:DC_SMTP_USERNAME: The user name
:DC_SMTP_PASSWORD: THe password. Be carefull not to expose your credentials.
:DC_SMTP_FROM_EMAIL_ADDR: The email address, the recipient will see as the
    sender.
:DC_SMTP_DISPLAY_NAME: The shown name of the sender

In the yaml configuration file you also be used to configure these values.
In addition you can configure the number of workers and the number of tries.
In the main yaml configuration, the parameters are in the.``mailcube`` section.

In the yaml file the prefix ``DC_SMTP_`` is omitted and the settings are
in lower case. If both are given, the environment variable has the higher
precedence.

.. code-block:: yaml

    mail_cube:
        host: smtp.yourserver.cloud
        username: mylogin
        password: MySeCrEtPaSsWoRd
        from_email_addr: some.email@gmail.com
        display_name: DigiBot
        number_of_tries: 1
        number_of_workers: 1


Configuring redis cache
~~~~~~~~~~~~~~~~~~~~~~~

DigiCubes supports Redis to cache certain data. This can halp to speed up
things.
Especially, if you are deploying digicubes in a docker swarm. If you are
deploying digicubes using a docker-compose file, it is highly recommended
to enable redis.

The Redis connection is configured via environment variables.

:DC_REDIS_DB: The number of the database. Defaults to 0. This is only
    important, if the digicubes web server and the digicubes api server
    share the same redis instance. In this case make sure different numbers
    are configured.

:DC_REDIS_PASSWORD: The password. Make shure not to expose it. If you have configured
    redis without password, you don't need to set this variable.

:DC_REDIS_PORT: The redis port. Defaults to 6379

:DC_REDIS_MAX_AGE: This is the max age in seconds. Data in the cache will automatically
    invalidate and cleaned up after this period. Defaults to 1800 seconds.

Configuring the Digicubes API endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The client needs to now where to find the api server. The configuration is done
via environment variables.

:DC_API_SERVER_PROTOCOL: The protocol to be used. Defaults to `http`.
:DC_API_SERVER_HOST: The digicubes api host. Defaults to `localhost`.
:DC_API_SERVER_PORT: The port to use. Defaults to 3000.
