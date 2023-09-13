FROM quay.io/keycloak/keycloak:latest as builder
# COPY --from=builder /opt/keycloak/ /opt/keycloak/
COPY /keycloak/provisioning/configure.sh /configure.sh
#RUN chmod -R 755 /configure.sh
# CMD sleep 1000
#CMD /opt/keycloak/bin/kcadm.sh config credentials --server http://traefik/guardian/keycloak --realm master --user admin --password admin
# # create default realm
#RUN /opt/keycloak/bin/kcadm.sh create realms -s realm=guardian_realm -s enabled=true -o

# # create default client
#RUN /opt/keycloak/bin/kcadm.sh create clients -r guardian_realm -s clientId=guardian_client -s publicClient=true -o

#COPY keycloak/kc_config.json /opt/keycloak/data/import/kc_config.json
# RUN /opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/kc_config.json


#ENTRYPOINT ["/bin/bash","configure.sh"]
ENTRYPOINT ["/bin/bash","configure.sh"]