#!/usr/bin/env bash

##################################################################
# Quick and dirty shell script to start the server for development
##################################################################

# Run server in development mode
watchgod argflow_ui.main argflow_ui --args examples --no-launch
