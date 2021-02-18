# PoC Stream Processor

A Proof of Concept of a stream processing application to read and process messages from a Kafka topic.

This PoC is implemented based on a [Faust application] using [Avro] as serializing mechanism. To integrate both it's 
using a couple of open source libraries:

* [python-schema-registry-client]
* [dataclasses-avroschema]

## Quick Start
1. Build the docker image:
```commandline
python make build
```
*It could ask for installing some dependencies, such as Clinner and Jinja2, if you aceept it will install them and once 
all requirements are installed you can run the script.*

2. Run the application:
```commandline
python make run
```

### Requirements

* [Python] 3.6+

### Environment variables
It is required defining some environment variables to have the application working: 
- KAFKA_URL
- KAFKA_TOPIC

[Python]: https://www.python.org
[Faust application]: https://faust.readthedocs.io/en/latest/userguide/application.html#what-is-an-application
[Avro]: https://avro.apache.org/docs/current/
[python-schema-registry-client]: https://github.com/marcosschroh/python-schema-registry-client/
[dataclasses-avroschema]: https://github.com/marcosschroh/dataclasses-avroschema/