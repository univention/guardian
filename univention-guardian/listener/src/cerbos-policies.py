#!/usr/bin/python3
#
# Univention guardian
#   Listener Module for installing policy bundles from LDAP into the Cerbos policy directory
#
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import bz2
import io
import json
import os
import shutil
import subprocess  # nosec B404
import tarfile
from pathlib import Path

from univention.listener import ListenerModuleHandler


POLICIES_DIR = Path('/usr/share/univention-guardian-server/policies')
GUARDIAN_SERVER_SERVICE = 'univention-guardian-server'
COMPOSE_FILE = '/usr/share/univention-guardian-server/docker-compose.yaml'
COMPOSE_PROJECT = 'univention-guardian-server'
CERBOS_UID = 64110
CERBOS_GID = 64110
DIR_MODE = 0o750
FILE_MODE = 0o640
RESTART_MARKER = Path('/run/univention-cerbos-policies-restart.pending')


class CerbosPoliciesListener(ListenerModuleHandler):
    class Configuration:
        name = 'cerbos-policies'
        description = 'Install policy bundles from LDAP settings/data into the Cerbos policy directory'
        ldap_filter = '(&(objectClass=univentionData)(univentionDataType=guardian/policy-bundle))'
        attributes = [
            'univentionData',
            'univentionDataMeta',
        ]

    def create(self, dn: str, new: dict[str, list[bytes]]) -> None:
        """Install a newly registered policy bundle and schedule a restart if it applied."""
        if self._install_and_validate(new):
            self._mark_restart_pending()

    def modify(
        self,
        dn: str,
        old: dict[str, list[bytes]],
        new: dict[str, list[bytes]],
        old_dn: str | None,
    ) -> None:
        """Install the changed policy bundle (removing its old location if it moved)
        and schedule a restart if it applied."""
        if self._install_and_validate(new, old_bundle_path=self._get_bundle_path(old)):
            self._mark_restart_pending()

    def remove(self, dn: str, old: dict[str, list[bytes]]) -> None:
        """Remove the bundle's directory, if present, and schedule a restart."""
        bundle_path = self._get_bundle_path(old)
        if not bundle_path.exists():
            return
        with self.as_root():
            self._rmtree(bundle_path)
            self._prune_empty_dirs(bundle_path.parent)
        self.logger.info('removed policy bundle %r', str(bundle_path))
        self._mark_restart_pending()

    def post_run(self) -> None:
        """Restart Cerbos at most once after the listener finishes processing
        pending changes, if a change marked a restart pending."""
        # As a current design decision we keep Cerbos's hot-reload
        # (watchForChanges, cerbos.yaml) disabled and apply new and changed
        # policy bundles by restarting Cerbos instead. This is not a Cerbos
        # limitation: current Cerbos would index a freshly renamed directory
        # recursively and could pick these up. We restart because we want
        # applying a bundle to be strictly atomic. Cerbos should switch from the
        # complete previous policy set to the complete new, already-validated
        # set in a single step and never serve anything in between.
        #
        # Secondarily, the Cerbos docs note that their change detection can be
        # inefficient and resource-intensive on some platforms when the watched
        # directory contains many files or is updated frequently, which a large
        # policy tree may be; restarting avoids relying on it.
        #
        # The restart runs once after the listener finishes processing the
        # pending changes (post_run), so several bundles installed together
        # result in a single restart. The decision uses the on-disk marker
        # rather than in-memory state, so the restart still occurs even if an
        # earlier listener run crashed before performing it.
        if not RESTART_MARKER.exists():
            return
        self.logger.info('restarting %s to apply policy changes', GUARDIAN_SERVER_SERVICE)
        with self.as_root():
            rc = subprocess.call(  # nosec B603
                ['/usr/bin/systemctl', 'try-restart', GUARDIAN_SERVER_SERVICE]
            )
        if rc == 0:
            self._clear_restart_pending()
        else:
            # Keep the marker so the next idle cycle retries the restart.
            self.logger.error('failed to restart %s (rc=%s); will retry', GUARDIAN_SERVER_SERVICE, rc)

    def _mark_restart_pending(self) -> None:
        with self.as_root():
            RESTART_MARKER.parent.mkdir(parents=True, exist_ok=True)
            RESTART_MARKER.touch()

    def _clear_restart_pending(self) -> None:
        with self.as_root():
            RESTART_MARKER.unlink(missing_ok=True)

    def _get_bundle_path(self, obj: dict[str, list[bytes]]) -> Path:
        """Resolve the bundle's directory under POLICIES_DIR from its ``app`` metadata."""
        app = json.loads(obj['univentionDataMeta'][0].decode('UTF-8'))['app']
        path = (POLICIES_DIR / app).resolve()
        if path == POLICIES_DIR or not path.is_relative_to(POLICIES_DIR):
            raise ValueError(f'invalid bundle path for app={app!r}: {path}')
        return path

    def _install_and_validate(
        self,
        obj: dict[str, list[bytes]],
        old_bundle_path: Path | None = None,
    ) -> bool:
        """Extract the bundle from the LDAP object's ``univentionData`` attribute
        (a bzip2-compressed tar), swap it into place, and validate the resulting
        tree with ``cerbos compile``. On failure everything is rolled back and
        ``False`` is returned so the previous state of the policies can be kept.
        """
        data = obj.get('univentionData', [b''])[0]
        if not data:
            return False
        install_path = self._get_bundle_path(obj)
        # Staging and backup dirs are dot-prefixed so Cerbos and `cerbos compile`
        # (both ignore hidden entries) never see half-extracted policies, and the
        # backup can't cause duplicate-definition errors.
        staging_path = install_path.with_name(f'.{install_path.name}.tmp')
        backup_path = self._get_backup_path(install_path)
        tar_bytes = bz2.decompress(data)

        # Only remove the old location when the bundle actually moved.
        if old_bundle_path is not None and (old_bundle_path == install_path or not old_bundle_path.exists()):
            old_bundle_path = None

        with self.as_root():
            install_path.parent.mkdir(parents=True, exist_ok=True)
            self._rmtree(staging_path)
            staging_path.mkdir()
            self._extract_bundle(tar_bytes, staging_path)
            self._apply_permissions(staging_path)

            # Swap the fully-extracted tree in, keeping dot-prefixed backups for
            # rollback: any previous contents at the install path (an in-place
            # update), and, if the bundle moved to a new path, its old location.
            self._rmtree(backup_path)
            had_previous = install_path.exists()
            if had_previous:
                install_path.rename(backup_path)
            staging_path.rename(install_path)
            if old_bundle_path is not None:
                old_backup_path = self._get_backup_path(old_bundle_path)
                self._rmtree(old_backup_path)
                old_bundle_path.rename(old_backup_path)

            # Validate the prospective tree
            error = self._compile_error()
            if error is not None:
                self._rmtree(install_path)
                if had_previous:
                    backup_path.rename(install_path)
                if old_bundle_path is not None:
                    self._get_backup_path(old_bundle_path).rename(old_bundle_path)
                self.logger.error(
                    'rejected invalid policy bundle for %r; rolled back (%s)',
                    str(install_path),
                    error,
                )
                return False

            self._rmtree(backup_path)
            if old_bundle_path is not None:
                self._rmtree(self._get_backup_path(old_bundle_path))
                self._prune_empty_dirs(old_bundle_path.parent)
        self.logger.info('installed policy bundle %r', str(install_path))
        return True

    def _compile_error(self) -> str | None:
        """Return None if the on-disk policy tree compiles, else the error output.

        Runs a one-off container from the univention-guardian-server compose
        file, so the Cerbos version and the ``/policies`` mount match the
        running server. Any failure (compilation error, or the check itself not
        running) is treated as a reason to reject the change and keep the
        previous policies.

        """
        try:
            proc = subprocess.run(  # nosec B603
                [
                    '/usr/bin/docker-compose',
                    '-f',
                    COMPOSE_FILE,
                    '-p',
                    COMPOSE_PROJECT,
                    'run',
                    '--rm',
                    '--no-deps',
                    '-e',
                    'CERBOS_NO_TELEMETRY=1',
                    'cerbos',
                    'compile',
                    '--skip-tests',
                    '--no-color',
                    '/policies',
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return f'could not run cerbos compile: {exc}'
        if proc.returncode == 0:
            return None
        output = '\n'.join(part for part in (proc.stdout.strip(), proc.stderr.strip()) if part)
        return output or f'exit code {proc.returncode}'

    def _extract_bundle(self, tar_bytes: bytes, staging: Path) -> None:
        """Extract the tar into ``staging``, rejecting members that aren't plain files/dirs or escape it."""
        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:*') as tar:
            for member in tar.getmembers():
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f'unsafe bundle member {member.name!r}')
                target = (staging / member.name).resolve()
                if not target.is_relative_to(staging):
                    raise ValueError(f'bundle member escapes {staging}: {member.name!r}')
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tar.extractfile(member)
                target.write_bytes(src.read() if src is not None else b'')

    def _apply_permissions(self, root: Path) -> None:
        """Recursively chown/chmod the tree to the Cerbos user with the configured modes."""
        os.chown(root, CERBOS_UID, CERBOS_GID)
        root.chmod(DIR_MODE)
        for dirpath, dirnames, filenames in os.walk(root):
            for name in dirnames:
                path = os.path.join(dirpath, name)
                os.chown(path, CERBOS_UID, CERBOS_GID)
                os.chmod(path, DIR_MODE)
            for name in filenames:
                path = os.path.join(dirpath, name)
                os.chown(path, CERBOS_UID, CERBOS_GID)
                os.chmod(path, FILE_MODE)

    def _prune_empty_dirs(self, directory: Path) -> None:
        """Remove now-empty parent directories up to (but not including) POLICIES_DIR."""
        with self.as_root():
            while directory != POLICIES_DIR and POLICIES_DIR in directory.parents:
                try:
                    directory.rmdir()
                except OSError:
                    break
                directory = directory.parent

    @staticmethod
    def _get_backup_path(directory: Path) -> Path:
        return directory.with_name(f'.{directory.name}.old')

    @staticmethod
    def _rmtree(path: Path) -> None:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
