# UMS Guardian Dependencies

This creates a "package" for UDM syntaxes, LDAP schemas, UMC modules and icons...

## Description

As UMS `container-ldap server` and `container-udm-rest` will all have dependencies
on this project, this is a way to package and access them from other images in
the registry without needing to copy plain text between repositories.

The result is a <2kB image that packages and ships all the components needed by
another repositories. This image will also adhere to the versioning in place for
other images in this repository.
