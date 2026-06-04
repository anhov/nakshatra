import { useState } from 'react';
import {
  ActivityIndicator, KeyboardAvoidingView, Platform,
  ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View,
} from 'react-native';
import { BirthProfile, useUser } from '../context/UserContext';
import { createUser } from '../services/api';

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4' };

function Field({ label, placeholder, value, onChangeText, keyboardType = 'default' }: {
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

export default function OnboardingScreen() {
  const { setProfile } = useUser();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [approxTime, setApproxTime] = useState(false);
  const [placeName, setPlaceName] = useState('');
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [tz, setTz] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async () => {
    setError('');
    if (!birthDate.match(/^\d{4}-\d{2}-\d{2}$/)) { setError('Birth date must be YYYY-MM-DD'); return; }
    if (!birthTime.match(/^\d{2}:\d{2}$/)) { setError('Birth time must be HH:MM'); return; }
    const latN = parseFloat(lat), lonN = parseFloat(lon);
    if (isNaN(latN) || isNaN(lonN)) { setError('Enter valid latitude and longitude'); return; }

    const profile: BirthProfile = {
      name, birthDate, birthTime, timezone: tz,
      latitude: latN, longitude: lonN,
      placeName, isApproximateTime: approxTime,
    };
    setLoading(true);
    try {
      await createUser(profile).catch(() => {});  // DB optional; don't block if unavailable
      await setProfile(profile);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView style={s.scroll} contentContainerStyle={s.container} keyboardShouldPersistTaps="handled">
        {/* Progress dots */}
        <View style={s.dots}>
          {[1,2,3].map(i => <View key={i} style={[s.dot, step >= i && s.dotActive]} />)}
        </View>

        {step === 1 && (
          <>
            <Text style={s.stepTitle}>Your birth details</Text>
            <Text style={s.stepSub}>We use Swiss Ephemeris to calculate your personal chart — the most accurate system available.</Text>
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

        {step === 2 && (
          <>
            <Text style={s.stepTitle}>Birth place</Text>
            <Text style={s.stepSub}>Enter the city and coordinates of where you were born.</Text>
            <Field label="City / place" placeholder="Kolkata, India" value={placeName} onChangeText={setPlaceName} />
            <Field label="Latitude" placeholder="22.57" value={lat} onChangeText={setLat} keyboardType="decimal-pad" />
            <Field label="Longitude" placeholder="88.36" value={lon} onChangeText={setLon} keyboardType="decimal-pad" />
            <Field label="Timezone (IANA)" placeholder="Asia/Kolkata" value={tz} onChangeText={setTz} />
            <Text style={s.hint}>Find coordinates at latlong.net or Google Maps (right-click a location).</Text>
            <View style={s.rowBtns}>
              <TouchableOpacity style={s.btnOutline} onPress={() => setStep(1)}><Text style={s.btnOutlineText}>← Back</Text></TouchableOpacity>
              <TouchableOpacity style={s.btn} onPress={() => setStep(3)}><Text style={s.btnText}>Next →</Text></TouchableOpacity>
            </View>
          </>
        )}

        {step === 3 && (
          <>
            <Text style={s.stepTitle}>Almost there</Text>
            <Text style={s.stepSub}>Review your details and tap Begin to generate your first reading.</Text>
            <View style={s.summaryCard}>
              {[['Name', name || '(not set)'], ['Date', birthDate], ['Time', birthTime + (approxTime ? ' (approx)' : '')],
                ['Place', placeName], ['Lat/Lon', `${lat}, ${lon}`], ['Timezone', tz]].map(([k, v]) => (
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

const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 28, paddingTop: 64, paddingBottom: 40 },
  dots: { flexDirection: 'row', gap: 8, marginBottom: 32 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: C.goldLight },
  dotActive: { backgroundColor: C.gold },
  stepTitle: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 8 },
  stepSub: { fontSize: 13, color: C.inkLight, lineHeight: 20, marginBottom: 24 },
  field: { marginBottom: 18 },
  fieldLabel: { fontSize: 10, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 6 },
  input: { borderBottomWidth: 1, borderBottomColor: C.goldLight, paddingVertical: 8, fontSize: 16, color: C.ink },
  checkRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 24 },
  check: { width: 20, height: 20, borderRadius: 4, borderWidth: 1.5, borderColor: C.goldLight },
  checkOn: { backgroundColor: C.gold, borderColor: C.gold },
  checkLabel: { fontSize: 13, color: C.inkLight },
  btn: { backgroundColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnDisabled: { opacity: 0.6 },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '500' },
  btnOutline: { borderWidth: 1.5, borderColor: C.ink, borderRadius: 12, paddingVertical: 16, alignItems: 'center', flex: 1 },
  btnOutlineText: { color: C.ink, fontSize: 15 },
  rowBtns: { flexDirection: 'row', gap: 12, marginTop: 8 },
  hint: { fontSize: 11, color: C.inkLight, marginBottom: 20, lineHeight: 16 },
  summaryCard: { backgroundColor: C.card, borderRadius: 12, padding: 16, marginBottom: 20 },
  summaryRow: { flexDirection: 'row', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.goldLight },
  summaryKey: { width: 80, fontSize: 12, color: C.inkLight },
  summaryVal: { flex: 1, fontSize: 13, color: C.ink },
  error: { color: '#E76F51', fontSize: 13, marginBottom: 12 },
});
