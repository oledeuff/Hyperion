#!/usr/bin/env python3
"""Build the public, static HyperION pages. No network or account credentials."""
from pathlib import Path
from html import escape
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
VERSION = '2026.11.24-rc2'
DATE = '24 novembre 2026'
BASELINE = 'fc9707f41135dcb8849a14e0ed4cdf52c8ae8129'

def i18n(fr, en, tag='span', attrs=''):
    return f'<{tag} data-fr="{escape(fr, quote=True)}" data-en="{escape(en, quote=True)}" {attrs}>{escape(fr)}</{tag}>'

MARK = '''<svg class="brand-mark" viewBox="0 0 64 64" fill="none" aria-hidden="true"><path d="M10 11H40V41H10zM24 24H54V54H24z" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M10 11L24 24M40 11L54 24M40 41L54 54M10 41L24 54" stroke="currentColor" stroke-width="1.5"/><circle cx="40" cy="11" r="3" fill="#f9968b"/><circle cx="24" cy="54" r="3" fill="#1db6c3"/></svg>'''

NAV = [
 ('index.html', 'L’hypercube', 'The hypercube'),
 ('presentation.html', 'Le projet', 'The project'),
 ('recherches.html', 'Axes de recherche', 'Research areas'),
 ('travaux.html', 'Travaux & actualités', 'Work & updates'),
 ('publications.html', 'Publications', 'Publications'),
 ('explorations.html', 'Explorations visuelles', 'Visual explorations'),
 ('ressources.html', 'Corpus & ressources', 'Corpora & resources'),
 ('syllabus/', 'Enseignement', 'Teaching'),
 ('accessibilite.html', 'Accessibilité', 'Accessibility'),
]

def page(filename, title, description, body, mainclass='document-main'):
    nav = ''.join(f'<a href="{href}"'+(' aria-current="page"' if href==filename else '')+'>'+i18n(fr,en)+'</a>' for href,fr,en in NAV)
    html = f'''<!doctype html>
<html lang="fr" data-theme="light"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · HyperION</title>
<meta name="description" content="{escape(description, quote=True)}">
<meta name="robots" content="noindex,follow">
<meta name="hyperion-version" content="{VERSION}">
<meta name="theme-color" content="#080f1c">
<link rel="icon" type="image/svg+xml" href="favicon-hyperion.svg">
<link rel="stylesheet" href="assets/site.css?v={VERSION}">
<script defer src="assets/site.js?v={VERSION}"></script>
</head><body>
<a class="skip-link" href="#main-content">{i18n('Aller au contenu','Skip to content')}</a>
<header class="topbar"><div class="header-inner">
<a class="brand" href="index.html" aria-label="HyperION — accueil">{MARK}<span class="brand-text"><span class="brand-title">HyperION</span>{i18n('Méthodes et technologies de l’hyperinvestigation','Methods and technologies of hyperinvestigation', attrs='class="brand-subtitle"')}</span></a>
<div class="topbar-controls">
<button id="lang-toggle" class="control" type="button" data-js-only aria-label="Read this page in English"><span data-lang-label="fr" class="lang-current">FR</span><span aria-hidden="true">/</span><span data-lang-label="en">EN</span></button>
<button id="theme-toggle" class="control" type="button" data-js-only aria-label="Thème clair" aria-pressed="true"><span data-theme-symbol aria-hidden="true">◐</span>{i18n('Thème','Theme',attrs='class="control-label"')}</button>
<details class="menu-disclosure"><summary class="control" aria-label="Menu" aria-controls="main-nav"><span aria-hidden="true">☰</span> {i18n('Menu','Menu',attrs='class="control-label"')}</summary><nav class="main-nav" id="main-nav" aria-label="Navigation principale">{nav}</nav></details>
</div></div></header>
<div class="test-notice">{i18n('Version de test sur GitHub Pages','Test version on GitHub Pages',tag='strong')} · {VERSION}</div>
<main id="main-content" class="{mainclass}" tabindex="-1">{body}</main>
<footer class="site-footer"><div class="footer-inner"><div><p>HyperION · Olivier Le Deuff · IUF 2025–2030</p><p>Université Bordeaux Montaigne · Laboratoire MICA</p><p>{i18n('Mise à jour','Updated')} {DATE} · CC BY</p></div><div class="footer-links"><a href="accessibilite.html">{i18n('Accessibilité','Accessibility')}</a><a href="ressources.html">{i18n('Ressources','Resources')}</a><a href="https://github.com/oledeuff/Hyperion">GitHub</a><a href="mailto:oledeuff@gmail.com">Contact</a></div></div></footer>
</body></html>'''
    (DOCS/filename).write_text(re.sub(r'(?m)^[ \t]+$', '', html), encoding='utf-8')

def block(fr, en):
    return f'<div class="lang-block" data-lang="fr">{fr}</div><div class="lang-block" data-lang="en" lang="en">{en}</div>'

def heading(kicker, title, lead):
    return f'<div class="page-heading"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p class="lead">{lead}</p></div>'

def toc(items, en=False):
    return '<aside class="page-aside"><h2>'+('On this page' if en else 'Dans cette page')+'</h2><ul class="page-aside-list">'+''.join(f'<li><a href="#{id}">{label}</a></li>' for id,label in items)+'</ul><div class="page-aside-meta"><a href="index.html">'+('Back to the hypercube' if en else 'Retour à l’hypercube')+'</a></div></aside>'

def original_page(name):
    source = subprocess.check_output(['git','show',f'{BASELINE}:docs/{name}'],cwd=ROOT,text=True)
    articles = re.findall(r'(<article class="page-article">[\s\S]*?</article>)',source)
    asides = re.findall(r'<aside class="page-aside">([\s\S]*?)</aside>',source)
    rendered=[]
    for j,article in enumerate(articles):
        article=re.sub(r'<figure class="hero-figure">[\s\S]*?</figure>','',article)
        article=re.sub(r'<div class="content-note">[\s\S]*?</div>','',article)
        article=article.replace('HYPERInvestigatON','hyperinvestigation')
        article=re.sub(r'(<h[23][^>]*>)\d+(?:\.\d+)*\.\s*',r'\1',article)
        # Correct two bibliographic records already identifiable in HAL; retain the full prose.
        article=article.replace('Le Deuff, O. (2021). <em>Hyperdocumentation.</em> ISTE Editions.', 'Le Deuff, O. (2022). <em>Hyperdocumentation.</em> ISTE Éditions. <span class="figure-caption">Version anglaise publiée en 2021.</span>')
        side=asides[j] if j<len(asides) else ''
        links=re.findall(r'<a href="#([^"]+)">([^<]+)</a>',side)
        links=[(id,re.sub(r'^\d+(?:\.\d+)*\.\s*','',label)) for id,label in links]
        language='fr' if j==0 else 'en'
        rendered.append(f'<div class="page-main lang-block" data-lang="{language}"'+(' lang="en"' if j else '')+'>'+article+toc(links,j>0)+'</div>')
    return ''.join(rendered)

