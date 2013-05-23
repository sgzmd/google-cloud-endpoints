var sensorsApi = null;

function init() {
  var ROOT = 'http://localhost:8080/_ah/api';
  gapi.client.load('sensors', 'v2', function() {
    listSensors();
  }, ROOT);
}

function rand(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function listSensors() {
  $('#sensors').html("");

  function app(html) {
    $('#sensors').append(html);
  }


  gapi.client.sensors.sensors.list().execute(function(resp) {
    console.log(resp);

    var table = $('#sensors').append("<table id='sensorsTable' class='bordered'>");

    $('#sensorsTable').append("<thead><tr><th>Sensor ID</th>" +
        "<th>Network ID</th><th>Sensor Type</th><th>Room</th>" +
        "<th>Active</th><th>Delete</th></tr></thead>");

    resp.sensors.forEach(function(sensor) {
      var html = "<tr>";

      var toggleActive = "<a href='#' onclick='toggleActive(" +
        sensor.sensor_id + "," + !sensor.active + ");'>" +
        sensor.active + "</a>";

      html += ("<td>" + sensor.sensor_id + "</td>");
      html += ("<td>" + sensor.network_id + "</td>");
      html += ("<td>" + sensor.sensor_type + "</td>");
      html += ("<td>" + sensor.room + "</td>");
      html += ("<td>" + toggleActive + "</td>");
      html += "<td><a href='#' onclick='deleteSensor(" + sensor.sensor_id + ");'>X</a></td>";

      html += "</tr>";
      $('#sensorsTable').append(html);

    });
  });

}

function toggleActive(sensorId, active) {
  var request = {
    'sensor_id': sensorId,
    'active': active
  };

  gapi.client.sensors.sensors.update(request).execute(function(resp) {
      console.log(resp);
      listSensors();
    });
}

function deleteSensor(sensorId) {
  var del = gapi.client.sensors.sensors['delete']
  del({'sensors': [{'sensor_id': sensorId}]}).execute(function(resp) {
    console.log(resp);
    listSensors();
  });
}

function createSensor() {
  var sensor = {
    'sensor_id': Math.floor(Math.random() * 78947564),
    'network_id': '192.168.0.' + Math.floor(Math.random() * 254),
    'room': rand(['LIVING_ROOM', 'BEDROOM', 'HALL']),
    'sensor_type': rand(['TEMPERATURE', 'MOTION']),
    'active': rand([true,false])
  };

  var request = {
    'sensors': [ sensor ]
  };

  gapi.client.sensors.sensors.insert(request).execute(function(resp) {
    console.log(resp);
    listSensors();
  })
}

$(function() {
  $( "#create-sensor" ).button().click(createSensor);
});
