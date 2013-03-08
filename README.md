<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js"></script>

Description
======================

This is a sample project for Google Cloud Endpoints technology. For the purpose of this project we assume that we are building a home automation system. We have a number of sensors running in our home, and we want to control which ones of them are active via web and mobile.

To achieve this, we need to build an a service and an API which should:

* Allow authenticated users to modify the state of the monitoring, e.g.     change the activity state of a given sensor, get list of sensors, etc.

* Provide a push-enabled update mechanism for in-home server which controls all the sensors installed in the household.

The API we design should be accessible for both web and native mobile applications.


API Design
-----------

Main concept of any RESTful API is a _collection_ - in our scenario this will be a `sensors` collection (in a real world we are likely to start with a collection of households if we want to support our product for more than one household which is quite possible).

There will be four main methods defined on `sensors` collection: `LIST`, `INSERT`, `UPDATE` and `DELETE`.

* `LIST` will return full list of sensors installed in a given household, along with their activity status. This is useful if we want to see all information about every sensor on one page.
* `INSERT` will allow us to install another sensor in the household.
* `UPDATE` will allow to change the information associated with a given sensor, such as `active`.
* `DELETE` will be used when we de-install certain sensor.


API Implementation
--------------

We will start with defining our API service:

<pre class="prettyprint">
    @endpoints.api(name='sensors',version='v1',
                   description='Sensors API')
    class SensorsAPI(remote.Service):
       # ...
</pre>

Here we have just defined a new API class, inheriting it from `remote.Service` provided by AppEngine SDK. We have also defined an annotation in which we specify:

* `name` - how API will be known to your application and sensors
* `version` - you can have multiple versions of the same API
* `description` - textual description to appear in API explorer.

Now we will define our first method.

<pre class="prettyprint">
    @endpoints.method(SensorsRequestMessage, SensorsResponseMessage,
                      path='sensors', http_method='POST',
                      name='sensors.insert')
    def sensors_insert(self, request):
</pre>

What we do here is define an API method which takes a _message_ of a type `SensorsRequestMessage` and returns a message of `SensorsResponseMessage`. We should probably explain this in a bit more details.

### Messages ###

A _message_ is one of the cornerstone ideas of an API. Everything we send to API and everything we receive back are _messages_. Internally message can be anything. For example, code below defines some message in JSON format:

<pre class="prettyprint">
    {
      "sensorNetworkId": "b5cd02ca-0763-4f34-95e0-73d3e18d3345",
      "sensorRoom": "living_room",
      "sensorType": "temperature",
      "sensorActive": "true"
    }
</pre>

Another format message can be sent in is [Google Protocol Buffers](https://code.google.com/p/protobuf) - high-efficient format which is very simple to use and is about 3 to 10 times more network-efficient compared to JSON and especially XML - this is particularly important for mobile devices which often suffer of a slow/intermittent connection to the Internet.

### Defining messages in ProtoRPC format ###

One of the most powerful features of Google Cloud Endpoints is ability to use simple Python classes which are converted to Protocol Buffers behind the scenes - this way you benefit of Protocol Buffers efficiency pretty much at zero cost. Let's define our message in a way that GCE understands it:

<pre class="prettyprint">
    class SensorMessage(messages.Message):
      class Room(messages.Enum):
        LIVING_ROOM = 1
        BEDROOM = 2
        HALL = 3

      class Type(messages.Enum):
        TEMPERATURE = 1
        MOTION = 2

      sensor_id = messages.IntegerField(1, required=True)
      network_id = messages.StringField(2)
      room = messages.EnumField('SensorMessage.Room', 3, default=LIVING_ROOM)
      kind = messages.EnumField('SensorMessage.Type', 4, default=TEMPERATURE)
      active = messages.BooleanField(5, default=True)
</pre>

Let's see what we just did. We started with defining a `SensorMessage` class, inheriting it from the AppEngine provided class `Message`.

In this message we define two _enum types_ - which are much like enums in any other language. Finally, we proceed with defining message's fields. This is how a field is defined:

<pre class="prettyprint">
      sensor_id = messages.IntegerField(1, required=True)
</pre>

We defined a field named `sensor_id` of a type Integer. First argument to `IntegerField` is a field order number - this is, in fact, an inheritance of Google Protocol Buffers, where all fields must be numbered - this allows more effective message encoding and decoding. We have also specified that this field is required - this can be done with any field without which message simply stops making sense.

Now that we have a `SensorMessage` we can go back and write up `SensorsRequestMessage` and `SensorsResponseMessage`.

<pre class="prettyprint">
    class SensorsRequestMessage(messages.Message):
      sensor = messages.MessageField('SensorMessage', 1, repeated=True)
</pre>

We define `SensorsRequestMessage` as a collection of `SensorMessage` objects - we would want to do this if, for example, we want to bulk add all sensors in the household. Similarly, we will define `SensorResponseMessage` as:

<pre class="prettyprint">
    class SensorsResponseMessage(messages.Message):
      class Status(messages.Enum):
        OK,
        FAILED

      status = messages.EnumField('SensorsResponseMessage.Status', 1)
      error = messages.StringField(2, repeated = True)
</pre>

This message contains a single status field which could either be `OK` or `FAILED` and a collection of error messages associated with it. An expected response for completely successful operation would be `status = OK` and empty `error` collection.

### Implementing `Insert` method

And now we can finally go ahead and implement our method! This is how the final (or semi-final) version of the `Insert` method will look like:

<pre class="prettyprint">
    @endpoints.method(SensorsRequestMessage, SensorsResponseMessage,
                      path='sensors', http_method='POST',
                      name='sensors.insert')
    def sensors_insert(self, request):
        """Exposes an API endpoint to install a sensor in household.

        Args:
            request: An instance of ScoreRequestMessage parsed from the API
                request.

        Returns:
            An instance of ScoreResponseMessage containing the score inserted,
            the time the score was inserted and the ID of the score.
        """
        for s in request.sensors:
          sensorEntity = Sensor(sensor_id=s.sensor_id,
                                network_id=s.network_id,
                                room=str(s.room),
                                sensor_type=str(s.sensor_type),
                                active=s.active)
          sensorEntity.put()

        response = SensorsResponseMessage()
        response.status = SensorsResponseMessage.Status.STATUS_OK

        return response
</pre>

Note, that we are using newly defined type `Sensor` here which is an AppEngine datastore type:

<pre class="prettyprint">
    class Sensor(db.Model):
      sensor_id = db.IntegerProperty(required = True)
      network_id = db.StringProperty()
      room = db.StringProperty()
      sensor_type = db.StringProperty()
      active = db.BooleanProperty()
</pre>

This is a similar to ProtoRPC concept - we define a class and AppEngine handles storing it in the database. You can read more about it in AppEngine documentation site.

### Time to play! ###

So now we have an API, capable of receiving calls and storing data in the database - amazing! Let's get it rolling and see how it works! First, we start a dev instance of AppEngine:

    $ dev_appserver.py --debug .

Now we can use Google API explorer to see how our API works. Navigate to [API explorer page](https://developers.google.com/apis-explorer/?base=http://localhost:8080/_ah/api_)
