
import random
import re

from google.appengine.ext import endpoints
from protorpc import remote, messages

from google.appengine.ext import db

CLIENT_ID = 'YOUR-CLIENT-ID'

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
  room = messages.EnumField('SensorMessage.Room', 3, default='LIVING_ROOM')
  sensor_type = messages.EnumField('SensorMessage.Type', 4, default='TEMPERATURE')
  active = messages.BooleanField(5, default=True)

class SensorsRequestMessage(messages.Message):
  sensors = messages.MessageField('SensorMessage', 1, repeated=True)

class SensorsResponseMessage(messages.Message):
  class Status(messages.Enum):
    STATUS_OK = 1
    STATUS_FAILED = 2

  status = messages.EnumField('SensorsResponseMessage.Status', 1, default='STATUS_OK')
  error = messages.StringField(2, repeated = True)

class Sensor(db.Model):
  sensor_id = db.IntegerProperty(required = True)
  network_id = db.StringProperty()
  room = db.StringProperty()
  sensor_type = db.StringProperty()
  active = db.BooleanProperty()

@endpoints.api(name='sensors', version='v1',
               description='Sensors API',
               allowed_client_ids=[CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID])
class SensorsApi(remote.Service):
  """Class which defines sensors API v1."""


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
                              room=s.room,
                              sensor_type=s.sensor_type,
                              active=s.active)
        sensorEntity.put()

      response = SensorsResponseMessage()
      response.status = 'STATUS_OK'

