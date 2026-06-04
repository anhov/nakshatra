import { BirthProfile } from '../context/UserContext';

// iOS simulator: localhost. Android emulator: 10.0.2.2. Physical device: your machine IP.
const BASE = 'http://192.168.10.110:8000/api/v1';

// Set this via in-app purchase / server validation in production.
// Stored in-app; never calculated on device.
let _tier: string = 'free';
export const setSubscriptionTier = (t: 'free' | 'premium' | 'pro') => { _tier = t; };
export const getSubscriptionTier = () => _tier;

function baseHeaders(): Record<string, string> {
  return { 'X-Subscription-Tier': _tier };
}

async function get<T>(path: string, params: Record<string, string | number | undefined> = {}): Promise<T> {
  const qs = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join('&');
  const url = `${BASE}${path}${qs ? '?' + qs : ''}`;
  const res = await fetch(url, { headers: baseHeaders() });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
  }
  return res.json();
}

async function post<T>(path: string, body: object): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...baseHeaders() },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
  }
  return res.json();
}

function birthParams(p: BirthProfile) {
  return {
    birth_date: p.birthDate,
    birth_time: p.birthTime,
    tz: p.timezone,
    lat: p.latitude,
    lon: p.longitude,
  };
}

function toISODate(d: Date) {
  return d.toISOString().split('T')[0];
}

// ── Today ──────────────────────────────────────────────────────────────────
export const fetchToday = (p: BirthProfile, queryDate?: Date) =>
  get('/today', { ...birthParams(p), query_date: queryDate ? toISODate(queryDate) : undefined });

// ── Month ──────────────────────────────────────────────────────────────────
export const fetchMonth = (p: BirthProfile, year: number, month: number) =>
  get('/month', { ...birthParams(p), year, month });

// ── Find Best Day ──────────────────────────────────────────────────────────
export const fetchCategories = () => get<{ categories: string[] }>('/find-best-day/categories');

export const fetchBestDays = (p: BirthProfile, category: string, daysAhead = 90) =>
  get('/find-best-day', { ...birthParams(p), category, days_ahead: daysAhead });

// ── Birth Chart + Dasha ────────────────────────────────────────────────────
export const fetchBirthChart = (p: BirthProfile) =>
  get('/chart/birth', { ...birthParams(p) });

export const fetchDasha = (p: BirthProfile) =>
  get('/dasha', { ...birthParams(p) });

// ── Content ────────────────────────────────────────────────────────────────
export const fetchUpcomingEkadashis = (tz: string, count = 6) =>
  get('/content/ekadashis/upcoming', { tz, count });

export const fetchAffirmation = (dashaLord: string, quality: string, dateStr: string) =>
  get('/content/affirmation', { dasha_lord: dashaLord, quality, date: dateStr });

export const fetchPlanetaryMantra = (planet: string) =>
  get(`/content/mantra/planet/${encodeURIComponent(planet)}`);

export const fetchNakshatraMantra = (nakshatra: string) =>
  get(`/content/mantra/nakshatra/${encodeURIComponent(nakshatra)}`);

// ── User onboarding ────────────────────────────────────────────────────────
export const createUser = (p: BirthProfile) =>
  post('/users', {
    name: p.name,
    birth_date: p.birthDate,
    birth_time: p.birthTime,
    timezone: p.timezone,
    latitude: p.latitude,
    longitude: p.longitude,
    place_name: p.placeName,
    is_approximate_time: p.isApproximateTime,
  });
