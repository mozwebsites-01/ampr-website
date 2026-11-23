#!/usr/bin/env python3
"""
Gerador do website da AMPR.

Uso:  python3 build.py
Lê os fragmentos em src/*.html, aplica o cabeçalho/rodapé comuns e escreve
as páginas finais em site/. Publique apenas a pasta site/.

Marcadores disponíveis dentro dos fragmentos:
  {{icon:nome}}               ícone SVG (ver ICONS)
  {{orbit}}                   órbitas animadas do átomo (banner)
  {{media:classe|texto alternativo|foto.jpg}}  espaço para fotografia (foto em site/assets/img/)
  {{contact_list}}            lista de contactos (ver CONTACT)
  {{gallery}}                 fotos em site/assets/img/galeria/
"""
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "site"
IMG = OUT / "assets" / "img"

# Endereço público do site. Ao mudar para o domínio final (ex.: https://www.ampr.org.mz),
# o site deixa de estar marcado como pré-visualização e passa a poder ser indexado pelo Google.
SITE_URL = "https://mozwebsites-01.github.io/ampr-website"
PREVIEW = "github.io" in SITE_URL

# TODO AMPR: preencher com os dados reais. Campos vazios não aparecem no site
# (a barra superior só aparece quando houver telefone ou e-mail).
CONTACT = {
    "phone": "",          # ex.: "+258 84 123 4567"
    "phone_href": "",     # ex.: "tel:+258841234567"
    "whatsapp": "",
    "whatsapp_href": "",  # ex.: "https://wa.me/258841234567"
    "email": "",
    "address": "",
    "hours": "",          # ex.: "Segunda a sexta, das 8h00 às 16h00"
    "facebook": "",
    "linkedin": "",
    "youtube": "",
}

NAV = [
    ("index.html", "Início"),
    ("sobre.html", "Sobre Nós"),
    ("o-que-fazemos.html", "O Que Fazemos"),
    ("membros.html", "Membros"),
    ("actividades.html", "Actividades"),
    ("recursos.html", "Recursos"),
    ("parceiros.html", "Parceiros"),
    ("contactos.html", "Contactos"),
]

