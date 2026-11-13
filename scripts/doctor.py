#!/usr/bin/env python3
"""Read-only ROS 2 / Isaac Sim environment inventory (Python 3.8+).

No packages, images, services, or settings are changed. Only --output writes a
file, and its parent directory must already exist. Missing tools and unmet
requirements are reported with exit code 0; invalid arguments/output errors use
nonzero exit codes. Docker connectivity is not a ROS 2 smoke test, and this tool
does not replace NVIDIA's Isaac Sim Compatibility Checker.
"""

import argparse
import csv
import datetime
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


GIB = 1024 ** 3
MIN_DISK_BYTES = 50 * 1000 ** 3  # Published storage reference: 50 GB, decimal.
SUGGESTED_DISK_BYTES = 100 * GIB  # Project recommendation, not a vendor minimum.
TARGET_UBUNTU = "24.04"
COMMAND_TIMEOUT_SECONDS = 8


def run_probe(command, timeout=COMMAND_TIMEOUT_SECONDS):
    """Run a fixed read-only command without exposing stderr or executable paths."""
    if shutil.which(command[0]) is None:
        return {"status": "missing"}
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except (OSError, UnicodeError):
        return {"status": "error"}
    if result.returncode != 0:
        return {"status": "failed", "returncode": result.returncode}
    return {"status": "ok", "stdout": result.stdout.strip()}


def version_probe(command, pattern):
    probe = run_probe(command)
    if probe["status"] != "ok":
        return probe
    match = re.search(pattern, probe["stdout"])
    if match is None:
        return {"status": "unrecognized"}
    return {"status": "ok", "version": match.group(1)}


def collect_os():
    result = {"system": platform.system(), "architecture": platform.machine()}
    if result["system"] != "Linux":
        result["status"] = "unsupported_probe_platform"
        return result
    try:
        content = Path("/etc/os-release").read_text(encoding="utf-8")
        values = {}
        for line in content.splitlines():
            key, separator, value = line.partition("=")
            if separator and key in ("ID", "VERSION_ID"):
                values[key] = value.strip().strip('"\'')
        result.update({
            "status": "ok" if values.get("ID") else "unknown",
            "distribution": values.get("ID"),
            "version": values.get("VERSION_ID"),
        })
    except (OSError, UnicodeError):
        result["status"] = "unknown"
    return result


def collect_ram(system):
    if system != "Linux":
        return {"status": "unsupported_probe_platform"}
    try:
        content = Path("/proc/meminfo").read_text(encoding="ascii")
        match = re.search(r"^MemTotal:\s+(\d+)\s+kB$", content, re.MULTILINE)
        if match:
            total = int(match.group(1)) * 1024
            return {"status": "ok", "total_bytes": total,
                    "total_gib": round(total / GIB, 2)}
    except (OSError, UnicodeError):
        pass
    return {"status": "unknown"}


def collect_disk(path):
    try:
        usage = shutil.disk_usage(path)
        return {"status": "ok", "total_bytes": usage.total,
                "free_bytes": usage.free,
                "total_gib": round(usage.total / GIB, 2),
                "free_gib": round(usage.free / GIB, 2),
                "filesystem_id": os.stat(path).st_dev}
    except OSError:
        return {"status": "unavailable"}


