"""`opengonio doctor`: the software survey. No hardware."""
from opengonio import doctor
from opengonio.cli import main


def test_required_software_is_found_and_the_command_exits_zero(capsys):
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "numpy" in out and "OpenCV" in out and "MISSING" not in out


def test_a_missing_required_package_fails_and_a_missing_hardware_package_only_warns():
    base = [doctor.Item("numpy", doctor.REQUIRED, "arrays", True, "2.0")]
    text, code = doctor.report(base + [doctor.Item("OpenCV", doctor.HARDWARE, "camera", False)])
    assert code == 0 and "absent" in text and "opengonio[hw]" in text
    text, code = doctor.report([doctor.Item("numpy", doctor.REQUIRED, "arrays", False)])
    assert code == 1 and "MISSING" in text


def test_opencv_features_match_what_the_code_calls():
    """camera/uvc.py, hdr/merge.py and scan/run.py call these; an OpenCV build without them must be reported."""
    feats = doctor.opencv_features()
    assert set(feats) == {"import", "aruco", "charuco", "hdr_debevec", "video_capture"}
    if feats["import"]:
        assert feats["hdr_debevec"] and feats["video_capture"]
