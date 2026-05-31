import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from unittest.mock import patch, MagicMock
from core.auto_updater import lancer_remplacement

_WINDOWS_ONLY = pytest.mark.skipif(
    sys.platform != "win32", reason="Windows uniquement (batch + cmd)"
)


@_WINDOWS_ONLY
def test_lorsque_remplacement_lance_alors_bat_utilise_create_no_window():
    """Lorsque le remplacement est lancé, alors le processus bat est créé avec CREATE_NO_WINDOW."""
    # Given
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        # When
        lancer_remplacement("C:\\Temp\\KaraTool_update.exe", "C:\\App\\KaraTool.exe")
        # Then
        _, kwargs = mock_popen.call_args
        assert kwargs["creationflags"] & subprocess.CREATE_NO_WINDOW
        assert not (kwargs["creationflags"] & subprocess.DETACHED_PROCESS)


@_WINDOWS_ONLY
def test_lorsque_remplacement_lance_alors_handles_non_herites():
    """Lorsque le remplacement est lancé, alors stdin/stdout/stderr sont redirigés vers DEVNULL."""
    # Given
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        # When
        lancer_remplacement("C:\\Temp\\KaraTool_update.exe", "C:\\App\\KaraTool.exe")
        # Then
        _, kwargs = mock_popen.call_args
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["stdout"] == subprocess.DEVNULL
        assert kwargs["stderr"] == subprocess.DEVNULL
