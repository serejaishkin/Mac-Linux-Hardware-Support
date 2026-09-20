from maclinux.build import execute_build, plan_build
from maclinux.platform import detect_platform


def test_build_is_dry_run_by_default():
    info = detect_platform({
        "ID": "ubuntu",
        "VERSION_ID": "24.04",
        "VERSION_CODENAME": "noble",
    })
    plan = plan_build("unknown-driver", info)
    result = execute_build(plan)
    assert result["status"] == "dry-run"
    assert result["executed"] is False


def test_unknown_driver_is_blocked():
    info = detect_platform({
        "ID": "ubuntu",
        "VERSION_ID": "24.04",
    })
    plan = plan_build("unknown-driver", info)
    assert plan.status == "unknown"
    assert "no build recipe" in plan.blockers
