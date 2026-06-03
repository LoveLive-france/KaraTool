import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch
from core.download_manager import build_ydl_opts, get_ffmpeg_path, DownloadManager


# --- get_ffmpeg_path ---


def test_lorsque_app_non_congelee_alors_retourne_cwd():
    """Lorsque l'app tourne en mode développement, alors get_ffmpeg_path retourne le répertoire courant."""
    # Given / When
    resultat = get_ffmpeg_path()
    # Then
    assert resultat == os.getcwd()


def test_lorsque_app_congelee_alors_retourne_meipass():
    """Lorsque l'app tourne en mode PyInstaller, alors get_ffmpeg_path retourne sys._MEIPASS."""
    # Given
    with patch.object(sys, "frozen", True, create=True):
        with patch.object(sys, "_MEIPASS", "/chemin/meipass", create=True):
            # When
            resultat = get_ffmpeg_path()
    # Then
    assert resultat == "/chemin/meipass"


# --- build_ydl_opts ---


def test_lorsque_format_video_alors_merge_output_format_est_mp4():
    """Lorsque le format est Vidéo, alors merge_output_format vaut mp4."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Vidéo", "/tmp")
    # Then
    assert options["merge_output_format"] == "mp4"


def test_lorsque_format_audio_alors_postprocessor_ffmpeg_extract_audio_present():
    """Lorsque le format est Audio, alors le postprocessor FFmpegExtractAudio est présent."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Audio", "/tmp")
    # Then
    cles_postprocessors = [p["key"] for p in options["postprocessors"]]
    assert "FFmpegExtractAudio" in cles_postprocessors


def test_lorsque_format_audio_alors_preferred_codec_est_mp3():
    """Lorsque le format est Audio, alors le codec préféré est mp3."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Audio", "/tmp")
    # Then
    postprocessor = next(
        p for p in options["postprocessors"] if p["key"] == "FFmpegExtractAudio"
    )
    assert postprocessor["preferredcodec"] == "mp3"


def test_lorsque_cookies_file_fourni_alors_cookiefile_present_dans_options():
    """Lorsque un fichier cookies est fourni, alors cookiefile est présent dans les options."""
    # Given / When
    options = build_ydl_opts(
        "https://example.com", "Audio", "/tmp", cookies_file="/cookies.txt"
    )
    # Then
    assert options["cookiefile"] == "/cookies.txt"


def test_lorsque_cookies_file_absent_alors_cookiefile_absent_des_options():
    """Lorsque aucun fichier cookies n'est fourni, alors cookiefile est absent des options."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Audio", "/tmp")
    # Then
    assert "cookiefile" not in options


def test_lorsque_rappel_progression_fourni_alors_progress_hooks_contient_rappel():
    """Lorsque un rappel de progression est fourni, alors progress_hooks contient ce rappel."""

    # Given
    def rappel(info):
        pass

    # When
    options = build_ydl_opts(
        "https://example.com", "Audio", "/tmp", rappel_progression=rappel
    )
    # Then
    assert rappel in options["progress_hooks"]


