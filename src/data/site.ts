// Central site data — single source of truth for NAP, links, reviews and photos.
// Change SITE.url once your domain is live; it feeds canonicals, sitemap, OG and schema.

export const SITE = {
  // TODO: replace with the real production domain before going live.
  url: 'https://beb-milano-malpensa-1.it',
  name: 'B&B Milano Malpensa 1',
  legalName: 'Bed&Breakfast Milano Malpensa 1',
  tagline: 'Bed & Breakfast a Castano Primo, vicino all\u2019aeroporto di Malpensa',
  address: {
    street: 'Via Lonate Pozzolo 1',
    zip: '20022',
    city: 'Castano Primo',
    province: 'MI',
    region: 'Lombardia',
    country: 'Italia',
  },
  geo: { lat: 45.5545398, lng: 8.7755763 },
  phoneDisplay: '339 294 6283',
  phoneHref: 'tel:+393392946283',
  whatsapp: 'https://wa.me/393392946283?text=' +
    encodeURIComponent('Ciao! Vorrei informazioni sul B&B Milano Malpensa 1.'),
  email: '', // no public email available; contact via phone / WhatsApp
  mapsUrl:
    'https://www.google.com/maps/place/Bed%26Breakfast+Milano+Malpensa+1/@45.5545398,8.7755763,17z/data=!4m10!3m9!1s0x4786f53a4bbdda75:0x41f8691062bb5953!5m3!1s2026-09-01!4m1!1i2!8m2!3d45.5545398!4d8.7755763!16s%2Fg%2F11r96nq8q',
  tripadvisorUrl:
    'https://www.tripadvisor.com/Hotel_Review-g3642464-d8367249-Reviews-B_b_Milano_Malpensa_1-Castano_Primo_Province_of_Milan_Lombardy.html',
  rating: { value: 3.7, count: 176 }, // Google
};

// Per-locale canonical paths — same slug, different locale prefix (it = default).
export const PAGES: Record<string, { it: string; en: string }> = {
  home: { it: '/', en: '/en/' },
  lavoro: { it: '/beb-per-lavoro/', en: '/en/beb-per-lavoro/' },
  malpensa: { it: '/beb-vicino-aeroporto-malpensa/', en: '/en/beb-vicino-aeroporto-malpensa/' },
  castano: { it: '/beb-castano-primo/', en: '/en/beb-castano-primo/' },
  camere: { it: '/camere/', en: '/en/camere/' },
  contatti: { it: '/contatti/', en: '/en/contatti/' },
};

export const I18N = {
  it: {
    langLabel: 'it-IT',
    brandName: 'B&B Milano Malpensa 1',
    brandSub: 'Bed & Breakfast · Castano Primo',
    brandAria: 'B&B Milano Malpensa 1 – home',
    menuAria: 'Apri il menu',
    navAria: 'Menu principale',
    cta: 'Chiama ora',
    ctaShort: 'Chiama',
    nav: [
      { href: PAGES.lavoro.it, label: 'Per lavoro' },
      { href: PAGES.malpensa.it, label: 'Vicino a Malpensa' },
      { href: PAGES.castano.it, label: 'Castano Primo' },
      { href: PAGES.camere.it, label: 'Camere' },
      { href: PAGES.contatti.it, label: 'Contatti' },
    ],
    footer: {
      about:
        'Bed & Breakfast a gestione familiare a Castano Primo, a pochi minuti dall\u2019aeroporto di Malpensa: navetta, parcheggio, colazione e camere comode per chi viaggia per lavoro.',
      sitemapTitle: 'Il sito',
      contactTitle: 'Contatti',
      book: 'Prenota direttamente (WhatsApp)',
      reviews: 'Recensioni',
    },
    reviewLabel: 'Recensione Google',
  },
  en: {
    langLabel: 'en',
    brandName: 'B&B Milano Malpensa 1',
    brandSub: 'Bed & Breakfast · Castano Primo',
    brandAria: 'B&B Milano Malpensa 1 – home',
    menuAria: 'Open menu',
    navAria: 'Main menu',
    cta: 'Call now',
    ctaShort: 'Call',
    nav: [
      { href: PAGES.lavoro.en, label: 'Business stays' },
      { href: PAGES.malpensa.en, label: 'Near Malpensa' },
      { href: PAGES.castano.en, label: 'Castano Primo' },
      { href: PAGES.camere.en, label: 'Rooms' },
      { href: PAGES.contatti.en, label: 'Contact' },
    ],
    footer: {
      about:
        'Family-run Bed & Breakfast in Castano Primo, a few minutes from Milan Malpensa airport: shuttle, parking, breakfast and comfortable rooms for business travellers.',
      sitemapTitle: 'Site',
      contactTitle: 'Contact',
      book: 'Book directly (WhatsApp)',
      reviews: 'Reviews',
    },
    reviewLabel: 'Google review',
  },
} as const;

