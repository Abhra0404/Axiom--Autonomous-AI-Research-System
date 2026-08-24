import hashlib
import json
from pathlib import Path

from app.models.schemas import Source


class SourceCache:

    def __init__(self, base_dir: str = ".cache/sources"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _key(self, url: str) -> str:
        return hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()

    def get(self, url: str) -> Source | None:

        cache_file = (
            self.base_dir
            / f"{self._key(url)}.json"
        )

        if not cache_file.exists():
            return None

        try:
            data = json.loads(
                cache_file.read_text(
                    encoding="utf-8"
                )
            )

            return Source.model_validate(data)

        except Exception:
            return None

    def set(self, source: Source) -> None:

        cache_file = (
            self.base_dir
            / f"{self._key(str(source.url))}.json"
        )

        cache_file.write_text(
            json.dumps(
                source.model_dump(
                    mode="json"
                ),
                indent=2,
            ),
            encoding="utf-8",
        )