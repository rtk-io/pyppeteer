#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'Chromium dowload module.'
from io import BytesIO
import logging
import os
from pathlib import Path, PosixPath
import stat
import sys
import platform
from urllib import request
from zipfile import ZipFile
from pyppeteer import __chromimum_revision__ as REVISION

logger = logging.getLogger(__name__)

CHROMIUM_EXECUTABLE_ARM64 = PosixPath('chromium-browser')
PLATFORM_ARM64 = 'aarch64'

DOWNLOADS_FOLDER = ((Path.home() / '.pyppeteer') / 'local-chromium')
DEFAULT_DOWNLOAD_HOST = 'https://storage.googleapis.com'
DOWNLOAD_HOST = os.environ.get(
    'PYPPETEER_DOWNLOAD_HOST', DEFAULT_DOWNLOAD_HOST)
BASE_URL = ''.join(['{}'.format(DOWNLOAD_HOST), '/chromium-browser-snapshots'])
downloadURLs = {
    'linux': ''.join(['{}'.format(BASE_URL), '/Linux_x64/', '{}'.format(REVISION), '/chrome-linux.zip']),
    'mac': ''.join(['{}'.format(BASE_URL), '/Mac/', '{}'.format(REVISION), '/chrome-mac.zip']),
    'win32': ''.join(['{}'.format(BASE_URL), '/Win/', '{}'.format(REVISION), '/chrome-win32.zip']),
    'win64': ''.join(['{}'.format(BASE_URL), '/Win_x64/', '{}'.format(REVISION), '/chrome-win32.zip']),
}
chromiumExecutable = {
    'linux': DOWNLOADS_FOLDER / REVISION / 'chrome-linux' / 'chrome',,
    'mac': ((((((DOWNLOADS_FOLDER / REVISION) / 'chrome-mac') / 'Chromium.app') / 'Contents') / 'MacOS') / 'Chromium'),
    'win32': (((DOWNLOADS_FOLDER / REVISION) / 'chrome-win32') / 'chrome.exe'),
    'win64': (((DOWNLOADS_FOLDER / REVISION) / 'chrome-win32') / 'chrome.exe'),
    'arm64': CHROMIUM_EXECUTABLE_ARM64,
}


def current_platform() -> str:
    'Get current platform name by short string.'
    if sys.platform.startswith('linux'):
        if platform.processor() == PLATFORM_ARM64:
            return 'arm64'
        return 'linux'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    elif sys.platform.startswith('win'):
        if (sys.maxsize > ((2 ** 31) - 1)):
            return 'win64'
        return 'win32'
    raise OSError(('Unsupported platform: ' + sys.platform))


def get_url() -> str:
    'Get chromium download url.'
    return downloadURLs[current_platform()]


def download_zip(url: str) -> bytes:
    'Download data from url.'
    logger.warning(
        'start chromium download.\nDownload may take a few minutes.')
    with request.urlopen(url) as f:
        data = f.read()
    logger.warning('chromium download done.')
    return data


def extract_zip(data: bytes, path: Path) -> None:
    'Extract zipped data to path.'
    if (current_platform() == 'mac'):
        import subprocess
        import shutil
        zip_path = (path / 'chrome.zip')
        if (not path.exists()):
            path.mkdir(parents=True)
        with zip_path.open('wb') as f:
            f.write(data)
        if (not shutil.which('unzip')):
            raise OSError(''.join(
                ['Failed to automatically extract chrome.zip.Please unzip ', '{}'.format(zip_path), ' manually.']))
        subprocess.run(['unzip', str(zip_path)], cwd=str(path))
        if (chromium_excutable().exists() and zip_path.exists()):
            zip_path.unlink()
    else:
        with ZipFile(BytesIO(data)) as zf:
            zf.extractall(str(path))
    exec_path = chromium_excutable()
    if (not exec_path.exists()):
        raise IOError('Failed to extract chromium.')
    exec_path.chmod(
        (((exec_path.stat().st_mode | stat.S_IXOTH) | stat.S_IXGRP) | stat.S_IXUSR))
    logger.warning(''.join(['chromium extracted to: ', '{}'.format(path)]))


def download_chromium() -> None:
    'Downlaod and extract chrmoium.'
    extract_zip(download_zip(get_url()), (DOWNLOADS_FOLDER / REVISION))


def chromium_excutable() -> Path:
    'Get path of the chromium executable.'
    return chromiumExecutable[current_platform()]


def check_chromium() -> bool:
    'Check if chromium is placed at correct path.'
    if current_platform() == 'arm64':
        return True
    return chromium_excutable().exists()
