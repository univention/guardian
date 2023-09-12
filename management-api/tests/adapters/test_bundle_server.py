from pathlib import Path
from unittest.mock import call

import pytest
import pytest_asyncio
from guardian_management_api.adapters.bundle_server import (
    BundleServerAdapter,
    BundleServerAdapterSettings,
)
from guardian_management_api.errors import BundleBuildError, BundleGenerationIOError
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
    async def test_generate_templates(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        await adapter.generate_templates()
        for part in (
            Path(adapter._data_bundle_name) / ".manifest",
            Path(adapter._data_bundle_name) / "guardian/mapping/data.json",
            Path(adapter._policy_bundle_name) / ".manifest",
        ):
            assert (Path(bundle_server_base_dir) / "templates" / part).exists()

    @pytest.mark.asyncio
    async def test_generate_templates_exists(
        self, adapter: BundleServerAdapter, bundle_server_base_dir
    ):
        await adapter.generate_templates()
        await adapter.generate_templates()
        for part in (
            Path(adapter._data_bundle_name) / ".manifest",
            Path(adapter._data_bundle_name) / "guardian/mapping/data.json",
            Path(adapter._policy_bundle_name) / ".manifest",
        ):
            assert (Path(bundle_server_base_dir) / "templates" / part).exists()

    @pytest.mark.asyncio
    async def test_generate_error(self, adapter: BundleServerAdapter, mocker):
        mock = mocker.MagicMock(side_effect=RuntimeError)
        mocker.patch("aiofiles.open", mock)
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
        subpath = (
            adapter._data_bundle_name
            if bundle_type == BundleType.data
            else adapter._policy_bundle_name
        )
        await adapter._build_bundle(bundle_type)
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
        process_mock = mocker.AsyncMock()
        subprocess_mock = mocker.AsyncMock(return_value=process_mock)
        process_mock.returncode = 1
        mocker.patch("asyncio.create_subprocess_shell", subprocess_mock)
        with pytest.raises(BundleBuildError):
            await adapter._build_bundle(BundleType.data)

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
        await adapter.schedule_bundle_build(BundleType.data)
        await adapter.schedule_bundle_build(BundleType.policies)
        await adapter.generate_bundles()
        assert build_bundle_mock.call_args_list == [
            call(BundleType.data),
            call(BundleType.policies),
        ]

    @pytest.mark.asyncio
    async def test_generate_bundles_empty_queue(
        self, adapter: BundleServerAdapter, mocker
    ):
        build_bundle_mock = mocker.AsyncMock()
        adapter._build_bundle = build_bundle_mock
        await adapter.generate_bundles()
        assert build_bundle_mock.call_args_list == []
