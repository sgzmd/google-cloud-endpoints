from google.appengine.ext import endpoints
from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel


# Represents a single sensor in application's database,
# inheriting it from EndpointsModel.
class Sensor(EndpointsModel):
  sensor_id = db.IntegerProperty(required = True)
  network_id = db.StringProperty()
  room = db.StringProperty()
  sensor_type = db.StringProperty()
  active = db.BooleanProperty()
