#!/bin/bash

echo "Waiting 30 seconds for keycloak-guardian-dev to be reachable"
sleep 30
/opt/keycloak/bin/kcadm.sh config credentials --server http://traefik/guardian/keycloak --realm master --user admin --password admin
sleep 1
/opt/keycloak/bin/kcadm.sh create realms -s realm=guardian_realm -s enabled=true -o
sleep 1
/opt/keycloak/bin/kcadm.sh create roles -r guardian_realm -s name=user
sleep 1
/opt/keycloak/bin/kcadm.sh create clients -r guardian_realm -s clientId=guardian_client -s publicClient=true -o
sleep 1
/opt/keycloak/bin/kcadm.sh create users -r guardian_realm -s username=guardian_user -s enabled=true -o --fields id,username
# sleep 1
# /opt/keycloak/bin/kcadm.sh set-password -r guardian_realm --username guardian_user --password univention
