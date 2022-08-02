import os
import subprocess as sp
from typing import Dict, List, Optional

from kraken.core import Project, Property, Task, TaskStatus


class CargoTestTask(Task):
    """This task runs `cargo test` using the specified parameters. It will respect the authentication
    credentials configured in :attr:`CargoProjectSettings.auth`."""

    #: Additional arguments to pass to the Cargo command-line.
    additional_args: Property[List[str]] = Property.default_factory(list)

    #: Whether to build incrementally or not.
    incremental: Property[Optional[bool]] = Property.default(None)

    #: Environment variables for the Cargo command.
    env: Property[Dict[str, str]] = Property.default_factory(dict)

    def __init__(self, name: str, project: Project) -> None:
        super().__init__(name, project)

    def get_cargo_command(self, env: Dict[str, str]) -> List[str]:
        incremental = self.incremental.get()
        if incremental is not None:
            env["CARGO_INCREMENTAL"] = "1" if incremental else "0"

        return ["cargo", "test"] + self.additional_args.get()

    def make_safe(self, args: List[str], env: Dict[str, str]) -> None:
        pass

    def execute(self) -> TaskStatus:
        env = self.env.get()
        command = self.get_cargo_command(env)

        safe_command = command[:]
        safe_env = env.copy()
        self.make_safe(safe_command, safe_env)
        self.logger.info("%s [env: %s]", safe_command, safe_env)

        result = sp.call(command, cwd=self.project.directory, env={**os.environ, **env})
        return TaskStatus.from_exit_code(safe_command, result)
