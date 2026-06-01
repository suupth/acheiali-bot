import asyncio
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Bot
from telegram.constants import ParseMode

# ============================================================
# CONFIGURAÇÕES
# ============================================================
TOKEN = "8959805650:AAEhkO-Cw17a0b88C3TdoV9a1CvvJR8nugA"
CANAL = "@acheiali"

# ============================================================
# FIREBASE
# ============================================================
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# BUSCAR PRODUTOS DO FIREBASE
# ============================================================
def buscar_produtos():
    docs = db.collection("produtos").stream()
    produtos = []
    for doc in docs:
        produtos.append(doc.to_dict())
    logger.info(f"🔄 {len(produtos)} produtos carregados do Firebase")
    return produtos

# ============================================================
# BUSCAR HORÁRIOS DO FIREBASE
# ============================================================
def buscar_horarios():
    try:
        doc = db.collection("config").document("horarios").get()
        if doc.exists:
            return doc.to_dict().get("lista", ["09:00","12:00","18:00","21:00"])
    except Exception as e:
        logger.error(f"Erro ao buscar horários: {e}")
    return ["09:00","12:00","18:00","21:00"]

# ============================================================
# MONTAR MENSAGEM
# ============================================================
def escape(text):
    chars = ['_','*','[',']','(',')','>','#','+','-','=','|','{','}','.','!','~','`']
    for c in chars:
        text = str(text).replace(c, f'\\{c}')
    return text

def montar_mensagem(produto, tipo="normal"):
    emoji = produto.get("emoji", "🛍️")
    nome = escape(produto.get("nome", "Produto"))
    old = escape(produto.get("preco_original") or produto.get("old", ""))
    price = escape(produto.get("preco_desconto") or produto.get("price", ""))
    desconto = escape(produto.get("desconto", ""))
    stars = escape(produto.get("avaliacao") or produto.get("stars", "4.5"))
    reviews = escape(produto.get("reviews", "100+"))
    link = produto.get("link", "https://www.aliexpress.com")
    frete = produto.get("frete", True)
    frete_txt = "🚚 *Frete grátis para o Brasil*" if frete else "📦 Verificar frete no site"
    tipo_real = produto.get("tipo", tipo)

    if tipo_real == "flash":
        return (
            f"⚡ *OFERTA RELÂMPAGO — Corre\\!*\n\n"
            f"{emoji} *{nome}*\n\n"
            f"🔴 ~~De: {old}~~\n"
            f"🟢 Por apenas: *{price}*\n"
            f"💥 *{desconto} DE DESCONTO\\!*\n\n"
            f"{frete_txt}\n"
            f"⭐ {stars} estrelas \\| {reviews} avaliações\n\n"
            f"⏳ *Oferta por tempo limitado\\!*\n\n"
            f"🛒 [Garantir agora]({link})\n\n"
            f"📲 _Encaminhe para quem vai querer\\!_"
        )
    else:
        return (
            f"🛍️ *ACHEI ALI — Oferta do Dia*\n\n"
            f"{emoji} *{nome}*\n\n"
            f"💰 ~~De: {old}~~\n"
            f"✅ Por: *{price}*\n"
            f"📉 Economia de *{desconto}*\n\n"
            f"{frete_txt}\n"
            f"⭐ {stars} estrelas \\| {reviews} avaliações\n\n"
            f"👉 [Comprar agora]({link})\n\n"
            f"⚠️ _Preço pode mudar a qualquer momento\\!_"
        )

# ============================================================
# LÓGICA DO BOT
# ============================================================
produto_index = 0

async def postar_produto(bot):
    global produto_index
    produtos = buscar_produtos()
    if not produtos:
        logger.warning("⚠️ Nenhum produto encontrado no Firebase!")
        return

    produto = produtos[produto_index % len(produtos)]
    produto_index += 1

    mensagem = montar_mensagem(produto)

    try:
        await bot.send_message(
            chat_id=CANAL,
            text=mensagem,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=False
        )
        logger.info(f"✅ Postado: {produto.get('nome','?')}")
    except Exception as e:
        logger.error(f"❌ Erro ao postar: {e}")

async def verificar_horario(bot):
    ultimo_postado = {}
    horarios = buscar_horarios()
    logger.info(f"🤖 Bot AcheiAli iniciado!")
    logger.info(f"📅 Horários: {', '.join(horarios)}")

    while True:
        # Recarrega horários a cada hora
        if datetime.now().minute == 0:
            horarios = buscar_horarios()

        agora = datetime.now().strftime("%H:%M")
        for horario in horarios:
            if agora == horario and ultimo_postado.get(horario) != datetime.now().date():
                ultimo_postado[horario] = datetime.now().date()
                await postar_produto(bot)

        await asyncio.sleep(30)

async def main():
    bot = Bot(token=TOKEN)
    info = await bot.get_me()
    logger.info(f"🤖 Bot conectado: @{info.username}")

    try:
        await bot.send_message(
            chat_id=CANAL,
            text="🟢 *Bot AcheiAli iniciado\\!*\n\nAgora lendo produtos direto do Firebase 🔥",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")

    await verificar_horario(bot)

if __name__ == "__main__":
    asyncio.run(main())
