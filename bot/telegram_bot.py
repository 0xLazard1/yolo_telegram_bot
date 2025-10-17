from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)
from services.image_processor import ImageProcessor
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramImageBot:
    """Classe principale du bot Telegram"""

    def __init__(self, config: Config):
        self.config = config
        self.image_processor = ImageProcessor()
        self.app = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour la commande /start"""
        welcome_message = (
            "👥 Bot de détection de personnes avec IA\n\n"
            "Envoyez-moi une photo et je compterai le nombre de personnes !\n\n"
            "Commandes disponibles :\n"
            "/start - Afficher ce message\n"
            "/help - Aide détaillée\n"
            "/stop - Arrêter le bot\n\n"
            "💡 Envoyez simplement une photo pour commencer !"
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour la commande /help"""
        help_message = (
            "ℹ️ Aide - Bot de détection de personnes\n\n"
            "Ce bot utilise l'intelligence artificielle (YOLOv8) pour détecter et compter "
            "les personnes dans vos photos.\n\n"
            "📸 Comment utiliser :\n"
            "1. Envoyez une photo\n"
            "2. Le bot analyse l'image\n"
            "3. Vous recevez l'image annotée avec :\n"
            "   • Des boîtes rouges autour de chaque personne\n"
            "   • Le nombre de personnes détectées\n"
            "   • Le score de confiance\n\n"
            "⚙️ Commandes :\n"
            "/start - Message de bienvenue\n"
            "/help - Cette aide\n"
            "/stop - Arrêter le bot\n\n"
            "💡 Astuce : Envoyez des photos avec une bonne qualité pour de meilleurs résultats !"
        )
        await update.message.reply_text(help_message)

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour la commande /stop"""
        await update.message.reply_text(
            "👋 Au revoir !\n\n"
            "Le bot s'arrête. Merci d'avoir utilisé ce service !\n\n"
            "Pour le relancer, l'administrateur devra le redémarrer manuellement."
        )
        logger.info(f"Commande /stop reçue de {update.effective_user.username}")
        # Arrête l'application
        self.app.stop_running()

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour les photos reçues"""
        try:
            await update.message.reply_text("⏳ Détection en cours...")

            # Récupération de la photo (meilleure résolution)
            photo = await update.message.photo[-1].get_file()
            photo_bytes = await photo.download_as_bytearray()

            logger.info(
                f"Photo reçue de {update.effective_user.username}, taille: {len(photo_bytes)} bytes"
            )

            # Traitement de l'image (détection de personnes)
            result_bytes, description, stats = self.image_processor.process_image(
                bytes(photo_bytes)
            )

            # Envoi du résultat
            await update.message.reply_photo(
                photo=result_bytes, caption=f"✅ {description}"
            )

            logger.info(f"Détection terminée pour {update.effective_user.username}: {stats['count']} personne(s)")

        except Exception as e:
            logger.error(f"Erreur lors du traitement: {str(e)}", exc_info=True)
            await update.message.reply_text(
                f"❌ Erreur lors du traitement de l'image: {str(e)}"
            )

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler pour les images envoyées en tant que fichiers"""
        await update.message.reply_text(
            "⚠️ Veuillez envoyer l'image en tant que photo, pas en tant que fichier."
        )

    def setup_handlers(self):
        """Configure tous les handlers du bot"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(
            MessageHandler(filters.Document.IMAGE, self.handle_document)
        )

    async def post_init(self, application):
        """Configure le menu de commandes Telegram"""
        commands = [
            ("start", "Afficher le message de bienvenue"),
            ("help", "Obtenir de l'aide sur l'utilisation du bot"),
            ("stop", "Arrêter le bot"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Menu de commandes configuré")

    def run(self):
        """Lance le bot"""
        logger.info("Démarrage du bot...")

        # Création de l'application
        self.app = Application.builder().token(self.config.TELEGRAM_TOKEN).post_init(self.post_init).build()

        # Configuration des handlers
        self.setup_handlers()

        # Lancement
        logger.info("Bot en ligne et prêt à recevoir des messages")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
