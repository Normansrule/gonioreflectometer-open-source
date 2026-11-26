"""The OpenCV code paths (camera frames, HDR merge, ChArUco calibration, image files) on synthetic images.

Skipped when OpenCV is not installed (`pip install "opengonio[hw]"`). No camera and no machine: these check that the
calls the project makes exist in the installed OpenCV and return what the rest of the code assumes.
"""
import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from opengonio import imageio  # noqa: E402
from opengonio.doctor import opencv_features  # noqa: E402
from opengonio.hdr.merge import exposure_ladder, merge, recover_response  # noqa: E402


def test_the_installed_opencv_has_every_part_the_code_calls():
    assert all(opencv_features().values()), opencv_features()


def test_hdr_merge_recovers_linear_radiance_from_gamma_encoded_frames():
    """Frames like a webcam gives (8 bit, gamma 2.2, clipped); the merge must undo the gamma (hdr/merge.py)."""
    rng = np.random.default_rng(5)
    radiance = np.exp(rng.uniform(np.log(0.02), np.log(20.0), size=(48, 64))).astype(np.float64)   # 1000:1 scene
    times = exposure_ladder(8.0, stops=7, step_ev=1.5)
    frames = []
    for t in times:
        v = np.clip(radiance * t / 1000.0 * 60.0, 0, 1) ** (1 / 2.2)
        frames.append(np.repeat((v * 255).round().astype(np.uint8)[:, :, None], 3, axis=2))
    response = recover_response(frames, times)
    assert response.shape == (256, 1, 3)
    hdr = merge(frames, times, response)[:, :, 0].astype(np.float64)
    ok = (hdr > 0) & np.isfinite(hdr)
    assert ok.mean() > 0.98
    slope = np.polyfit(np.log(radiance[ok]), np.log(hdr[ok]), 1)[0]
    assert slope == pytest.approx(1.0, abs=0.08)             # linear in radiance, not gamma 0.45
    ratio = hdr[ok] / radiance[ok]
    assert np.std(np.log(ratio)) < 0.15                      # one scale factor over the whole range


def test_charuco_board_is_found_and_calibrates_a_camera():
    """The call sequence of scan/run.py calibrate_scan(), on rendered views of the same 7 x 5 board."""
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    board = cv2.aruco.CharucoBoard((7, 5), 10.0, 7.0, d)
    det = cv2.aruco.CharucoDetector(board)
    flat = board.generateImage((700, 500), marginSize=20)
    W, H, f = 960, 720, 900.0
    K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1.0]])
    corners = np.array([[0, 0, 0], [70, 0, 0], [70, 50, 0], [0, 50, 0]], dtype=np.float64)      # board outline, mm
    src = np.array([[20, 20], [680, 20], [680, 480], [20, 480]], dtype=np.float32)              # same outline in `flat`
    obj_pts, img_pts = [], []
    for rx, ry, rz, tz in ((0.0, 0.0, 0.0, 130), (0.45, 0.0, 0.1, 140), (-0.4, 0.2, -0.1, 140), (0.1, 0.5, 0.2, 150),
                           (0.2, -0.5, 0.0, 150), (0.5, 0.4, -0.3, 160), (-0.3, -0.4, 0.3, 135), (0.35, -0.2, 0.5, 145)):
        R = cv2.Rodrigues(np.array([rx, ry, rz]))[0]
        t = np.array([-35.0, -25.0, tz]) - R @ np.array([35.0, 25.0, 0.0]) + np.array([35.0, 25.0, 0.0])
        cam = (R @ corners.T).T + t
        px = (K @ cam.T).T
        dst = (px[:, :2] / px[:, 2:]).astype(np.float32)
        view = cv2.warpPerspective(flat, cv2.getPerspectiveTransform(src, dst), (W, H), borderValue=255)
        cc, ids, _, _ = det.detectBoard(view)
        if ids is None or len(ids) < 6:
            continue
        o, i = board.matchImagePoints(cc, ids)
        obj_pts.append(o); img_pts.append(i)
    assert len(obj_pts) >= 6
    rms, Kc, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, (W, H), None, None)
    assert rms < 1.0 and len(rvecs) == len(obj_pts)
    assert Kc[0, 0] == pytest.approx(f, rel=0.05) and Kc[1, 1] == pytest.approx(f, rel=0.05)
    assert cv2.Rodrigues(rvecs[0])[0].shape == (3, 3)


def test_image_files_keep_rgb_order_through_opencv(tmp_path):
    """Camera frames are RGB everywhere in the project; OpenCV files are BGR. A red pixel must come back red."""
    img = np.zeros((6, 8, 3), np.uint8)
    img[:, :, 0] = 200; img[2, 3] = (10, 120, 250)
    for name in ("a.png", "a.tif"):
        assert imageio.save_image(tmp_path / name, img)
        back = imageio.default_reader()(tmp_path / name)
        assert back.shape == img.shape and np.array_equal(back, img)
    grey = (np.arange(48, dtype=np.uint8) * 5).reshape(6, 8)
    assert imageio.save_image(tmp_path / "g.png", grey)
    assert np.array_equal(imageio.default_reader()(tmp_path / "g.png"), grey)