# ---------------------------------------------------------------- ícones
_I = {
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "cap": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/><path d="M22 10v6"/>',
    "users": '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "slides": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="m10 7 4 3-4 3z"/>',
    "news": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8z"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "menu": '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "handshake": '<path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/>',
    "whatsapp": '<path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/>',
}
_FILLED = {
    "facebook": '<path d="M14 8.5V6.8c0-.8.2-1.3 1.4-1.3H17V2.3c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.1H7.7v3.3h2.7V22h3.4v-10.2h2.8l.4-3.3H14z"/>',
    "linkedin": '<path d="M6.94 5a2 2 0 1 1-4-.002 2 2 0 0 1 4 .002zM7 8.48H3V21h4V8.48zm6.32 0H9.34V21h3.94v-6.57c0-3.66 4.77-4 4.77 0V21H22v-7.93c0-6.17-7.06-5.94-8.72-2.91l.04-1.68z"/>',
    "youtube": '<path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.75 15.02V8.98L15.5 12l-5.75 3.02z"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    if name in _FILLED:
        return f'<svg{c} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{_FILLED[name]}</svg>'
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')


# ---------------------------------------------------------------- órbitas
def trefoil(cx, cy, r1, r2):
    """Trevo radiológico: três pás de 60°, uma para baixo e duas para cima."""
    parts = []
    for c in (90, 210, 330):
        a0, a1 = math.radians(c - 30), math.radians(c + 30)
        p = lambda r, a: f"{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}"
        parts.append(f"M{p(r1, a0)} L{p(r2, a0)} A{r2} {r2} 0 0 1 {p(r2, a1)} L{p(r1, a1)} A{r1} {r1} 0 0 0 {p(r1, a0)}Z")
    return " ".join(parts)


def orbit_svg():
    rings = [  # (rotação, cor, duração da electrão)
        (90, "#3DBE74", "11s"),
        (30, "#E8304F", "14s"),
        (-30, "#F2B705", "9s"),
    ]
    ell = "M50 300 a250 92 0 1 0 500 0 a250 92 0 1 0 -500 0"
    g = []
    for i, (rot, col, dur) in enumerate(rings):
        g.append(
            f'<g transform="rotate({rot} 300 300)">'
            f'<path class="orbit-ring" d="{ell}" stroke="{col}" />'
            f'<circle r="9" fill="{col}"><animateMotion dur="{dur}" repeatCount="indefinite" '
            f'begin="-{i * 3}s" path="{ell}"/></circle></g>'
        )
    return f'''<svg class="orbit-svg" viewBox="0 0 600 600" aria-hidden="true" focusable="false">
  <g class="orbit-spin rev">
    <circle cx="300" cy="300" r="292" fill="none" stroke="#D21034" stroke-width="2.4" stroke-dasharray="560 360 300 615" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    <circle cx="300" cy="300" r="272" fill="none" stroke="#D21034" stroke-opacity=".6" stroke-width="1.2" stroke-dasharray="380 300 520 510" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
  </g>
  <circle cx="300" cy="300" r="190" fill="none" stroke="#fff" stroke-opacity=".07"/>
  <circle cx="300" cy="300" r="120" fill="none" stroke="#fff" stroke-opacity=".06"/>
  <g class="orbit-spin">{''.join(g)}</g>
  <g class="orbit-pulse"><circle cx="300" cy="300" r="58" fill="#F2B705" fill-opacity=".12"/></g>
  <circle cx="300" cy="300" r="38" fill="#F2B705"/>
  <path d="{trefoil(300, 300, 9, 32)}" fill="#0D1A14"/>
  <circle cx="300" cy="300" r="5.5" fill="#0D1A14"/>
</svg>'''


ORBIT = orbit_svg()

MINI_ATOM = ('<svg class="media-mark" viewBox="0 0 600 600" aria-hidden="true"><g fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="3">'
             '<ellipse cx="300" cy="300" rx="250" ry="92" transform="rotate(90 300 300)"/>'
             '<ellipse cx="300" cy="300" rx="250" ry="92" transform="rotate(30 300 300)"/>'
             '<ellipse cx="300" cy="300" rx="250" ry="92" transform="rotate(-30 300 300)"/></g>'
             '<circle cx="300" cy="300" r="30" fill="#F2B705"/></svg>')


def media(arg):
    """Espaço para fotografia. Mostra a foto se existir em site/assets/img/, senão um painel neutro."""
    cls, alt, photo = (arg.split("|") + ["", "", ""])[:3]
    if photo and not (IMG / photo).exists() and photo == "jornada.jpg" and (IMG / "foto-seminario.jpg").exists():
        photo, alt = "foto-seminario.jpg", "Profissionais de saúde num seminário técnico"
    if photo and (IMG / photo).exists():
        return f'<div class="media {cls}"><img src="assets/img/{photo}" alt="{alt}" loading="lazy"></div>'
    return f'<div class="media {cls}" aria-hidden="true">{MINI_ATOM}</div>'


def contact_list():
    rows = [
        ("pin", "Endereço", CONTACT["address"], ""),
        ("phone", "Telefone", CONTACT["phone"], CONTACT["phone_href"]),
        ("whatsapp", "WhatsApp", CONTACT["whatsapp"], CONTACT["whatsapp_href"]),
        ("mail", "E-mail", CONTACT["email"], f"mailto:{CONTACT['email']}" if CONTACT["email"] else ""),
        ("clock", "Horário de atendimento", CONTACT["hours"], ""),
    ]
    items = []
    for ic, label, value, href in rows:
        if not value:
            continue
        val = f'<a href="{href}">{value}</a>' if href else f"<span>{value}</span>"
        items.append(f"<li>{icon(ic)}<div><strong>{label}</strong>{val}</div></li>")
    if not items:
        return '<p class="muted">O endereço, o telefone e o e-mail da AMPR vão ser publicados aqui. Até lá, use o formulário.</p>'
    return '<ul class="info-list">' + "".join(items) + "</ul>"


def gallery():
    folder = IMG / "galeria"
    photos = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if folder.exists() else []
    if not photos:
        return '<p class="empty-note">As fotografias das jornadas e formações vão ser publicadas aqui, organizadas por evento.</p>'
    imgs = "".join(f'<img src="assets/img/galeria/{p.name}" alt="Actividade da AMPR" loading="lazy">' for p in photos)
    return f'<div class="gallery">{imgs}</div>'


def render_tokens(html):
    html = re.sub(r"\{\{icon:([\w-]+)(?::([\w -]+))?\}\}", lambda m: icon(m.group(1), m.group(2) or ""), html)
    html = html.replace("{{orbit}}", ORBIT)
    html = re.sub(r"\{\{media:([^}]*)\}\}", lambda m: media(m.group(1)), html)
    html = html.replace("{{contact_list}}", contact_list())
    html = html.replace("{{gallery}}", gallery())
    def photo_bg(m):
        f = m.group(1)
        if (IMG / f).exists():
            return f'<div class="hero-bg has-photo" style="background-image:url(assets/img/{f})" aria-hidden="true"></div>'
        return ""
    html = re.sub(r"\{\{photo_bg:([\w.-]+)\}\}", photo_bg, html)
    hero = IMG / "hero.jpg"
    html = html.replace("{{hero_bg}}",
                        '<div class="hero-bg has-photo" style="background-image:url(assets/img/hero.jpg)" aria-hidden="true"></div>'
                        if hero.exists() else '<div class="hero-bg"></div>')
    return html


# ---------------------------------------------------------------- layout
CTA_JOIN = "Torne-se membro"


def socials(cls):
    links = [(k, n) for k, n in (("facebook", "Facebook"), ("linkedin", "LinkedIn"), ("youtube", "YouTube")) if CONTACT[k]]
    if not links:
        return ""
    lis = "".join(f'<li><a href="{CONTACT[k]}" aria-label="{n} da AMPR">{icon(k)}</a></li>' for k, n in links)
    return f'<ul class="{cls}" aria-label="Redes sociais">{lis}</ul>'


def has_topbar():
    return bool(CONTACT["phone"] or CONTACT["email"])


def topbar():
    if not has_topbar():
        return ""
    left = []
    if CONTACT["phone"]:
        left.append(f'<li><a href="{CONTACT["phone_href"]}">{icon("phone")}{CONTACT["phone"]}</a></li>')
    if CONTACT["email"]:
        left.append(f'<li><a href="mailto:{CONTACT["email"]}">{icon("mail")}{CONTACT["email"]}</a></li>')
    return f'''<div class="topbar">
    <div class="container topbar-inner">
      <ul>{"".join(left)}</ul>
      {socials("socials-mini")}
    </div>
  </div>'''


def header(current):
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{href}"{cur if href == current else ""}>{label}</a></li>'
        for href, label in NAV
    )
    return f'''{topbar()}
<header class="site-header" id="site-header">
  <div class="flagline" aria-hidden="true"></div>
  <div class="container header-inner">
    <a class="brand" href="index.html" aria-label="AMPR, página inicial">
      <img class="logo-chip" src="assets/img/ampr-logo.jpg" alt="" width="520" height="430">
      <span class="brand-text"><span class="brand-name">AMPR</span><span class="brand-sub">Associação Moçambicana de Protecção Radiológica</span></span>
    </a>
    <nav class="main-nav" id="main-nav" aria-label="Menu principal">
      <ul>{items}<li class="nav-cta-mobile"><a href="membros.html#adesao">{CTA_JOIN}</a></li></ul>
    </nav>
    <a class="btn header-cta btn-sm" href="membros.html#adesao">{CTA_JOIN}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav">
      {icon("menu", "icon-open")}{icon("x", "icon-close")}<span class="sr-only">Abrir ou fechar o menu</span>
    </button>
  </div>
</header>'''


