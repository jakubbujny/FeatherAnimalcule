#!/usr/bin/env python3
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

REQ_LIBS = REPO_ROOT / "circuitpython-requirements.txt"
REQ_BUNDLE_DEVICE = REPO_ROOT / "circuitpython-requirements-bundle.txt"          # .mpy bundle URL
REQ_BUNDLE_IDE = REPO_ROOT / "circuitpython-requirements-bundle-ide.txt"         # .py bundle URL

SRC_DIR = REPO_ROOT / "src"
DEFAULT_MOUNT = Path("/Volumes/CIRCUITPY")

CACHE_DIR = REPO_ROOT / ".cache" / "circuitpython"
BUNDLES_DIR = CACHE_DIR / "bundles"


def read_first_nonempty_line(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    raise ValueError(f"No usable lines found in: {path}")


def read_requirements(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    if not out:
        raise ValueError(f"No libraries listed in: {path}")
    return out


def detect_mountpoint() -> Path:
    env = os.environ.get("CPY_MOUNT")
    if env:
        p = Path(env)
        if p.exists():
            return p
        raise FileNotFoundError(f"CPY_MOUNT set but not found: {p}")

    if DEFAULT_MOUNT.exists():
        return DEFAULT_MOUNT

    volumes = Path("/Volumes")
    if volumes.exists():
        for p in volumes.iterdir():
            if p.is_dir() and p.name.upper().startswith("CIRCUITPY"):
                return p

    raise FileNotFoundError(
        "Could not find CIRCUITPY mount. Set CPY_MOUNT env var to the mount path."
    )


def url_cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def download_if_needed(url: str, dest_zip: Path) -> None:
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    if dest_zip.exists() and dest_zip.stat().st_size > 0:
        return  # cached
    print(f"Downloading bundle:\n  {url}\n-> {dest_zip}")
    with urllib.request.urlopen(url) as resp, open(dest_zip, "wb") as f:
        shutil.copyfileobj(resp, f)
    if dest_zip.stat().st_size == 0:
        raise RuntimeError("Downloaded zip is empty")


def extract_if_needed(zip_path: Path, extract_dir: Path) -> None:
    marker = extract_dir / ".extracted_ok"
    if marker.exists():
        return
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting bundle (cached):\n  {zip_path}\n-> {extract_dir}")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)
    marker.write_text("ok", encoding="utf-8")


def find_bundle_lib_dir(extract_dir: Path) -> Path:
    # common layout: lib/ at root
    direct = extract_dir / "lib"
    if direct.is_dir():
        return direct

    # or top-level folder containing lib/
    for child in extract_dir.iterdir():
        if child.is_dir():
            cand = child / "lib"
            if cand.is_dir():
                return cand

    # fallback: any lib folder
    for p in extract_dir.rglob("lib"):
        if p.is_dir():
            return p

    raise FileNotFoundError(f"Could not find 'lib' directory inside extracted bundle: {extract_dir}")


def copy_lib_item(bundle_lib: Path, name: str, dest_lib: Path) -> None:
    candidates = [
        bundle_lib / f"{name}.mpy",
        bundle_lib / f"{name}.py",
        bundle_lib / name,  # package dir
    ]

    src: Optional[Path] = None
    for c in candidates:
        if c.exists():
            src = c
            break

    if src is None:
        raise FileNotFoundError(f"Library '{name}' not found in bundle lib/ ({bundle_lib})")

    dest_lib.mkdir(parents=True, exist_ok=True)

    if src.is_dir():
        dst = dest_lib / src.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Installed dir:  {name}")
    else:
        shutil.copy2(src, dest_lib / src.name)
        print(f"Installed file: {src.name}")


def rsync_code(src: Path, mount: Path) -> None:
    if not src.exists():
        print(f"Skipping code sync: {src} not found")
        return

    cmd = [
        "rsync", "-av", "--delete",
        "--exclude", "lib/***",          # circpython deps live on board lib/
        "--exclude", "sd/***",           # keep SD mount-point directory on board
        "--exclude", "sd",
        "--exclude", "__pycache__",
        "--exclude", "boot_out.txt",     # keep device-generated file
        "--exclude", ".DS_Store",
        "--exclude", "._*",
        "--exclude", ".Trashes",
        "--exclude", ".Spotlight-V100",
        "--exclude", ".fseventsd",
        str(src) + "/",
        str(mount) + "/",
        ]
    print("Syncing code:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ensure_sd_mount_dir(mount: Path, mount_dir_name: str = "sd") -> Path:
    """
    Ensure the SD mount-point directory exists on the board filesystem.

    CircuitPython requires the mount-point directory (e.g. '/sd') to exist
    before calling storage.mount(..., '/sd').
    """
    p = mount / mount_dir_name
    if p.is_dir():
        return p
    if p.exists():
        raise RuntimeError(f"Expected SD mount-point to be a directory but found a file: {p}")
    p.mkdir(parents=False, exist_ok=True)
    print(f"Created SD mount-point directory: {p}")
    return p


def prepare_bundle(url: str) -> tuple[Path, Path]:
    """
    Returns: (zip_path, extracted_lib_dir)
    """
    key = url_cache_key(url)
    zip_path = BUNDLES_DIR / key / Path(url).name
    extract_dir = BUNDLES_DIR / key / "extracted"

    download_if_needed(url, zip_path)
    extract_if_needed(zip_path, extract_dir)
    lib_dir = find_bundle_lib_dir(extract_dir)
    return zip_path, lib_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deploy CircuitPython code (and optionally libraries) to a mounted CIRCUITPY device.")
    p.add_argument(
        "--mount",
        type=Path,
        default=None,
        help="CIRCUITPY mount path (overrides auto-detect and CPY_MOUNT env var).",
    )
    p.add_argument(
        "--sync-lib",
        action="store_true",
        help="Also install libraries to /lib from the configured CircuitPython bundle.",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    mount = args.mount if args.mount is not None else detect_mountpoint()
    print(f"\nBoard mount:      {mount}")

    # Ensure SD mount-point directory exists (e.g. '/sd' on the board)
    ensure_sd_mount_dir(mount, "sd")

    # Sync your code without touching lib/ (default behavior)
    rsync_code(SRC_DIR, mount)

    # Ensure SD mount-point directory exists *after* rsync (rsync --delete might otherwise remove it)
    ensure_sd_mount_dir(mount, "sd")

    if args.sync_lib:
        libs = read_requirements(REQ_LIBS)
        device_url = read_first_nonempty_line(REQ_BUNDLE_DEVICE)
        ide_url = read_first_nonempty_line(REQ_BUNDLE_IDE)

        # Prepare both bundles (cached download + cached extraction)
        device_zip, device_lib = prepare_bundle(device_url)  # .mpy bundle used for install to board
        ide_zip, ide_lib = prepare_bundle(ide_url)           # .py bundle used for IDE indexing

        dest_lib = mount / "lib"

        print(f"\nDevice bundle zip:{device_zip}")
        print(f"Device bundle lib:{device_lib}")
        print(f"IDE bundle zip:   {ide_zip}")
        print(f"IDE bundle lib:   {ide_lib}")
        print("\n👉 IntelliJ: add this folder as Library/Sources so imports resolve:")
        print(f"   {ide_lib}\n")

        # Install requested libs onto the board from the DEVICE bundle
        for name in libs:
            copy_lib_item(device_lib, name, dest_lib)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: command failed with exit code {e.returncode}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        raise