ENTRIES = [
 ('presentation.html','#1db6c3','Le projet','The project','Chaire IUF 2025–2030','IUF chair 2025–2030','Une enquête sur les méthodes, les documents et les technologies qui transforment les pratiques d’investigation.','Investigating the methods, documents and technologies that transform investigative practices.'),
 ('recherches.html#epistemologie','#76cdcd','Épistémologie','Epistemology','Histoire & concepts','History & concepts','Retracer les cultures de l’enquête, de l’héritage documentaire aux régimes contemporains de preuve.','Tracing cultures of inquiry, from documentary traditions to contemporary forms of evidence.'),
 ('recherches.html#pratiques','#f9968b','Pratiques & méthodes','Practices & methods','Corpus & terrains','Corpora & fieldwork','Étudier les opérations d’enquête, les usages de l’IA et les médiations de la preuve.','Studying investigative operations, the uses of AI and the mediation of evidence.'),
 ('ressources.html#cosma','#f27438','Ingénierie documentaire','Documentary engineering','Fiches, liens & graphes','Records, links & graphs','Organiser les documents et qualifier leurs relations. Cosma et les expérimentations du projet prolongent ce travail.','Organising documents and qualifying their relationships through Cosma and the project’s experiments.'),
 ('recherches.html#hyperlitteratie','#83c9c7','Hyperlittératie','Hyperliteracy','Lire, enquêter & transmettre','Reading, inquiry & transmission','Articuler les capacités informationnelles, techniques et politiques nécessaires pour conduire et comprendre une enquête.','Connecting the informational, technical and political capacities needed to conduct and understand an investigation.'),
 ('travaux.html','#f6bf8b','Travaux & actualités','Work & updates','Depuis 2025','Since 2025','Retrouver les publications, les ressources et les expérimentations qui nourrissent la première année d’HyperION.','Explore the publications, resources and experiments contributing to HyperION’s first year.'),
 ('publications.html','#6fcfbd','Publications','Publications','Textes & communications','Papers & conference contributions','Lire les travaux récents, leurs références complètes et leurs versions accessibles.','Read recent work, full bibliographic references and available versions.'),
 ('explorations.html','#9ab6f6','Explorations visuelles','Visual explorations','Un atelier de recherche','A research workshop','Parcourir les fiches des strates et la boîte à billes de Rouletabille.','Browse the strata records and Rouletabille’s box of marbles.'),
 ('ressources.html','#c3b5e9','Corpus & ressources','Corpora & resources','MatrioscIA, Osintosphère & Cosma','MatrioscIA, Osintosphere & Cosma','Accéder aux rapports, aux dépôts et aux ressources documentaires associés au programme.','Access the reports, repositories and documentary resources associated with the programme.'),
 ('syllabus/','#9dcbe9','Enseignement','Teaching','Hyperinvestigation · 2026–2027','Hyperinvestigation · 2026–2027','Un syllabus évolutif et cinq supports de cours pour travailler les traces, les littératies et les protocoles d’enquête.','An evolving syllabus and five course resources on traces, literacies and investigative protocols.'),
 ('https://cv.hal.science/olivier-le-deuff','#b7cebc','Olivier Le Deuff','Olivier Le Deuff','Université Bordeaux Montaigne · MICA','Bordeaux Montaigne University · MICA','Professeur en sciences de l’information et de la communication, membre senior de l’Institut universitaire de France.','Professor of information and communication sciences and senior member of the Institut universitaire de France.'),
 ('https://github.com/oledeuff/Hyperion','#c7d4e8','Code & versions','Code & versions','Recherche ouverte','Open research','Le dépôt public conserve les sources du site, les fiches et les expérimentations.','The public repository holds the website source, records and experiments.'),
]
entries=[dict(href=e[0],color=e[1],title={'fr':e[2],'en':e[3]},tag={'fr':e[4],'en':e[5]},description={'fr':e[6],'en':e[7]}) for e in ENTRIES]

def cube_fallback():
    geometry_script = "import {projectVertices,edges,primaryNodes} from './docs/assets/hypercube-geometry.js'; console.log(JSON.stringify({points:projectVertices(),edges,nodes:primaryNodes}));"
    geometry=json.loads(subprocess.check_output(['node','--input-type=module','-e',geometry_script],cwd=ROOT,text=True))
    points=[((v[0]+1)*400,(1-v[1])*235) for v in geometry['points']]
    svg=['<svg class="fallback-cube" viewBox="180 -10 420 420" role="group" aria-label="Tesseract et accès aux rubriques">']
    svg.append('<g class="cube-faces" aria-hidden="true">')
    for face in [[0,1,3,2],[0,2,6,4],[0,1,5,4]]:
        svg.append('<polygon points="'+' '.join(f'{points[i][0]:.2f},{points[i][1]:.2f}' for i in face)+'"/>')
    svg.append('</g><g fill="none" stroke-linecap="round" aria-hidden="true">')
    for a,b in geometry['edges']:
        kind='cube-spoke' if (a<8)!=(b<8) else 'cube-outer' if a<8 else 'cube-inner'
        x1,y1=points[a];x2,y2=points[b]
        svg.append(f'<line class="{kind}" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" vector-effect="non-scaling-stroke"/>')
    svg.append('</g>')
    for node in geometry['nodes']:
        e=entries[node['entry']];x,y=points[node['vertex']]
        label=e['title']['fr'];english=e['title']['en']
        svg.append(f'<a class="cube-hotspot" href="{e["href"]}" data-entry-index="{node["entry"]}" aria-label="{escape(label,quote=True)}" data-i18n-aria data-fr="{escape(label,quote=True)}" data-en="{escape(english,quote=True)}"><title>{escape(label)}</title><circle cx="{x:.2f}" cy="{y:.2f}" r="27" fill="transparent"/><circle class="cube-hotspot-ring" cx="{x:.2f}" cy="{y:.2f}" r="13"/><circle class="cube-hotspot-core" cx="{x:.2f}" cy="{y:.2f}" r="7"/></a>')
    return ''.join(svg)+'</svg>'

FALLBACK=cube_fallback()

