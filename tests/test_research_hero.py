from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parent.parent
SCRIPT = REPOSITORY / "scripts" / "research-hero"
PROFILE = REPOSITORY / "profiles" / "RESEARCH.md"
BEGIN_PREFIX = "<!-- RESEARCH-HERO:BEGIN"
END_MARKER = "<!-- RESEARCH-HERO:END -->"


def profile_block() -> str:
    text = PROFILE.read_text(encoding="utf-8")
    start = text.index(BEGIN_PREFIX)
    end = text.index(END_MARKER, start) + len(END_MARKER)
    return text[start:end]


class ResearchHeroTests(unittest.TestCase):
    def run_script(
        self, command: str, project: Path, expected_returncode: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(SCRIPT), command, str(project)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            expected_returncode,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        return result

    def test_install_into_empty_project_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.run_script("install", project)
            self.assertEqual(
                (project / "AGENTS.md").read_text(encoding="utf-8"),
                profile_block() + "\n",
            )
            self.run_script("check", project)

    def test_install_prepends_and_preserves_existing_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            original = "# Existing instructions\n\nKeep this byte-for-byte.\n"
            (project / "AGENTS.md").write_text(original, encoding="utf-8")
            self.run_script("install", project)
            installed = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(installed, profile_block() + "\n\n" + original)

    def test_repeated_install_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            first = self.run_script("install", project)
            content = (project / "AGENTS.md").read_bytes()
            second = self.run_script("install", project)
            self.assertIn("installed:", first.stdout)
            self.assertIn("unchanged:", second.stdout)
            self.assertEqual((project / "AGENTS.md").read_bytes(), content)

    def test_update_replaces_old_block_and_preserves_project_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            project_text = "# Project-specific rules\n"
            old = (
                "<!-- RESEARCH-HERO:BEGIN version=0.0.1 -->\n"
                "old rules\n"
                "<!-- RESEARCH-HERO:END -->\n\n"
                + project_text
            )
            (project / "AGENTS.md").write_text(old, encoding="utf-8")
            result = self.run_script("update", project)
            self.assertIn("updated:", result.stdout)
            self.assertEqual(
                (project / "AGENTS.md").read_text(encoding="utf-8"),
                profile_block() + "\n\n" + project_text,
            )

    def test_check_reports_missing_or_outdated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.run_script("check", project, expected_returncode=1)
            (project / "AGENTS.md").write_text(
                "<!-- RESEARCH-HERO:BEGIN version=0.0.1 -->\n"
                "old\n"
                "<!-- RESEARCH-HERO:END -->\n",
                encoding="utf-8",
            )
            self.run_script("check", project, expected_returncode=1)

    def test_malformed_markers_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            malformed = "<!-- RESEARCH-HERO:BEGIN version=broken -->\nkeep me\n"
            agents = project / "AGENTS.md"
            agents.write_text(malformed, encoding="utf-8")
            self.run_script("install", project, expected_returncode=2)
            self.assertEqual(agents.read_text(encoding="utf-8"), malformed)

    def test_remove_restores_existing_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            original = "# Existing instructions\n"
            (project / "AGENTS.md").write_text(original, encoding="utf-8")
            self.run_script("install", project)
            self.run_script("remove", project)
            self.assertEqual(
                (project / "AGENTS.md").read_text(encoding="utf-8"), original
            )

    def test_remove_from_new_file_leaves_empty_agents_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.run_script("install", project)
            self.run_script("remove", project)
            self.assertEqual((project / "AGENTS.md").read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
