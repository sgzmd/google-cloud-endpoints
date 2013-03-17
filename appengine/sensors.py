
import logging
import random
import re

from google.appengine.ext import endpoints
from google.appengine.ext import db

from protorpc import remote, messages

# We will use logging.levelname(...) for logging which is a standard
# facility provided by AppEngine - no configuration required
logging.getLogger().setLevel(logging.DEBUG)

# Replace this with your JS/Android/iOS client ID
CLIENT_ID = 'YOUR-CLIENT-ID'

# Converts RPC SensorMessage object to datastore Sensor.
def SensorRpcToDb(s):
  """ Converts SensorMessage to db-level Sensor object. """
  return Sensor(key_name=str(s.sensor_id),
                             sensor_id=s.sensor_id,
                             network_id=s.network_id,
                             room=str(s.room),
                             sensor_type=str(s.sensor_type),
                             active=s.active)

class EnumHelpers:
  @classmethod
  def RoomFromString(clazz, str):
    return {
      'LIVING_ROOM': SensorMessage.Room.LIVING_ROOM,
      'BEDROOM': SensorMessage.Room.BEDROOM,
      'HALL': SensorMessage.Room.HALL
    }.get(str, SensorMessage.Room.UNDEFINED)

  @classmethod
  def TypeFromString(clazz, str):
    return {
      'MOTION': SensorMessage.Type.MOTION,
      'TEMPERATURE': SensorMessage.Type.TEMPERATURE
    }.get(str, SensorMessage.Type.UNDEFINED)


class SensorMessage(messages.Message):
  """
  Represents a single Sensor entity. Inherits ProtoRPC's Message and will be used for
  representing messages between the API and the client. Google Cloud Endpoints framework
  will handle behind-the-scenes conversion of objects of this type to and from on-the-wire
  format (Protocol Buffers, JSON, etc).
  """
  class Room(messages.Enum):
    LIVING_ROOM = 1
    BEDROOM = 2
    HALL = 3
    UNDEFINED = 255


  class Type(messages.Enum):
    TEMPERATURE = 1
    MOTION = 2
    UNDEFINED = 255

  # a unique identifier of sensor in this system
  sensor_id = messages.IntegerField(1, required=True)

  # e.g. sensor IP address
  network_id = messages.StringField(2)
  room = messages.EnumField('SensorMessage.Room', 3, default='LIVING_ROOM')
  sensor_type = messages.EnumField('SensorMessage.Type', 4, default='TEMPERATURE')
  active = messages.BooleanField(5, default=True)

# Contains potentially multiple sensors
class SensorsRequestMessage(messages.Message):
  sensors = messages.MessageField('SensorMessage', 1, repeated=True)

class ListSensorsRequest(messages.Message):
  # we don't need anything just yet
  pass

# Sent in response to Add / Update operations
class SensorsResponseMessage(messages.Message):
  class Status(messages.Enum):
    STATUS_OK = 1
    STATUS_FAILED = 2

  status = messages.EnumField('SensorsResponseMessage.Status', 1, default='STATUS_OK')
  error = messages.StringField(2, repeated = True)

  # in case response should include sensors
  sensors = messages.MessageField('SensorMessage', 3, repeated=True)

# Represents a single sensor in application's database
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


  @endpoints.method(SensorsRequestMessage,
                    SensorsResponseMessage,
                    path='sensors',
                    http_method='POST',
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
      response = SensorsResponseMessage()
      response.status = SensorsResponseMessage.Status.STATUS_OK
      errors = []

      for s in request.sensors:
        if Sensor.get_by_key_name(str(s.sensor_id)):
          err = "Record with sensor_id = {0} already exists, will not add".format(s.sensor_id)
          logging.warning(err)
          response.status = SensorsResponseMessage.Status.STATUS_FAILED
          errors.append(err)
        else:
          sensorEntity = SensorRpcToDb(s)
          sensorEntity.put()

      response.error = errors
      return response

  @endpoints.method(ListSensorsRequest,
                    SensorsResponseMessage,
                    path='sensors',
                    http_method='GET',
                    name='sensors.list')
  def sensors_list(self, request):
    """Returns a collection of all sensors installed in the household.

    Args:
      request: an instance of ListSensorsRequest, empty object.

    Returns:
      Collection of SensorMessage objects.
    """
    logging.info("sensors_list called: %s", str(request))
    response = SensorsResponseMessage()

    sensor_list = []
    for sensor in Sensor.all():
      sm = SensorMessage(sensor_id=sensor.sensor_id,
                         network_id=sensor.network_id,
                         room=EnumHelpers.RoomFromString(sensor.room),
                         sensor_type=EnumHelpers.TypeFromString(sensor.sensor_type),
                         active=sensor.active)
      logging.info("Creating SensorMessage: %s", str(sm))
      sensor_list.append(sm)

    logging.info("Final sensor list: %s", str(sensor_list))
    response.sensors = sensor_list
    response.status = SensorsResponseMessage.Status.STATUS_OK

    return response


  @endpoints.method(SensorMessage,
                    SensorsResponseMessage,
                    path='sensors',
                    http_method='PUT',
                    name='sensors.update')
  def sensor_update(self, request):
    """Updates sensor information in the datastore.

    Args:
      request: instance of SensorMessage, sensor to be updated, should
      only include fields to be updated.

    Returns:
      Instance of SensorMessage containing updated information.
    """
    response = SensorsResponseMessage()

    logging.info("sensor_update: %s", str(request))
    sensor = Sensor.get_by_key_name(str(request.sensor_id))

    if not sensor:
      err = "Sensor sensor_id={0} not found".format(request.sensor_id)
      logging.warning(err)
      response.status = SensorsResponseMessage.Status.STATUS_FAILED
      response.error  = [ err ]
      return response

    logging.info("Sensor: %s", str(sensor))

    if request.active != None:
      sensor.active = request.active

    sensor.put()

    sm = SensorMessage(sensor_id=sensor.sensor_id,
                       network_id=sensor.network_id,
                       room=EnumHelpers.RoomFromString(sensor.room),
                       active=sensor.active)


    response.sensors = [ sm ]
    response.status = SensorsResponseMessage.Status.STATUS_OK

    return response

  @endpoints.method(SensorsRequestMessage,
                    SensorsResponseMessage,
                    path='sensors-delete',
                    http_method="POST",
                    name='sensors.delete')
  def sensor_delete(self, request):
    """ Deletes a sensor with a specified sensor_id.

    Args:
      request: instance of SensorsRequestMessage, list of sensors to be deleted.

    Returns:
      Instance of SensorsResponseMessage.
    """
    response = SensorsResponseMessage()
    response.status = SensorsResponseMessage.Status.STATUS_OK
    errors = []

    logging.info("delete()")
    logging.info(request)

    for s in request.sensors:
      sensor = Sensor.get_by_key_name(str(s.sensor_id))
      if not sensor:
        err = "Record with sensor_id = {0} does not exists".format(s.sensor_id)
        logging.warning(err)
        response.status = SensorsResponseMessage.Status.STATUS_FAILED
        errors.append(err)
      else:
        sensor.delete()

    response.error = errors
    return response


APPLICATION = endpoints.api_server([SensorsApi],
                                   restricted=False)
