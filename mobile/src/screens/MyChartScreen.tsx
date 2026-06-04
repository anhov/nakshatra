import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useUser } from '../context/UserContext';
import { fetchBirthChart, fetchDasha, fetchNakshatraMantra, fetchPlanetaryMantra } from '../services/api';

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4' };

interface Graha { name: string; sign: string; house: number; nakshatra: string; is_retrograde: boolean; strength: string; navamsha: string }
interface Lagna { sign: string; sign_degree: number; nakshatra: string; navamsha?: string }
interface ActivePeriod { mahadasha: string; md_start: string; md_end: string; md_elapsed_pct: number; antardasha: string; ad_start: string; ad_end: string; ad_elapsed_pct: number }
interface Dasha { moon_nakshatra: string; dasha_lord_at_birth: string; active: ActivePeriod | null }

const STRENGTH_COLOR: Record<string, string> = { Exalted: '#2D6A4F', 'Own Sign': '#52B788', Neutral: C.inkLight, Debilitated: '#E76F51' };

function ProgressBar({ pct, color }: { pct: number; color: string }) {
  return (
    <View style={{ height: 4, backgroundColor: '#E8D5A3', borderRadius: 2, marginTop: 6 }}>
      <View style={{ height: 4, width: `${pct}%`, backgroundColor: color, borderRadius: 2 }} />
    </View>
  );
}