PUBS = [
 dict(id='osint-literacies',year=2026,type='chapitre',status='Paru',authors='Olivier Le Deuff, Rayya Roumanos, Thais Barbosa de Almeida',title='OSINT and Literacies: Towards a Political and Technical Vision of Information and Media Literacies',venue='Information Literacy in an AI-Driven World, Communications in Computer and Information Science, vol. 2864, Springer, p. 312–323.',description='Les pratiques d’enquête en sources ouvertes nourrissent une approche politique et technique des littératies informationnelles et médiatiques.',en='Open-source investigative practices inform a political and technical approach to information and media literacies.',links=[('HAL','https://hal.science/hal-05579644v1'),('DOI','https://doi.org/10.1007/978-3-032-17272-3_26')],source='https://www.iut.u-bordeaux-montaigne.fr/notre-institut/recherche/publications/2026-osint-and-literacies-towards-a-political-and-technical-vision-of-information-and-media-literacies/'),
 dict(id='boutcha',year=2026,type='chapitre',status='Paru',authors='Olivier Le Deuff, Rayya Roumanos',title='OSINT et Imago : Boutcha comme lieu de mémoire du journalisme d’investigation',venue='Faire preuve par l’image ? Enquêtes filmiques, usages judiciaires et enjeux esthétiques, p. 36–55. ISBN 978-2-37896-583-9.',description='L’étude du massacre de Boutcha interroge le travail des images, leur transformation en preuves et la mémoire documentaire de l’événement.',en='The study of the Bucha massacre examines images, their transformation into evidence and the documentary memory of the event.',links=[('HAL','https://hal.science/hal-05672743v1')],source='https://www.iut.u-bordeaux-montaigne.fr/notre-institut/recherche/publications/2026-osint-et-imago-boutcha-comme-lieu-de-memoire-du-journalisme-d-investigation/'),
 dict(id='question-algorithmique',year=2026,type='chapitre',status='Paru',authors='Rayya Roumanos, Olivier Le Deuff',title='S’emparer de la question algorithmique : un triple défi socio-professionnel, technique et épistémique pour les journalistes',venue='(Des)ordres informationnels. Journalisme, IA & Datas, p. 62–94. ISBN 978-2-493458-47-6.',description='Une analyse des compétences et des conditions professionnelles requises pour enquêter sur les systèmes algorithmiques.',en='An analysis of the skills and professional conditions required to investigate algorithmic systems.',links=[('HAL','https://hal.science/hal-05672699v1')],source='https://cv.hal.science/olivier-le-deuff'),
 dict(id='mediation-donnees',year=2026,type='article',status='Paru',authors='Ugo Verdi, Olivier Le Deuff, Nathalie Pinède',title='Repenser la culture des données à travers une première étude exploratoire du concept de médiation des données',venue='Approches Théoriques en Information-Communication, n° 12 (2), p. 235–255.',description='Une étude exploratoire du travail de médiation qui rend les données intelligibles et discutables.',en='An exploratory study of the mediation work that makes data understandable and open to discussion.',links=[('HAL','https://hal.science/hal-05713888v1'),('DOI','https://doi.org/10.3917/atic.012.0235')],source='https://cv.hal.science/olivier-le-deuff'),
 dict(id='pocl',year=2026,type='actes',status='Paru',authors='Olivier Le Deuff',title='Des données à l’objet. Les POCL (Petits objets connectés ludiques) entre culture technique et œuvre ouverte',venue='Dans Fabrique des données dans les organisations. Nouvelles épistémologies, pratiques et gouvernances, actes de CiDE.24, dir. Nathalie Pinède, Ugo Verdi et Guy Melançon. Europia. ISBN 979-10-90094-78-9. Communication initiale en novembre 2025.',description='Les petits objets connectés interrogent la culture technique, l’expérimentation et les formes ouvertes de production de connaissances.',en='Small connected objects raise questions about technical culture, experimentation and open forms of knowledge production.',links=[('Éditeur','https://europia.org/edition/livres/doc/Cide24.htm'),('HAL · communication 2025','https://shs.hal.science/halshs-05379049v2')],source='https://europia.org/edition/livres/doc/Cide24.htm'),
 dict(id='matrioscia',year=2025,type='rapport',status='Rapport disponible',authors='Olivier Le Deuff, Rayya Roumanos',title='Rapport final du projet MatrioscIA. MATRIce Osint pour les Cas d’usage de l’IA',venue='Institut des hautes études du ministère de l’Intérieur ; MICA. Novembre 2025.',description='Un projet lancé avant HyperION, dont les résultats alimentent le programme IUF. Le rapport examine les usages de l’IA dans l’OSINT et leurs conditions techniques, professionnelles et éthiques.',en='A project launched before HyperION whose results inform the IUF programme. The report studies AI in OSINT and its technical, professional and ethical conditions.',links=[('HAL','https://shs.hal.science/halshs-05404123v1'),('Dépôt du projet','https://github.com/oledeuff/MatrioscIA')],source='https://www.iut.u-bordeaux-montaigne.fr/notre-institut/recherche/publications/2025-rapport-final-du-projet-matrioscia-matrice-osint-pour-les-cas-d-usage-de-l-ia/'),
 dict(id='orbicom',year=2025,type='communication',status='Communication déposée',authors='Rayya Roumanos, Thais Barbosa de Almeida, Olivier Le Deuff',title='Le recours à l’IA dans les enquêtes OSINT : innover depuis les marges',venue='Congrès Orbicom – GTnum – ITI LiRic CIAREI, « Communication, intelligence artificielle, remédiation, éthique et inclusion », Strasbourg, septembre 2025.',description='Cette communication précède l’entrée à l’IUF et documente les usages de l’IA dans les enquêtes en sources ouvertes.',en='This conference contribution predates the IUF appointment and documents the use of AI in open-source investigations.',links=[('HAL','https://hal.science/hal-05311206v1')],source='https://cv.hal.science/olivier-le-deuff'),
]

def home():
    first=entries[0]
    shortcuts=''.join(f'<a href="{entries[i]["href"]}" data-entry-index="{i}">{i18n(entries[i]["title"]["fr"],entries[i]["title"]["en"])}</a>' for i in [0,1,2,3,6,8])
    listing=''.join(f'<li><a href="{e["href"]}" data-entry-index="{i}">{i18n(e["title"]["fr"],e["title"]["en"])}</a></li>' for i,e in enumerate(entries))
    body=f'''<div class="hypercube-layout"><section class="scene-shell" aria-labelledby="home-title"><div class="scene-heading"><div class="eyebrow">{i18n('Chaire de recherche IUF · 2025–2030','IUF research chair · 2025–2030')}</div><h1 id="home-title">{i18n('Les dimensions de l’hyperinvestigation','Dimensions of hyperinvestigation')}</h1><p class="lead">{i18n('Comment enquêter dans un monde hyperdocumenté ? HyperION étudie les documents, les méthodes et les technologies qui rendent les événements intelligibles et les preuves discutables.','How do we investigate a hyperdocumented world? HyperION studies the documents, methods and technologies that make events intelligible and evidence open to scrutiny.')}</p></div>
<div class="scene-stage" id="hypercube-stage">{FALLBACK}<span class="scene-mode" id="scene-mode">{i18n('Tesseract · accès directs','Tesseract · direct links')}</span></div><nav class="cube-shortcuts" aria-label="Accès directs du tesseract">{shortcuts}</nav>
<div class="scene-tools"><button type="button" class="control" id="scene-pause" aria-pressed="false" data-js-only disabled>{i18n('Mettre en pause','Pause animation')}</button><button type="button" class="control" id="scene-reset" data-js-only disabled>{i18n('Réinitialiser la vue','Reset view')}</button><a href="explorations.html">{i18n('Les explorations visuelles','Visual explorations')}</a></div><p class="scene-help">{i18n('Cliquez sur un point coloré ou choisissez un lien sous le cube pour ouvrir une rubrique.','Click a coloured point or choose a link below the cube to open a section.', attrs='id="scene-help-text"')}</p></section>
<aside class="entry-panel" aria-label="Entrées du projet"><p class="entry-caption">{i18n('Explorer le projet','Explore the project')}</p><article class="entry-card" id="entry-card"><span class="entry-tag" id="entry-tag">{i18n(first['tag']['fr'],first['tag']['en'])}</span><h2 id="entry-title">{i18n(first['title']['fr'],first['title']['en'])}</h2><p id="entry-description">{i18n(first['description']['fr'],first['description']['en'])}</p><a class="button-link" id="entry-link" href="presentation.html">{i18n('Explorer cette rubrique','Explore this section')}</a></article><ul class="entry-list">{listing}</ul></aside></div>
<section class="home-section" aria-labelledby="recent-title"><div class="section-title-line"><h2 id="recent-title">{i18n('Le programme en mouvement','The programme in motion')}</h2><a href="travaux.html">{i18n('Tous les travaux','All work')}</a></div><div class="work-grid">
<article class="work-item"><div class="meta">{i18n('2026 · Littératies & enquête','2026 · Literacies & inquiry')}</div><h3>OSINT and Literacies</h3><p>{i18n('Un chapitre avec Rayya Roumanos et Thais Barbosa de Almeida pour penser ensemble les dimensions techniques et politiques de l’enquête.','A chapter with Rayya Roumanos and Thais Barbosa de Almeida connecting the technical and political dimensions of investigation.')}</p><a href="publications.html#osint-literacies">{i18n('Lire la référence','Read the reference')}</a></article>
<article class="work-item"><div class="meta">{i18n('2025–2026 · IA & pratiques OSINT','2025–2026 · AI & OSINT practices')}</div><h3>{i18n('Les prolongements de MatrioscIA','Building on MatrioscIA')}</h3><p>{i18n('Le rapport final, les ressources documentaires et l’analyse des usages de l’IA alimentent le chantier sur les méthodes d’hyperinvestigation.','The final report, documentary resources and analysis of AI practices inform the study of hyperinvestigation methods.')}</p><a href="ressources.html#matrioscia">{i18n('Consulter les ressources','Browse the resources')}</a></article>
<article class="work-item"><div class="meta">{i18n('2026–2027 · Enseignement','2026–2027 · Teaching')}</div><h3>{i18n('L’enquête comme atelier','Inquiry as a workshop')}</h3><p>{i18n('Le cours Hyperinvestigation relie hyperlittératie, traces, algorithmes et documentation du protocole. Le syllabus donne accès aux cinq premiers supports.','The Hyperinvestigation course connects hyperliteracy, traces, algorithms and protocol documentation. The syllabus links to the first five course resources.')}</p><a href="syllabus/">{i18n('Ouvrir le syllabus','Open the syllabus')}</a></article></div></section>
<section class="home-section" aria-labelledby="axes-title"><div class="section-title-line"><h2 id="axes-title">{i18n('Trois axes qui se croisent','Three intersecting research areas')}</h2><a href="recherches.html">{i18n('Parcourir les recherches','Browse research')}</a></div><div class="axes-list"><article><h3>{i18n('Épistémologie','Epistemology')}</h3><p>{i18n('Retracer les cultures de l’enquête et examiner comment des traces acquièrent une valeur de preuve.','Tracing cultures of inquiry and examining how traces acquire evidential value.')}</p></article><article><h3>{i18n('Pratiques','Practices')}</h3><p>{i18n('Observer les méthodes et les opérations documentaires des journalistes, des chercheurs et des collectifs d’investigation.','Studying the methods and documentary operations of journalists, researchers and investigative collectives.')}</p></article><article><h3>{i18n('Ingénierie','Engineering')}</h3><p>{i18n('Expérimenter des instruments qui relient les documents, explicitent leurs transformations et donnent à discuter les résultats.','Experimenting with tools that connect documents, make transformations explicit and open findings to discussion.')}</p></article></div></section>
<script type="application/json" id="hypercube-entries">{json.dumps(entries,ensure_ascii=False)}</script><script type="module" src="assets/hypercube.js?v={VERSION}"></script>'''
    page('index.html','Méthodes et technologies de l’hyperinvestigation','HyperION, chaire IUF 2025–2030 portée par Olivier Le Deuff. Épistémologie, pratiques et ingénierie de l’hyperinvestigation.',body,'home-main')

