import json
import logging
import time

import requests

import keycloak

KEYCLOAK_URL = "http://traefik/guardian/keycloak/"

logger = None


class KeycloakConfigurator:
    def __init__(self, realm_name, client_name, user_name):
        self.logger = self.get_logger()
        self.wait_for_keycloak()
        self.realm_name = realm_name
        self.client_name = client_name
        self.user_name = user_name
        self.keycloak_admin = keycloak.KeycloakAdmin(
            connection=self.connect(realm_name="master")
        )

    def get_logger(
        self,
    ):
        _logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s [%(name)-12s] %(message)s"
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
        _logger.setLevel(logging.DEBUG)
        return _logger

    def wait_for_keycloak(self):
        self.logger.info("Waiting for keycloak.")
        while True:
            try:
                res = requests.get(KEYCLOAK_URL, timeout=5, allow_redirects=True)
                if res.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass

            time.sleep(1.0)
        self.logger.info("Keycloak now accessible.")
        time.sleep(5.0)

    def connect(self, realm_name=None):
        return keycloak.KeycloakOpenIDConnection(
            server_url=KEYCLOAK_URL,
            username="admin",  # nosec
            password="admin",  # nosec
            realm_name=realm_name,
            user_realm_name="master",
            verify=False,
        )

    def configure(self):
        # create realm
        self.logger.info(f"Creating Realm: {self.realm_name}")

        # lets keep this simple and always start fresh
        try:
            self.keycloak_admin.delete_realm(self.realm_name)
        except keycloak.exceptions.KeycloakDeleteError:
            pass
        self.keycloak_admin.create_realm(
            payload={"realm": self.realm_name, "enabled": True}, skip_exists=True
        )
        time.sleep(1.0)

        # change to new realm
        self.keycloak_admin = keycloak.KeycloakAdmin(
            connection=self.connect(realm_name=self.realm_name)
        )

        # create clients
        client_config = json.load(
            open(
                "/keycloak/provisioning/guardian_client_management_api_config.json", "r"
            )
        )
        self.keycloak_admin.create_client(payload=client_config, skip_exists=True)
        client_config = json.load(
            open("/keycloak/provisioning/guardian_client_ui_config.json", "r")
        )
        self.keycloak_admin.create_client(payload=client_config, skip_exists=True)

        # create user
        self.logger.info(f"Creating User: {self.user_name}")
        try:
            self.keycloak_admin.create_user(
                {
                    "username": self.user_name,
                    "enabled": True,
                    "credentials": [
                        {
                            "value": "univention",
                            "type": "password",
                        }
                    ],
                }
            )
        except Exception as exc:
            self.logger.info(f"User {self.user_name} already exists!")
            self.logger.debug(exc)


if __name__ == "__main__":
    configurator = KeycloakConfigurator(
        realm_name="GuardianDev", client_name="guardian", user_name="dev"
    )
    configurator.configure()
