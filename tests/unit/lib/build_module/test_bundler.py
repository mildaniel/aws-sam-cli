from unittest import TestCase
from unittest.mock import patch, Mock

from parameterized import parameterized

from samcli.lib.build.bundler import EsbuildBundlerManager
from tests.unit.commands.buildcmd.test_build_context import DummyStack


class EsbuildBundler_is_node_option_set(TestCase):
    @parameterized.expand(
        [
            (
                {"Properties": {"Environment": {"Variables": {"NODE_OPTIONS": "--enable-source-maps"}}}},
                True,
            ),
            (
                {"Properties": {"Environment": {"Variables": {"NODE_OPTIONS": "nothing"}}}},
                False,
            ),
        ]
    )
    def test_is_node_option_set(self, resource, expected_result):
        esbuild_bundler_manager = EsbuildBundlerManager(Mock())
        self.assertEqual(esbuild_bundler_manager._is_node_option_set(resource), expected_result)

    def test_enable_source_map_missing(self):
        esbuild_bundler_manager = EsbuildBundlerManager(Mock())
        self.assertFalse(esbuild_bundler_manager._is_node_option_set({"Properties": {}}))


class EsbuildBundler_enable_source_maps(TestCase):
    @parameterized.expand(
        [
            (
                {
                    "Resources": {
                        "test": {"Metadata": {"BuildMethod": "esbuild", "BuildProperties": {"Sourcemap": True}}}
                    }
                },
            ),
            (
                {
                    "Resources": {
                        "test": {
                            "Properties": {"Environment": {"Variables": {"NODE_OPTIONS": "--something"}}},
                            "Metadata": {"BuildMethod": "esbuild", "BuildProperties": {"Sourcemap": True}},
                        }
                    }
                },
            ),
        ]
    )
    def test_enable_source_maps_only_source_map(self, template):
        esbuild_manager = EsbuildBundlerManager(stack=Mock(), template=template)

        updated_template = esbuild_manager.enable_source_maps()

        for _, resource in updated_template["Resources"].items():
            self.assertIn("--enable-source-maps", resource["Properties"]["Environment"]["Variables"]["NODE_OPTIONS"])

    @parameterized.expand(
        [
            ({"Resources": {"test": {"Metadata": {"BuildMethod": "esbuild"}}}}, True),
            (
                {
                    "Resources": {
                        "test": {
                            "Properties": {"Environment": {"Variables": {"NODE_OPTIONS": "--enable-source-maps"}}},
                            "Metadata": {"BuildMethod": "esbuild"},
                        }
                    }
                },
                True,
            ),
            (
                {
                    "Resources": {
                        "test": {
                            "Metadata": {"BuildMethod": "esbuild", "BuildProperties": {"Sourcemap": False}},
                        }
                    }
                },
                False,
            ),
        ]
    )
    def test_enable_source_maps_only_node_options(
        self,
        template,
        expected_value,
    ):
        esbuild_manager = EsbuildBundlerManager(Mock(), template)
        esbuild_manager._is_node_option_set = Mock()
        esbuild_manager._is_node_option_set.return_value = True
        updated_template = esbuild_manager.enable_source_maps()

        for _, resource in updated_template["Resources"].items():
            self.assertEqual(resource["Metadata"]["BuildProperties"]["Sourcemap"], expected_value)

    def test_warnings_printed(self):
        template = {
            "Resources": {
                "test": {
                    "Properties": {
                        "Environment": {"Variables": {"NODE_OPTIONS": ["--something"]}},
                    },
                    "Metadata": {"BuildMethod": "esbuild", "BuildProperties": {"Sourcemap": True}},
                }
            }
        }
        esbuild_manager = EsbuildBundlerManager(Mock(), template=template)
        esbuild_manager._warn_using_source_maps = Mock()
        esbuild_manager._warn_invalid_node_options = Mock()
        esbuild_manager.enable_source_maps()

        esbuild_manager._warn_using_source_maps.assert_called()
        esbuild_manager._warn_invalid_node_options.assert_called()


class EsbuildBundler_esbuild_configured(TestCase):
    @parameterized.expand(
        [
            (
                {
                    "test": {
                        "Properties": {
                            "Environment": {"Variables": {"NODE_OPTIONS": ["--something"]}},
                        },
                        "Metadata": {"BuildMethod": "esbuild", "BuildProperties": {"Sourcemap": True}},
                        "Type": "AWS::Serverless::Function",
                    }
                },
                True,
            ),
            (
                {
                    "test": {
                        "Properties": {
                            "Environment": {"Variables": {"NODE_OPTIONS": ["--something"]}},
                        },
                        "Metadata": {"BuildMethod": "Makefile", "BuildProperties": {"Sourcemap": True}},
                        "Type": "AWS::Serverless::Function",
                    }
                },
                False,
            ),
        ],
    )
    def test_detects_if_esbuild_is_configured(self, stack_resources, expected):
        stack = DummyStack(stack_resources)
        stack.stack_path = "/path"
        stack.location = "/location"
        esbuild_manager = EsbuildBundlerManager(stack)
        self.assertEqual(esbuild_manager.esbuild_configured(), expected)