def research():
    fr=heading('Programme scientifique','De la documentation aux régimes de preuve','HyperION étudie l’enquête au croisement des sciences de l’information et de la communication, des cultures documentaires et du journalisme. Trois axes organisent le programme et se rencontrent dans les mêmes corpus.')
    fr+='''<h2 id="epistemologie">Épistémologie de l’hyperinvestigation</h2><p>Un document conserve les conditions d’une observation, mais son interprétation demande un travail d’enquête. Cet axe reconstruit les généalogies documentaires et techniques de ce travail. Il rapproche l’hyperdocumentation de Paul Otlet des cultures forensic et des pratiques d’investigation contemporaines.</p><p>Les figures de l’enquête, notamment les détectives de fiction, offrent un autre terrain pour étudier le repérage des indices, l’abduction et les manières de rendre une démonstration intelligible. Les travaux sur Rouletabille et les strates de l’hyperinvestigation prolongent cette exploration.</p><p class="paired-links"><a href="epistemologie.html">Lire le cadre épistémologique</a><a href="rouletabille.html">Explorer Rouletabille</a></p>
<h2 id="pratiques">Pratiques et méthodes</h2><p>Les enquêtes en sources ouvertes combinent des documents de provenances et de temporalités différentes. L’analyse porte sur les opérations qui les collectent, les confrontent et les transforment, puis sur les récits et les preuves qui en résultent.</p><p>Le programme prolonge les recherches d’Osintoscope et de MatrioscIA. Il examine les usages de l’IA, les formes du journalisme hyperdocumenté et la distinction entre une relation repérée et une relation suffisamment documentée pour soutenir une affirmation. Le corpus d’hyperinvestigations demeure un chantier de recherche.</p><p class="paired-links"><a href="typologie.html">Parcourir la typologie</a><a href="ressources.html#matrioscia">Retrouver MatrioscIA</a></p>
<h2 id="ingenierie">Ingénierie documentaire et logicielle</h2><p>Une fiche, un graphe et un document rendent visibles des aspects différents d’une enquête. Les expérimentations associent ces formes pour conserver la provenance des pièces et qualifier les relations. Elles prolongent le travail mené autour de Cosma, conçu par Arthur Perret et développé par Guillaume Brioudes.</p><p>La perspective d’une version de Cosma dédiée à l’hyperinvestigation, désignée comme « Skritch » dans le programme, relève du développement en cours. Les prototypes disponibles sur ce site explorent déjà les strates, les espaces de relations et les accès aux fiches.</p><p><a href="explorations.html">Ouvrir l’atelier d’explorations</a></p>
<h2 id="hyperlitteratie">Hyperlittératie et transmission</h2><p>Comprendre une enquête demande de lire les documents, d’évaluer les traitements et d’apprécier les conditions de sa démonstration. L’hyperlittératie articule ces capacités à une culture technique et politique de l’information. Elle engage aussi les collectifs, leurs outils et leurs infrastructures documentaires.</p><p>Les travaux sur les littératies OSINT et la question algorithmique alimentent cette réflexion. Le cours Hyperinvestigation en constitue un espace d’expérimentation pédagogique, où l’on travaille les traces, les hypothèses et la construction d’un protocole révisable.</p><h2 id="paradata">Documenter le cheminement</h2><p>La provenance indique d’où vient une pièce. Les paradata éclairent les opérations, les choix et les transformations qui accompagnent son traitement. Les conserver aide à comprendre comment une conclusion a été produite, à en discuter les limites et à reprendre une partie de l’enquête.</p><p class="paired-links"><a href="publications.html#osint-literacies">OSINT and Literacies</a><a href="syllabus/">Syllabus Hyperinvestigation</a></p>'''
    en=heading('Research programme','From documentation to evidential practices','HyperION studies inquiry at the intersection of information and communication sciences, documentary cultures and journalism. Three research areas intersect within shared corpora.')
    en+='''<h2 id="epistemologie-en">Epistemology of hyperinvestigation</h2><p>This area reconstructs the documentary and technical genealogies of investigation, connecting Paul Otlet’s hyperdocumentation with forensic cultures and contemporary investigative practices.</p><p>Fictional detectives provide a further perspective on clues, abduction and the intelligibility of a demonstration. The Rouletabille and strata experiments extend this research.</p><p><a href="epistemologie.html">Read the epistemological framework</a></p><h2 id="pratiques-en">Practices and methods</h2><p>Open-source investigations combine documents from different sources and time frames. This research examines the operations that collect, compare and transform them, and the evidence and narratives that result.</p><p>It builds on Osintoscope and MatrioscIA, studying AI practices, hyperdocumented journalism and the difference between a detected relationship and a documented evidential claim. The hyperinvestigation corpus is an ongoing research project.</p><p><a href="typologie.html">Browse the typology</a></p><h2 id="ingenierie-en">Documentary and software engineering</h2><p>Records, graphs and documents reveal different aspects of an investigation. Experiments connect these forms to preserve provenance and qualify relationships. They build on Cosma, designed by Arthur Perret and developed by Guillaume Brioudes.</p><p>A dedicated hyperinvestigation version of Cosma, referred to as “Skritch” in the programme, remains a development prospect. Existing prototypes explore strata, relationships and access to documentary records.</p><p><a href="explorations.html">Open the visual workshop</a></p><h2 id="hyperlitteratie-en">Hyperliteracy and teaching</h2><p>Understanding an investigation requires reading documents, assessing transformations and examining the conditions of a demonstration. Hyperliteracy connects these capacities with a technical and political culture of information, including the collective organisation of tools and documentary infrastructures.</p><p>Work on OSINT literacies and algorithmic literacy informs the Hyperinvestigation course, where students study traces, hypotheses and revisable investigative protocols.</p><h2 id="paradata-en">Documenting the process</h2><p>Provenance records where a document comes from. Paradata describe the operations, choices and transformations involved in processing it. Preserving them helps readers understand how a conclusion was produced, discuss its limits and revisit part of an investigation.</p><p><a href="syllabus/">Hyperinvestigation syllabus</a></p>'''
    content='<div class="page-main lang-block" data-lang="fr"><article class="page-article">'+fr+'</article>'+toc([('epistemologie','Épistémologie'),('pratiques','Pratiques'),('ingenierie','Ingénierie'),('hyperlitteratie','Hyperlittératie'),('paradata','Paradata')])+'</div>'
    content+='<div class="page-main lang-block" data-lang="en" lang="en"><article class="page-article">'+en+'</article>'+toc([('epistemologie-en','Epistemology'),('pratiques-en','Practices'),('ingenierie-en','Engineering'),('hyperlitteratie-en','Hyperliteracy'),('paradata-en','Paradata')],True)+'</div>'
    page('recherches.html','Axes de recherche','Épistémologie, pratiques et ingénierie. Hyperlittératie, provenance et paradata dans le programme HyperION.',content)

