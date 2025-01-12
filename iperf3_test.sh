#!/bin/bash

stack_name="bwcheck"
docker stack rm $stack_name
docker stack deploy -c alpine-os.yaml $stack_name