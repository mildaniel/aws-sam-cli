import os
import shutil
from typing import Optional
from unittest import TestCase, skipIf
from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired

from samcli.lib.utils.osutils import copytree
from tests.testing_utils import SKIP_DOCKER_MESSAGE, SKIP_DOCKER_TESTS, get_sam_command

TIMEOUT = 300


@skipIf(SKIP_DOCKER_TESTS, SKIP_DOCKER_MESSAGE)
class InvokeIntegBase(TestCase):
    template: Optional[Path] = None
    moved_to_scratch = False

    @classmethod
    def setUpClass(cls):
        cls.cmd = get_sam_command()
        cls.integration_dir = cls.get_integ_dir()
        cls.move_test_files_into_scratch_dir()
        cls.test_data_path = cls.integration_dir.joinpath("testdata")
        if cls.template:
            cls.template_path = str(cls.test_data_path.joinpath("invoke", cls.template))
        cls.event_path = str(cls.test_data_path.joinpath("invoke", "event.json"))
        cls.event_utf8_path = str(cls.test_data_path.joinpath("invoke", "event_utf8.json"))
        cls.env_var_path = str(cls.test_data_path.joinpath("invoke", "vars.json"))

    @classmethod
    def move_test_files_into_scratch_dir(cls):
        if cls.moved_to_scratch:
            return
        cls.moved_to_scratch = True
        scratch_dir = Path(__file__).resolve().parent.joinpath(".tmp", str(uuid.uuid4()).replace("-", "")[:10],
                                                               "testdata")
        shutil.rmtree(scratch_dir, ignore_errors=True)
        os.makedirs(scratch_dir)
        copytree(str(Path(cls.integration_dir).joinpath("testdata")), str(scratch_dir))
        cls.integration_dir = str(scratch_dir.parent)

    @staticmethod
    def get_integ_dir():
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def get_command_list(
        function_to_invoke,
        template_path=None,
        event_path=None,
        env_var_path=None,
        parameter_overrides=None,
        region=None,
        no_event=None,
        profile=None,
        layer_cache=None,
        docker_network=None,
        invoke_image=None,
        hook_name=None,
        beta_features=None,
        terraform_plan_file=None,
    ):
        command_list = [get_sam_command(), "local", "invoke", function_to_invoke]

        if template_path:
            command_list = command_list + ["-t", template_path]

        if event_path:
            command_list = command_list + ["-e", event_path]

        if env_var_path:
            command_list = command_list + ["-n", env_var_path]

        if no_event:
            command_list = command_list + ["--no-event"]

        if profile:
            command_list = command_list + ["--profile", profile]

        if layer_cache:
            command_list = command_list + ["--layer-cache-basedir", layer_cache]

        if docker_network:
            command_list = command_list + ["--docker-network", docker_network]

        if parameter_overrides:
            arg_value = " ".join(
                ["ParameterKey={},ParameterValue={}".format(key, value) for key, value in parameter_overrides.items()]
            )
            command_list = command_list + ["--parameter-overrides", arg_value]

        if region:
            command_list = command_list + ["--region", region]

        if invoke_image:
            command_list = command_list + ["--invoke-image", invoke_image]

        if hook_name:
            command_list = command_list + ["--hook-name", hook_name]

        if beta_features is not None:
            command_list = command_list + ["--beta-features" if beta_features else "--no-beta-features"]

        if terraform_plan_file:
            command_list += ["--terraform-plan-file", terraform_plan_file]

        return command_list

    def get_build_command_list(
        self,
        template_path=None,
        cached=None,
        parallel=None,
        use_container=None,
    ):
        command_list = [self.cmd, "build"]

        if template_path:
            command_list = command_list + ["-t", template_path]

        if cached:
            command_list = command_list + ["-c"]

        if parallel:
            command_list = command_list + ["-p"]

        if use_container:
            command_list = command_list + ["-u"]

        return command_list

    def run_command(self, command_list, env=None):
        process = Popen(command_list, stdout=PIPE, env=env)
        try:
            (stdout, stderr) = process.communicate(timeout=TIMEOUT)
            return stdout, stderr, process.returncode
        except TimeoutExpired:
            process.kill()
            raise
