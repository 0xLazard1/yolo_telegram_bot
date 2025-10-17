from bot.telegram_bot import TelegramImageBot
from config import Config


def main():
    """Point d'entrée de l'application"""
    # Chargement de la configuration
    config = Config.from_env()

    # Création et lancement du bot
    bot = TelegramImageBot(config)
    bot.run()


if __name__ == "__main__":
    main()
