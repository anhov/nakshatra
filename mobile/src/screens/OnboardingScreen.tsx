import * as Location from 'expo-location';
import { useState } from 'react';
import {
  ActivityIndicator,
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
  green: '#2D6A4F', red: '#E76F51',
};

// ── Date helpers (user sees DD/MM/YYYY, API gets YYYY-MM-DD) ─────────────────

function formatDateInput(raw: string): string {
  const d = raw.replace(/\D/g, '').slice(0, 8);
  if (d.length <= 2) return d;
  if (d.length <= 4) return `${d.slice(0, 2)}/${d.slice(2)}`;
  return `${d.slice(0, 2)}/${d.slice(2, 4)}/${d.slice(4)}`;
}

function displayToISO(display: string): string {
  const parts = display.split('/');
  if (parts.length === 3 && parts[2].length === 4) {
    return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
  }
  return '';
}

function validateDate(display: string): string {
  const iso = displayToISO(display);
  if (!iso) return 'Enter date as DD/MM/YYYY';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return 'That date doesn\'t look right';
  if (d.getFullYear() < 1900 || d.getFullYear() > new Date().getFullYear()) return 'Check the year';
  return '';
}

// ── Time helpers (user sees HH:MM + AM/PM, API gets 24h HH:MM) ──────────────

function formatTimeInput(raw: string): string {
  const d = raw.replace(/\D/g, '').slice(0, 4);
  if (d.length <= 2) return d;
  return `${d.slice(0, 2)}:${d.slice(2)}`;
}

function to24h(display: string, ampm: 'AM' | 'PM'): string {
  const [hStr, mStr] = display.split(':');
  let h = parseInt(hStr ?? '0', 10);
  const m = parseInt(mStr ?? '0', 10);
  if (isNaN(h) || isNaN(m)) return '';
  if (ampm === 'AM') { if (h === 12) h = 0; }
  else               { if (h !== 12) h += 12; }
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

function validateTime(display: string): string {
  if (!display.includes(':')) return '';  // still typing
  const [hStr, mStr] = display.split(':');
  const h = parseInt(hStr, 10), m = parseInt(mStr, 10);
  if (isNaN(h) || h < 1 || h > 12) return 'Hours should be 1–12';
  if (mStr.length === 2 && (isNaN(m) || m > 59)) return 'Minutes should be 00–59';
  return '';
}

// ── Geocoding ────────────────────────────────────────────────────────────────

interface Place { display_name: string; lat: string; lon: string }

async function searchPlaces(q: string): Promise<Place[]> {
  if (q.length < 2) return [];
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=5`;
  const res = await fetch(url, { headers: { 'Accept-Language': 'en' } });
  return res.json();
}

async function getTimezone(lat: number, lon: number): Promise<string> {
  try {
    const res = await fetch(`https://timeapi.io/api/timezone/coordinate?latitude=${lat}&longitude=${lon}`);
    const data = await res.json();
    return data.timeZone ?? Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }
}

// ── Reusable label ────────────────────────────────────────────────────────────

function Label({ text }: { text: string }) {
  return <Text style={s.fieldLabel}>{text}</Text>;
}

// ── Main screen ───────────────────────────────────────────────────────────────

