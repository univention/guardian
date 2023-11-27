#!/bin/bash

###############################################################################
#                                                                             #
#  Generate a configure-keycloak shell script from templates.                 #
#  The configure-keycloak script can be used to update existing Keycloak      #
#  clients after they have been created (e.g., adding additional              #
#  redirectUris and adding PKCE support).                                     #
#                                                                             #
###############################################################################

APP_NAME=$1
CUSTOM_CONTENT_TEMPLATE=$2
KEYCLOAK_TEMP_FILE=$3

SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

if [ -z "$APP_NAME" ] || [ -z "$CUSTOM_CONTENT_TEMPLATE" ] || [ -z "$KEYCLOAK_TEMP_FILE" ]; then
    cat <<-END
Generate a configure-keycloak shell script from templates.

Usage:

    generate-configure-keycloak.sh <APP_NAME> <PATH_TO_CUSTOM_CONTENT_TEMPLATE> <OUTPUT_FILE>

Example:

    cd appcenter-management/
    ./../appcenter-common/keycloak/generate-configure-keycloak.sh guardian-management-api templates/configure-keycloak.tmpl configure-keycloak.temp

ERROR: missing one or more arguments.
END
    exit 1
fi

if [ ! -f $CUSTOM_CONTENT_TEMPLATE ]; then
    echo "ERROR: $CUSTOM_CONTENT_TEMPLATE: file does not exist!"
    exit 1
fi

cp $SCRIPT_DIR/configure-keycloak.tmpl $KEYCLOAK_TEMP_FILE

sed -i \
    -e "/%COPYRIGHT%/r $SCRIPT_DIR/../copyright.tmpl" -e "/%COPYRIGHT%/d" \
    -e "/%KEYCLOAK-HEADER%/r $SCRIPT_DIR/configure-keycloak-header.tmpl" -e "/%KEYCLOAK-HEADER%/d" \
    -e "/%KEYCLOAK-HELPERS%/r $SCRIPT_DIR/configure-keycloak-helpers.tmpl" -e "/%KEYCLOAK-HELPERS%/d" \
    -e "/%CUSTOM-CODE%/r $CUSTOM_CONTENT_TEMPLATE" -e "/%CUSTOM-CODE%/d" \
    -e "/%KEYCLOAK-FOOTER%/r $SCRIPT_DIR/configure-keycloak-main-footer.tmpl" -e "/%KEYCLOAK-FOOTER%/d" \
    $KEYCLOAK_TEMP_FILE

sed -i "s/%COPYRIGHT-YEAR%/$(date +'%Y')/g" $KEYCLOAK_TEMP_FILE
sed -i "s/%APP%/$APP_NAME/g" $KEYCLOAK_TEMP_FILE
sed -i "/%COMMENT%.*/d" $KEYCLOAK_TEMP_FILE
