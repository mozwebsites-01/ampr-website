# Website da AMPR

Website institucional da Associação Moçambicana de Protecção Radiológica, construído a partir do documento *AMPR — Conteúdos do Website*. É HTML/CSS/JS estático, sem dependências.

## Estrutura

```
ampr-website/
├── build.py        ← gerador: junta cabeçalho/rodapé às páginas
├── src/            ← conteúdo de cada página (editar aqui)
└── site/           ← website final (publicar esta pasta)
    ├── *.html
    └── assets/ (css, js, img)
```

## Editar e gerar

1. Edite o texto em `src/<página>.html` (ou os contactos em `CONTACT` no topo de `build.py`).
2. Gere o site: `python3 build.py`
3. Pré-visualize: `python3 -m http.server 8090 --directory site` e abra http://localhost:8090

> Não edite os ficheiros em `site/*.html` directamente: são substituídos a cada `python3 build.py`.

## Publicar

Basta carregar o conteúdo da pasta `site/` para qualquer alojamento estático (Vercel, Netlify, GitHub Pages ou o servidor do domínio). Actualize `SITE_URL` em `build.py` com o domínio final.

## Fotografias

As fotografias actuais vêm do Freepik (descarregadas com a conta Premium, que dispensa a atribuição de autoria). Guarde o comprovativo de licença da conta.

| Ficheiro em `site/assets/img/` | Onde aparece | Imagem Freepik |
|---|---|---|
| `hero.jpg` | Banner da página inicial | Técnica de radiologia a preparar o aparelho de raios X |
| `foto-sobre.jpg` | Cabeçalho de Sobre Nós | Médico a analisar um exame |
| `foto-areas.jpg` | Cabeçalho de O Que Fazemos | Especialista a explicar um raio X |
| `foto-membros.jpg` | Cabeçalho de Membros | Equipa a discutir resultados de diagnóstico |
| `foto-actividades.jpg` | Cabeçalho de Actividades | Apresentação num seminário médico |
| `foto-seminario.jpg` | Notícia da jornada (imagem ilustrativa) | Plateia num seminário médico |

**Foto real da jornada:** guarde-a como `jornada.jpg` e gere de novo. Substitui automaticamente a imagem ilustrativa do seminário na página inicial, em Actividades e na notícia. Para trocar outra foto, use o mesmo nome de ficheiro (cerca de 1800 px de largura, JPG com menos de 400 KB).

**Galeria:** coloque as fotos das actividades em `site/assets/img/galeria/`.

## Formulários

Os formulários (adesão, contacto, newsletter) validam os campos, mas **ainda não enviam dados**. Para os ligar, crie um formulário num serviço como Formspree ou Getform (ou um servidor próprio) e coloque o URL no atributo `data-endpoint=""` do `<form>` em `src/membros.html`, `src/contactos.html` e no rodapé (`build.py`, função `footer`).

## Informação a fornecer pela AMPR

Os itens marcados com `TODO AMPR` no código:

- [ ] Telefone, WhatsApp, e-mail, endereço e horário (`CONTACT` em `build.py`). Campos vazios não aparecem; a barra superior com contactos só surge quando houver telefone ou e-mail
- [ ] Localização exacta no mapa (`src/contactos.html`)
- [ ] Ligações das redes sociais (`CONTACT` em `build.py`)
- [ ] Números reais para o contador (membros, eventos, províncias, parceiros). A secção está pronta, comentada em `src/index.html`
- [ ] Nomes dos titulares dos órgãos sociais (`src/sobre.html`)
- [ ] Categorias de membro, valores de jóia e quota, conforme os estatutos
- [ ] Data, local, temas e oradores da jornada (`src/noticia-jornada.html`, campos `[entre parênteses rectos]`)
- [ ] Próximas jornadas e formações, data de fundação e data da Assembleia Geral (`src/actividades.html`)
- [ ] Lista de parceiros com logótipos e ligações (`src/parceiros.html`)
- [ ] Confirmar que a lista de legislação está actualizada (`src/recursos.html`)
- [ ] Estatutos em PDF, apresentações e boletim (`src/recursos.html`)
- [ ] Logótipo em alta resolução (PNG transparente ou vector), em substituição de `ampr-logo.jpg`
- [ ] Domínio final (`SITE_URL` em `build.py`) e revisão jurídica da política de privacidade

## Tipografia

- Títulos: **Schibsted Grotesk**
- Texto: **Atkinson Hyperlegible Next** (desenhada pelo Braille Institute para máxima legibilidade)

As fontes estão em `site/assets/fonts/` (licença SIL Open Font License) e não dependem do Google Fonts.

## Regras de texto

O `build.py` avisa se alguma página tiver travessões (— ou –) no texto. Use vírgula, ponto ou dois pontos.

## Publicação

O site está publicado no GitHub Pages: https://mozwebsites-01.github.io/ampr-website/

Cada `git push` para `main` volta a publicar a pasta `site/` automaticamente (`.github/workflows/pages.yml`). Corra `python3 build.py` antes do commit.

Enquanto o endereço for o do GitHub Pages, o site está marcado para não ser indexado pelo Google (`noindex`). Ao mudar `SITE_URL` em `build.py` para o domínio final, essa marca sai sozinha.
