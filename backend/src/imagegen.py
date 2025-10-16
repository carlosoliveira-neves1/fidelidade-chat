# imagegen.py — gera arte padrão personalizada para WhatsApp (PNG)
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Cores da CDC
VINHO = (104, 0, 38)     # #680026
DOURADO = (214, 167, 46) # #D6A72E
CREME = (250, 245, 235)  # #FAF5EB
CHUMBO = (33, 33, 33)

def _load_font(size=64):
    # tenta fontes comuns; fallback para default
    try:
        # Deixe a fonte opcionalmente configurável via env
        font_path = os.getenv("CARD_FONT_PATH")
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        # Windows: Arial
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def _load_logo():
    # Logo opcional: BACKEND_LOGO_PATH no .env
    logo_path = os.getenv("BACKEND_LOGO_PATH")
    if logo_path and os.path.exists(logo_path):
        try:
            return Image.open(logo_path).convert("RGBA")
        except Exception:
            pass
    return None

def make_card(cliente_nome: str, visitas: int, meta: int, faltam: int):
    W, H = 1080, 1080  # quadrado padrão feed/whatsapp
    img = Image.new("RGB", (W, H), CREME)
    draw = ImageDraw.Draw(img)

    # topo vinho
    draw.rectangle([0,0,W,360], fill=VINHO)

    # linhas douradas decorativas
    draw.rectangle([0,340,W,360], fill=DOURADO)

    # logo (se houver)
    logo = _load_logo()
    if logo:
        # redimensiona para caber no topo
        max_h = 220
        ratio = max_h / logo.height
        logo2 = logo.resize((int(logo.width*ratio), int(logo.height*ratio)))
        img.paste(logo2, (60, 60), logo2)

    # textos
    title_font = _load_font(78)
    name_font = _load_font(64)
    big_font = _load_font(120)
    small_font = _load_font(44)

    # Título topo (à direita do logo)
    title = "Programa de Fidelidade"
    tw, th = draw.textsize(title, font=title_font)
    draw.text((W-60-tw, 80), title, font=title_font, fill=(255,255,255))

    # saudação
    hello = f"Olá, {cliente_nome.split()[0]}!"
    draw.text((60, 420), hello, font=name_font, fill=CHUMBO)

    # pontuação
    pontos = f"Você tem {visitas} visita(s)"
    draw.text((60, 520), pontos, font=big_font, fill=VINHO)

    # meta/ faltam
    if faltam <= 0:
        frase = "Você já pode resgatar seu brinde!"
        fillc = VINHO
    else:
        frase = f"Faltam {faltam} visita(s) para o brinde."
        fillc = CHUMBO
    draw.text((60, 670), f"Meta: {meta} visitas", font=name_font, fill=CHUMBO)
    draw.text((60, 760), frase, font=name_font, fill=fillc)

    # rodapé
    footer = "Casa do Cigano • Obrigado pela visita!"
    fw, fh = draw.textsize(footer, font=small_font)
    draw.text(((W-fw)//2, 980-fh), footer, font=small_font, fill=CHUMBO)

    # borda fina
    draw.rectangle([5,5,W-5,H-5], outline=VINHO, width=6)

    # retorna bytes PNG
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.getvalue()
