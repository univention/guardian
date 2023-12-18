# Migrations for the Management API

## Notes

### Migration versioning

Each version of the Management API should have at most one migration file. The revision number should match
the version of the Management API. This way it is easy to understand which state the database has for every version.

### About condition files

The builtin conditions added with the migration 1.0.0 are placed in the folder `1.0.0_builtin_conditions`.
If more conditions are added with a later migration, please make sure to create a new directory
appropriate for your migration. This will ensure that each condition is added with the table structure it expects
and migrated properly if applicable.

## Changelog

## 1.0.0_initial_schema

- Add initial tables for app, namespace, role, condition, permission, context, capability
- Add guardian app, namespaces and app admin
- Add builtin conditions
