import requests
import time
import logging
import json
import keycloak

KEYCLOAK_URL = "http://traefik/guardian/keycloak/"

logger = None

class KeycloakConfigurator:
    def __init__(self,realm_name,client_name,user_name):
        self.realm_name=realm_name
        self.client_name=client_name
        self.user_name=user_name
        self.keycloak_admin = keycloak.KeycloakAdmin(connection=self.connect(realm_name="master"))
        self.logger = logger
        
    def connect(self,realm_name=None):
        return keycloak.KeycloakOpenIDConnection(
            server_url=KEYCLOAK_URL,
            username="admin",
            password="admin",
            realm_name=realm_name,
            user_realm_name="master",
            verify=False,
        )
    
    def configure(self):
        # create realm
        
        self.logger.info(f"Creating Realm: {self.realm_name}")
        res = self.keycloak_admin.create_realm(payload={"realm": self.realm_name,"enabled":True},skip_exists=True)
        time.sleep(1.0)
        self.keycloak_admin = keycloak.KeycloakAdmin(connection=self.connect(realm_name=self.realm_name))

        # # create client
        #client_config = json.load(open("/keycloak/provisioning/guardian.json","r"))
        client_config = json.load(open("/keycloak/provisioning/localhost_guardian.json","r"))
        self.keycloak_admin.create_client(payload=client_config,skip_exists=True)
        
        # create user
        self.logger.info(f"Creating User: {self.user_name}")

        try:
            self.keycloak_admin.create_user({
                "username": self.user_name,
                "enabled": True,
                "credentials": [
                    {
                        "value": "univention",
                        "type": "password",
                    }
                ],
            })
        except Exception as exc:
            self.logger.info(f"User {self.user_name} already exists!")
            self.logger.debug(exc)


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    _logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.DEBUG)
    return _logger


def wait_for_keycloak(logger):
    logger.info("Waiting for keycloak.")
    while (requests.get(KEYCLOAK_URL).status_code != 200):
        time.sleep(1.0)
    logger.info("Keycloak now accessible.")
    time.sleep(5.0)


if __name__ == "__main__":
    #time.sleep(100000.0)
    logger = get_module_logger(__name__) # .info("HELLO WORLD!")
    wait_for_keycloak(logger)    
    configurator = KeycloakConfigurator(
        realm_name="GuardianDev",
        client_name="guardian",
        user_name="devuser"
    )
    configurator.configure()
