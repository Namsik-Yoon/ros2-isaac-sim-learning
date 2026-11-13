"""Decision and failure-path checks; no ROS, Docker daemon, or GPU required."""

import importlib.util
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "doctor", Path(__file__).resolve().parent.parent / "scripts" / "doctor.py")
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


def report(os_version="24.04", free_bytes=120 * doctor.GIB, daemon="ok"):
    return {
        "os": {"system": "Linux", "status": "ok", "distribution": "ubuntu", "version": os_version},
        "docker": {"cli": {"status": "ok"}, "daemon": {"status": daemon}},
        "disks": {"project": {"status": "ok", "free_bytes": free_bytes}},
    }


class ReadinessTests(unittest.TestCase):
    def test_older_host_does_not_block_docker_ros(self):
        actual = doctor.assess_readiness(report(os_version="20.04"))
        self.assertEqual(actual["docker_ros_basics"]["status"], "ready_for_smoke_test")
        self.assertEqual(actual["isaac_native"]["os_check"], "does_not_match_target")

    def test_low_disk_is_separate_from_docker_readiness(self):
        actual = doctor.assess_readiness(report(free_bytes=18 * doctor.GIB))
        self.assertEqual(actual["docker_ros_basics"]["status"], "ready_for_smoke_test")
        self.assertEqual(actual["isaac_native"]["project_disk_check"], "below_reference_minimum")

    def test_minimum_and_recommendation_are_distinct(self):
        for free_bytes, expected in [
            (doctor.MIN_DISK_BYTES - 1, "below_reference_minimum"),
            (doctor.MIN_DISK_BYTES, "below_project_recommendation"),
            (doctor.SUGGESTED_DISK_BYTES, "meets_project_recommendation"),
        ]:
            with self.subTest(free_bytes=free_bytes):
                actual = doctor.assess_readiness(report(free_bytes=free_bytes))
                self.assertEqual(actual["isaac_native"]["project_disk_check"], expected)

    def test_basic_checks_never_claim_isaac_compatibility(self):
        actual = doctor.assess_readiness(report())
        self.assertEqual(actual["isaac_native"]["status"], "requires_compatibility_check")

    def test_unreachable_docker_needs_diagnosis(self):
        actual = doctor.assess_readiness(report(daemon="timeout"))
        self.assertEqual(actual["docker_ros_basics"]["status"], "needs_setup_or_diagnosis")

    def test_missing_disk_remains_unknown(self):
        fixture = report()
        fixture["disks"]["project"] = {"status": "unavailable"}
        actual = doctor.assess_readiness(fixture)
        self.assertEqual(actual["isaac_native"]["project_disk_check"], "unknown")


class ProbeTests(unittest.TestCase):
    @patch.object(doctor.shutil, "which", return_value=None)
    def test_missing_tool_is_graceful(self, _which):
        self.assertEqual(doctor.run_probe(["nvidia-smi"]), {"status": "missing"})

    @patch.object(doctor.shutil, "which", return_value="/mock/tool")
    @patch.object(doctor.subprocess, "run", side_effect=subprocess.TimeoutExpired("docker", 8))
    def test_timed_out_tool_is_graceful(self, _run, _which):
        self.assertEqual(doctor.run_probe(["docker", "info"]), {"status": "timeout"})

    @patch.object(doctor.shutil, "which", return_value="/mock/tool")
    @patch.object(doctor.subprocess, "run", return_value=subprocess.CompletedProcess(
        args=["docker"], returncode=1, stdout="", stderr="private user and daemon details"))
    def test_failure_does_not_expose_stderr(self, _run, _which):
        self.assertEqual(doctor.run_probe(["docker", "info"]), {"status": "failed", "returncode": 1})

    @patch.object(doctor, "run_probe", return_value={
        "status": "ok", "stdout": "Example GPU, 24576, 555.42.02\nSecond GPU, 16384, 555.42.02"})
    def test_multiple_gpus_are_parsed_without_support_claims(self, _probe):
        actual = doctor.collect_gpus()
        self.assertEqual(len(actual["devices"]), 2)
        self.assertEqual(actual["devices"][0]["vram_mib"], 24576)
        self.assertNotIn("supported", actual)

    @patch.object(doctor, "run_probe", return_value={"status": "ok", "stdout": "GPU, N/A, 555.42.02"})
    def test_unexpected_gpu_memory_is_graceful(self, _probe):
        self.assertEqual(doctor.collect_gpus(), {"status": "unrecognized"})


class CliTests(unittest.TestCase):
    @patch.object(doctor, "collect_report", return_value={"collected": True})
    def test_json_defaults_to_stdout(self, _collect):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), patch.object(doctor.Path, "write_text") as write:
            result = doctor.main(["--json"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue()), {"collected": True})
        write.assert_not_called()

    @patch.object(doctor, "collect_report", return_value={"collected": True})
    def test_explicit_output_saves_json(self, _collect):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "report.json"
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                result = doctor.main(["--json", "--output", str(destination)])
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(destination.read_text()), {"collected": True})
            self.assertEqual(stdout.getvalue(), "")

    @patch.object(doctor, "collect_report", return_value={"collected": True})
    def test_output_error_is_nonzero_and_does_not_create_parent(self, _collect):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder) / "absent"
            with contextlib.redirect_stderr(io.StringIO()):
                result = doctor.main(["--json", "--output", str(parent / "report.json")])
            self.assertEqual(result, 1)
            self.assertFalse(parent.exists())


if __name__ == "__main__":
    unittest.main()