def test_lorsque_rappel_progression_absent_alors_progress_hooks_absent_des_options():
    """Lorsque aucun rappel de progression n'est fourni, alors progress_hooks est absent des options."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Audio", "/tmp")
    # Then
    assert "progress_hooks" not in options


def test_lorsque_dossier_destination_fourni_alors_outtmpl_contient_ce_dossier():
    """Lorsque un dossier destination est fourni, alors outtmpl commence par ce dossier."""
    # Given / When
    options = build_ydl_opts("https://example.com", "Audio", "/mon/dossier")
    # Then
    assert options["outtmpl"].startswith("/mon/dossier")


# --- DownloadManager.add ---


def test_lorsque_premier_ajout_alors_identifiant_est_zero():
    """Lorsque le premier item est ajouté, alors son identifiant est 0."""
    # Given
    manager = DownloadManager(on_update=lambda *_: None)
    # When
    identifiant = manager.add("https://example.com", "Audio")
    # Then
    assert identifiant == 0


def test_lorsque_deux_ajouts_alors_identifiants_sont_sequentiels():
    """Lorsque deux items sont ajoutés, alors leurs identifiants sont 0 et 1."""
    # Given
    manager = DownloadManager(on_update=lambda *_: None)
    # When
    premier = manager.add("https://example.com/a", "Audio")
    deuxieme = manager.add("https://example.com/b", "Vidéo")
    # Then
    assert premier == 0
    assert deuxieme == 1


# --- DownloadManager.set_folder / set_cookies / clear_cookies ---


def test_lorsque_dossier_defini_alors_dossier_destination_mis_a_jour():
    """Lorsque set_folder est appelé, alors dossier_destination est mis à jour."""
    # Given
    manager = DownloadManager(on_update=lambda *_: None)
    # When
    manager.set_folder("/nouveau/dossier")
    # Then
    assert manager.dossier_destination == "/nouveau/dossier"


def test_lorsque_cookies_definis_alors_cookies_file_mis_a_jour():
    """Lorsque set_cookies est appelé, alors cookies_file est mis à jour."""
    # Given
    manager = DownloadManager(on_update=lambda *_: None)
    # When
    manager.set_cookies("/chemin/cookies.txt")
    # Then
    assert manager.cookies_file == "/chemin/cookies.txt"


def test_lorsque_cookies_vides_alors_cookies_file_est_none():
    """Lorsque clear_cookies est appelé, alors cookies_file vaut None."""
    # Given
    manager = DownloadManager(on_update=lambda *_: None)
    manager.set_cookies("/chemin/cookies.txt")
    # When
    manager.clear_cookies()
    # Then
    assert manager.cookies_file is None


# --- DownloadManager._run_all (téléchargeur injecté) ---


def test_lorsque_telechargement_reussi_alors_on_update_appele_avec_statut_termine():
    """Lorsque le téléchargement réussit, alors on_update est appelé avec le statut Terminé."""
    # Given
    mises_a_jour = []
    manager = DownloadManager(
        on_update=lambda identifiant, statut, progression: mises_a_jour.append(statut),
        telecharger=lambda url, options: None,
    )
    manager.add("https://example.com", "Audio")
    # When
    manager._run_all()
    # Then
    assert any("✔️" in statut for statut in mises_a_jour)


def test_lorsque_telecharger_leve_exception_alors_on_update_appele_avec_statut_erreur():
    """Lorsque le téléchargeur lève une exception, alors on_update est appelé avec le statut Erreur."""
    # Given
    mises_a_jour = []

    def telecharger_qui_echoue(url, options):
        raise RuntimeError("réseau indisponible")

    manager = DownloadManager(
        on_update=lambda identifiant, statut, progression: mises_a_jour.append(statut),
        telecharger=telecharger_qui_echoue,
    )
    manager.add("https://example.com", "Audio")
    # When
    manager._run_all()
    # Then
    assert any("❌" in statut for statut in mises_a_jour)


def test_lorsque_telecharger_leve_exception_alors_telechargements_suivants_continuent():
    """Lorsque le téléchargeur échoue sur un item, alors les items suivants sont quand même traités."""
    # Given
    mises_a_jour = []
    appels = []

    def telecharger_premier_echoue(url, options):
        appels.append(url)
        if len(appels) == 1:
            raise RuntimeError("échec premier")

    manager = DownloadManager(
        on_update=lambda identifiant, statut, progression: mises_a_jour.append(statut),
        telecharger=telecharger_premier_echoue,
    )
    manager.add("https://example.com/a", "Audio")
    manager.add("https://example.com/b", "Audio")
    # When
    manager._run_all()
    # Then
    assert len(appels) == 2
    assert any("✔️" in statut for statut in mises_a_jour)


def test_lorsque_hook_downloading_alors_on_update_appele_avec_progression_calculee():
    """Lorsque le hook signale downloading avec 50/100 octets, alors on_update reçoit 0.5."""
    # Given
    progressions = []

    def telecharger_avec_hook(url, options):
        for rappel in options.get("progress_hooks", []):
            rappel(
                {"status": "downloading", "downloaded_bytes": 50, "total_bytes": 100}
            )

    manager = DownloadManager(
        on_update=lambda identifiant, statut, progression: progressions.append(
            (statut, progression)
        ),
        telecharger=telecharger_avec_hook,
    )
    manager.add("https://example.com", "Audio")
    # When
    manager._run_all()
    # Then
    assert any(
        statut == "⬇️ Téléchargement" and progression == 0.5
        for statut, progression in progressions
    )


def test_lorsque_hook_finished_alors_on_update_appele_avec_statut_conversion():
    """Lorsque le hook signale finished, alors on_update est appelé avec le statut Conversion."""
    # Given
    mises_a_jour = []

    def telecharger_avec_hook(url, options):
        for rappel in options.get("progress_hooks", []):
            rappel({"status": "finished"})

    manager = DownloadManager(
        on_update=lambda identifiant, statut, progression: mises_a_jour.append(statut),
        telecharger=telecharger_avec_hook,
    )
    manager.add("https://example.com", "Audio")
    # When
    manager._run_all()
    # Then
    assert "🔄 Conversion..." in mises_a_jour


def test_lorsque_total_bytes_absent_alors_pas_de_division_par_zero():
    """Lorsque total_bytes et total_bytes_estimate sont absents, alors aucune ZeroDivisionError n'est levée."""

    # Given
    def telecharger_avec_hook(url, options):
        for rappel in options.get("progress_hooks", []):
            rappel(
                {
                    "status": "downloading",
                    "downloaded_bytes": 50,
                    "total_bytes": None,
                    "total_bytes_estimate": None,
                }
            )

    manager = DownloadManager(
        on_update=lambda *_: None,
        telecharger=telecharger_avec_hook,
    )
    manager.add("https://example.com", "Audio")
    # When / Then
    manager._run_all()  # ne doit pas lever ZeroDivisionError
