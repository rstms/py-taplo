# lame and kludgy wrapper for taplo

# https://taplo.tamasfe.dev/

import atexit
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from .config import config_toml


def reaper(pathname):
    Path(pathname).unlink(missing_ok=True)


class Taplo:

    config = None
    taplo = None

    def __init__(self):
        if self.taplo is None:
            self.__class__.taplo = self._run(["which", "taplo"])
            self.version()
        if self.config is None:
            with NamedTemporaryFile(delete=False) as tf:
                tf.write(config_toml.encode())
                self.__class__.config = str(Path(tf.name).resolve())
            atexit.register(reaper, pathname=self.config)
        self.defaults = {
            "colors": "never",
            "config": self.config,
            "no-auto-config": None,
        }
        self.no_config = {"colors": "never"}

    def _run(self, args):
        return subprocess.check_output(args).decode().strip()

    def _cmd(
        self, cmd, input_file=None, *, opts=None, selector=None, **kwargs
    ):
        cmdvec = [self.taplo, cmd]
        if opts is None:
            opts = self.defaults
        opts.update(**kwargs)
        for k, v in opts.items():
            k = "--" + k
            k = k.replace("_", "-")
            if v is None:
                cmdvec.append(k)
            else:
                cmdvec.extend([k, v])
        if input_file is not None:
            if isinstance(input_file, Path):
                input_file = str(input_file.resolve())
            cmdvec.append(input_file)
        if selector is not None:
            cmdvec.append(selector)
        return cmdvec

    def _pipe(self, toml_file, cmd):
        with Path(toml_file).open("r") as ifp:
            proc = subprocess.run(
                cmd, stdin=ifp, capture_output=True, text=True
            )
        if proc.stderr:
            sys.stderr.write(proc.stderr)
            sys.stderr.flush()
        if proc.returncode != 0:
            raise RuntimeError(f"{cmd} exited {proc.returncode}")
        return proc.stdout

    def version(self):
        output = self._run([self.taplo, "--version"])
        m = re.match(r"^taplo\s(\d+\.\d+\.\d+)$", output)
        if not m:
            raise RuntimeError(f"unexpected: {output=}")
        return m.groups()[0]

    def lint(self, toml_file, in_place=True, **kwargs):
        if in_place:
            return self._run(self._cmd("lint", toml_file, **kwargs))
        else:
            return self._pipe(toml_file, self._cmd("lint", "-", **kwargs))

    def fmt(self, toml_file, in_place=True, **kwargs):
        if in_place:
            return self._run(self._cmd("fmt", toml_file, **kwargs))
        else:
            return self._pipe(toml_file, self._cmd("fmt", "-", **kwargs))

    def get(self, toml_file, output_format="value", selector=None):
        cmd = self._cmd(
            "get",
            None,
            opts=self.no_config,
            output_format=output_format,
            selector=selector,
        )
        return self._pipe(toml_file, cmd).strip()

    def json(self, toml_file, selector=None):
        return self.get(toml_file, "json", selector)

    def dict(self, toml_file, selector=None):
        return json.loads(self.get(toml_file, "json", selector))

    def toml(self, toml_file, selector=None):
        return self.get(toml_file, "toml", selector)

    def raw(self, toml_file, selector=None):
        return self.get(toml_file, "value", selector)

    def help(self):
        return self._run(self._cmd("help"))

    def get_config(self):
        return self.dict(self.config)
