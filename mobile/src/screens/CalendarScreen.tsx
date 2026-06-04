import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useUser } from '../context/UserContext';
import { fetchMonth, fetchToday } from '../services/api';

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4' };
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

interface DaySummary { date: string; score: number; quality: string; color: string }
interface DayDetail { score: number; quality: string; tagline: string; moon_nakshatra: string; avoid_text: string }

export default function CalendarScreen() {
  const { profile } = useUser();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [days, setDays] = useState<DaySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<DayDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    if (!profile) return;
    setLoading(true);
    fetchMonth(profile, year, month)
      .then((r: any) => setDays(r.days))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [profile, year, month]);

  const selectDay = (dateStr: string) => {
    setSelected(dateStr);
    setDetail(null);
    if (!profile) return;
    setDetailLoading(true);
    fetchToday(profile, new Date(dateStr))
      .then(d => setDetail(d as DayDetail))
      .catch(console.error)
      .finally(() => setDetailLoading(false));
  };

  const prevMonth = () => { if (month === 1) { setYear(y => y - 1); setMonth(12); } else setMonth(m => m - 1); };
  const nextMonth = () => { if (month === 12) { setYear(y => y + 1); setMonth(1); } else setMonth(m => m + 1); };

  const firstDay = new Date(year, month - 1, 1).getDay();
  const monthName = new Date(year, month - 1).toLocaleDateString('en-US', { month: 'long' });

  return (
    <ScrollView style={s.scroll} contentContainerStyle={s.container}>
      <View style={s.header}>
        <TouchableOpacity onPress={prevMonth}><Text style={s.arrow}>‹</Text></TouchableOpacity>
        <Text style={s.monthTitle}>{monthName} {year}</Text>
        <TouchableOpacity onPress={nextMonth}><Text style={s.arrow}>›</Text></TouchableOpacity>
      </View>

      <View style={s.dayRow}>
        {DAYS.map(d => <Text key={d} style={s.dayLabel}>{d}</Text>)}
      </View>

      {loading ? <ActivityIndicator color={C.gold} style={{ marginTop: 40 }} /> : (
        <View style={s.grid}>
          {Array(firstDay).fill(null).map((_, i) => <View key={`e${i}`} style={s.cell} />)}
          {days.map(d => {
            const dayNum = parseInt(d.date.split('-')[2]);
            const isSelected = d.date === selected;
            const isToday = d.date === now.toISOString().split('T')[0];
            return (
              <TouchableOpacity key={d.date} style={[s.cell, isSelected && s.cellSelected]} onPress={() => selectDay(d.date)}>
                <View style={[s.dot, { backgroundColor: d.color }, isToday && s.todayRing]}>
                  <Text style={[s.dayNum, isToday && s.todayNum]}>{dayNum}</Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}

      {/* Legend */}
      <View style={s.legend}>
        {[['#2D6A4F','Excellent'],['#52B788','Very Good'],['#74C69D','Good'],['#F4A261','Mixed'],['#E76F51','Challenging']].map(([c,l]) => (
          <View key={l} style={s.legendItem}>
            <View style={[s.legendDot, { backgroundColor: c as string }]} />
            <Text style={s.legendLabel}>{l}</Text>
          </View>
        ))}
      </View>

      {/* Day detail */}
      {selected && (
        <View style={s.detail}>
          <Text style={s.detailDate}>{new Date(selected).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
          {detailLoading ? <ActivityIndicator color={C.gold} /> : detail ? (
            <>
              <Text style={s.detailScore}>{detail.score}/10 · {detail.quality}</Text>
              <Text style={s.detailTagline}>{detail.tagline}</Text>
              <Text style={s.detailMoon}>Moon in {detail.moon_nakshatra}</Text>
              <Text style={s.detailAvoid}>{detail.avoid_text}</Text>
            </>
          ) : null}
        </View>
      )}
    </ScrollView>
  );
}

const CELL = 44;
const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 20, paddingTop: 56, paddingBottom: 40 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 },
  arrow: { fontSize: 28, color: C.gold, paddingHorizontal: 12 },
  monthTitle: { fontSize: 20, color: C.ink, fontWeight: '300', letterSpacing: 1 },
  dayRow: { flexDirection: 'row', marginBottom: 8 },
  dayLabel: { width: CELL, textAlign: 'center', fontSize: 11, color: C.inkLight, letterSpacing: 1 },
  grid: { flexDirection: 'row', flexWrap: 'wrap' },
  cell: { width: CELL, height: CELL, alignItems: 'center', justifyContent: 'center' },
  cellSelected: { backgroundColor: C.goldLight, borderRadius: 8 },
  dot: { width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  todayRing: { borderWidth: 2, borderColor: C.ink },
  dayNum: { fontSize: 13, color: '#fff', fontWeight: '500' },
  todayNum: { fontWeight: '700' },
  legend: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 16 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendLabel: { fontSize: 10, color: C.inkLight },
  detail: { backgroundColor: C.card, borderRadius: 12, padding: 16, marginTop: 20 },
  detailDate: { fontSize: 14, color: C.inkLight, marginBottom: 8 },
  detailScore: { fontSize: 22, color: C.ink, fontWeight: '300', marginBottom: 6 },
  detailTagline: { fontSize: 13, color: C.inkLight, lineHeight: 20, marginBottom: 8 },
  detailMoon: { fontSize: 12, color: C.gold, marginBottom: 6 },
  detailAvoid: { fontSize: 12, color: '#C4673A', fontStyle: 'italic' },
});
