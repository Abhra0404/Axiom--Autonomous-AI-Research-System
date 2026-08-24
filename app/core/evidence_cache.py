import hashlib
import json
from pathlib import Path

from app.models.schemas import EvidenceAnalysis


class EvidenceCache:

    def __init__(
        self,
        base_dir: str = ".cache/evidence",
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _key(self, content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        content: str,
    ) -> EvidenceAnalysis | None:

        cache_file = (
            self.base_dir
            / f"{self._key(content)}.json"
        )

        if not cache_file.exists():
            return None

        try:
            data = json.loads(
                cache_file.read_text(
                    encoding="utf-8"
                )
            )

            return EvidenceAnalysis.model_validate(
                data
            )

        except Exception:
            return None

    def set(
        self,
        content: str,
        analysis: EvidenceAnalysis,
    ) -> None:

        cache_file = (
            self.base_dir
            / f"{self._key(content)}.json"
        )

        cache_file.write_text(
            json.dumps(
                analysis.model_dump(
                    mode="json"
                ),
                indent=2,
            ),
            encoding="utf-8",
        )