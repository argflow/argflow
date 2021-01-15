# Architecture

The application consists of two components:

- A Python server that provides the required functionality for interacting with the system and the Argflow library.

- A web-based frontend built with React.

These components communicate with each other primarily through an REST API. You can view its [Swagger](https://swagger.io/) documentation and try out certain requests by visiting the `/api/docs` path. Additionally, websockets are used to send events to the frontend app from the server, for example to notify it that a change has been detected on the fileystem.

Extensibility has been an important goal in the design of the portal. The portal supports loading custom visualisers through a plugin system to allow you to develop and customise visualisers as needed. See the [visualisers](../visualisers) section for more details on this.
