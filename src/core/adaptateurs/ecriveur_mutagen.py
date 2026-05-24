from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError


class EcriveurMutagen:
    def embedder_cover(self, chemin_audio: str, donnees_jpeg: bytes) -> None:
        suffixe = Path(chemin_audio).suffix.lower()
        if suffixe == ".mp3":
            self._embedder_mp3(chemin_audio, donnees_jpeg)
        elif suffixe == ".flac":
            self._embedder_flac(chemin_audio, donnees_jpeg)

    def _embedder_mp3(self, chemin_audio: str, donnees_jpeg: bytes) -> None:
        try:
            tags = ID3(chemin_audio)
        except ID3NoHeaderError:
            tags = ID3()
        tags.delall("APIC")
        tags.add(
            APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=donnees_jpeg,
            )
        )
        tags.save(chemin_audio)

    def _embedder_flac(self, chemin_audio: str, donnees_jpeg: bytes) -> None:
        audio = FLAC(chemin_audio)
        audio.clear_pictures()
        image = Picture()
        image.type = 3
        image.mime = "image/jpeg"
        image.data = donnees_jpeg
        audio.add_picture(image)
        audio.save()
