import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

# ============================================================
# CONFIGURAÇÕES
# ============================================================
TOKEN = "8959805650:AAEhkO-Cw17a0b88C3TdoV9a1CvvJR8nugA"
CANAL = "@acheiali"

# ============================================================
# PRODUTOS COM LINKS DE AFILIADO
# Adicione mais produtos nesta lista!
# ============================================================
produtos = [
    {
        "emoji": "🎧",
        "nome": "Lenovo GM2 Pro TWS Bluetooth — Noise Cancelling",
        "preco_original": "R$ 105,19",
        "preco_desconto": "R$ 47,59",
        "desconto": "55%",
        "avaliacao": "4.9",
        "reviews": "67",
        "vendidos": "700+",
        "frete": True,
        "link": "https://s.click.aliexpress.com/e/_c4DxN8G9",
        "categoria": "Eletrônicos"
    },
    {
        "emoji": "🕷️",
        "nome": "Colar Aranha Prata Y2K — Huitan Spider Necklace",
        "preco_original": "R$ 17,33",
        "preco_desconto": "R$ 6,99",
        "desconto": "60%",
        "avaliacao": "4.7",
        "reviews": "259",
        "vendidos": "900+",
        "frete": True,
        "link": "https://s.click.aliexpress.com/e/_c421tJvF",
        "categoria": "Moda"
    },
    {
        "emoji": "🥊",
        "nome": "Protetor Bucal Boxe — Sports Brace Mouthguard",
        "preco_original": "R$ 10,61",
        "preco_desconto": "R$ 6,99",
        "desconto": "34%",
        "avaliacao": "4.4",
        "reviews": "563",
        "vendidos": "5.000+",
        "frete": True,
        "link": "https://s.click.aliexpress.com/e/_c4UOCHlT",
        "categoria": "Esportes"
    },
    {
        "emoji": "⛓️",
        "nome": "Colar Prata 925 Sterling — Lobster Clasp Necklace",
        "preco_original": "R$ 8,94",
        "preco_desconto": "R$ 6,99",
        "desconto": "22%",
        "avaliacao": "4.4",
        "reviews": "1.186",
        "vendidos": "10.000+",
        "frete": True,
        "link": "https://s.click.aliexpress.com/e/_c31l6SYV",
        "categoria": "Moda"
    },
    {
        "emoji": "📿",
        "nome": "Corrente Grossa Hiphop Cuban Link — Stainless Steel",
        "preco_original": "R$ 9,13",
        "preco_desconto": "R$ 6,99",
        "desconto": "23%",
        "avaliacao": "4.5",
        "reviews": "1.349",
        "vendidos": "5.000+",
        "frete": True,
        "link": "https://s.click.aliexpress.com/e/_c4SW23GD",
        "categoria": "Moda"
    },
]

# ============================================================
# HORÁRIOS DE POSTAGEM (24h)
# Você pode adicionar ou remover horários!
# ============================================================
HORARIOS = ["09:00", "12:00", "18:00", "21:00"]

# ============================================================
# TEMPLATES DE MENSAGEM
# ============================================================
def montar_mensagem(produto, tipo="normal"):
    frete = "🚚 *Frete grátis para o Brasil*" if produto["frete"] else "📦 Verificar frete no site"

    if tipo == "flash":
        return (
            f"⚡ *OFERTA RELÂMPAGO — Corre\\!*\n\n"
            f"{produto['emoji']} *{produto['nome']}*\n\n"
            f"🔴 ~~De: {produto['preco_original']}~~\n"
            f"🟢 Por apenas: *{produto['preco_desconto']}*\n"
            f"💥 *{produto['desconto']} DE DESCONTO\\!*\n\n"
            f"{frete}\n"
            f"⭐ {produto['avaliacao']} estrelas \\| {produto['reviews']} avaliações\n"
            f"🏆 {produto['vendidos']} vendidos\n\n"
            f"⏳ *Oferta por tempo limitado\\!*\n\n"
            f"🛒 [Garantir agora]({produto['link']})\n\n"
            f"📲 _Encaminhe para quem vai querer\\!_"
        )
    else:
        return (
            f"🛍️ *ACHEI ALI — Oferta do Dia*\n\n"
            f"{produto['emoji']} *{produto['nome']}*\n\n"
            f"💰 ~~De: {produto['preco_original']}~~\n"
            f"✅ Por: *{produto['preco_desconto']}*\n"
            f"📉 Economia de *{produto['desconto']}*\n\n"
            f"{frete}\n"
            f"⭐ {produto['avaliacao']} estrelas \\| {produto['reviews']} avaliações\n\n"
            f"👉 [Comprar agora]({produto['link']})\n\n"
            f"⚠️ _Preço pode mudar a qualquer momento\\!_"
        )

# ============================================================
# LÓGICA DO BOT
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)

produto_index = 0

async def postar_produto(bot, tipo="normal"):
    global produto_index
    produto = produtos[produto_index % len(produtos)]
    produto_index += 1

    mensagem = montar_mensagem(produto, tipo)

    try:
        await bot.send_message(
            chat_id=CANAL,
            text=mensagem,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=False
        )
        logger.info(f"✅ Postado: {produto['nome']}")
    except Exception as e:
        logger.error(f"❌ Erro ao postar: {e}")

async def verificar_horario(bot):
    ultimo_postado = {}
    logger.info("🤖 Bot AcheiAli iniciado! Aguardando horários...")
    logger.info(f"📅 Horários configurados: {', '.join(HORARIOS)}")

    while True:
        agora = datetime.now().strftime("%H:%M")

        for horario in HORARIOS:
            if agora == horario and ultimo_postado.get(horario) != datetime.now().date():
                ultimo_postado[horario] = datetime.now().date()
                # Hora do almoço e noite = flash sale
                tipo = "flash" if horario in ["12:00", "21:00"] else "normal"
                await postar_produto(bot, tipo)

        await asyncio.sleep(30)

async def main():
    bot = Bot(token=TOKEN)
    info = await bot.get_me()
    logger.info(f"🤖 Bot conectado: @{info.username}")

    # Envia mensagem de teste ao iniciar
    try:
        await bot.send_message(
            chat_id=CANAL,
            text="🟢 *Bot AcheiAli iniciado\\!*\n\nPostagens automáticas ativadas\\! 🚀",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        logger.info("✅ Mensagem de teste enviada!")
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e} — Verifique se o bot é admin do canal.")

    await verificar_horario(bot)

if __name__ == "__main__":
    asyncio.run(main())