export type Locale = keyof typeof I18N;

// Template prices based on the average cost of B&Bs in the Malpensa / Castano
// Primo area — always visible, indicative nightly rates (breakfast included).
export const PRICES = {
  single: { it: 'da €45', en: 'from €45' },
  double: { it: 'da €60', en: 'from €60' },
  twin: { it: 'da €60', en: 'from €60' },
  triple: { it: 'da €75', en: 'from €75' },
  family: { it: 'da €90', en: 'from €90' },
  group: { it: 'da €25 a letto', en: 'from €25 per bed' },
  note: {
    it: 'Prezzi indicativi a notte, colazione inclusa. Sconti per soggiorni lunghi e settimanali.',
    en: 'Indicative nightly rates, breakfast included. Discounts for long and weekly stays.',
  },
  weekly: { it: 'Tariffa settimanale per lavoro su richiesta', en: 'Weekly business rates on request' },
} as const;

// Genuine positive reviews published on Google (curated, not fabricated).
export const REVIEWS = [
  {
    quote:
      'Se cercate una soluzione pratica, pulita e con un eccellente rapporto qualit\u00e0-prezzo vicino a Malpensa, questo B&B \u00e8 una garanzia. Ci torner\u00f2 sicuramente!',
    author: 'Rita N.',
    detail: 'Recensione Google',
  },
  {
    quote:
      'Avevo un\u2019attesa di 12 ore in aeroporto. Ho chiamato questo B&B senza aver prenotato in anticipo: il proprietario \u00e8 venuto a prendermi in aeroporto e mi ha riportato quando dovevo partire. Disponibile e alla mano: come soggiornare da un amico.',
    author: 'Gaetano D.',
    detail: 'Recensione Google',
  },
  {
    quote:
      'Grandissimo Luciano, persona d\u2019oro: siamo rimasti davvero soddisfatti del servizio offerto, camera pulita e accogliente. Il servizio navetta davvero impeccabile.',
    author: 'Manuele L.',
    detail: 'Recensione Google',
  },
  {
    quote:
      'Luciano, il nostro host, \u00e8 molto disponibile e professionale: ci ha procurato delle bici per fare delle escursioni sul Canale Villoresi. Camera spaziosa e accogliente.',
    author: 'Angelo L.',
    detail: 'Recensione Google',
  },
  {
    quote:
      'Ottimo per ciclisti: situato lungo una pista ciclabile sul Canale Villoresi, con possibilit\u00e0 di tenere la bicicletta in camera gratuitamente. Nell\u2019insieme ottimo servizio.',
    author: 'Nicola P.',
    detail: 'Recensione Google',
  },
  {
    quote:
      'Il proprietario \u00e8 una persona molto gentile e disponibile. Le camere sono ben pulite e fornite di tutte le necessit\u00e0. Posizione molto comoda, vicino alla stazione: facilissimi spostamenti.',
    author: 'Nicola S.',
    detail: 'Recensione Google',
  },
];

export interface Photo {
  src: string;
  alt: string;
  w: number;
  h: number;
}

const PHOTOS = '/photos';

