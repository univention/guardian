<!--
SPDX-FileCopyrightText: 2026 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
-->

# How to deploy a Cerbos policy bundle for your app or package

## 1. Organize your policy files

Place all policy files for your bundle inside a dedicated directory in your
source package.

On registration, the contents of your policy directory are installed into
`/usr/share/univention-guardian-server/policies/<app>/` on the system where
Cerbos runs (without their parent directory).

For example:

```text
your-policies/
├── resource_policies/portal_tile.yaml
└── derived_roles/portal_roles.yaml
```

With `app` set to `portal` (step 3), this source directory tree would be installed as:

```text
/usr/share/univention-guardian-server/policies/portal/resource_policies/portal_tile.yaml
/usr/share/univention-guardian-server/policies/portal/derived_roles/portal_roles.yaml
```

Directory structure & restrictions:

- You can create nested subdirectories inside your policy directory — their
  structure will be preserved.

- Include only regular files and standard directories. Anything else (such as
  symlinks or hardlinks) will cause the bundle to be rejected.

## 2. Build the tar

Create a plain, uncompressed tar.

```sh
tar -C /path/to/your-policies -cf /path/to/bundle.tar .
```

## 3. Register the bundle

Register the tar as a `settings/data` object, for example from a join script:

```sh
. /usr/share/univention-lib/all.sh
ucs_registerLDAPExtension "$@" \
  --name portal-policies \
  --data /path/to/bundle.tar \
  --data_meta '{"app": "portal", "version": "1"}' \
  --data_type "guardian/policy-bundle"
```

Your policy bundle is validated with `cerbos compile` before it is applied. If
it does not compile, the previous state of your policies is kept and the new
bundle is discarded.

## Test your policies before you ship them

The compile check on registration proves your policies are valid, not that they
allow and deny what you intend. Write Cerbos policy tests — YAML files whose
names end in `_test.yaml` — and run them in your pipeline before you register a
bundle. See the Cerbos docs on
[testing policies](https://docs.cerbos.dev/cerbos/latest/policies/compile#testing).

```sh
cerbos compile /path/to/your-policies
```

`cerbos compile` compiles every policy and runs every test suite it finds; a
non-zero exit means a policy failed to compile or an expectation was not met.

Keep test files out of the registered bundle — build the tar (step 2) with them
excluded:

```sh
tar -C /path/to/your-policies --exclude='*_test.yaml' -cf /path/to/bundle.tar .
```

## Update, move, and remove a bundle

When you run `ucs_registerLDAPExtension` again for a bundle that is already
registered, what happens depends on the identifier (`--name` or if that is
omitted, the file name in `--data`) and the `app` value in `--data_meta` you
pass:

- **UPDATE:** Use the same identifier and same value for `app` — the existing
  bundle is replaced in place. This represents a regular update of your
  policies.
- **MOVE:** Use the same identifier and change the `app` value — the bundle
  is moved. The new subdirectory is installed and the old one is removed in the
  same operation.
- **REMOVE:** Unregister with `ucs_unregisterLDAPExtension`, passing the
  registered identifier, for example from your package's unjoin script:

  ```sh
  ucs_unregisterLDAPExtension "$@" --data <identifier>
  ```

## Current limitations

A bundle is one `settings/data` object in LDAP, and two values decide what a later
registration (`ucs_registerLDAPExtension`) affects:

- **The object identifier** — the `cn` of the object
  (`cn=<identifier>,cn=data,cn=univention,<ldap_base>`). The identifier is taken
  from `--name` when you pass one; when `--name` is omitted, it defaults to the
  base name of the `--data` file (for example `bundle.tar`). Either way, this
  identifier is what marks two registrations as the same object.
- **The `app` value in --data_meta** — defines the name of the subdirectory under
  `/usr/share/univention-guardian-server/policies/` into which the files and
  directories of your policy directory are installed.

Choose both explicitly and make both specific to your app or package. Neither
value is namespaced, and the current implementation does not record which
provider owns an object or a directory, so overlapping values overwrite each
other:

- **Identifier shared with another registration** — the registrations resolve to
  the same object, and the last registration overwrites the bundle. This happens
  when two registrations pass the same `--name`, or, with `--name` omitted, use
  the same `--data` file name.
- **`app` shared with another bundle** — even as separate LDAP objects (two
  different identifiers), both install into the same `policies/<app>/`
  directory. An install replaces that directory as a whole, so one bundle's
  files overwrite the other's on disk; and unregistering either object deletes
  the shared directory and removes both providers' policies.
