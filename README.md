<script src="https://google-code-prettify.googlecode.com/svn/loader/run_prettify.js"></script>

Important note
==============

This project was created to support a lecture on Google Cloud Endpoints. To fully benefit of this example, you should
at least go through this slideshow:

[romankirillov.info/google-cloud-endpoints.html](http://romankirillov.info/google-cloud-endpoints.html)

Description
======================

This is a sample project for Google Cloud Endpoints technology. For the purpose of this project we assume that we are building a home automation system. We have a number of sensors running in our home, and we want to control which ones of them are active via web and mobile.

To achieve this, we need to build an a service and an API which should:

* Allow authenticated users to modify the state of the monitoring, e.g.     change the activity state of a given sensor, get list of sensors, etc.

* Provide a push-enabled update mechanism for in-home server which controls all the sensors installed in the household.

The API we design should be accessible for both web and native mobile applications.

