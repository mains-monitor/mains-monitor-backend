# Mains Monitor - Backend

* Receives updates form Mains Monitor device
* All the processing is done using AWS Lambda functions in python
* Stores electricity state changelog in DynamoDB
* Sends out Telegram messages to preconfigured users or channels when electricity state changes
* Provides info about blackout schedule if enabled with every Telegram message
* Blackout schedule is a static json file stored in S3