// Schema.org builders — always produce valid JSON-LD (validated at build).
import { I18N, PAGES, SITE, type Locale } from './site';

const tel = '+393392946283';

const DESCRIPTIONS: Record<Locale, string> = {
  it: 'Bed & Breakfast a Castano Primo (MI), a 15 km dall\u2019aeroporto di Malpensa: camere con bagno privato, navetta aeroporto, parcheggio, colazione e tariffe convenienti per chi viaggia per lavoro.',
  en: 'Bed & Breakfast in Castano Primo (Milan), 15 km from Malpensa airport: rooms with private bathroom, airport shuttle, parking, breakfast and affordable rates for business travellers.',
};

export function lodgingSchema(lang: Locale): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'LodgingBusiness',
    '@id': `${SITE.url}/${lang === 'it' ? '' : 'en/'}#lodging`,
    name: SITE.legalName,
    alternateName: SITE.name,
    url: lang === 'it' ? SITE.url : `${SITE.url}/en/`,
    telephone: tel,
    image: `${SITE.url}/og.jpg`,
    description: DESCRIPTIONS[lang],
    priceRange: '\u20ac45\u2013\u20ac120',
    address: {
      '@type': 'PostalAddress',
      streetAddress: SITE.address.street,
      addressLocality: SITE.address.city,
      postalCode: SITE.address.zip,
      addressRegion: SITE.address.province,
      addressCountry: 'IT',
    },
    geo: {
      '@type': 'GeoCoordinates',
      latitude: SITE.geo.lat,
      longitude: SITE.geo.lng,
    },
    hasMap: SITE.mapsUrl,
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: String(SITE.rating.value),
      reviewCount: String(SITE.rating.count),
      bestRating: '5',
    },
    amenityFeature: [
      { '@type': 'LocationFeatureSpecification', name: 'Parking', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Free Wi-Fi', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Breakfast', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Air conditioning', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Pets allowed', value: true },
    ],
    sameAs: [SITE.bookingUrl, SITE.tripadvisorUrl, SITE.mapsUrl],
    knowsLanguage: ['it', 'en'],
  };
  return JSON.stringify(s);
}

export function websiteSchema(lang: Locale): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SITE.url}/${lang === 'it' ? '' : 'en/'}#website`,
    url: lang === 'it' ? SITE.url : `${SITE.url}/en/`,
    name: SITE.name,
    inLanguage: lang === 'it' ? 'it-IT' : 'en',
    publisher: { '@id': `${SITE.url}/#lodging` },
  };
  return JSON.stringify(s);
}

export function breadcrumbSchema(lang: Locale, items: { name: string; key: string }[]): string {
  const itemList = items.map((it, i) => ({
    '@type': 'ListItem',
    position: i + 1,
    name: it.name,
    item: `${SITE.url}${PAGES[it.key][lang]}`,
  }));
  const lastPath = PAGES[items.at(-1)?.key ?? 'home'][lang];
  const s = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    '@id': `${SITE.url}${lastPath}#breadcrumb`,
    itemListElement: itemList,
  };
  return JSON.stringify(s);
}

export function faqSchema(lang: Locale, faqs: { q: string; a: string }[]): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    '@id': `${SITE.url}${PAGES.malpensa[lang]}#faq`,
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };
  return JSON.stringify(s);
}
