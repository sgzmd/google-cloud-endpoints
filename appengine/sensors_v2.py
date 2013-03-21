from google.appengine.ext import endpoints
from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel

# Represents a single sensor in application's database,
# inheriting it from EndpointsModel.
class Sensor(EndpointsModel):
  # indicates which members of this class are in fact attributes
  # id is provided automagically
  _message_fields_schema = ('id',
                            'network_id',
                            'room',
                            'sensor_type',
                            'active',
                            'created')

  network_id = db.StringProperty()
  room = db.StringProperty()
  sensor_type = db.StringProperty()
  active = db.BooleanProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

