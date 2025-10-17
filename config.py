import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration de l'application"""

    TELEGRAM_TOKEN: str
    MAX_IMAGE_SIZE: int = 4096

    def __post_init__(self):
        if not self.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN est requis")

    @classmethod
    def from_env(cls):
        """Charge la config depuis les variables d'environnement"""
        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            raise ValueError(
                "TELEGRAM_TOKEN non trouvé dans les variables d'environnement. "
                "Définissez-le avec: export TELEGRAM_TOKEN='votre_token'"
            )
        return cls(TELEGRAM_TOKEN=token)
