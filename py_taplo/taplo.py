# lame and kludgy wrapper for taplo

# https://taplo.tamasfe.dev/

import atexit
import json
import os
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from .config import config_toml


def reaper(pathname):
    os.unlink(pathname)


class Taplo:

    config = None
    taplo = None

    def __init__(self):
        if self.taplo is None:
            self.__class__.taplo = self.run("which", "taplo")
            self.version()
        if self.config is None:
            with NamedTemporaryFile(delete=False) as tf:
                tf.write(config_toml)
                self.__class__.config = str(Path(tf.name).resolve())
        atexit.register(reaper, pathname=self.config)
        self.defaults = {
            "colors": "never",
            "config": self.config,
            "no-auto-config": None,
        }
        self.no_config = {"colors": "never"}

    def _run(self, *args):
        return subprocess.check_output(list(args)).decode().strip()

    def version(self):
        output = self.run(self.taplo, "--version")
        m = re.match(r"^taplo\s(\d+\.\d+\.\d+)$")
        if not m:
            raise RuntimeError(f"unexpected: {output=}")
        return m.groups()[0]

    def _cmd(
        self, cmd, input_file=None, *, opts=None, selector=None, **kwargs
    ):
        cmdvec = [self.taplo, cmd]
        if opts is None:
            opts = self.defaults
        opts.update(**kwargs)
        for k, v in opts.items():
            k = "--" + k
            if v is None:
                cmdvec.append(k)
            else:
                cmdvec.extend([k, v])
        if input_file is not None:
            if input_file != "-":
                input_file = str(input_file.resolve())
            cmdvec.append(input_file)
        if selector is not None:
            cmdvec.append(selector)
        return cmdvec

    def _pipe(self, toml_file, cmd):
        with Path(toml_file).open("r") as ifp:
            proc = subprocess.run(
                cmd, input=ifp, capture_output=True, check=True, text=True
            )
        if proc.stderr:
            raise RuntimeError(proc.stderr)
        return proc.stdout

    def lint(self, toml_file):
        return self.run(self._cmd("lint", toml_file))

    def fmt(self, toml_file, in_place=True):
        if in_place:
            return self.run(self._cmd("fmt", toml_file))
        else:
            return self._pipe(toml_file, self._cmd("fmt", "-"))

    def get(self, toml_file, output_format="value", selector=None):
        cmd = self._cmd(
            "get",
            None,
            opts=self.no_config,
            output_format=output_format,
            selector=selector,
        )
        return self._pipe(toml_file, cmd)

    def json(self, toml_file, selector=None):
        return self.get(toml_file, "json", selector)

    def dict(self, toml_file, selector=None):
        return json.loads(self.get(toml_file, "json", selector))

    def toml(self, toml_file, selector=None):
        return self.get(toml_file, "toml", selector)

    def help(self):
        return self.run(self._cmd("help"))

    def get_config(self):
        return self.dict(self.config)
