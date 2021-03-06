# Todo

- [ ] Add requirements to Setup.py

# Setup and Installation

For OS X and Linux the following bash will install all dependencies and run the program.

- **Configuration**.

  First thing you should do is create a `.env` file in the `API` directory.

    - SSL Configuration
        - Generate your pem file, the below will generate a file
            ```bash
             #!/usr/bin/env bash --posix
    
            openssl req -x509 -newkey rsa:2048 -nodes \
                -sha256 -subj "/CN=localhost"         \
                -keyout development.pem               \
                    -out development.pem
            
            [[ "${?}" == "0" ]] && echo "Generated PEM Certificate(s)"
            ```
        - Move the `development.pem` file to the root directory (`MFC-ELO`)
        - In your `.env` add the following
            ```ini
            UVICORN_SSL_KEYFILE=development.pem
            UVICORN_SSL_CERTFILE=development.pem
            UVICORN_SSL_VERSION=2
            UVICORN_SSL_CERT_REQS=0
            UVICORN_LOOP=uvloop
            ```

    - Configure your JWT
        - Generate the secret
            ```bash
            python3 -c "import secrets; print(secrets.token_urlsafe(32))"
            ```
            - Add to your `.env` the following:
                ```ini
                JWT_SECRET=YOUR KEY HERE
                JWT_ALGORITHM=HS256
                ```
              Where `JWT_SECRET` equals the string generated by the python call earlier.

    - Configure your database
        - Only postgresql version `13+` is supported
        - Connect your postgresql database typically done via `psql` and issue the following command
            ```
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            ```
          That installs the ossp extensions that are used to generate UUIDs.
        - In your `.env` file add a line for key `SQL_DB_URL` with the conneciton info to your postgres database;
          example:
            ```ini
            SQL_DB_URL=postgresql://user:password@your.ip.address.here/DatabaseName
            ```
          Where `user` is the postgresql username, `password` is the password for said user,
          `our.ip.address.here` being the ip to your postgresql database and `DatabaseName` being the name of the
          database you're connecting to.

    - Once all of the above is finished ensure you are one in the root directory of the project (`MFC-ELO`)
      and execute the following:
        ```bash
         #!/usr/bin/env bash --posix
      
        python -m venv venv
        source venv/bin/activate
        pip install wheel
        pip install --upgrade pip
        pip install -r requirements.txt
        python setup.py install
        python -m API
        ```

# Configuration

It is *highly* recommended that a `.env` file is created within the `API` directory, otherwise all of your environment
variables will need to be exported by default into your environment

A important note:

A default user *is* created for you on the initial run of the API:

| Username | Password
| :---     | :---
| admin    | Admin1234@

It is recommended that you update that user's password once the API is ready to go.

## SSL Configuration

To generate your key use the following:

```bash
#!/usr/bin/env bash --posix

openssl req -x509 -newkey rsa:2048 -nodes \
    -sha256 -subj "/CN=localhost"         \
    -keyout development.pem               \
        -out development.pem
        
[[ "${?}" == "0" ]] && echo "Generated PEM Certificate(s)"
```

Once that is done add to your `.env` or environment:

```ini
UVICORN_SLL_KEYFILE = PATH_TO_PEM_FILE
UVICORN_SSL_CERTFILE = PATH_TO_PEM_FILE
UVICORN_SSL_VERSION = 2
UVICORN_SSL_CERT_REQS = 0
```

On `PATH_TO_PEM_FILE` you can either use a relative path from the `API/` directory or a full path. It is recommended to
place the `.pem` file in the `API/` directory and point the path of both the key and cert files to the name of
the `.pem`, in this case `development.pem`.

## Postgresql Configuration

### Database URL

To set the database URL set in your `.env` or environment: `sql_db_url=YOUR URL HERE`, see **Environment Variables**

### OSSP Extension Installation

Connect and execute to your database:

```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

We use this extension for UUID generation purposes

### Config File

Change your timezone in `postgresql.conf` to `UTC`.

#### Locations

`postgresql.conf` on M1 Mac is located at `/Users/user/Library/Application Support/Postgres/var-13`

## Logging

For logging to work you *must* define a `log_config.yaml` file within the `API` directory based on the the python
logging [dictConfig](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details) *or* set the
appropriate log path in your environment, see **Environment Variables**.

Within your own `log_config.yaml`, assuming you don't use the default, ensure you set `disable_existing_loggers` to
**false**.

An example config in yaml, and the one that ships by default:

```yaml
version: 1
disable_existing_loggers: false # Important, otherwise messages will not be logged. Keep this as false
formatters:
  standard:
    format: '[%(asctime)s][%(threadName)s][%(name)s.%(funcName)s:%(lineno)d][%(levelname)s] %(message)s'
handlers:
  default_stream_handler:
    class: logging.StreamHandler
    formatter: standard
    level: INFO
    stream: ext://sys.stdout
  default_file_handler:
    backupCount: 5
    class: logging.handlers.RotatingFileHandler
    filename: API.log
    formatter: standard
    level: DEBUG
  error_file_handler:
    backupCount: 5
    class: logging.handlers.RotatingFileHandler
    delay: true
    filename: API_Error.log
    formatter: standard
    level: ERROR
loggers:
  '': # The root logger, best to leave it undefined (don't enter a string)
    handlers:
      - default_stream_handler
      - default_file_handler
      - error_file_handler
    level: DEBUG
    propagate: false
```

# Environment Variables

All environment variables are entered in uppercase.

## Logging Variables

All logging variables are preceded by log_

| Key             | Example Value | Description
| :---            | :---          | :---
| LOG_CONFIG_PATH | /Users/user/mfc_elo_api/log_config.yaml | The path (including the name of the file) of your log config.

## JWT Variables

All jwt variables are preceded by `JWT_`

| Key           | Example Value                                                            | Description
| :---          | :---                                                                     | :---
| JWT_SECRET    | d18edfac5b16c1839a203aadc57df7c3303b9c76707398996da65dcb2797889f1ec4a2de | The JWT secret used to generate JWT tokens, ideally at least 32 characters long.
| JWT_ALGORITHM | HS256                                                                    | The algorithm that is used when generating JWT tokens

## SQL Variables

All sql variables are preceded by `SQL_`

| Key        | Example Value                                          | Description
| :---       | :---                                                   | :---
| SQL_DB_URL | `postgresql://username:password@0.0.0.0:5432/Database` | The database connection url, *only* supports postgresql due to the need for postgresql UUID functions

## Uvicorn Variables

See [uvicorn settings](https://www.uvicorn.org/settings/) for uvicorn configuration.

Effectively, take the name of each setting, append `UVICORN_` to the start of it in your environment and that's how you
pass arguments to uvicorn in this application.

For example, if you wanted to set the host that uvicorn runs on the host var would be `UVICORN_HOST`.