def publications():
    intro=block(heading('Textes & communications','Publications récentes','Une sélection de travaux parus ou déposés depuis 2025, associés aux axes d’HyperION et aux projets qui le précèdent. Les références distinguent le rapport, les articles, les chapitres et les communications.'),heading('Papers & conference contributions','Recent publications','A selection of work published or deposited since 2025, associated with HyperION and the projects on which it builds. Reports, articles, chapters and conference contributions are identified separately.'))
    filters=f'''<form class="filters" role="search" data-js-only onsubmit="return false"><label for="publication-search">{i18n('Rechercher un titre, un auteur, un thème','Search by title, author or topic')}<input id="publication-search" type="search" autocomplete="off"></label><label for="publication-year">{i18n('Année','Year')}<select id="publication-year"><option value="">2025–2026</option><option value="2026">2026</option><option value="2025">2025</option></select></label><label for="publication-type">{i18n('Type de document','Document type')}<select id="publication-type"><option value="">Tous / All</option><option value="article">Article</option><option value="chapitre">Chapitre / Chapter</option><option value="actes">Actes / Proceedings</option><option value="rapport">Rapport / Report</option><option value="communication">Communication</option></select></label></form><p class="filter-count" id="publication-count" role="status" aria-live="polite">7 références</p><p id="publication-empty" hidden>{i18n('Aucune référence ne correspond à ces critères.','No reference matches these criteria.')}</p>'''
    records=[]
    status_en={'Paru':'Published','Rapport disponible':'Report available','Communication déposée':'Conference contribution deposited'}
    for p in PUBS:
        links=''.join(f'<a href="{url}">{escape(label)}</a>' for label,url in p['links'])
        records.append(f'''<article class="publication" id="{p['id']}" data-year="{p['year']}" data-type="{p['type']}"><div class="publication-year">{p['year']}</div><div><span class="status">{i18n(p['status'],status_en[p['status']])}</span><h2>{escape(p['title'])}</h2><p class="citation">{escape(p['authors'])}. ({p['year']}). <em>{escape(p['venue'])}</em></p><p class="description">{i18n(p['description'],p['en'])}</p><div class="resource-links">{links}</div></div></article>''')
    note=f'<p class="source-note">{i18n("Les dates suivent les notices bibliographiques et les pages des éditeurs. Une communication de 2025 peut avoir donné lieu à une publication en 2026. Cette sélection ne vaut pas bibliographie exhaustive.","Dates follow bibliographic records and publisher pages. A 2025 conference contribution may have been published in 2026. This selection is not an exhaustive bibliography.")} <a href="https://cv.hal.science/olivier-le-deuff">{i18n("Bibliographie complète sur HAL","Full bibliography on HAL")}</a>.</p>'
    page('publications.html','Publications','Publications 2025–2026 liées à HyperION, à l’OSINT, aux littératies et à l’ingénierie documentaire.',intro+filters+''.join(records)+note)
    data={'version':VERSION,'checked_on':'2026-11-24','selection':'Public references only. No private records or draft attachments.','publications':PUBS}
    (DOCS/'data').mkdir(exist_ok=True)
    (DOCS/'data/publications.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def work():
    items=[
     ('2026','Parutions','Published work','Littératies, images et données','Literacies, images and data','Les travaux publiés en 2026 portent sur les littératies OSINT, les images de Boutcha, la question algorithmique dans le journalisme, la médiation des données et les POCL. Ils donnent plusieurs prises sur les axes du programme.','The 2026 publications address OSINT literacies, images from Bucha, the algorithmic question in journalism, data mediation and small connected objects. They inform several areas of the programme.','publications.html','Lire les publications','Read the publications'),
     ('Oct. 2026','Ressource disponible','Available resource','Le cours Hyperinvestigation','The Hyperinvestigation course','Le syllabus 2026–2027 relie responsabilité des organisations, architecture de l’information et conduite d’enquête. Cinq supports accessibles abordent l’hyperinvestigation, les cultures de l’enquête, l’hyperlittératie, les traces et le protocole.','The 2026–2027 syllabus connects organisational accountability, information architecture and investigative practice. Five course resources address hyperinvestigation, cultures of inquiry, hyperliteracy, traces and protocols.','syllabus/','Consulter le syllabus','Browse the syllabus'),
     ('2025–2026','Prototypes disponibles','Available prototypes','Un atelier de représentations','An experimental visual workshop','Les pages consacrées aux strates et à Rouletabille organisent des accès aux fiches et mettent à l’épreuve différentes représentations de l’enquête. Ces objets conservent leur statut d’expérimentations.','Pages on strata and Rouletabille provide access to documentary records and test different representations of inquiry. They remain experimental prototypes.','explorations.html','Explorer les prototypes','Explore the prototypes'),
     ('Nov. 2025','Rapport disponible','Report available','MatrioscIA, un point d’appui','MatrioscIA as a starting point','Lancé avant la chaire IUF, MatrioscIA donne lieu à un rapport final et à des ressources sur les usages de l’IA dans les enquêtes OSINT. Ces résultats alimentent les recherches méthodologiques d’HyperION.','Launched before the IUF chair, MatrioscIA produced a final report and resources on AI in OSINT investigations. Its findings inform HyperION’s methodological research.','ressources.html#matrioscia','Retrouver le rapport et les ressources','Find the report and resources'),
     ('Nov. 2025','Communication puis actes','Conference contribution and proceedings','Des données à l’objet','From data to objects','La contribution à CiDE.24 porte sur les Petits objets connectés ludiques, la culture technique et l’œuvre ouverte. Les actes sont publiés chez Europia en 2026.','The CiDE.24 contribution examines small connected objects, technical culture and the open work. The proceedings were published by Europia in 2026.','publications.html#pocl','Consulter la référence','Read the reference'),
    ]
    introduction=block(heading('Première année · 2025–2026','Les travaux d’HyperION','Depuis l’entrée à l’IUF à l’automne 2025, les publications, les corpus et les expérimentations prolongent un travail antérieur sur la documentation et les littératies. Cette page rassemble les résultats accessibles et précise les chantiers encore ouverts.'),heading('First year · 2025–2026','HyperION at work','Since the IUF appointment in autumn 2025, publications, corpora and experiments have extended earlier work on documentation and literacies. This page brings together available outputs and identifies ongoing work.'))
    content='<div class="timeline">'
    for date,status,status_en,title,title_en,desc,desc_en,href,label,label_en in items:
        content+=f'<article class="timeline-item"><div class="timeline-date">{date}</div><div><span class="status">{i18n(status,status_en)}</span><h2>{i18n(title,title_en)}</h2><p>{i18n(desc,desc_en)}</p><a href="{href}">{i18n(label,label_en)}</a></div></article>'
    content+='</div>'
    ongoing_fr='''<h2 id="chantiers">Chantiers de recherche en cours</h2><p>Le corpus d’hyperinvestigations se construit en croisant les acteurs, les méthodes et les régimes documentaires. Les travaux sur les littératies, les paradata et les coulisses de l’enquête interrogent les conditions dans lesquelles une méthode peut être comprise et reprise.</p><p>Les généalogies de l’enquête, les dispositifs de <em>world monitoring</em> et l’intelligibilité des preuves constituent d’autres terrains de travail. Les développements de Cosma pour l’hyperinvestigation demeurent un chantier d’ingénierie.</p><p><a href="recherches.html">Situer ces travaux dans les axes de recherche</a></p>'''
    ongoing_en='''<h2 id="chantiers-en">Ongoing research</h2><p>The hyperinvestigation corpus connects actors, methods and documentary practices. Work on literacies, paradata and investigative backstages examines the conditions under which a method can be understood and revisited.</p><p>Genealogies of inquiry, world-monitoring systems and the intelligibility of evidence provide further research directions. Hyperinvestigation-oriented developments of Cosma remain an engineering project.</p><p><a href="recherches.html">Explore the research programme</a></p>'''
    content+=block('<article class="page-article">'+ongoing_fr+'</article>','<article class="page-article">'+ongoing_en+'</article>')
    page('travaux.html','Travaux et actualités','Résultats accessibles et chantiers de recherche depuis le démarrage de la chaire IUF HyperION en 2025.',introduction+content)

def resource_item(id,meta,title,description,links):
    return f'<article class="resource-item" id="{id}"><div class="meta">{meta}</div><h2>{title}</h2><p>{description}</p><div class="resource-links">'+''.join(f'<a href="{href}">{label}</a>' for href,label in links)+'</div></article>'

def resources():
    intro=block(heading('Documents, corpus & logiciels','Les ressources du programme','Rapports et dépôts donnent accès au travail documentaire. Les ressources antérieures à HyperION sont identifiées comme des appuis du programme ; les développements annoncés conservent leur statut de chantier.'),heading('Documents, corpora & software','Programme resources','Reports and repositories provide access to the documentary work. Resources developed before HyperION are identified as foundations; planned developments remain ongoing work.'))
    data=[
     ('matrioscia','Rapport · 2025','MatrioscIA','Le rapport final d’Olivier Le Deuff et Rayya Roumanos étudie les usages de l’IA dans les investigations en sources ouvertes. Le dépôt rassemble les ressources produites par le projet. MatrioscIA a commencé avant l’IUF.','The final report by Olivier Le Deuff and Rayya Roumanos studies AI in open-source investigations. The repository contains project resources. MatrioscIA began before the IUF chair.',[('https://shs.hal.science/halshs-05404123v1','Rapport sur HAL'),('https://github.com/oledeuff/MatrioscIA','Dépôt MatrioscIA')]),
     ('osintosphere','Graphe documentaire','Osintosphère','Un dépôt de documentation sur les acteurs et les pratiques de l’OSINT, dans la continuité du travail sur les graphes documentaires.','A documentary repository on OSINT actors and practices, extending work on documentary graphs.',[('https://github.com/oledeuff/Osintosphere','Dépôt Osintosphère')]),
     ('cosma','Logiciel libre · développement continu','Cosma','Cosma est conçu par Arthur Perret et développé par Guillaume Brioudes. Il transforme des fiches reliées en un graphe documentaire navigable. HyperION étudie ses prolongements pour l’enquête ; la version dédiée Skritch relève du développement en cours.','Cosma, designed by Arthur Perret and developed by Guillaume Brioudes, turns linked records into a navigable documentary graph. HyperION investigates extensions for inquiry; the dedicated Skritch version remains under development.',[('https://cosma.arthurperret.fr/index.html','Site et documentation de Cosma'),('https://revue30.org/projets/experimenter-cosma-avec-stylo/','Expérimentation Cosma & Stylo')]),
     ('fiches','Fiches & représentations','Strates de l’hyperinvestigation','Les fiches décrivent strates, épistrates, parastrates et opérateurs de l’enquête. Plusieurs interfaces proposent d’en explorer les relations.','Records describe investigative strata, epistrata, parastrata and operators. Several interfaces explore their relationships.',[('explorations.html','Interfaces d’exploration'),('https://github.com/oledeuff/Hyperion/tree/main/docs/fiches','Fiches sources')]),
     ('enseignement','Cours · 2026–2027','Hyperinvestigation','Le syllabus évolutif et les cinq premiers supports relient les notions aux opérations d’enquête.','The evolving syllabus and first five course resources connect concepts with investigative operations.',[('syllabus/','Syllabus'),('syllabus/seance-01.html','Séance 1'),('syllabus/seance-03.html','Hyperlittératie'),('syllabus/seance-05.html','Construire un protocole')]),
     ('sources','Code & versions','Les sources d’HyperION','Le dépôt public conserve les pages, les fiches et l’historique des évolutions du site. GitHub Pages sert de site de test avant le transfert d’une version validée vers Huma-Num.','The public repository holds pages, records and version history. GitHub Pages serves as a test site before a validated version is transferred to Huma-Num.',[('https://github.com/oledeuff/Hyperion','Dépôt HyperION'),('publications.html','Références bibliographiques')]),
    ]
    items=''.join(resource_item(id,i18n(meta,meta),title,i18n(fr,en),links) for id,meta,title,fr,en,links in data)
    page('ressources.html','Corpus et ressources','Rapport MatrioscIA, Osintosphère, Cosma, fiches et ressources pédagogiques du programme HyperION.',intro+'<div class="resource-list">'+items+'</div>')

def explorations():
    intro=block(heading('Atelier visuel','Explorer les formes de l’enquête','Parcourir les fiches de l’hyperinvestigation et les cultures de l’enquête. Ces deux vues relient les représentations aux documents qu’elles donnent à lire.'),heading('Visual workshop','Exploring forms of inquiry','Browse hyperinvestigation records and cultures of inquiry. These two views connect representations with the documents they open for reading.'))
    strata_visual='<svg viewBox="0 0 300 150" aria-hidden="true"><g fill="none" stroke-width="2"><rect x="35" y="20" width="180" height="26" rx="5" stroke="#165d87"/><rect x="55" y="52" width="180" height="26" rx="5" stroke="#00818e"/><rect x="75" y="84" width="180" height="26" rx="5" stroke="#b95537"/><rect x="95" y="116" width="160" height="20" rx="5" stroke="#6493a8"/></g></svg>'
    marbles_visual='<svg viewBox="0 0 300 150" aria-hidden="true"><rect x="45" y="15" width="210" height="120" rx="18" fill="none" stroke="#8a6935" stroke-width="2"/><g fill="#b58a45" stroke="#785927"><circle cx="92" cy="55" r="14"/><circle cx="143" cy="44" r="10"/><circle cx="191" cy="58" r="16"/><circle cx="115" cy="100" r="17"/><circle cx="168" cy="100" r="12"/><circle cx="218" cy="104" r="9"/></g></svg>'
    data=[
      ('strates','Fiches & relations','Strates, épistrates, parastrates','Un index de fiches pour lire les définitions, les exemples et les risques associés à chaque catégorie. La représentation en cubes et l’index ouvrent les mêmes documents.','An index of records with definitions, examples and risks for each category. The cube view and index open the same documents.',[('stratescubes.html','Parcourir les fiches')],strata_visual),
      ('rouletabille','Cultures de l’enquête','La boîte à billes de Rouletabille','Explorer les raisonnements, les sens et les médiations documentaires chez le détective de Gaston Leroux. Chaque bille renvoie à une section du dossier.','Explore reasoning, the senses and documentary mediation in Gaston Leroux’s detective stories. Each marble opens a section of the dossier.',[('rouletabille.html','Explorer Rouletabille')],marbles_visual),
    ]
    items=''
    for id,meta,title,fr,en,links,visual in data:
        items+=resource_item(id,i18n(meta,meta),title,i18n(fr,en),links).replace('<h2>','<div class="exploration-visual">'+visual+'</div><h2>',1)
    note=block('<p class="source-note">Pour poursuivre la lecture, consulter le <a href="epistemologie.html">cadre épistémologique</a>, la <a href="typologie.html">typologie</a> et les <a href="https://github.com/oledeuff/Hyperion/tree/main/docs/fiches">fiches sources</a>.</p>','<p class="source-note">Continue with the <a href="epistemologie.html">epistemological framework</a>, the <a href="typologie.html">typology</a> and the <a href="https://github.com/oledeuff/Hyperion/tree/main/docs/fiches">source records</a>.</p>')
    page('explorations.html','Explorations visuelles','Fiches des strates et boîte à billes de Rouletabille : deux accès documentaires aux cultures de l’enquête.',intro+'<div class="resource-list">'+items+'</div>'+note)

def accessibility():
    fr=heading('Lire & naviguer','Accessibilité et confort de lecture','L’exploration WebGL et la lecture des documents proposent deux accès complémentaires au programme.')+'''<h2 id="navigation">Naviguer dans le site</h2><p>Le lien « Aller au contenu » apparaît au début de la navigation au clavier. Le menu en liste s’ouvre avec Entrée ou Espace et se referme avec Échap. Les liens de rubrique de l’accueil donnent accès aux mêmes contenus que l’hypercube.</p><h2 id="animation">Régler l’animation</h2><p>Le bouton de pause arrête la rotation de l’hypercube. Si la préférence de réduction des animations est activée dans votre système, la rotation est arrêtée au chargement. L’animation s’interrompt aussi quand l’onglet est masqué.</p><p>Lorsque WebGL est indisponible, une représentation statique prend le relais. La navigation, les publications et les autres pages de lecture restent accessibles.</p><h2 id="lecture">Lire et imprimer</h2><p>Le bouton « Thème » alterne entre un fond sombre et un fond clair. Le choix de langue et de thème est conservé dans le navigateur lorsque le stockage local est disponible. Les pages de lecture peuvent être agrandies et imprimées.</p><h2 id="limites">État et limites</h2><p>Cette version améliore la navigation au clavier, les contrastes, la taille des textes et les alternatives à l’animation. Elle n’a pas fait l’objet d’un audit de conformité RGAA. Les prototypes historiques de l’atelier présentent des niveaux d’accessibilité différents ; les fiches sources et les pages de lecture fournissent des accès complémentaires.</p><p>Pour signaler une difficulté, écrire à <a href="mailto:oledeuff@gmail.com">oledeuff@gmail.com</a> en indiquant la page et l’action concernées.</p>'''
    en=heading('Reading & navigation','Accessibility and reading comfort','The WebGL exploration and documentary pages provide complementary access to the programme.')+'''<h2 id="navigation-en">Navigation</h2><p>A skip link appears at the start of keyboard navigation. Open the list menu using Enter or Space and close it using Escape. Homepage section links provide access to the same content as the hypercube.</p><h2 id="animation-en">Animation</h2><p>The pause button stops rotation. Rotation starts paused when the system’s reduced-motion preference is enabled. The animation also pauses when the tab is hidden. When WebGL is unavailable, a static representation takes over; navigation and reading pages remain available.</p><h2 id="lecture-en">Reading and printing</h2><p>The theme button switches between dark and light backgrounds. Language and theme choices are stored locally when browser storage is available. Reading pages can be enlarged and printed.</p><h2 id="limites-en">Status and limitations</h2><p>This version improves keyboard navigation, contrast, text sizes and alternatives to animation. It has not undergone a formal RGAA accessibility audit. Historical visual prototypes have varying accessibility levels; source records and reading pages provide complementary access.</p><p>Report a difficulty to <a href="mailto:oledeuff@gmail.com">oledeuff@gmail.com</a>, including the page and action involved.</p>'''
    page('accessibilite.html','Accessibilité','Navigation au clavier, pause du WebGL, réduction du mouvement, thèmes et limites connues.',block('<article class="page-article">'+fr+'</article>','<article class="page-article">'+en+'</article>'))

def teaching_and_legacy():
    """Keep the taught material, making the existing syllabus directly readable."""
    old_index=subprocess.check_output(['git','show',f'{BASELINE}:docs/syllabus/index.html'],cwd=ROOT,text=True)
    base=subprocess.check_output(['git','show',f'{BASELINE}:docs/syllabus/syllabus-base.html'],cwd=ROOT,text=True)
    styles=re.search(r'style.textContent=`([\s\S]*?)`;',old_index).group(1)
    base=base.replace('</head>',f'<style>{styles}</style></head>')
    base=re.sub(r'(<div class="kicker">[\s\S]*?</div>)',r'\1<div class="version-note">Version de travail · 14 octobre 2026</div>',base,count=1)
    intro=re.search(r"first.innerHTML='([^']+)';",old_index).group(1)
    note=re.search(r"note.innerHTML='([^']+)';",old_index).group(1)
    base=re.sub(r'(<h2 id="organisation-generale">[\s\S]*?</h2>)\s*<p>[\s\S]*?</p>',lambda m:m.group(1)+'<p>'+intro+'</p><div class="progress-note">'+note+'</div>',base,count=1)
    timeline_labels=iter(['S1–S3 · parcours réalisé','S4–S5 · parcours réalisé','suite · à ajuster'])
    base=re.sub(r'(<div aria-label="Parcours du semestre" class="timeline">)([\s\S]*?)(</div>)',lambda m:m.group(1)+re.sub(r'<small>[\s\S]*?</small>',lambda _: '<small>'+next(timeline_labels)+'</small>',m.group(2),count=3)+m.group(3),base,count=1)
    sessions=list(re.finditer(r'<details class="session"[\s\S]*?</details>',base))
    for index,match in reversed(list(enumerate(sessions[:5]))):
        session=match.group()
        support=f'<a class="support-link" href="seance-0{index+1}.html">Voir les slides — séance {index+1}</a><p class="session-status">Support intégré au syllabus à partir de la version effectivement enseignée.</p>'
        session=session.replace('<div class="session-content">','<div class="session-content">'+support,1)
        if index==4:
            for variable,label in [('contenus','Contenus'),('objectifs','Objectifs'),('exemplaire','Document exemplaire')]:
                replacement=re.search(variable+r".innerHTML='([^']+)';",old_index).group(1)
                session=re.sub(r'<p><strong>'+label+r'\.</strong>[\s\S]*?</p>',lambda _: '<p>'+replacement+'</p>',session,count=1)
        base=base[:match.start()]+session+base[match.end():]
    base=base.replace("Les cours d'OSINT consituent", "Les cours d'OSINT constituent")
    (DOCS/'syllabus/index.html').write_text(base,encoding='utf-8')
    # The teaching pages retain their established visual identity.
    for path in (DOCS/'syllabus').glob('*.html'):
        html=path.read_text()
        if path.name in ['index.html','syllabus-base.html'] and 'hyperion-reading-fixes' not in html:
            html=html.replace('</head>','''<style id="hyperion-reading-fixes">a{overflow-wrap:anywhere}h1.hero-title{overflow-wrap:anywhere;hyphens:auto}:focus-visible{outline:3px solid #086c78;outline-offset:4px}@media(max-width:600px){.hero-inner{padding:34px 18px;gap:24px}h1.hero-title{font-size:clamp(2rem,10vw,3.1rem);line-height:1.05}.session-summary{grid-template-columns:70px minmax(0,1fr) 18px}.session-title{overflow-wrap:anywhere}.session-content{padding-inline:14px}}@media print{.hyperion-return{display:none}}</style><noscript><style>.mobile-nav,.side .tools{display:none!important}.side{display:block!important;position:static}.side nav{flex-direction:row;flex-wrap:wrap}</style></noscript></head>''')
        if '#deck{' in html and 'hyperion-slide-return' not in html:
            html=html.replace('</head>','<style id="hyperion-slide-return">.hyperion-return{position:fixed;top:0;left:0;z-index:1100;max-width:100vw;padding:8px 14px;border-radius:0 0 10px 0}</style></head>')
        if 'hyperion-return' not in html:
            return_style='''<style>.hyperion-return{display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:10px 24px;background:#0c1727;color:#dfeef3;font:14px/1.5 system-ui;border-bottom:1px solid #34465b}.hyperion-return a{color:#80dde3;text-decoration:underline;text-underline-offset:3px}.hyperion-return a:focus-visible{outline:3px solid #ffe0a8;outline-offset:4px}@media print{.hyperion-return{display:none}}@media(prefers-reduced-motion:reduce){*{animation:none!important;scroll-behavior:auto!important}}</style>'''
            html=html.replace('</head>',return_style+'</head>')
            return_bar='<nav class="hyperion-return" aria-label="Retour au site HyperION"><a href="../index.html">HyperION · Accueil</a><a href="index.html">Syllabus</a><span>2026–2027</span></nav>'
            html=html.replace('<body>','<body>'+return_bar,1)
        if 'name="robots"' not in html: html=html.replace('</head>','<meta name="robots" content="noindex,follow"></head>')
        path.write_text(re.sub(r'(?m)^[ \t]+$', '', html),encoding='utf-8')
    legacy=['rouletabille.html','hinton-planche.html','hyperstratessimple.html','hyperstrates.html','sitestrates.html','stratescubes.html','tesseract.html']
    for name in legacy:
        path=DOCS/name
        html=path.read_text()
        if 'hyperion-return' not in html:
            html=html.replace('</head>','''<style>.hyperion-return{display:flex;gap:20px;flex-wrap:wrap;flex-shrink:0;padding:10px 20px;background:#0c1727;color:#e5f3f7;font:14px/1.6 system-ui;border-bottom:1px solid #34465b}.hyperion-return a{color:#80dde3;text-decoration:underline;text-underline-offset:3px}.hyperion-return a:focus-visible{outline:3px solid #ffe0a8;outline-offset:4px}@media print{.hyperion-return{display:none}}@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style></head>''')
            html=html.replace('<body>','<body><nav class="hyperion-return" aria-label="HyperION"><a href="index.html">HyperION · Accueil</a><a href="explorations.html">Explorations visuelles</a><a href="typologie.html">Accès textuel · typologie</a></nav>',1)
        if 'name="robots"' not in html: html=html.replace('</head>','<meta name="robots" content="noindex,follow"></head>')
        if name in ['rouletabille.html','stratescubes.html']:
            kind='strates' if name=='stratescubes.html' else 'rouletabille'
            html=html.replace('<html lang="fr">',f'<html lang="fr" data-theme="light" data-atelier="{kind}">')
            assets=f'<link id="atelier-assets" rel="stylesheet" href="assets/atelier.css?v={VERSION}"><script defer src="assets/atelier.js?v={VERSION}"></script>'
            if 'id="atelier-assets"' not in html: html=html.replace('</head>',assets+'</head>')
            else: html=re.sub(r'<link id="atelier-assets"[\s\S]*?</script>',assets,html,count=1)
            if 'id="atelier-theme"' not in html:
                html=html.replace('</nav>','<button class="atelier-control" id="atelier-theme" aria-pressed="true">Thème clair</button><button class="atelier-control" id="atelier-pause" aria-pressed="false">Mettre en pause</button></nav>',1)
            if name=='stratescubes.html':
                html=html.replace('angle += 0.3;', 'if(document.documentElement.dataset.motion!=="paused") angle += 0.3;') if 'dataset.motion' not in html else html
                html=html.replace('id="indexSearch"', 'id="indexSearch" aria-label="Rechercher une fiche"') if 'aria-label="Rechercher une fiche"' not in html else html
                if 'li.tabIndex = 0' not in html:
                    html=html.replace('li.className = "index-item";', 'li.className = "index-item"; li.tabIndex = 0; li.setAttribute("role", "button");')
                    html=html.replace('li.addEventListener("click", () => selectFiche(n.id));', 'li.addEventListener("click", () => selectFiche(n.id));\n        li.addEventListener("keydown", event => {if(event.key==="Enter"||event.key===" "){event.preventDefault();selectFiche(n.id);}});')
            else:
                html=html.replace('t += 0.01;', 'if(document.documentElement.dataset.motion!=="paused") t += 0.01;') if 'dataset.motion' not in html else html
                html=html.replace('el.scrollIntoView({ behavior: "smooth", block: "start" });','el.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });')
        # Replace obsolete global CDN builds with the matching, locally held ES module.
        if 'three@0.160.0/build/three.min.js' in html:
            html=re.sub(r'<script src="https://[^" ]+three@0\.160\.0/build/three\.min\.js"></script>','',html)
            html=re.sub(r'<script src="https://[^" ]+three@0\.160\.0/examples/js/controls/OrbitControls\.js"></script>','',html)
            imports='import * as THREE from "./assets/vendor/three.module.js";'
            if name=='hyperstrates.html':
                imports='import * as Three from "./assets/vendor/three.module.js"; import { OrbitControls } from "./assets/vendor/OrbitControls.js"; const THREE = {...Three, OrbitControls};'
            html=html.replace('<script>','<script type="module">'+imports,1)
        path.write_text(re.sub(r'(?m)^[ \t]+$', '', html),encoding='utf-8')

def build():
    (DOCS/'assets').mkdir(exist_ok=True)
    (DOCS/'favicon-hyperion.svg').write_text((ROOT/'favicon-hyperion.svg').read_text(),encoding='utf-8')
    home(); research(); publications(); work(); resources(); explorations(); accessibility()
    for name,title,desc in [
      ('presentation.html','Le projet','Présentation scientifique de la chaire IUF HyperION 2025–2030.'),
      ('epistemologie.html','Épistémologie','Fondements épistémologiques de l’hyperdocumentation et de l’hyperinvestigation.'),
      ('typologie.html','Typologie des hyperinvestigations','Acteurs, pratiques et régimes de preuve de l’hyperinvestigation.'),
    ]: page(name,title,desc,original_page(name))
    teaching_and_legacy()
    (DOCS/'version.json').write_text(json.dumps({'version':VERSION,'date':'2026-11-24','environment':'github-test','production':'https://hyperion.huma-num.fr/'},indent=2)+'\n')
    print(f'Built HyperION {VERSION}: 10 public pages and publication data.')

if __name__=='__main__': build()
