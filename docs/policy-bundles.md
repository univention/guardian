<!--
SPDX-FileCopyrightText: 2026 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
-->

# Deploying your own policies

This guide is for app and package developers who need to distribute their own
Cerbos policies across a UCS domain. You register your policies as a bundle in
LDAP; the included listener installs, validates and activates them on every server
running the Guardian. For the delivery model and architecture, see
[`architecture.md`](architecture.md).

## 1. Organize your policy files

Place all policy files for your bundle inside a dedicated directory in your
source package:

```text
your-policies/
├── resource_policies/portal_tile.yaml
└── derived_roles/portal_roles.yaml
```

On registration, the contents of your directory are installed into
`/usr/share/univention-guardian-server/policies/<app>/` on every server where
Cerbos runs (the parent directory is not included). With `app` set to `portal`
(step 4), the tree above installs as:

```text
/usr/share/univention-guardian-server/policies/portal/resource_policies/portal_tile.yaml
/usr/share/univention-guardian-server/policies/portal/derived_roles/portal_roles.yaml
```

Restrictions:

- Nested subdirectories are preserved.
- Include only regular files and standard directories. Anything else (such as
  symlinks or hardlinks) causes the bundle to be rejected.

## 2. Test your policies before registration

The compile check on registration confirms your policies are valid, not that they
allow and deny what you intend. Write Cerbos policy tests — YAML files whose
names end in `_test.yaml` — and run them in your pipeline before you register a
bundle. See the Cerbos docs on
[testing policies](https://docs.cerbos.dev/cerbos/latest/policies/compile#testing).

```sh
cerbos compile /path/to/your-policies
```

`cerbos compile` compiles every policy and runs every test suite it finds; a
non-zero exit means a policy failed to compile or an expectation was not met.

## 3. Build the tar

Create a plain, uncompressed tar. Exclude test files from the registered bundle:

```sh
tar -C /path/to/your-policies --exclude='*_test.yaml' -cf /path/to/bundle.tar .
```

## 4. Register the bundle

Register the tar as a `settings/data` object, for example from a join script:

```sh
. /usr/share/univention-lib/all.sh
ucs_registerLDAPExtension "$@" \
  --name portal-policies \
  --data /path/to/bundle.tar \
  --data_meta '{"app": "portal", "version": "1"}' \
  --data_type "guardian/policy-bundle"
```

The bundle is validated with `cerbos compile` before it is applied. If it does
not compile, your previous policies are kept and the new bundle is discarded.

## Update, move, and remove a bundle

When you run `ucs_registerLDAPExtension` again for a bundle that is already
registered, the outcome depends on the identifier (`--name`, or the `--data`
file name if `--name` is omitted) and the `app` value in `--data_meta`:

- **Update** — same identifier and same `app`: the existing bundle is replaced in
  place. This is a regular policy update.
- **Move** — same identifier, different `app`: the new subdirectory is installed
  and the old one is removed in the same operation.
- **Remove** — unregister with `ucs_unregisterLDAPExtension`, passing the
  registered identifier, for example from your unjoin script:

  ```sh
  ucs_unregisterLDAPExtension "$@" --data <identifier>
  ```

## Naming: avoid collisions

A bundle is one `settings/data` object in LDAP, and two values decide what a
later registration affects. Neither is namespaced, and the implementation does
not record which provider owns an object or directory, so overlapping values
overwrite each other. Choose both explicitly and make both specific to your app.

- **The object identifier** — the `cn` of the object
  (`cn=<identifier>,cn=data,cn=univention,<ldap_base>`), taken from `--name` or,
  if omitted, the base name of the `--data` file. This is what marks two
  registrations as the same object. If two registrations share it, the last one
  overwrites the bundle.
- **The `app` value in `--data_meta`** — the name of the subdirectory under
  `policies/` that your files install into. If two separate LDAP objects share
  it, both install into the same `policies/<app>/` directory; an install replaces
  that directory as a whole, so one bundle overwrites the other on disk, and
  unregistering either object deletes the shared directory and removes both
  providers' policies.
