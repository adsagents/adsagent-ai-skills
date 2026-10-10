from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "cloud-agent-setup.sh"
BASH = shutil.which("bash")


class CloudAgentSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="skill-pack-setup-")
        self.addCleanup(self.temp.cleanup)
        self.scratch = Path(self.temp.name)
        self.bin = self.scratch / "bin"
        self.bin.mkdir()
        self.home = self.scratch / "home"
        self.home.mkdir()
        self.calls = self.scratch / "calls.txt"
        self.env = {
            "PATH": str(self.bin),
            "HOME": str(self.home),
            "CLOUD_SETUP_CALL_LOG": str(self.calls),
        }

    def _provide_uv(self, exit_code: int = 0) -> None:
        uv = self.bin / "uv"
        uv.write_text(
            f"#!{BASH}\n"
            'printf "%s\\n" "$PWD" "$@" > "$CLOUD_SETUP_CALL_LOG"\n'
            f"exit {exit_code}\n",
            encoding="utf-8",
        )
        uv.chmod(0o755)

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [BASH, str(SETUP), *args],
            cwd=self.scratch,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_existing_uv_prepares_only_pinned_validation_tools(self) -> None:
        self._provide_uv()
        repo = self.scratch / "checkout with spaces"
        repo.mkdir()

        result = self._run(str(repo))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.calls.read_text(encoding="utf-8").splitlines(),
            [
                str(repo), "run", "--no-project", "--managed-python",
                "--python", "3.12", "--with", "pytest==9.0.2",
                "python", "-m", "pytest", "--version",
            ],
        )
        self.assertEqual(list(repo.iterdir()), [])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_default_root_is_independent_of_callers_working_directory(self) -> None:
        self._provide_uv()
        (self.bin / "dirname").symlink_to(shutil.which("dirname"))

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text().splitlines()[0], str(ROOT))

    def test_missing_uv_fails_without_downloading_an_installer(self) -> None:
        result = self._run(str(ROOT))

        self.assertEqual(result.returncode, 127)
        self.assertIn("provision it in the cloud image", result.stderr)
        self.assertFalse(self.calls.exists())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_package_manager_failure_is_propagated(self) -> None:
        self._provide_uv(exit_code=23)

        result = self._run(str(ROOT))

        self.assertEqual(result.returncode, 23)
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