def footer():
    contacts = []
    if CONTACT["phone"]:
        contacts.append(f'<li><a href="{CONTACT["phone_href"]}">{CONTACT["phone"]}</a></li>')
    if CONTACT["email"]:
        contacts.append(f'<li><a href="mailto:{CONTACT["email"]}">{CONTACT["email"]}</a></li>')
    contacts.append('<li><a href="contactos.html">Página de contactos</a></li>')
    return f'''<footer class="site-footer">
  <div class="flagline" aria-hidden="true"></div>
  <div class="container footer-main">
    <div>
      <div class="footer-brand">
        <img class="logo-chip" src="assets/img/ampr-logo.jpg" alt="Logótipo da AMPR" width="520" height="430" loading="lazy">
        <strong>AMPR</strong>
      </div>
      <p class="footer-tagline">Associação Moçambicana de Protecção Radiológica. Pelo uso seguro das radiações ionizantes em Moçambique.</p>
      {socials("socials")}
    </div>
    <nav aria-label="Ligações rápidas">
      <h2>Ligações rápidas</h2>
      <ul class="footer-links">
        <li><a href="sobre.html">Sobre Nós</a></li>
        <li><a href="o-que-fazemos.html">O Que Fazemos</a></li>
        <li><a href="membros.html">Membros</a></li>
        <li><a href="actividades.html">Actividades</a></li>
        <li><a href="recursos.html">Recursos</a></li>
        <li><a href="contactos.html">Contactos</a></li>
      </ul>
    </nav>
    <div>
      <h2>Newsletter</h2>
      <p>Receba as novidades da AMPR no seu e-mail.</p>
      <form class="newsletter js-form" data-endpoint="" data-success="Subscrição feita. Vai receber a próxima newsletter da AMPR." novalidate>
        <label class="sr-only" for="nl-email">E-mail</label>
        <input class="input" id="nl-email" name="email" type="email" placeholder="nome@exemplo.com" autocomplete="email" required>
        <button class="btn" type="submit">Subscrever</button>
        <div class="form-status" role="status" aria-live="polite"></div>
      </form>
      <ul class="footer-links" style="margin-top:1.5rem">{"".join(contacts)}</ul>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>© 2026 AMPR. Todos os direitos reservados.</p>
    <ul><li><a href="privacidade.html">Política de privacidade e de cookies</a></li></ul>
  </div>
</footer>'''


