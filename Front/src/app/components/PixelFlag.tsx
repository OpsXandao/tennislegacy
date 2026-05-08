interface PixelFlagProps {
  countryCode?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const FLAG_ASSETS = import.meta.glob('../../assets/flags/*.png', {
  eager: true,
  import: 'default',
}) as Record<string, string>

const R74N_FLAG_ASSETS = import.meta.glob('../../assets/flags/r74n-country/*.png', {
  eager: true,
  import: 'default',
}) as Record<string, string>

const FLAG_BY_CODE = Object.fromEntries(
  Object.entries(FLAG_ASSETS).map(([path, url]) => {
    const match = path.match(/\/([A-Z]{3})\.png$/)
    return [match?.[1] ?? path, url]
  })
) as Record<string, string>

const FLAG_BY_R74N_SLUG = Object.fromEntries(
  Object.entries(R74N_FLAG_ASSETS).map(([path, url]) => {
    const match = path.match(/\/([^/]+)\.png$/)
    return [match?.[1] ?? path, url]
  })
) as Record<string, string>

const ISO2_TO_3: Record<string, string> = {
  AR: 'ARG',
  AU: 'AUS',
  AT: 'AUT',
  BE: 'BEL',
  BR: 'BRA',
  BG: 'BUL',
  CA: 'CAN',
  CL: 'CHI',
  CN: 'CHN',
  CO: 'COL',
  HR: 'CRO',
  CZ: 'CZE',
  DK: 'DEN',
  ES: 'ESP',
  FI: 'FIN',
  FR: 'FRA',
  GB: 'GBR',
  DE: 'GER',
  GR: 'GRE',
  IT: 'ITA',
  JP: 'JPN',
  KZ: 'KAZ',
  KR: 'KOR',
  NO: 'NOR',
  PL: 'POL',
  PT: 'POR',
  RU: 'RUS',
  RS: 'SRB',
  CH: 'SUI',
  SE: 'SWE',
  US: 'USA',
}

const ISO3_TO_2: Record<string, string> = {
  ARG: 'AR',
  AUS: 'AU',
  AUT: 'AT',
  BEL: 'BE',
  BRA: 'BR',
  BUL: 'BG',
  CAN: 'CA',
  CHI: 'CL',
  CHN: 'CN',
  COL: 'CO',
  CRO: 'HR',
  CZE: 'CZ',
  DEN: 'DK',
  ESP: 'ES',
  FIN: 'FI',
  FRA: 'FR',
  GBR: 'GB',
  GER: 'DE',
  GRE: 'GR',
  ITA: 'IT',
  JPN: 'JP',
  KAZ: 'KZ',
  KOR: 'KR',
  NOR: 'NO',
  POL: 'PL',
  POR: 'PT',
  RUS: 'RU',
  SRB: 'RS',
  SUI: 'CH',
  SWE: 'SE',
  USA: 'US',
  // Extras frequently found in tennis data
  UKR: 'UA',
  ROU: 'RO',
  LAT: 'LV',
  NZL: 'NZ',
  INA: 'ID',
  GEO: 'GE',
  TPE: 'TW',
  TWN: 'TW',
  IND: 'IN',
  MEX: 'MX',
  SVK: 'SK',
  SLO: 'SI',
  HUN: 'HU',
  RSA: 'ZA',
  THA: 'TH',
  PHI: 'PH',
  EGY: 'EG',
  UZB: 'UZ',
  BLR: 'BY',
  HKG: 'HK',
  NED: 'NL',
  ECU: 'EC',
  PER: 'PE',
  URU: 'UY',
  PAR: 'PY',
  BOL: 'BO',
  VEN: 'VE',
  DOM: 'DO',
  GUA: 'GT',
  ESA: 'SV',
  CRC: 'CR',
  PUR: 'PR',
}

const ISO2_TO_R74N_SLUG: Record<string, string> = {
  CD: 'dr_congo',
  CG: 'republic_of_the_congo',
  HK: 'hong_kong',
  KN: 'saint_kitts_and_nevis',
  LC: 'saint_lucia',
  MM: 'myanmar',
  PS: 'palestine',
  SZ: 'swaziland',
  TR: 'turkey',
  VC: 'saint_vincent_and_the_grenadines',
}

const TOURNAMENT_LOCATION_MAP: Array<[string, string]> = [
  ['melbourne', 'AUS'],
  ['sydney', 'AUS'],
  ['brisbane', 'AUS'],
  ['adelaide', 'AUS'],
  ['paris', 'FRA'],
  ['lyon', 'FRA'],
  ['marseille', 'FRA'],
  ['london', 'GBR'],
  ['eastbourne', 'GBR'],
  ['nottingham', 'GBR'],
  ['wimbledon', 'GBR'],
  ['madrid', 'ESP'],
  ['barcelona', 'ESP'],
  ['mallorca', 'ESP'],
  ['rome', 'ITA'],
  ['turin', 'ITA'],
  ['milan', 'ITA'],
  ['hamburg', 'GER'],
  ['berlin', 'GER'],
  ['munich', 'GER'],
  ['stuttgart', 'GER'],
  ['tokyo', 'JPN'],
  ['osaka', 'JPN'],
  ['beijing', 'CHN'],
  ['shanghai', 'CHN'],
  ['wuhan', 'CHN'],
  ['hong kong', 'HK'],
  ['new york', 'USA'],
  ['miami', 'USA'],
  ['indian wells', 'USA'],
  ['cincinnati', 'USA'],
  ['delray beach', 'USA'],
  ['houston', 'USA'],
  ['toronto', 'CAN'],
  ['montreal', 'CAN'],
  ['vancouver', 'CAN'],
  ['buenos aires', 'ARG'],
  ['cordoba', 'ARG'],
  ['córdoba', 'ARG'],
  ['santiago', 'CHI'],
  ['bogota', 'COL'],
  ['bogotá', 'COL'],
  ['rio', 'BRA'],
  ['sao paulo', 'BRA'],
  ['são paulo', 'BRA'],
  ['florianopolis', 'BRA'],
  ['florianópolis', 'BRA'],
  ['basel', 'SUI'],
  ['geneva', 'SUI'],
  ['genebra', 'SUI'],
  ['gstaad', 'SUI'],
  ['belgrade', 'SRB'],
  ['warsaw', 'POL'],
  ['varsovia', 'POL'],
  ['varsóvia', 'POL'],
  ['porto', 'POR'],
  ['lisbon', 'POR'],
  ['lisboa', 'POR'],
  ['oslo', 'NOR'],
  ['copenhagen', 'DEN'],
  ['atenas', 'GRE'],
  ['athens', 'GRE'],
]

function normalizeCode(countryCode?: string): string {
  const raw = String(countryCode || '').trim()
  if (!raw) return ''

  const bracketMatch = raw.match(/^\[([A-Z]{2,3})\]/i)
  if (bracketMatch) {
    const code = bracketMatch[1].toUpperCase()
    return code.length === 2 ? (ISO2_TO_3[code] || code) : code
  }

  const cleaned = raw.toUpperCase().replace('[', '').replace(']', '').trim()
  if (cleaned.length === 2) return ISO2_TO_3[cleaned] || cleaned
  return cleaned
}

function slugify(value?: string): string {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/&/g, ' and ')
    .replace(/['’.]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_')
    .toLowerCase()
}

function extractIso2(countryCode?: string): string | undefined {
  const raw = String(countryCode || '').trim()
  if (!raw) return undefined

  const bracketMatch = raw.match(/^\[([A-Z]{2,3})\]/i)
  if (bracketMatch) {
    const code = bracketMatch[1].toUpperCase()
    return code.length === 3 ? (ISO3_TO_2[code] || undefined) : code
  }

  const cleaned = raw.toUpperCase().replace('[', '').replace(']', '').trim()
  if (cleaned.length === 2) return cleaned
  if (cleaned.length === 3) return ISO3_TO_2[cleaned] || undefined
  return undefined
}

function regionToR74nSlug(iso2: string): string | undefined {
  const override = ISO2_TO_R74N_SLUG[iso2]
  if (override) return override

  if (typeof Intl === 'undefined' || typeof Intl.DisplayNames === 'undefined') {
    return undefined
  }

  try {
    const regionNames = new Intl.DisplayNames(['en'], { type: 'region' })
    const englishName = regionNames.of(iso2)
    if (!englishName) return undefined
    return slugify(englishName)
  } catch (e) {
    console.warn(`[PixelFlag] Failed to get display name for region: ${iso2}`, e)
    return undefined
  }
}

function resolveFlagSrc(countryCode?: string): { src?: string; label: string } {
  const code = normalizeCode(countryCode)
  if (FLAG_BY_CODE[code]) {
    return { src: FLAG_BY_CODE[code], label: code }
  }

  const iso2 = extractIso2(countryCode)
  if (iso2) {
    const slug = regionToR74nSlug(iso2)
    if (slug && FLAG_BY_R74N_SLUG[slug]) {
      return { src: FLAG_BY_R74N_SLUG[slug], label: iso2 }
    }
  }

  const directSlug = slugify(countryCode)
  if (FLAG_BY_R74N_SLUG[directSlug]) {
    return { src: FLAG_BY_R74N_SLUG[directSlug], label: code || countryCode || '???' }
  }

  return { label: code || countryCode || '???' }
}

export function inferCountryCodeFromText(text?: string): string | undefined {
  const normalized = String(text || '').trim().toLowerCase()
  if (!normalized) return undefined
  for (const [token, code] of TOURNAMENT_LOCATION_MAP) {
    if (normalized.includes(token)) return code
  }
  return undefined
}

export function PixelFlag({ countryCode, size = 'md', className = '' }: PixelFlagProps) {
  const { src, label } = resolveFlagSrc(countryCode)
  const dims =
    size === 'sm'
      ? { width: 18, height: 12 }
      : size === 'lg'
      ? { width: 32, height: 21 }
      : size === 'xl'
      ? { width: 48, height: 32 }
      : { width: 24, height: 16 }

  if (!src) {
    return (
      <div
        className={`inline-flex items-center justify-center border border-[#00e5ff] bg-black text-[#00e5ff] arcade-font text-[8px] ${className}`}
        style={{ width: dims.width, height: dims.height }}
      >
        {String(label).slice(0, 3).toUpperCase()}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={label}
      width={dims.width}
      height={dims.height}
      className={`inline-block border border-[#0a0a0a] bg-black object-contain ${className}`}
      style={{ imageRendering: 'pixelated' }}
    />
  )
}