export default function OnboardingScreen() {
  const { setProfile } = useUser();
  const [step, setStep] = useState(1);

  // Step 1
  const [name, setName]             = useState('');
  const [dateDisplay, setDateDisplay] = useState('');
  const [dateError, setDateError]   = useState('');
  const [timeDisplay, setTimeDisplay] = useState('');
  const [timeError, setTimeError]   = useState('');
  const [ampm, setAmpm]             = useState<'AM' | 'PM'>('AM');
  const [approxTime, setApproxTime] = useState(false);

  // Step 2
  const [cityQuery, setCityQuery]       = useState('');
  const [suggestions, setSuggestions]   = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState('');
  const [lat, setLat]   = useState<number | null>(null);
  const [lon, setLon]   = useState<number | null>(null);
  const [tz, setTz]     = useState('');
  const [locLoading, setLocLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  // ── Handlers ─────────────────────────────────────────────────────────────

  const handleDate = (raw: string) => {
    const formatted = formatDateInput(raw);
    setDateDisplay(formatted);
    if (formatted.length === 10) setDateError(validateDate(formatted));
    else setDateError('');
  };

  const handleTime = (raw: string) => {
    const formatted = formatTimeInput(raw);
    setTimeDisplay(formatted);
    setTimeError(validateTime(formatted));
  };

  const handleCity = async (text: string) => {
    setCityQuery(text);
    setSelectedPlace(''); setLat(null); setLon(null);
    const results = await searchPlaces(text);
    setSuggestions(results);
  };

  const selectPlace = async (p: Place) => {
    setLocLoading(true);
    setSuggestions([]);
    const short = p.display_name.split(',').slice(0, 2).join(',').trim();
    setCityQuery(short); setSelectedPlace(short);
    const latN = parseFloat(p.lat), lonN = parseFloat(p.lon);
    setLat(latN); setLon(lonN);
    setTz(await getTimezone(latN, lonN));
    setLocLoading(false);
  };

  const useGPS = async () => {
    setLocLoading(true); setError('');
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') { setError('Location denied. Search for your city instead.'); return; }
      const loc  = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      const { latitude, longitude } = loc.coords;
      const [geo] = await Location.reverseGeocodeAsync({ latitude, longitude });
      const city  = [geo.city ?? geo.region ?? 'Current location', geo.country].filter(Boolean).join(', ');
      setCityQuery(city); setSelectedPlace(city);
      setLat(latitude); setLon(longitude);
      setTz(await getTimezone(latitude, longitude));
    } catch { setError('Could not get location. Search for your city instead.'); }
    finally  { setLocLoading(false); }
  };

  const goToStep2 = () => {
    const dErr = validateDate(dateDisplay);
    if (dErr) { setDateError(dErr); return; }
    if (!approxTime) {
      const tErr = validateTime(timeDisplay);
      if (tErr || !timeDisplay.includes(':')) { setTimeError(tErr || 'Enter your birth time'); return; }
    }
    setStep(2);
  };

  const submit = async () => {
    setError('');
    if (!lat || !lon) { setError('Please select a birth city.'); return; }
    const iso = displayToISO(dateDisplay);
    const time24 = approxTime ? '06:00' : to24h(timeDisplay, ampm);
    const profile: BirthProfile = {
      name, birthDate: iso, birthTime: time24,
      timezone: tz || Intl.DateTimeFormat().resolvedOptions().timeZone,
      latitude: lat, longitude: lon, placeName: selectedPlace,
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

        <View style={s.dots}>
          {[1, 2, 3].map(i => <View key={i} style={[s.dot, step >= i && s.dotActive]} />)}
        </View>

        {/* ── Step 1 ─────────────────────────────────────────────────────── */}
        {step === 1 && (
          <>
            <Text style={s.stepTitle}>When were you born?</Text>
            <Text style={s.stepSub}>Your birth details are used to calculate your personal Vedic chart.</Text>

            {/* Name */}
            <View style={s.field}>
              <Label text="Your name (optional)" />
              <TextInput style={s.input} placeholder="First name" placeholderTextColor={C.inkLight}
                value={name} onChangeText={setName} />
            </View>

            {/* Date — DD/MM/YYYY */}
            <View style={s.field}>
              <Label text="Date of birth" />
              <TextInput
                style={[s.input, dateError ? s.inputError : null]}
                placeholder="DD / MM / YYYY"
                placeholderTextColor={C.inkLight}
                value={dateDisplay}
                onChangeText={handleDate}
                keyboardType="number-pad"
                maxLength={10}
              />
              {dateError ? <Text style={s.hint_err}>{dateError}</Text> : null}
              {dateDisplay.length === 10 && !dateError
                ? <Text style={s.hint_ok}>✓ {dateDisplay}</Text> : null}
            </View>

            {/* Approximate time toggle */}
            <TouchableOpacity style={s.checkRow} onPress={() => { setApproxTime(a => !a); setTimeError(''); }}>
              <View style={[s.check, approxTime && s.checkOn]} />
              <Text style={s.checkLabel}>I don't know my exact birth time</Text>
            </TouchableOpacity>

            {/* Time — HH:MM + AM/PM */}
            {!approxTime && (
              <View style={s.field}>
                <Label text="Time of birth" />
                <View style={s.timeRow}>
                  <TextInput
                    style={[s.input, s.timeInput, timeError ? s.inputError : null]}
                    placeholder="HH : MM"
                    placeholderTextColor={C.inkLight}
                    value={timeDisplay}
                    onChangeText={handleTime}
                    keyboardType="number-pad"
                    maxLength={5}
                  />
                  <View style={s.ampmRow}>
                    {(['AM', 'PM'] as const).map(val => (
                      <TouchableOpacity
                        key={val}
                        style={[s.ampmBtn, ampm === val && s.ampmActive]}
                        onPress={() => setAmpm(val)}
                      >
                        <Text style={[s.ampmText, ampm === val && s.ampmTextActive]}>{val}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
                {timeError ? <Text style={s.hint_err}>{timeError}</Text> : null}
              </View>
            )}

            <TouchableOpacity style={s.btn} onPress={goToStep2}>
              <Text style={s.btnText}>Next →</Text>
            </TouchableOpacity>
          </>
        )}

        {/* ── Step 2 ─────────────────────────────────────────────────────── */}
        {step === 2 && (
          <>
            <Text style={s.stepTitle}>Where were you born?</Text>
            <Text style={s.stepSub}>Search for your birth city or tap the button to use your device location.</Text>

            <TouchableOpacity style={s.gpsBtn} onPress={useGPS} disabled={locLoading}>
              {locLoading
                ? <ActivityIndicator color={C.gold} size="small" />
                : <Text style={s.gpsBtnText}>📍  Use my current location</Text>}
            </TouchableOpacity>

            <Text style={s.orText}>— or type your birth city —</Text>

            <View style={s.field}>
              <Label text="Birth city" />
              <TextInput
                style={s.input}
                placeholder="e.g. London, Mumbai, New York"
                placeholderTextColor={C.inkLight}
                value={cityQuery}
                onChangeText={handleCity}
              />
            </View>

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

            {selectedPlace && lat && (
              <View style={s.confirmedCard}>
                <Text style={s.confirmedCheck}>✓</Text>
                <View>
                  <Text style={s.confirmedCity}>{selectedPlace}</Text>
                  <Text style={s.confirmedTz}>Timezone: {tz}</Text>
                </View>
              </View>
            )}

            {error ? <Text style={s.hint_err}>{error}</Text> : null}

            <View style={s.rowBtns}>
              <TouchableOpacity style={s.btnOutline} onPress={() => setStep(1)}>
                <Text style={s.btnOutlineText}>← Back</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[s.btn, (!lat || !lon) && s.btnDisabled]}
                onPress={() => lat && lon ? setStep(3) : setError('Please select a city first.')}
              >
                <Text style={s.btnText}>Next →</Text>
              </TouchableOpacity>
            </View>
          </>
        )}

        {/* ── Step 3 ─────────────────────────────────────────────────────── */}
        {step === 3 && (
          <>
            <Text style={s.stepTitle}>Almost there</Text>
            <Text style={s.stepSub}>Everything looks right? Tap Begin to see your first reading.</Text>

            <View style={s.summaryCard}>
              {[
                ['Name',      name || '(not set)'],
                ['Date',      dateDisplay],
                ['Time',      approxTime ? 'Unknown (approx. 6 AM used)' : `${timeDisplay} ${ampm}`],
                ['Place',     selectedPlace],
                ['Timezone',  tz],
              ].map(([k, v]) => (
                <View key={k} style={s.summaryRow}>
                  <Text style={s.summaryKey}>{k}</Text>
                  <Text style={s.summaryVal}>{v}</Text>
                </View>
              ))}
            </View>

            {error ? <Text style={s.hint_err}>{error}</Text> : null}

            <View style={s.rowBtns}>
              <TouchableOpacity style={s.btnOutline} onPress={() => setStep(2)}>
                <Text style={s.btnOutlineText}>← Back</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[s.btn, loading && s.btnDisabled]} onPress={submit} disabled={loading}>
                {loading ? <ActivityIndicator color="#fff" /> : <Text style={s.btnText}>Begin ✦</Text>}
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
  container: { padding: 28, paddingTop: 64, paddingBottom: 56 },

  dots:      { flexDirection: 'row', gap: 8, marginBottom: 32 },
  dot:       { width: 8, height: 8, borderRadius: 4, backgroundColor: C.goldLight },
  dotActive: { backgroundColor: C.gold },

  stepTitle: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 8 },
  stepSub:   { fontSize: 13, color: C.inkLight, lineHeight: 20, marginBottom: 28 },

  field:      { marginBottom: 22 },
  fieldLabel: { fontSize: 10, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 8 },
  input:      { borderBottomWidth: 1.5, borderBottomColor: C.goldLight, paddingVertical: 10, fontSize: 18, color: C.ink, letterSpacing: 1 },
  inputError: { borderBottomColor: C.red },

  hint_err: { fontSize: 12, color: C.red, marginTop: 4 },
  hint_ok:  { fontSize: 12, color: C.green, marginTop: 4 },

  // Time row
  timeRow:   { flexDirection: 'row', alignItems: 'center', gap: 12 },
  timeInput: { flex: 1 },
  ampmRow:   { flexDirection: 'row', gap: 6 },
  ampmBtn:   { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 8, borderWidth: 1.5, borderColor: C.goldLight },
  ampmActive: { backgroundColor: C.gold, borderColor: C.gold },
  ampmText:   { fontSize: 13, color: C.inkLight },
  ampmTextActive: { color: '#fff', fontWeight: '600' },

  // Checkbox
  checkRow:  { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 20 },
  check:     { width: 20, height: 20, borderRadius: 4, borderWidth: 1.5, borderColor: C.goldLight },
  checkOn:   { backgroundColor: C.gold, borderColor: C.gold },
  checkLabel: { fontSize: 13, color: C.inkLight },

  // GPS
  gpsBtn:     { backgroundColor: C.card, borderRadius: 12, paddingVertical: 16, alignItems: 'center', marginBottom: 16, borderWidth: 1.5, borderColor: C.goldLight },
  gpsBtnText: { fontSize: 15, color: C.ink },
  orText:     { textAlign: 'center', fontSize: 12, color: C.inkLight, marginBottom: 20 },

  // City dropdown
  dropdown:       { backgroundColor: C.card, borderRadius: 10, marginTop: -12, marginBottom: 16, borderWidth: 1, borderColor: C.goldLight, overflow: 'hidden' },
  suggestion:     { padding: 14 },
  suggestionBorder: { borderBottomWidth: 1, borderBottomColor: C.goldLight },
  suggestionText: { fontSize: 13, color: C.ink },

  // Confirmed location
  confirmedCard:  { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: '#EAF5EE', borderRadius: 10, padding: 14, marginBottom: 20 },
  confirmedCheck: { fontSize: 20, color: C.green },
  confirmedCity:  { fontSize: 14, color: C.ink, fontWeight: '500' },
  confirmedTz:    { fontSize: 12, color: C.inkLight, marginTop: 2 },

  // Buttons
  btn:            { backgroundColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnDisabled:    { opacity: 0.35 },
  btnText:        { color: '#fff', fontSize: 15, fontWeight: '500' },
  btnOutline:     { borderWidth: 1.5, borderColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnOutlineText: { color: C.ink, fontSize: 15 },
  rowBtns:        { flexDirection: 'row', gap: 12, marginTop: 8 },

  // Summary
  summaryCard: { backgroundColor: C.card, borderRadius: 12, padding: 16, marginBottom: 20 },
  summaryRow:  { flexDirection: 'row', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.goldLight },
  summaryKey:  { width: 80, fontSize: 12, color: C.inkLight },
  summaryVal:  { flex: 1, fontSize: 13, color: C.ink },
});
