import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useUser } from '../context/UserContext';
import { fetchBestDays, fetchCategories } from '../services/api';

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4' };

const ICONS: Record<string, string> = {
  Travel: '✈️', Contracts: '📝', Medical: '🏥', Relationships: '💕',
  Moving: '🏠', 'New Project': '🚀', Interview: '💼', Surgery: '⚕️',
  Investment: '💰', Wedding: '💍', Meeting: '🤝', 'Creative Work': '🎨',
  Learning: '📚', 'Spiritual Practice': '🧘', Other: '✦',
};

interface BestDay { date: string; rank: number; score: number; quality: string; reason: string; tags: string[] }

export default function FindBestDayScreen() {
  const { profile } = useUser();
  const [categories, setCategories] = useState<string[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [results, setResults] = useState<BestDay[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCategories().then(r => setCategories(r.categories)).catch(console.error);
  }, []);

  const search = (cat: string) => {
    setSelected(cat);
    setResults([]);
    if (!profile) return;
    setLoading(true);
    fetchBestDays(profile, cat, 90)
      .then((r: any) => setResults(r.results))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <ScrollView style={s.scroll} contentContainerStyle={s.container}>
      <Text style={s.title}>Find Your Best Day</Text>
      <Text style={s.subtitle}>Choose an activity to find the top 3 upcoming dates</Text>

      <View style={s.grid}>
        {categories.map(cat => (
          <TouchableOpacity key={cat} style={[s.chip, selected === cat && s.chipSelected]} onPress={() => search(cat)}>
            <Text style={s.chipEmoji}>{ICONS[cat] ?? '✦'}</Text>
            <Text style={[s.chipLabel, selected === cat && s.chipLabelSelected]}>{cat}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading && <ActivityIndicator color={C.gold} style={{ marginTop: 32 }} />}

      {results.length > 0 && (
        <>
          <Text style={s.resultsTitle}>Best dates for {selected}</Text>
          {results.map(d => (
            <View key={d.date} style={s.result}>
              <View style={s.resultHeader}>
                <View style={s.rankBadge}><Text style={s.rankText}>#{d.rank}</Text></View>
                <Text style={s.resultDate}>{new Date(d.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
                <Text style={s.resultScore}>{d.score}/10</Text>
              </View>
              <Text style={s.resultQuality}>{d.quality}</Text>
              <Text style={s.resultReason}>{d.reason}</Text>
              {d.tags.length > 0 && (
                <View style={s.tagRow}>
                  {d.tags.map(t => <View key={t} style={s.tag}><Text style={s.tagText}>{t}</Text></View>)}
                </View>
              )}
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 24, paddingTop: 56, paddingBottom: 40 },
  title: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 6 },
  subtitle: { fontSize: 13, color: C.inkLight, marginBottom: 24 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 24 },
  chip: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 10,
    backgroundColor: C.card, borderRadius: 20, gap: 6 },
  chipSelected: { backgroundColor: C.gold },
  chipEmoji: { fontSize: 16 },
  chipLabel: { fontSize: 13, color: C.ink },
  chipLabelSelected: { color: '#fff' },
  resultsTitle: { fontSize: 11, letterSpacing: 2, textTransform: 'uppercase', color: C.inkLight, marginBottom: 16 },
  result: { backgroundColor: C.card, borderRadius: 12, padding: 16, marginBottom: 12 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 6, gap: 10 },
  rankBadge: { width: 28, height: 28, borderRadius: 14, backgroundColor: C.gold, alignItems: 'center', justifyContent: 'center' },
  rankText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  resultDate: { flex: 1, fontSize: 15, color: C.ink, fontWeight: '400' },
  resultScore: { fontSize: 18, color: C.gold },
  resultQuality: { fontSize: 12, color: C.inkLight, marginBottom: 8 },
  resultReason: { fontSize: 13, color: C.ink, lineHeight: 19, marginBottom: 8 },
  tagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tag: { backgroundColor: C.goldLight, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  tagText: { fontSize: 11, color: C.ink },
});
