import { useEffect, useState } from 'react';
import {
  ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';
import { useUser } from '../context/UserContext';
import { fetchToday } from '../services/api';

const C = {
  cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F',
  gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4',
};

function greeting() {
  const h = new Date().getHours();
  return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
}

function scoreColor(score: number) {
  if (score >= 8) return '#2D6A4F';
  if (score >= 6.5) return '#52B788';
  if (score >= 5) return '#F4A261';
  return '#E76F51';
}

interface Activity { emoji: string; title: string; description: string; timing: string | null }
interface TodayData {
  score: number; quality: string; tagline: string;
  moon_nakshatra: string; paksha: string; tithi_label: string;
  current_mahadasha: string; current_antardasha: string;
  activities: Activity[];
  avoid_text: string; avoid_suggestion: string;
  best_times: string[]; avoid_times: string[];
}

export default function TodayScreen() {
  const { profile } = useUser();
  const [data, setData] = useState<TodayData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) { setLoading(false); return; }
    fetchToday(profile)
      .then(d => setData(d as TodayData))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [profile]);

  if (loading) return <View style={s.center}><ActivityIndicator color={C.gold} size="large" /></View>;

  if (!profile) return (
    <View style={s.center}>
      <Text style={s.bodyText}>Complete onboarding to see your daily reading.</Text>
    </View>
  );

  if (error || !data) return (
    <View style={s.center}>
      <Text style={s.errorText}>{error ?? 'Something went wrong.'}</Text>
    </View>
  );

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  return (
    <ScrollView style={s.scroll} contentContainerStyle={s.container}>
      <Text style={s.greeting}>{greeting()}{profile.name ? `, ${profile.name}` : ''}</Text>
      <Text style={s.dateText}>{today}</Text>

      {/* Score strip */}
      <View style={[s.scoreStrip, { borderLeftColor: scoreColor(data.score) }]}>
        <Text style={[s.scoreNumber, { color: scoreColor(data.score) }]}>{data.score}</Text>
        <Text style={s.scoreSlash}>/10</Text>
        <View style={s.scoreRight}>
          <Text style={s.scoreLabel}>{data.quality}</Text>
          <Text style={s.moonLine}>Moon in {data.moon_nakshatra} · {data.paksha}</Text>
        </View>
      </View>

      <Text style={s.tagline}>{data.tagline}</Text>

      <View style={s.divider} />

      {/* Dasha */}
      <View style={s.metaRow}>
        <View style={s.metaChip}><Text style={s.metaLabel}>Life period</Text><Text style={s.metaVal}>{data.current_mahadasha}</Text></View>
        <View style={s.metaChip}><Text style={s.metaLabel}>Sub-period</Text><Text style={s.metaVal}>{data.current_antardasha}</Text></View>
        <View style={s.metaChip}><Text style={s.metaLabel}>Lunar day</Text><Text style={s.metaVal}>{data.tithi_label}</Text></View>
      </View>

      <View style={s.divider} />

      {/* Activities */}
      <Text style={s.sectionTitle}>Favourable Today</Text>
      <View style={s.grid}>
        {data.activities.map((a, i) => (
          <View key={i} style={s.card}>
            <Text style={s.cardEmoji}>{a.emoji}</Text>
            <Text style={s.cardTitle}>{a.title}</Text>
            <Text style={s.cardDesc}>{a.description}</Text>
            {a.timing && <View style={s.timingBadge}><Text style={s.timingText}>{a.timing}</Text></View>}
          </View>
        ))}
      </View>

      <View style={s.divider} />

      {/* Best times */}
      <Text style={s.sectionTitle}>Best Windows</Text>
      {data.best_times.map((t, i) => (
        <View key={i} style={s.timeRow}>
          <Text style={s.timeIcon}>✦</Text>
          <Text style={s.timeText}>{t}</Text>
        </View>
      ))}

      {/* Avoid */}
      <View style={s.avoidStrip}>
        <Text style={s.avoidTitle}>Better to avoid</Text>
        <Text style={s.avoidText}>{data.avoid_text}</Text>
        <Text style={s.avoidSuggestion}>{data.avoid_suggestion}</Text>
        {data.avoid_times.map((t, i) => (
          <Text key={i} style={s.avoidTime}>⚠ {t}</Text>
        ))}
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 24, paddingTop: 60, paddingBottom: 40 },
  center: { flex: 1, backgroundColor: C.cream, alignItems: 'center', justifyContent: 'center', padding: 24 },
  greeting: { fontSize: 12, letterSpacing: 2, color: C.gold, textTransform: 'uppercase', marginBottom: 4 },
  dateText: { fontSize: 24, fontWeight: '300', color: C.ink, marginBottom: 20 },
  scoreStrip: { flexDirection: 'row', alignItems: 'center', borderLeftWidth: 3, paddingLeft: 12, marginBottom: 16 },
  scoreNumber: { fontSize: 42, fontWeight: '200' },
  scoreSlash: { fontSize: 18, color: C.inkLight, marginLeft: 2, marginTop: 14 },
  scoreRight: { marginLeft: 12 },
  scoreLabel: { fontSize: 18, color: C.ink, fontWeight: '400' },
  moonLine: { fontSize: 12, color: C.inkLight, marginTop: 2 },
  tagline: { fontSize: 15, color: C.inkLight, lineHeight: 22, marginBottom: 4 },
  divider: { height: 1, backgroundColor: C.goldLight, marginVertical: 20, opacity: 0.7 },
  metaRow: { flexDirection: 'row', gap: 8 },
  metaChip: { flex: 1, backgroundColor: C.card, borderRadius: 8, padding: 10 },
  metaLabel: { fontSize: 9, color: C.inkLight, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 3 },
  metaVal: { fontSize: 12, color: C.ink, fontWeight: '500' },
  sectionTitle: { fontSize: 10, letterSpacing: 2, color: C.inkLight, textTransform: 'uppercase', marginBottom: 12 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  card: { width: '47%', backgroundColor: C.card, borderRadius: 12, padding: 14 },
  cardEmoji: { fontSize: 22, marginBottom: 6 },
  cardTitle: { fontSize: 13, color: C.ink, fontWeight: '600', marginBottom: 4 },
  cardDesc: { fontSize: 11, color: C.inkLight, lineHeight: 16 },
  timingBadge: { marginTop: 8, backgroundColor: C.goldLight, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3, alignSelf: 'flex-start' },
  timingText: { fontSize: 10, color: C.ink },
  timeRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  timeIcon: { color: C.gold, marginRight: 8, fontSize: 12 },
  timeText: { fontSize: 13, color: C.ink },
  avoidStrip: { backgroundColor: '#FDF5E6', borderRadius: 12, padding: 16, marginTop: 4, borderLeftWidth: 3, borderLeftColor: '#F4A261' },
  avoidTitle: { fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', color: '#C4673A', marginBottom: 6 },
  avoidText: { fontSize: 13, color: C.ink, marginBottom: 4 },
  avoidSuggestion: { fontSize: 12, color: C.inkLight, fontStyle: 'italic', marginBottom: 8 },
  avoidTime: { fontSize: 12, color: '#C4673A', marginTop: 2 },
  bodyText: { fontSize: 14, color: C.inkLight, textAlign: 'center' },
  errorText: { fontSize: 13, color: C.ink, textAlign: 'center' },
});
