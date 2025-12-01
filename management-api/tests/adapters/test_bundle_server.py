import os
from pathlib import Path
from unittest.mock import call

import orjson
import pytest
import pytest_asyncio
from guardian_management_api.adapters.bundle_server import (
    BundleServerAdapter,
    BundleServerAdapterSettings,
)
from guardian_management_api.errors import BundleBuildError, BundleGenerationIOError
from guardian_management_api.models.base import PersistenceGetManyResult
from guardian_management_api.models.capability import (
    Capability,
    CapabilityConditionParameter,
    CapabilityConditionRelation,
    ParametrizedCondition,
)
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.role import Role
from guardian_management_api.ports.bundle_server import BundleType


class TestBundleServerAdapter:
    @pytest_asyncio.fixture
    async def adapter(self, bundle_server_base_dir) -> BundleServerAdapter:
        adapter = BundleServerAdapter()
        await adapter.configure(
            BundleServerAdapterSettings(base_dir=bundle_server_base_dir)
        )
        return adapter

    @pytest.mark.asyncio
    async def test_prepare_directories(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        await adapter.prepare_directories()
        for sub_dir in ("bundles", "templates", "build"):
            assert (Path(bundle_server_base_dir) / sub_dir).exists()

    @pytest.mark.asyncio
    async def test_prepare_directories_exists(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        await adapter.prepare_directories()
        await adapter.prepare_directories()
        for sub_dir in ("bundles", "templates", "build"):
            assert (Path(bundle_server_base_dir) / sub_dir).exists()

    @pytest.mark.asyncio
    async def test_prepare_directories_error(
        self, adapter: BundleServerAdapter, bundle_server_base_dir, mocker
    ):
        mock = mocker.MagicMock(side_effect=RuntimeError)
        mocker.patch("aiofiles.os.makedirs", mock)
        with pytest.raises(BundleGenerationIOError):
            await adapter.prepare_directories()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("patch_env")
    async def test_generate_templates(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        adapter._policy_bundle_template_src = os.environ[
            "BUNDLE_SERVER_ADAPTER__POLICY_BUNDLE_TEMPLATE_SRC"
        ]
        await adapter.generate_templates()
        for part in (
            Path(adapter._data_bundle_name) / ".manifest",
            Path(adapter._policy_bundle_name) / ".manifest",
        ):
            assert (Path(bundle_server_base_dir) / "templates" / part).exists()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("patch_env")
    async def test_generate_templates_exists(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        adapter._policy_bundle_template_src = os.environ[
            "BUNDLE_SERVER_ADAPTER__POLICY_BUNDLE_TEMPLATE_SRC"
        ]
        await adapter.generate_templates()
        await adapter.generate_templates()
        for part in (
            Path(adapter._data_bundle_name) / ".manifest",
            Path(adapter._policy_bundle_name) / ".manifest",
        ):
            assert (Path(bundle_server_base_dir) / "templates" / part).exists()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("patch_env")
    async def test_generate_error(self, adapter: BundleServerAdapter, mocker):
        mock = mocker.MagicMock(side_effect=RuntimeError)
        mocker.patch("aiofiles.open", mock)
        adapter._policy_bundle_template_src = os.environ[
            "BUNDLE_SERVER_ADAPTER__POLICY_BUNDLE_TEMPLATE_SRC"
        ]
        with pytest.raises(BundleGenerationIOError):
            await adapter.generate_templates()

    @pytest.mark.parametrize("bundle_type", [BundleType.data, BundleType.policies])
    @pytest.mark.asyncio
    async def test__prepare_build_dir(
        self, adapter: BundleServerAdapter, mocker, bundle_server_base_dir, bundle_type
    ):
        rmtree_mock = mocker.AsyncMock()
        copytree_mock = mocker.AsyncMock()
        mocker.patch("aioshutil.rmtree", rmtree_mock)
        mocker.patch("aioshutil.copytree", copytree_mock)
        subpath = (
            adapter._data_bundle_name
            if bundle_type == BundleType.data
            else adapter._policy_bundle_name
        )
        await adapter._prepare_build_directory(
            Path(bundle_server_base_dir), subpath, mocker.Mock()
        )
        assert rmtree_mock.call_args_list == [
            call(Path(bundle_server_base_dir) / "build" / subpath)
        ]
        assert copytree_mock.call_args_list == [
            call(
                Path(bundle_server_base_dir) / "templates" / subpath,
                Path(bundle_server_base_dir) / "build" / subpath,
            )
        ]

    @pytest.mark.parametrize("bundle_type", [BundleType.data, BundleType.policies])
    @pytest.mark.asyncio
    async def test__build_bundle(
        self, adapter: BundleServerAdapter, mocker, bundle_server_base_dir, bundle_type
    ):
        process_mock = mocker.AsyncMock()
        subprocess_mock = mocker.AsyncMock(return_value=process_mock)
        process_mock.returncode = 0
        mocker.patch("asyncio.create_subprocess_shell", subprocess_mock)
        prepare_build_dir_mock = mocker.AsyncMock()
        adapter._prepare_build_directory = prepare_build_dir_mock
        adapter._generate_mapping = mocker.AsyncMock()
        adapter._dump_conditions = mocker.AsyncMock()
        subpath = (
            adapter._data_bundle_name
            if bundle_type == BundleType.data
            else adapter._policy_bundle_name
        )
        await adapter._build_bundle(bundle_type, mocker.AsyncMock(), mocker.AsyncMock())
        build_cmd = (
            f"opa build -b {Path(bundle_server_base_dir) / 'build' / subpath} -o "
            f"{Path(bundle_server_base_dir) / 'bundles' / subpath}.tar.gz"
        )
        assert subprocess_mock.call_args_list == [call(build_cmd)]
        process_mock.communicate.assert_called_once()

    @pytest.mark.asyncio
    async def test__prepare_build_directory_build_dir_not_found(
        self, adapter: BundleServerAdapter, mocker, bundle_server_base_dir
    ):
        rmtree_mock = mocker.AsyncMock(side_effect=FileNotFoundError)
        copytree_mock = mocker.AsyncMock()
        mocker.patch("aioshutil.rmtree", rmtree_mock)
        mocker.patch("aioshutil.copytree", copytree_mock)
        await adapter._prepare_build_directory(
            Path(bundle_server_base_dir), adapter._data_bundle_name, mocker.MagicMock()
        )

    @pytest.mark.asyncio
    async def test__build_bundle_build_error(
        self, adapter: BundleServerAdapter, mocker, bundle_server_base_dir
    ):
        adapter._prepare_build_directory = mocker.AsyncMock()
        adapter._generate_mapping = mocker.AsyncMock()
        adapter._dump_conditions = mocker.AsyncMock()
        process_mock = mocker.AsyncMock()
        subprocess_mock = mocker.AsyncMock(return_value=process_mock)
        process_mock.returncode = 1
        mocker.patch("asyncio.create_subprocess_shell", subprocess_mock)
        with pytest.raises(BundleBuildError):
            await adapter._build_bundle(
                BundleType.data, mocker.AsyncMock(), mocker.AsyncMock()
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "bundle_type,queue",
        [
            (BundleType.data, "_data_bundle_queue"),
            (BundleType.policies, "_policies_bundle_queue"),
        ],
    )
    async def test_schedule_bundle_build(
        self, adapter: BundleServerAdapter, bundle_type, queue
    ):
        queue = getattr(adapter, queue)
        await adapter.schedule_bundle_build(bundle_type)
        assert queue.full()
        assert queue.qsize() == 1
        await adapter.schedule_bundle_build(bundle_type)
        assert queue.full()
        assert queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_generate_bundles(self, adapter: BundleServerAdapter, mocker):
        build_bundle_mock = mocker.AsyncMock()
        adapter._build_bundle = build_bundle_mock
        cond_persistence_mock = mocker.AsyncMock()
        cap_persistence_mock = mocker.AsyncMock()
        await adapter.schedule_bundle_build(BundleType.data)
        await adapter.schedule_bundle_build(BundleType.policies)
        await adapter.generate_bundles(cond_persistence_mock, cap_persistence_mock)
        assert build_bundle_mock.call_args_list == [
            call(BundleType.data, cond_persistence_mock, cap_persistence_mock),
            call(BundleType.policies, cond_persistence_mock, cap_persistence_mock),
        ]

    @pytest.mark.asyncio
    async def test_generate_bundles_empty_queue(
        self, adapter: BundleServerAdapter, mocker
    ):
        build_bundle_mock = mocker.AsyncMock()
        adapter._build_bundle = build_bundle_mock
        await adapter.generate_bundles(mocker.AsyncMock(), mocker.AsyncMock())
        assert build_bundle_mock.call_args_list == []

    @pytest.mark.asyncio
    async def test_dump_conditions(self, adapter: BundleServerAdapter, mocker, tmpdir):
        cond_persistence_mock = mocker.AsyncMock()
        many_cond_mock = mocker.MagicMock()
        many_cond_mock.objects = [mocker.MagicMock()]
        many_cond_mock.objects[0].name = "test"
        many_cond_mock.objects[0].app_name = "guardian"
        many_cond_mock.objects[0].namespace_name = "builtin"
        many_cond_mock.objects[0].code = b"Q09ERQ=="
        cond_persistence_mock.read_many = mocker.AsyncMock(return_value=many_cond_mock)
        (Path(tmpdir) / "conditions/guardian/conditions").mkdir(parents=True)
        await adapter._dump_conditions(
            cond_persistence_mock, Path(tmpdir) / "conditions"
        )
        assert (Path(tmpdir) / "conditions/guardian/conditions").exists()
        with open(
            (
                Path(tmpdir)
                / "conditions/guardian/conditions/guardian__builtin__test.rego"
            ),
            "r",
        ) as fd:
            assert fd.read() == "CODE"

    @pytest.mark.asyncio
    async def test_dump_conditions_error(
        self, adapter: BundleServerAdapter, mocker, tmpdir
    ):
        cond_persistence_mock = mocker.AsyncMock()
        cond_persistence_mock.read_many = mocker.AsyncMock(side_effect=RuntimeError)
        with pytest.raises(
            BundleGenerationIOError,
            match="An error occurred while writing the conditions to files.",
        ):
            await adapter._dump_conditions(
                cond_persistence_mock, Path(tmpdir) / "conditions"
            )

    @pytest.mark.asyncio
    async def test__generate_mapping(
        self, adapter: BundleServerAdapter, mocker, tmpdir
    ):
        async def _read_many(*args, **kwargs):
            return PersistenceGetManyResult(
                total_count=3,
                objects=[
                    Capability(
                        app_name="app",
                        namespace_name="namespace",
                        name="cap1",
                        display_name="cap1",
                        role=Role(
                            app_name="app",
                            namespace_name="namespace",
                            name="role",
                            display_name="role",
                        ),
                        permissions=[
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm1"
                            ),
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm2"
                            ),
                        ],
                        relation=CapabilityConditionRelation.AND,
                        conditions=[
                            ParametrizedCondition(
                                app_name="app",
                                namespace_name="namespace",
                                name="cond1",
                                parameters=[
                                    CapabilityConditionParameter(name="a", value=1),
                                    CapabilityConditionParameter(name="b", value=True),
                                ],
                            ),
                            ParametrizedCondition(
                                app_name="app",
                                namespace_name="namespace",
                                name="cond2",
                                parameters=[
                                    CapabilityConditionParameter(
                                        name="c", value="three"
                                    ),
                                    CapabilityConditionParameter(name="d", value=4.0),
                                ],
                            ),
                        ],
                    ),
                    Capability(
                        app_name="app",
                        namespace_name="namespace",
                        name="cap2",
                        display_name="cap2",
                        role=Role(
                            app_name="app",
                            namespace_name="namespace",
                            name="role",
                            display_name="role",
                        ),
                        permissions=[
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm3"
                            ),
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm4"
                            ),
                        ],
                        relation=CapabilityConditionRelation.AND,
                        conditions=[],
                    ),
                    Capability(
                        app_name="app",
                        namespace_name="namespace",
                        name="cap3",
                        display_name="cap3",
                        role=Role(
                            app_name="app",
                            namespace_name="namespace",
                            name="role2",
                            display_name="role2",
                        ),
                        permissions=[
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm1"
                            ),
                            Permission(
                                app_name="app", namespace_name="namespace", name="perm2"
                            ),
                        ],
                        relation=CapabilityConditionRelation.OR,
                        conditions=[],
                    ),
                ],
            )

        cap_persistence_mock = mocker.MagicMock()
        cap_persistence_mock.read_many = _read_many
        target_dir = Path(tmpdir) / "mapping"
        (target_dir / "guardian/mapping").mkdir(parents=True)
        await adapter._generate_mapping(cap_persistence_mock, target_dir)
        with open(target_dir / "guardian/mapping/data.json", "rb") as file:
            result = orjson.loads(file.read())
        assert result == {
            "roleCapabilityMapping": {
                "app:namespace:role": [
                    {
                        "appName": "app",
                        "namespace": "namespace",
                        "permissions": ["perm1", "perm2"],
                        "relation": "AND",
                        "conditions": [
                            {
                                "name": "app:namespace:cond1",
                                "parameters": {"a": 1, "b": True},
                            },
                            {
                                "name": "app:namespace:cond2",
                                "parameters": {"c": "three", "d": 4.0},
                            },
                        ],
                    },
                    {
                        "appName": "app",
                        "namespace": "namespace",
                        "permissions": ["perm3", "perm4"],
                        "relation": "AND",
                        "conditions": [],
                    },
                ],
                "app:namespace:role2": [
                    {
                        "appName": "app",
                        "namespace": "namespace",
                        "permissions": ["perm1", "perm2"],
                        "relation": "OR",
                        "conditions": [],
                    },
                ],
            }
        }

    @pytest.mark.asyncio
    async def test__generate_mapping_error(
        self, adapter: BundleServerAdapter, mocker, tmpdir
    ):
        cap_persistence_mock = mocker.AsyncMock()
        cap_persistence_mock.read_many = mocker.AsyncMock(side_effect=RuntimeError)
        with pytest.raises(
            BundleGenerationIOError,
            match="An error occurred while writing the role capability mapping to files.",
        ):
            await adapter._generate_mapping(
                cap_persistence_mock, Path(tmpdir) / "mapping"
            )