export default function MyChartScreen() {
  const { profile } = useUser();
  const [chart, setChart] = useState<any>(null);
  const [dasha, setDasha] = useState<Dasha | null>(null);
  const [mantra, setMantra] = useState<any>(null);
  const [nakMantra, setNakMantra] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) { setLoading(false); return; }
    Promise.all([fetchBirthChart(profile), fetchDasha(profile)])
      .then(([c, d]: [any, any]) => {
        setChart(c); setDasha(d);
        if (d.active) {
          fetchPlanetaryMantra(d.active.mahadasha).then(setMantra).catch(console.error);
        }
        const moon = c.grahas.find((g: Graha) => g.name === 'Moon');
        if (moon) fetchNakshatraMantra(moon.nakshatra).then(setNakMantra).catch(console.error);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [profile]);

  if (!profile) return <View style={s.center}><Text style={s.body}>Complete onboarding to see your chart.</Text></View>;
  if (loading) return <View style={s.center}><ActivityIndicator color={C.gold} size="large" /></View>;
  if (!chart || !dasha) return <View style={s.center}><Text style={s.body}>Could not load chart.</Text></View>;

  const lagna: Lagna = chart.lagna;
  const grahas: Graha[] = chart.grahas;
  const sun = grahas.find(g => g.name === 'Sun');
  const moon = grahas.find(g => g.name === 'Moon');
  const active = dasha.active;

  return (
    <ScrollView style={s.scroll} contentContainerStyle={s.container}>
      <Text style={s.screenTitle}>My Chart</Text>

      {/* Key signs */}
      <View style={s.triRow}>
        <View style={s.triCard}><Text style={s.triLabel}>Rising Sign</Text><Text style={s.triVal}>{lagna.sign}</Text></View>
        <View style={s.triCard}><Text style={s.triLabel}>Moon Sign</Text><Text style={s.triVal}>{moon?.sign ?? '—'}</Text></View>
        <View style={s.triCard}><Text style={s.triLabel}>Sun Sign</Text><Text style={s.triVal}>{sun?.sign ?? '—'}</Text></View>
      </View>
      <View style={[s.triRow, { marginTop: 8 }]}>
        <View style={[s.triCard, { flex: 1 }]}><Text style={s.triLabel}>Birth Star</Text><Text style={s.triVal}>{moon?.nakshatra ?? '—'}</Text></View>
        <View style={[s.triCard, { flex: 1 }]}><Text style={s.triLabel}>D-9 Lagna</Text><Text style={s.triVal}>{lagna.navamsha ?? '—'}</Text></View>
      </View>

      <View style={s.divider} />

      {/* Dasha */}
      {active && (
        <View style={s.section}>
          <Text style={s.sectionTitle}>Current Life Period</Text>
          <View style={s.dashaCard}>
            <Text style={s.dashaLabel}>Major Period</Text>
            <Text style={s.dashaValue}>{active.mahadasha} Mahadasha</Text>
            <Text style={s.dashaDate}>{active.md_start.split('T')[0]} → {active.md_end.split('T')[0]}</Text>
            <ProgressBar pct={active.md_elapsed_pct} color={C.gold} />
            <Text style={s.dashaLabel2}>Sub-Period</Text>
            <Text style={s.dashaValue2}>{active.antardasha} Antardasha</Text>
            <Text style={s.dashaDate}>{active.ad_start.split('T')[0]} → {active.ad_end.split('T')[0]}</Text>
            <ProgressBar pct={active.ad_elapsed_pct} color={C.inkLight} />
          </View>
          {nakMantra && (
            <View style={s.mantraCard}>
              <Text style={s.mantraLabel}>Today's Energy — {moon?.nakshatra}</Text>
              <Text style={s.mantraTheme}>{nakMantra.energy_theme}</Text>
            </View>
          )}
          {mantra && (
            <View style={s.mantraCard}>
              <Text style={s.mantraLabel}>{active.mahadasha} Period Mantra</Text>
              <Text style={s.mantraText}>{mantra.beej_mantra}</Text>
              <Text style={s.mantraPhonetic}>{mantra.phonetics}</Text>
              <Text style={s.mantraMeaning}>{mantra.meaning}</Text>
            </View>
          )}
        </View>
      )}

      <View style={s.divider} />

      {/* Grahas */}
      <Text style={s.sectionTitle}>Planetary Positions</Text>
      {grahas.map(g => (
        <View key={g.name} style={s.grahaRow}>
          <Text style={s.grahaName}>{g.name}{g.is_retrograde ? ' ℞' : ''}</Text>
          <Text style={s.grahaSign}>{g.sign}</Text>
          <Text style={s.grahaHouse}>H{g.house}</Text>
          <Text style={[s.grahaStrength, { color: STRENGTH_COLOR[g.strength] ?? C.inkLight }]}>{g.strength}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 24, paddingTop: 56, paddingBottom: 40 },
  center: { flex: 1, backgroundColor: C.cream, alignItems: 'center', justifyContent: 'center', padding: 24 },
  screenTitle: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 20 },
  triRow: { flexDirection: 'row', gap: 8 },
  triCard: { flex: 1, backgroundColor: C.card, borderRadius: 10, padding: 12 },
  triLabel: { fontSize: 9, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 4 },
  triVal: { fontSize: 15, color: C.ink, fontWeight: '400' },
  divider: { height: 1, backgroundColor: C.goldLight, marginVertical: 20, opacity: 0.7 },
  section: { gap: 10 },
  sectionTitle: { fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', color: C.inkLight, marginBottom: 12 },
  dashaCard: { backgroundColor: C.card, borderRadius: 12, padding: 16 },
  dashaLabel: { fontSize: 9, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 2 },
  dashaValue: { fontSize: 18, color: C.ink, fontWeight: '300' },
  dashaDate: { fontSize: 11, color: C.inkLight, marginBottom: 4 },
  dashaLabel2: { fontSize: 9, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginTop: 12, marginBottom: 2 },
  dashaValue2: { fontSize: 15, color: C.ink, fontWeight: '300' },
  mantraCard: { backgroundColor: C.card, borderRadius: 12, padding: 16 },
  mantraLabel: { fontSize: 9, letterSpacing: 1.5, textTransform: 'uppercase', color: C.gold, marginBottom: 6 },
  mantraTheme: { fontSize: 13, color: C.inkLight, lineHeight: 19 },
  mantraText: { fontSize: 15, color: C.ink, fontWeight: '400', marginBottom: 4 },
  mantraPhonetic: { fontSize: 11, color: C.inkLight, fontStyle: 'italic', marginBottom: 4 },
  mantraMeaning: { fontSize: 12, color: C.inkLight, lineHeight: 17 },
  grahaRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.goldLight },
  grahaName: { width: 80, fontSize: 13, color: C.ink, fontWeight: '500' },
  grahaSign: { flex: 1, fontSize: 13, color: C.ink },
  grahaHouse: { width: 32, fontSize: 12, color: C.inkLight },
  grahaStrength: { width: 80, fontSize: 11, textAlign: 'right' },
  body: { fontSize: 14, color: C.inkLight, textAlign: 'center' },
});
