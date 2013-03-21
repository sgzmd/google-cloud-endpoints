from google.appengine.ext import endpoints
from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel

# Represents a single sensor in application's database,
# inheriting it from EndpointsModel.
class SensorModel(EndpointsModel):
  # used by EndpointsModel to detect which members are in fact
  # fields which must be serialised and stored in the datastore.
  _message_fields_schema = ('id', 'network_id', 'room', 'sensor_type', 'active')

  network_id = ndb.StringProperty()
  room = ndb.StringProperty()
  sensor_type = ndb.StringProperty()
  active = ndb.BooleanProperty()

@endpoints.api(name='sensors',
               version='v2',
               description='Sensors API')
class SensorsApi(remote.Service):
  """Class which defines sensors API v2."""

  # Here, since the schema includes an ID, it is possible that the entity
  # sensor_model has an ID, hence we could be specifying a new ID in the datastore
  # or overwriting an existing entity. If no ID is included in the ProtoRPC
  # request, then no key will be set in the model and the ID will be set after
  # the put completes.
  @SensorModel.method(path='sensormodel',
                      http_method='POST',
                      name='sensor.put')
  def insert_or_update(self, sensor_model):
    """
    Creates new SensorModel and saves it in datastore OR overwrites
    a SensorModel with the same ID (effectively, updates it).
    """
    sensor_model.put()
    return sensor_model

  # Allows an entity to be retrieved from it's ID.
  # We override the schema of the ProtoRPC
  # request message to limit to a single field: "id".
  # Since "id" is one of the helper methods provided by EndpointsModel,
  # we may use it as one of our request_fields.
  @SensorModel.method(request_fields=('id',),
                  path='sensormodel/{id}',
                  http_method='GET',
                  name='sensor.get')
  def get(self, sensor_model):
    if not sensor_model.from_datastore:
      raise endpoints.NotFoundException('MyModel not found.')
    return sensor_model

  # As SensorModel.method replaces a ProtoRPC request message to an entity of our
  # model, SensorModel.query_method replaces it with a query object for our model.
  # By default, this query will take no arguments (the ProtoRPC request message
  # is empty) and will return a response with two fields: items and
  # nextPageToken. "nextPageToken" is simply a string field for paging through
  # result sets. "items" is what is called a "MessageField", meaning its value
  # is a ProtoRPC message itself; it is also a repeated field, meaning we have
  # an array of values rather than a single value. The nested ProtoRPC message
  # in the definition of "items" uses the same schema in SensorModel.method, so each
  # value in the "items" array will have the fields attr1, attr2 and created.
  # As with MyModel.method, overrides can be specified for both the schema of
  # the request that defines the query and the schema of the messages contained
  # in the "items" list. We'll see how to use these in further examples.
  @SensorModel.query_method(path='sensors', name='sensormodel.list')
  def list(self, query):
    # We have no filters that we need to apply, so we just return the query
    # object as is. As we'll see in further examples, we can augment the query
    # using environment variables and other parts of the request state.
    return query

APPLICATION = endpoints.api_server([SensorsApi], restricted=False)
