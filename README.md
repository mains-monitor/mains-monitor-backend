# Mains Monitor - Backend

* Receives updates form Mains Monitor device
* All the processing is done using AWS Lambda functions in python
* Stores electricity state changelog in DynamoDB
* Sends out Telegram messages to preconfigured channels when electricity state changes
* Provides info about blackout schedule if enabled with every Telegram message
* Blackout schedule is a static json file stored in S3

# Environment setup

The first thing to do is to call:

    npm i

That will install necessary components fo Serverless Framework. Then, create some configuration files.

The primary files for deployment are ``secrets.<env_name>.json``.
You need to create at least one.

Here is an example content of such file:

    {
        "TELEGRAM_TOKEN": "foo",
        "BOT_HANDLER_SECRET": "bar",
        "DEVICE_HANDLER_SECRET": "baz"
    }

You need to create a Telegram bot, obtain the bot token, and then use it as ``TELEGRAM_TOKEN`` in the file.

The other two variables may have random values, whatever you wish, but note, they are going to be a part of various URLs, so you are a bit restricted.

The appropriate secrets file is loaded into by ``sls`` when you run

    sls deploy --stage=stage

The above example will load ``secrets.stage.json`` file before the actual deployment.

## Development

> You might have AWS credentials to be pre-loaded into your environment before you start.

For development purposes there is a ``dump_env.sh``. It calls ``sls export-env -s <env name>`` under the hood and generates ``.env`` file suitable for local development and testing in VSCode for example.

Usage example:

    ./dump_env.sh stage

Another one:

    ./dump_env.sh prod

To load .env file use the following script:

    source ./load_env.sh