def collect_gpus():
    probe = run_probe([
        "nvidia-smi", "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ])
    if probe["status"] != "ok":
        return probe
    devices = []
    try:
        for row in csv.reader(io.StringIO(probe["stdout"])):
            if len(row) != 3:
                raise ValueError("Unexpected GPU columns")
            name, memory_mib, driver = (value.strip() for value in row)
            devices.append({"name": name, "vram_mib": int(memory_mib),
                            "driver_version": driver})
    except (csv.Error, ValueError):
        return {"status": "unrecognized"}
    return {"status": "ok" if devices else "empty", "devices": devices}


def collect_docker():
    cli = version_probe(["docker", "--version"], r"Docker version ([0-9][\w.+-]*)")
    if cli["status"] == "missing":
        return {"cli": cli, "daemon": {"status": "not_checked"}}
    probe = run_probe(["docker", "info", "--format", "{{json .ServerVersion}}"])
    if probe["status"] != "ok":
        daemon = probe
    else:
        try:
            version = json.loads(probe["stdout"])
            if not isinstance(version, str) or not re.fullmatch(r"[0-9][\w.+-]*", version):
                raise ValueError("Unexpected Docker version")
            daemon = {"status": "ok", "version": version}
        except (ValueError, TypeError):
            daemon = {"status": "unrecognized"}
    return {"cli": cli, "daemon": daemon}


def assess_readiness(report):
    """Keep Docker ROS prerequisites independent from native Isaac requirements."""
    docker = report["docker"]
    docker_ready = docker["daemon"]["status"] == "ok"
    docker_status = "ready_for_smoke_test" if docker_ready else "needs_setup_or_diagnosis"
    docker_notes = [
        "Docker daemon 연결 확인까지만 수행합니다. ROS 2 컨테이너 실행/통신은 별도 검증합니다.",
        "호스트 Ubuntu 버전과 네이티브 ROS 2 설치 여부는 Docker ROS 준비 판정에 사용하지 않습니다.",
    ]
    if not docker_ready:
        docker_notes.append("Docker 설치·실행·현재 사용자의 접근 권한 또는 연결 설정을 확인하세요.")

    system = report["os"]
    os_status = "unknown"
    if system.get("status") == "ok":
        matches = system.get("distribution") == "ubuntu" and system.get("version") == TARGET_UBUNTU
        os_status = "matches_target" if matches else "does_not_match_target"
    elif system.get("system") != "Linux":
        os_status = "does_not_match_target"

    disk = report["disks"]["project"]
    disk_status = "unknown"
    if disk["status"] == "ok":
        if disk["free_bytes"] < MIN_DISK_BYTES:
            disk_status = "below_reference_minimum"
        elif disk["free_bytes"] < SUGGESTED_DISK_BYTES:
            disk_status = "below_project_recommendation"
        else:
            disk_status = "meets_project_recommendation"
    prerequisites_missing = (
        os_status == "does_not_match_target"
        or disk_status == "below_reference_minimum"
    )
    isaac_status = "prerequisites_need_attention" if prerequisites_missing else "requires_compatibility_check"
    return {
        "docker_ros_basics": {"status": docker_status, "notes": docker_notes},
        "isaac_native": {
            "status": isaac_status,
            "target_os": "Ubuntu " + TARGET_UBUNTU,
            "os_check": os_status,
            "project_disk_check": disk_status,
            "reference_minimum_free_bytes": MIN_DISK_BYTES,
            "project_recommended_free_bytes": SUGGESTED_DISK_BYTES,
            "notes": [
                "Ubuntu 24.04는 이 프로젝트의 목표입니다. 다른 OS 전체의 지원 여부를 판정하지 않습니다.",
                "디스크 판정은 프로젝트 위치 기준이며 /mnt 용량과 합산하지 않습니다.",
                "50 GB는 설치 요구사항 참고치, 여유 100 GiB는 캐시·빌드를 위한 프로젝트 권장치입니다.",
                "GPU 이름·VRAM·드라이버 정보만으로 Isaac Sim 지원을 확정하지 않습니다.",
                "Isaac Sim Compatibility Checker 및 선택 버전의 요구사항 확인이 필요합니다.",
            ],
        },
    }


def collect_report(project_dir):
    system = collect_os()
    disks = {"project": collect_disk(project_dir), "mnt": collect_disk(Path("/mnt"))}
    same_filesystem = None
    if all(disk["status"] == "ok" for disk in disks.values()):
        same_filesystem = disks["project"]["filesystem_id"] == disks["mnt"]["filesystem_id"]
    for disk in disks.values():
        disk.pop("filesystem_id", None)
    report = {
        "schema_version": 1,
        "collected_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "os": system,
        "gpu": collect_gpus(),
        "ram": collect_ram(system["system"]),
        "disks": disks,
        "project_and_mnt_same_filesystem": same_filesystem,
        "docker": collect_docker(),
        "native_ros2": {
            "command_available": shutil.which("ros2") is not None,
            "note": "현재 셸 PATH 기준입니다. ROS 설치 후 환경을 source하지 않았다면 발견되지 않을 수 있습니다.",
        },
        "git": version_probe(["git", "--version"], r"git version ([0-9][\w.+-]*)"),
        "python": {"version": platform.python_version()},
    }
    report["readiness"] = assess_readiness(report)
    report["exit_policy"] = "정보 수집 완료는 0입니다. 사양 부족·도구 부재는 실패 종료가 아니며, 인자/출력 오류는 0이 아닙니다."
    return report


def format_text(report):
    system = report["os"]
    lines = ["ROS 2 / Isaac Sim 환경 진단 (읽기 전용)",
             "수집 시각 (UTC): " + report["collected_at_utc"],
             "OS: {} {} {} ({})".format(
                 system["system"], system.get("distribution") or "?",
                 system.get("version") or "?", system["architecture"]),
             "Python: " + report["python"]["version"],
             "Git: " + report["git"].get("version", report["git"]["status"])]
    if system["system"] != "Linux":
        lines.append("이 진단기는 Linux를 기준으로 작성되어 OS 세부 정보와 RAM 확인이 제한됩니다.")
    ram = report["ram"]
    lines.append("RAM: {}".format(str(ram["total_gib"]) + " GiB" if ram["status"] == "ok" else ram["status"]))
    gpu = report["gpu"]
    if gpu["status"] == "ok":
        for index, device in enumerate(gpu["devices"]):
            lines.append("GPU {}: {} / VRAM {} MiB / driver {}".format(
                index, device["name"], device["vram_mib"], device["driver_version"]))
    else:
        lines.append("GPU 조회: " + gpu["status"])
    for label, disk in report["disks"].items():
        if disk["status"] == "ok":
            lines.append("디스크 {}: 여유 {} / 전체 {} GiB".format(label, disk["free_gib"], disk["total_gib"]))
        else:
            lines.append("디스크 {}: {}".format(label, disk["status"]))
    if report["project_and_mnt_same_filesystem"]:
        lines.append("프로젝트와 /mnt는 같은 파일시스템입니다. 여유 공간을 더해서 계산하지 마세요.")
    docker = report["docker"]
    lines.append("Docker CLI: {} / daemon: {}".format(
        docker["cli"].get("version", docker["cli"]["status"]),
        docker["daemon"].get("version", docker["daemon"]["status"])))
    lines.append("현재 셸의 ros2 명령: " + ("발견" if report["native_ros2"]["command_available"] else "미발견"))
    lines.append(report["native_ros2"]["note"])
    for label, result in report["readiness"].items():
        lines.extend(["", label + ": " + result["status"]])
        if label == "isaac_native":
            lines.append("OS: {} / 디스크: {}".format(result["os_check"], result["project_disk_check"]))
        lines.extend("- " + note for note in result["notes"])
    lines.extend(["", "종료 코드: " + report["exit_policy"]])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ROS 2 / Isaac Sim 환경을 읽기 전용으로 점검합니다.",
        epilog="사양 부족·도구 부재에도 수집 완료 시 exit 0. 인자/출력 오류는 nonzero. 자동 설치·삭제·설정 변경 없음.",
    )
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    parser.add_argument("--output", type=Path, help="결과를 지정 파일에 저장 (상위 폴더가 있어야 함, 기존 파일 덮어쓰기)")
    args = parser.parse_args(argv)
    report = collect_report(Path(__file__).resolve().parent.parent)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.json else format_text(report)
    if args.output:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except (OSError, UnicodeError):
            print("진단 결과를 저장하지 못했습니다. 출력 경로와 쓰기 권한을 확인하세요.", file=sys.stderr)
            return 1
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
