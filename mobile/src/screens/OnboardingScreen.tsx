import * as Location from 'expo-location';
import { useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { BirthProfile, useUser } from '../context/UserContext';

const C = {
  cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F',
  gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4',
};

// ── Geocoding via OpenStreetMap Nominatim (free, no API key) ─────────────────
interface PlaceSuggestion {
  display_name: string;
  lat: string;
  lon: string;
  address: { country_code?: string };
}

async function searchPlaces(query: string): Promise<PlaceSuggestion[]> {
  if (query.length < 2) return [];
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&addressdetails=1`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
  return res.json();
}

async function getTimezone(lat: number, lon: number): Promise<string> {
  try {
    const res = await fetch(
      `https://timeapi.io/api/timezone/coordinate?latitude=${lat}&longitude=${lon}`
    );
    const data = await res.json();
    return data.timeZone ?? Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Field({
  label, placeholder, value, onChangeText, keyboardType = 'default',
}: {
  label: string; placeholder: string; value: string;
  onChangeText: (t: string) => void; keyboardType?: any;
}) {
  return (
    <View style={s.field}>
      <Text style={s.fieldLabel}>{label}</Text>
      <TextInput
        style={s.input}
        placeholder={placeholder}
        placeholderTextColor={C.inkLight}
        value={value}
        onChangeText={onChangeText}
        keyboardType={keyboardType}
        autoCapitalize="none"
      />
    </View>
  );
}

// ── Main screen ───────────────────────────────────────────────────────────────

export default function OnboardingScreen() {
  const { setProfile } = useUser();
  const [step, setStep] = useState(1);

  // Step 1 — birth date/time
  const [name, setName]           = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [approxTime, setApproxTime] = useState(false);

  // Step 2 — birth place
  const [cityQuery, setCityQuery]       = useState('');
  const [suggestions, setSuggestions]   = useState<PlaceSuggestion[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<string>('');
  const [lat, setLat]   = useState<number | null>(null);
  const [lon, setLon]   = useState<number | null>(null);
  const [tz, setTz]     = useState('');
  const [locLoading, setLocLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  // ── Place search ─────────────────────────────────────────────────────────
  const handleCityChange = async (text: string) => {
    setCityQuery(text);
    setSelectedPlace('');
    setLat(null); setLon(null);
    if (text.length >= 2) {
      const results = await searchPlaces(text);
      setSuggestions(results);
    } else {
      setSuggestions([]);
    }
  };

  const selectPlace = async (place: PlaceSuggestion) => {
    setLocLoading(true);
    setSuggestions([]);
    const shortName = place.display_name.split(',').slice(0, 2).join(',').trim();
    setCityQuery(shortName);
    setSelectedPlace(shortName);
    const latN = parseFloat(place.lat);
    const lonN = parseFloat(place.lon);
    setLat(latN);
    setLon(lonN);
    const timezone = await getTimezone(latN, lonN);
    setTz(timezone);
    setLocLoading(false);
  };

  // ── GPS ──────────────────────────────────────────────────────────────────
  const useMyLocation = async () => {
    setLocLoading(true);
    setError('');
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setError('Location permission denied. Search for your city instead.');
        setLocLoading(false);
        return;
      }
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      const { latitude, longitude } = loc.coords;

      // Reverse geocode to get city name
      const [geo] = await Location.reverseGeocodeAsync({ latitude, longitude });
      const city = [geo.city ?? geo.region ?? 'Current location', geo.country].filter(Boolean).join(', ');
      setCityQuery(city);
      setSelectedPlace(city);
      setLat(latitude);
      setLon(longitude);

      const timezone = await getTimezone(latitude, longitude);
      setTz(timezone);
    } catch {
      setError('Could not get location. Search for your city instead.');
    }
    setLocLoading(false);
  };

  // ── Submit ────────────────────────────────────────────────────────────────
  const submit = async () => {
    setError('');
    if (!birthDate.match(/^\d{4}-\d{2}-\d{2}$/)) { setError('Date must be YYYY-MM-DD, e.g. 1990-04-15'); return; }
    if (!birthTime.match(/^\d{2}:\d{2}$/))        { setError('Time must be HH:MM, e.g. 08:30'); return; }
    if (!lat || !lon)                               { setError('Please search for or detect your birth city.'); return; }

    const profile: BirthProfile = {
      name,
      birthDate,
      birthTime,
      timezone: tz || Intl.DateTimeFormat().resolvedOptions().timeZone,
      latitude: lat,
      longitude: lon,
      placeName: selectedPlace,
      isApproximateTime: approxTime,
    };
    setLoading(true);
    await setProfile(profile);
    setLoading(false);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={s.scroll} contentContainerStyle={s.container} keyboardShouldPersistTaps="handled">

        {/* Progress dots */}
        <View style={s.dots}>
          {[1, 2, 3].map(i => <View key={i} style={[s.dot, step >= i && s.dotActive]} />)}
        </View>

        {/* ── Step 1 — Birth date & time ─────────────────────────────────── */}
        {step === 1 && (
          <>
            <Text style={s.stepTitle}>When were you born?</Text>
            <Text style={s.stepSub}>Your birth date and time are used to calculate your personal Vedic chart.</Text>

            <Field label="Your name (optional)" placeholder="First name" value={name} onChangeText={setName} />
            <Field label="Date of birth" placeholder="1990-04-15" value={birthDate} onChangeText={setBirthDate} />
            <Field label="Time of birth" placeholder="08:30" value={birthTime} onChangeText={setBirthTime} />

            <TouchableOpacity style={s.checkRow} onPress={() => setApproxTime(a => !a)}>
              <View style={[s.check, approxTime && s.checkOn]} />
              <Text style={s.checkLabel}>I don't know my exact birth time</Text>
            </TouchableOpacity>

            <TouchableOpacity style={s.btn} onPress={() => setStep(2)}>
              <Text style={s.btnText}>Next →</Text>
            </TouchableOpacity>
          </>
        )}

        {/* ── Step 2 — Birth place ───────────────────────────────────────── */}
        {step === 2 && (
          <>
            <Text style={s.stepTitle}>Where were you born?</Text>
            <Text style={s.stepSub}>Search for your birth city or tap the button to use your current location.</Text>

            {/* GPS button */}
            <TouchableOpacity style={s.gpsBtn} onPress={useMyLocation} disabled={locLoading}>
              {locLoading
                ? <ActivityIndicator color={C.gold} size="small" />
                : <Text style={s.gpsBtnText}>📍  Use my current location</Text>
              }
            </TouchableOpacity>

            <Text style={s.orText}>— or search —</Text>

            {/* City search */}
            <View style={s.field}>
              <Text style={s.fieldLabel}>Birth city</Text>
              <TextInput
                style={s.input}
                placeholder="e.g. London, Mumbai, New York"
                placeholderTextColor={C.inkLight}
                value={cityQuery}
                onChangeText={handleCityChange}
              />
            </View>

            {/* Suggestions dropdown */}
            {suggestions.length > 0 && (
              <View style={s.dropdown}>
                {suggestions.map((p, i) => (
                  <TouchableOpacity
                    key={i}
                    style={[s.suggestion, i < suggestions.length - 1 && s.suggestionBorder]}
                    onPress={() => selectPlace(p)}
                  >
                    <Text style={s.suggestionText}>{p.display_name.split(',').slice(0, 3).join(', ')}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            {/* Confirmed location */}
            {selectedPlace && lat && lon && (
              <View style={s.confirmedCard}>
                <Text style={s.confirmedEmoji}>✓</Text>
                <View>
                  <Text style={s.confirmedCity}>{selectedPlace}</Text>
                  <Text style={s.confirmedDetail}>Timezone: {tz}</Text>
                </View>
              </View>
            )}

            {error ? <Text style={s.error}>{error}</Text> : null}

            <View style={s.rowBtns}>
              <TouchableOpacity style={s.btnOutline} onPress={() => setStep(1)}><Text style={s.btnOutlineText}>← Back</Text></TouchableOpacity>
              <TouchableOpacity
                style={[s.btn, (!lat || !lon) && s.btnDisabled]}
                onPress={() => { if (lat && lon) setStep(3); else setError('Please select a city first.'); }}
                disabled={!lat || !lon}
              >
                <Text style={s.btnText}>Next →</Text>
              </TouchableOpacity>
            </View>
          </>
        )}

        {/* ── Step 3 — Confirm ───────────────────────────────────────────── */}
        {step === 3 && (
          <>
            <Text style={s.stepTitle}>Almost there</Text>
            <Text style={s.stepSub}>Check your details and tap Begin to see your first reading.</Text>

            <View style={s.summaryCard}>
              {[
                ['Name',     name || '(not set)'],
                ['Date',     birthDate],
                ['Time',     birthTime + (approxTime ? ' (approximate)' : '')],
                ['Place',    selectedPlace],
                ['Timezone', tz],
              ].map(([k, v]) => (
                <View key={k} style={s.summaryRow}>
                  <Text style={s.summaryKey}>{k}</Text>
                  <Text style={s.summaryVal}>{v}</Text>
                </View>
              ))}
            </View>

            {error ? <Text style={s.error}>{error}</Text> : null}

            <View style={s.rowBtns}>
              <TouchableOpacity style={s.btnOutline} onPress={() => setStep(2)}><Text style={s.btnOutlineText}>← Back</Text></TouchableOpacity>
              <TouchableOpacity style={[s.btn, loading && s.btnDisabled]} onPress={submit} disabled={loading}>
                {loading ? <ActivityIndicator color="#fff" /> : <Text style={s.btnText}>Begin</Text>}
              </TouchableOpacity>
            </View>
          </>
        )}

      </ScrollView>
    </KeyboardAvoidingView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────

const s = StyleSheet.create({
  scroll:    { flex: 1, backgroundColor: C.cream },
  container: { padding: 28, paddingTop: 64, paddingBottom: 48 },

  dots:      { flexDirection: 'row', gap: 8, marginBottom: 32 },
  dot:       { width: 8, height: 8, borderRadius: 4, backgroundColor: C.goldLight },
  dotActive: { backgroundColor: C.gold },

  stepTitle: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 8 },
  stepSub:   { fontSize: 13, color: C.inkLight, lineHeight: 20, marginBottom: 24 },

  field:      { marginBottom: 20 },
  fieldLabel: { fontSize: 10, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 6 },
  input:      { borderBottomWidth: 1, borderBottomColor: C.goldLight, paddingVertical: 10, fontSize: 16, color: C.ink },

  checkRow:  { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 28 },
  check:     { width: 20, height: 20, borderRadius: 4, borderWidth: 1.5, borderColor: C.goldLight },
  checkOn:   { backgroundColor: C.gold, borderColor: C.gold },
  checkLabel: { fontSize: 13, color: C.inkLight },

  gpsBtn:     { backgroundColor: C.card, borderRadius: 12, paddingVertical: 16, alignItems: 'center', marginBottom: 16, borderWidth: 1.5, borderColor: C.goldLight },
  gpsBtnText: { fontSize: 15, color: C.ink },

  orText: { textAlign: 'center', fontSize: 12, color: C.inkLight, marginBottom: 16 },

  dropdown:       { backgroundColor: C.card, borderRadius: 10, marginTop: -10, marginBottom: 16, overflow: 'hidden', borderWidth: 1, borderColor: C.goldLight },
  suggestion:     { padding: 14 },
  suggestionBorder: { borderBottomWidth: 1, borderBottomColor: C.goldLight },
  suggestionText: { fontSize: 13, color: C.ink },

  confirmedCard:  { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: '#EAF5EE', borderRadius: 10, padding: 14, marginBottom: 20 },
  confirmedEmoji: { fontSize: 18, color: '#2D6A4F' },
  confirmedCity:  { fontSize: 14, color: C.ink, fontWeight: '500' },
  confirmedDetail: { fontSize: 12, color: C.inkLight, marginTop: 2 },

  btn:         { backgroundColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnDisabled: { opacity: 0.4 },
  btnText:     { color: '#fff', fontSize: 15, fontWeight: '500' },
  btnOutline:  { borderWidth: 1.5, borderColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnOutlineText: { color: C.ink, fontSize: 15 },
  rowBtns:     { flexDirection: 'row', gap: 12, marginTop: 8 },

  summaryCard: { backgroundColor: C.card, borderRadius: 12, padding: 16, marginBottom: 20 },
  summaryRow:  { flexDirection: 'row', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.goldLight },
  summaryKey:  { width: 80, fontSize: 12, color: C.inkLight },
  summaryVal:  { flex: 1, fontSize: 13, color: C.ink },

  error: { color: '#E76F51', fontSize: 13, marginBottom: 12 },
});
