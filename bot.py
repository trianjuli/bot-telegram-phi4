"""
Main Telegram Bot untuk evaluasi diskusi dan tugas
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from core.knowledge_base import KnowledgeBase
from core.agent import EvaluationAgent

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSE_TYPE, INPUT_CONTENT = range(2)

# Initialize knowledge base and agent
kb = KnowledgeBase()
agent = EvaluationAgent(kb)


class EvaluationBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN tidak ditemukan di .env")
        
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup command dan message handlers"""
        
        # Start command
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("menu", self.menu))
        
        # Conversation handler untuk evaluasi
        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^📝 Evaluasi Diskusi$"), self.ask_content_diskusi),
                MessageHandler(filters.Regex("^📄 Evaluasi Tugas$"), self.ask_content_tugas),
            ],
            states={
                CHOOSE_TYPE: [
                    MessageHandler(filters.Regex("^(Diskusi|Tugas)$"), self.choose_type),
                ],
                INPUT_CONTENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_content),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        
        self.app.add_handler(conv_handler)
        
        # Inline buttons
        self.app.add_handler(MessageHandler(filters.Regex("^💬 Lihat Rubrik$"), self.show_rubric))
        self.app.add_handler(MessageHandler(filters.Regex("^ℹ️ Info Bot$"), self.info_bot))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        
        welcome_text = f"""
Halo {user.first_name}! 👋

Saya adalah **AI Agent untuk Evaluasi Diskusi dan Tugas Mahasiswa**.

Gunakan bot ini untuk:
✅ Mengevaluasi diskusi kelas
✅ Mengevaluasi tugas mahasiswa
✅ Mendapatkan feedback detail dan skor otomatis
✅ Melihat rubrik penilaian

Silakan pilih menu di bawah untuk memulai!
"""
        
        await self.show_menu(update, context, welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
**Panduan Penggunaan Bot:**

📝 **Evaluasi Diskusi**
• Klik tombol "📝 Evaluasi Diskusi"
• Masukkan teks diskusi yang akan dinilai
• AI akan mengevaluasi dan memberikan skor

📄 **Evaluasi Tugas**
• Klik tombol "📄 Evaluasi Tugas"
• Masukkan teks tugas yang akan dinilai
• AI akan mengevaluasi dan memberikan skor

💬 **Lihat Rubrik**
• Klik tombol "💬 Lihat Rubrik"
• Pilih tipe rubrik yang ingin dilihat

**Perintah Tersedia:**
/start - Tampilkan menu utama
/help - Tampilkan bantuan ini
/menu - Tampilkan menu
/cancel - Batalkan operasi

**Kriteria Penilaian:**
• Untuk Diskusi: Partisipasi, Kualitas Konten, Interaksi, Ketepatan Waktu
• Untuk Tugas: Orisinalitas, Struktur & Organisasi, Akurasi, Referensi & Bukti
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        await self.show_menu(update, context)

    async def show_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, greeting: str = None):
        """Display menu with buttons"""
        menu_text = greeting or "Pilih menu yang ingin Anda gunakan:"
        
        keyboard = [
            ["📝 Evaluasi Diskusi", "📄 Evaluasi Tugas"],
            ["💬 Lihat Rubrik", "ℹ️ Info Bot"],
        ]
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

    async def ask_content_diskusi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for diskusi content"""
        context.user_data['eval_type'] = 'diskusi'
        
        text = """
Silakan masukkan teks diskusi yang akan dievaluasi.

⚠️ Pastikan teks diskusi:
• Memiliki minimal 20 karakter
• Berisi konten yang jelas dan relevan
• Tidak ada data pribadi yang sensitif

Ketik /cancel jika ingin membatalkan.
"""
        
        await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return INPUT_CONTENT

    async def ask_content_tugas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for tugas content"""
        context.user_data['eval_type'] = 'tugas'
        
        text = """
Silakan masukkan teks tugas yang akan dievaluasi.

⚠️ Pastikan teks tugas:
• Memiliki minimal 20 karakter
• Berisi jawaban/konten yang lengkap
• Tidak ada data pribadi yang sensitif

Ketik /cancel jika ingin membatalkan.
"""
        
        await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return INPUT_CONTENT

    async def choose_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Choose evaluation type"""
        tipe = update.message.text.lower()
        context.user_data['eval_type'] = tipe
        
        text = f"Masukkan konten {tipe} yang akan dievaluasi:"
        await update.message.reply_text(text)
        
        return INPUT_CONTENT

    async def process_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process the submitted content"""
        konten = update.message.text
        eval_type = context.user_data.get('eval_type', 'diskusi')
        user_id = update.effective_user.id
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 Sedang mengevaluasi... Ini mungkin memakan waktu beberapa detik."
        )
        
        try:
            # Run evaluation
            if eval_type == 'diskusi':
                result = agent.evaluate_diskusi(konten, str(user_id))
            else:
                result = agent.evaluate_tugas(konten, str(user_id))
            
            # Generate report
            report = agent.generate_feedback_report(result)
            
            # Delete processing message and send report
            await processing_msg.delete()
            await update.message.reply_text(report, parse_mode='Markdown')
            
            # Show menu again
            await self.show_menu(update, context, "Evaluasi selesai! Pilih menu berikutnya:")
            
        except Exception as e:
            await processing_msg.delete()
            error_msg = f"❌ Error saat evaluasi: {str(e)}\n\nSilakan coba lagi atau hubungi admin."
            await update.message.reply_text(error_msg)
            await self.show_menu(update, context)
        
        return ConversationHandler.END

    async def show_rubric(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show evaluation rubric"""
        text = """
Pilih rubrik yang ingin dilihat:

**Rubrik Diskusi:**
"""
        
        rubric_diskusi = kb.get_rubric('diskusi')
        for k in rubric_diskusi.get('kriteria', []):
            text += f"\n• **{k['nama']}** (Bobot: {k['bobot']}%)"
            text += f"\n  {k['deskripsi']}"

        text += "\n\n**Rubrik Tugas:**\n"
        
        rubric_tugas = kb.get_rubric('tugas')
        for k in rubric_tugas.get('kriteria', []):
            text += f"\n• **{k['nama']}** (Bobot: {k['bobot']}%)"
            text += f"\n  {k['deskripsi']}"

        await update.message.reply_text(text, parse_mode='Markdown')
        await self.show_menu(update, context)

    async def info_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot information"""
        info_text = """
**ℹ️ Informasi Bot**

**Nama:** AI Evaluation Bot
**Versi:** 1.0.0
**Fungsi:** Evaluasi Diskusi dan Tugas Mahasiswa

**Fitur:**
✅ Evaluasi otomatis menggunakan AI (Phi4)
✅ Penilaian berbasis rubrik kurikulum
✅ Feedback detail dan saran perbaikan
✅ Sistem scoring terukur
✅ Laporan terstruktur

**Model AI:** Phi4 (via Ollama)
**Status:** Online dan siap digunakan

**Untuk informasi lebih lanjut, gunakan /help**
"""
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
        await self.show_menu(update, context)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel operation"""
        await update.message.reply_text(
            "Operasi dibatalkan.",
            reply_markup=ReplyKeyboardRemove()
        )
        await self.show_menu(update, context, "Kembali ke menu utama.")
        return ConversationHandler.END

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")

    def run(self):
        """Run the bot"""
        logger.info("Bot sedang berjalan...")
        self.app.run_polling()


if __name__ == "__main__":
    bot = EvaluationBot()
    bot.run()
