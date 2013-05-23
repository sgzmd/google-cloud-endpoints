import sensors
import sensors_v2

from google.appengine.ext import endpoints

APPLICATION = endpoints.api_server([
  sensors.SensorsApi,
  sensors_v2.SensorsApi], restricted=False)
