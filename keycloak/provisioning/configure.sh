#!/bin/bash

echo "Waiting for keycloak-guardian-dev to be reachable"
while ! /opt/keycloak/bin/kcadm.sh config credentials --server http://traefik/guardian/keycloak --realm master --user admin --password admin; do sleep 5; done;

#sleep 1
/opt/keycloak/bin/kcadm.sh create realms -s realm=GuardianDev -s enabled=true -o
#sleep 1
/opt/keycloak/bin/kcadm.sh create roles -r GuardianDev -s name=user
#sleep 1
/opt/keycloak/bin/kcadm.sh create roles -r GuardianDev -s name=admin
#sleep 1
/opt/keycloak/bin/kcadm.sh create clients -r GuardianDev -s clientId=guardian -s publicClient=true -s 'redirectUris=["http://traefik/guardian/authorization/docs/oauth2-redirect"]' -o
#sleep 1
/opt/keycloak/bin/kcadm.sh create groups -r GuardianDev -b '{"name": "Admins"}'
#sleep 1
/opt/keycloak/bin/kcadm.sh create users -r GuardianDev -s username=guardian_user -s enabled=true -o --fields id,username
#sleep 1
/opt/keycloak/bin/kcadm.sh set-password -r GuardianDev --username guardian_user --new-password univention
