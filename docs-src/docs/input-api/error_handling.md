---
title: Errors
description: Dealing with Errors
---


When the client sends a http request to the Input API and waits until it receives a response. If the response code is 2xx \(the status code for a successful call\) the client converts the received message into a python object which can be viewed or used. However if the Input API responds with an error code \(4xx or 5xx\) the python client will raise an error. It's up to the user to decide if and how the want to handle this error.
