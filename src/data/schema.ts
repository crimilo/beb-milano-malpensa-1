// Schema.org builders — always produce valid JSON-LD (validated at build).
import { SITE } from './site';

const tel = '+393392946283';

export function lodgingSchema(): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'LodgingBusiness',
    '@id': `${SITE.url}/#lodging`,
    name: SITE.legalName,
    alternateName: SITE.name,
    url: SITE.url,
    telephone: tel,
    image: `${SITE.url}/og.jpg`,
    description:
      'Bed & Breakfast a Castano Primo (MI), a 15 km dall\u2019aeroporto di Malpensa: camere con bagno privato, navetta aeroporto, parcheggio, colazione e pista ciclabile del Canale Villoresi a due passi.',
    priceRange: '\u20ac\u20ac',
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
      { '@type': 'LocationFeatureSpecification', name: 'Parcheggio', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Wi-Fi gratuito', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Colazione', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Aria condizionata', value: true },
      { '@type': 'LocationFeatureSpecification', name: 'Animali ammessi', value: true },
    ],
    sameAs: [SITE.bookingUrl, SITE.tripadvisorUrl, SITE.mapsUrl],
    knowsLanguage: ['it', 'en'],
  };
  return JSON.stringify(s);
}

export function websiteSchema(): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    '@id': `${SITE.url}/#website`,
    url: SITE.url,
    name: SITE.name,
    inLanguage: 'it-IT',
    publisher: { '@id': `${SITE.url}/#lodging` },
  };
  return JSON.stringify(s);
}

export function breadcrumbSchema(items: { name: string; path: string }[]): string {
  const itemList = items.map((it, i) => ({
    '@type': 'ListItem',
    position: i + 1,
    name: it.name,
    item: `${SITE.url}${it.path}`,
  }));
  const s = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    '@id': `${SITE.url}${items.at(-1)?.path}#breadcrumb`,
    itemListElement: itemList,
  };
  return JSON.stringify(s);
}

export function faqSchema(faqs: { q: string; a: string }[]): string {
  const s = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    '@id': `${SITE.url}/beb-vicino-aeroporto-malpensa/#faq`,
    mainEntity: faqs.map((f) => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  };
  return JSON.stringify(s);
}