FONTS = ('<link rel="preload" href="assets/fonts/schibsted-grotesk.woff2" as="font" type="font/woff2" crossorigin>'
         '<link rel="preload" href="assets/fonts/atkinson-next.woff2" as="font" type="font/woff2" crossorigin>')


def page(filename, meta, body):
    title = meta["title"]
    desc = meta["description"]
    extra = meta.get("head", "")
    url = f"{SITE_URL}/{'' if filename == 'index.html' else filename}"
    body_cls = ""
    return f'''<!doctype html>
<html lang="pt-MZ">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0A5C3A">{'<meta name="robots" content="noindex">' if PREVIEW else ''}
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_MZ">
<meta property="og:site_name" content="AMPR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/img/ampr-logo.jpg">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="assets/css/styles.css">
<script>document.documentElement.classList.add("js")</script>
{extra}
</head>
<body{body_cls}>
<a class="skip-link" href="#conteudo">Saltar para o conteúdo</a>
{header(filename)}
<main id="conteudo">
{body}
</main>
{footer()}
<script src="assets/js/main.js" defer></script>
</body>
</html>
'''


def check_dashes(html, name):
    """Os travessões (— –) não entram no texto do site."""
    visible = re.sub(r"<!--.*?-->|<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    if re.search("[–—]", visible):
        print(f"  aviso: {name} tem travessões no texto")


def build():
    count = 0
    for src in sorted(SRC.glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--(.*?)-->", raw, re.S)
        meta = json.loads(m.group(1))
        body = render_tokens(raw[m.end():].strip())
        meta["head"] = render_tokens(meta.get("head", ""))
        html = page(src.name, meta, body)
        check_dashes(html, src.name)
        (OUT / src.name).write_text(html, encoding="utf-8")
        count += 1
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if p.name == 'index.html' else p.name}</loc></url>"
                   for p in sorted(SRC.glob("*.html")))
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"{count} páginas geradas em {OUT}")


if __name__ == "__main__":
    build()