export const PHOTO = {
  struttura: { src: `${PHOTOS}/struttura-bnb.avif`, alt: 'La struttura del B&B Milano Malpensa 1 vista dall\u2019esterno, con il cartello all\u2019ingresso', w: 1600, h: 1067 },
  giardino: { src: `${PHOTOS}/giardino-albero.avif`, alt: 'Albero e giardino davanti al B&B', w: 1600, h: 2133 },
  piante: { src: `${PHOTOS}/piante-ingresso.avif`, alt: 'Piante all\u2019ingresso della struttura', w: 1600, h: 1067 },
  piazza: { src: `${PHOTOS}/piazza-castano-primo.avif`, alt: 'La piazza di Castano Primo, vicino al B&B', w: 1600, h: 1200 },
  cartellone: { src: `${PHOTOS}/cartellone-ingresso.avif`, alt: 'Il cartellone con il nome del B&B Milano Malpensa 1', w: 1600, h: 1200 },
  bici: { src: `${PHOTOS}/bici-esterno.avif`, alt: 'Biciclette a disposizione degli ospiti fuori dal B&B', w: 640, h: 480 },
  fiume: { src: `${PHOTOS}/fiume-ticino.avif`, alt: 'Il fiume Ticino nei pressi di Castano Primo', w: 1600, h: 1200 },
  fiumePieno: { src: `${PHOTOS}/fiume-pieno.avif`, alt: 'Il Ticino in piena, vista dal sentiero', w: 1600, h: 1200 },
  fiumeRiva: { src: `${PHOTOS}/fiume-riva.avif`, alt: 'Riva del Ticino tra la vegetazione', w: 1600, h: 2844 },
  fiumePrimavera: { src: `${PHOTOS}/fiume-primavera.avif`, alt: 'Il Ticino in primavera', w: 1600, h: 1200 },
  vistaFiume: { src: `${PHOTOS}/vista-fiume-natura.avif`, alt: 'Vista sul fiume e sulla natura nei dintorni del B&B', w: 1600, h: 1200 },
  vistaFiumePrimavera: { src: `${PHOTOS}/vista-fiume-primavera.avif`, alt: 'La natura in primavera vicino al B&B', w: 1600, h: 2133 },
  salotto: { src: `${PHOTOS}/salotto.avif`, alt: 'Il salotto accogliente del B&B', w: 1024, h: 683 },
  salottoTavolo: { src: `${PHOTOS}/salotto-tavolo.avif`, alt: 'Tavolo del salotto con sedie', w: 679, h: 452 },
  salotto2: { src: `${PHOTOS}/salotto-2.avif`, alt: 'Angolo del salotto con divano', w: 699, h: 439 },
  veranda: { src: `${PHOTOS}/veranda.avif`, alt: 'Veranda con tavolino e sedie', w: 452, h: 678 },
  bandiera: { src: `${PHOTOS}/sedia-bandiera.avif`, alt: 'Sedia con la bandiera inglese nel salotto', w: 1280, h: 2560 },
  tv: { src: `${PHOTOS}/tv-in-camera.avif`, alt: 'Televisore in camera', w: 1600, h: 2133 },
  colazione: { src: `${PHOTOS}/colazione-merende.avif`, alt: 'Cestino con merendine e dolci per la colazione', w: 640, h: 480 },
  scalinata: { src: `${PHOTOS}/scalinata.avif`, alt: 'Scalinata che porta al piano superiore', w: 679, h: 452 },
  lettoMatrimoniale: { src: `${PHOTOS}/letto-matrimoniale.avif`, alt: 'Camera con letto matrimoniale', w: 1600, h: 2133 },
  lettoMatrimoniale3: { src: `${PHOTOS}/letto-matrimoniale-3.avif`, alt: 'Letto matrimoniale con copriletto', w: 1536, h: 2048 },
  lettoSingoli: { src: `${PHOTOS}/letti-singoli.avif`, alt: 'Camera con due letti singoli', w: 678, h: 452 },
  dueLettiSingoli: { src: `${PHOTOS}/due-letti-singoli.avif`, alt: 'Due letti singoli con testiere', w: 632, h: 474 },
  quattroLetti: { src: `${PHOTOS}/quattro-letti.avif`, alt: 'Camera con quattro letti, ideale per gruppi', w: 640, h: 480 },
  castello2: { src: `${PHOTOS}/matrimoniale-castello-2singoli.avif`, alt: 'Camera con letto matrimoniale, letto a castello e due letti singoli', w: 1024, h: 768 },
  castelloSingolo: { src: `${PHOTOS}/matrimoniale-castello-singolo.avif`, alt: 'Camera con letto matrimoniale, letto a castello e un letto singolo', w: 1600, h: 1200 },
  lettoCastello: { src: `${PHOTOS}/letto-castello.avif`, alt: 'Letto a castello in camera', w: 675, h: 900 },
  matrimonialeSingolo: { src: `${PHOTOS}/matrimoniale-singolo.avif`, alt: 'Camera con letto matrimoniale e letto singolo', w: 1024, h: 768 },
  castelloBasso: { src: `${PHOTOS}/letto-castello-basso.avif`, alt: 'Letto basso al primo piano del castello', w: 1600, h: 1200 },
  bagno5: { src: `${PHOTOS}/bagno-5.avif`, alt: 'Bagno privato con doccia', w: 1600, h: 2133 },
  bagno3: { src: `${PHOTOS}/bagno-3.avif`, alt: 'Bagno privato della camera', w: 1600, h: 2133 },
  bagno7: { src: `${PHOTOS}/bagno-7.avif`, alt: 'Bagno con lavandino e specchio', w: 1600, h: 2133 },
  bagno9: { src: `${PHOTOS}/bagno-9.avif`, alt: 'Particolare del bagno privato', w: 1600, h: 2133 },
} as const;
