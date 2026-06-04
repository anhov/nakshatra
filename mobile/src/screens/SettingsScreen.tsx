import { useEffect, useState } from 'react';
import {
  ActivityIndicator, Alert, ScrollView, StyleSheet,
  Switch, Text, TouchableOpacity, View,
} from 'react-native';
import { useUser } from '../context/UserContext';
import {
  registerForPushNotifications,
  scheduleMorningNotification,
} from '../services/notifications';
import {
  labelEvents,
  readUpcomingEvents,
  requestCalendarPermission,
} from '../services/calendarSync';
import type { LabelledEvent } from '../services/calendarSync';

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A', goldLight: '#E8D5A3', card: '#FDFAF4' };

// In a real app this comes from IAP / server; hardcoded to "free" for demo
const SUBSCRIPTION_TIER: 'free' | 'premium' | 'pro' = 'free';

const LABEL_COLOR = { Good: '#2D6A4F', Okay: '#F4A261', Reschedule: '#E76F51' };

export default function SettingsScreen() {
  const { profile } = useUser();
  const [morningEnabled, setMorningEnabled] = useState(true);
  const [morningHour, setMorningHour] = useState(7);
  const [calendarEvents, setCalendarEvents] = useState<LabelledEvent[]>([]);
  const [calendarLoading, setCalendarLoading] = useState(false);
  const [pushToken, setPushToken] = useState<string | null>(null);
  const isPremium = SUBSCRIPTION_TIER !== 'free';

  useEffect(() => {
    if (isPremium) {
      registerForPushNotifications().then(t => {
        setPushToken(t);
        scheduleMorningNotification({ enabled: morningEnabled, hour: morningHour, minute: 0 });
      });
    }
  }, []);

  const syncCalendar = async () => {
    if (!profile) return;
    setCalendarLoading(true);
    try {
      const granted = await requestCalendarPermission();
      if (!granted) { Alert.alert('Calendar access denied'); setCalendarLoading(false); return; }
      const events = await readUpcomingEvents(14);
      const labelled = await labelEvents(events, profile);
      setCalendarEvents(labelled);
    } catch (e: any) {
      Alert.alert('Sync failed', e.message);
    } finally {
      setCalendarLoading(false);
    }
  };

  const toggleMorning = (val: boolean) => {
    setMorningEnabled(val);
    if (isPremium) scheduleMorningNotification({ enabled: val, hour: morningHour, minute: 0 });
  };

  return (
    <ScrollView style={s.scroll} contentContainerStyle={s.container}>
      <Text style={s.title}>Settings</Text>

      {/* Subscription */}
      <View style={s.section}>
        <Text style={s.sectionTitle}>Subscription</Text>
        <View style={s.planCard}>
          <Text style={s.planName}>{SUBSCRIPTION_TIER === 'free' ? 'Free Plan' : SUBSCRIPTION_TIER === 'premium' ? 'Premium' : 'Jyotishi Pro'}</Text>
          {SUBSCRIPTION_TIER === 'free' && (
            <>
              <Text style={s.planDesc}>You are on the free plan. Upgrade to unlock:</Text>
              {['All 4 daily activity cards', 'Full timing windows (Choghadiya + Hora)', 'Calendar sync & event labelling', 'Affirmations & mantras', 'Find Best Day — all 15 categories', 'Morning daily push notification', 'Ekadashi eve reminders'].map(f => (
                <Text key={f} style={s.planFeature}>· {f}</Text>
              ))}
              <TouchableOpacity style={s.upgradeBtn}>
                <Text style={s.upgradeBtnText}>Upgrade to Premium — $7.99/mo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={s.proBtn}>
                <Text style={s.proBtnText}>Jyotishi Pro — $19.99/mo</Text>
              </TouchableOpacity>
            </>
          )}
          {SUBSCRIPTION_TIER !== 'free' && (
            <Text style={s.planDesc}>All features are unlocked. Thank you for your support!</Text>
          )}
        </View>
      </View>

      {/* Notifications */}
      <View style={s.section}>
        <Text style={s.sectionTitle}>Notifications</Text>
        {!isPremium ? (
          <View style={s.gatedBanner}>
            <Text style={s.gatedText}>Notifications require Premium. Upgrade to receive your morning daily reading and Ekadashi reminders.</Text>
          </View>
        ) : (
          <View style={s.card}>
            <View style={s.row}>
              <View style={{ flex: 1 }}>
                <Text style={s.rowLabel}>Morning daily reading</Text>
                <Text style={s.rowSub}>Every day at {morningHour}:00 {morningHour < 12 ? 'AM' : 'PM'}</Text>
              </View>
              <Switch
                value={morningEnabled}
                onValueChange={toggleMorning}
                trackColor={{ false: C.goldLight, true: C.gold }}
                thumbColor="#fff"
              />
            </View>
            {pushToken && <Text style={s.tokenText}>Push registered ✓</Text>}
          </View>
        )}
      </View>

      {/* Calendar sync */}
      <View style={s.section}>
        <Text style={s.sectionTitle}>Calendar Sync</Text>
        {!isPremium ? (
          <View style={s.gatedBanner}>
            <Text style={s.gatedText}>Calendar sync requires Premium. Upgrade to see Good / Okay / Reschedule labels on your events.</Text>
          </View>
        ) : (
          <>
            <Text style={s.calDesc}>Read your next 14 days of events and label them based on your personal astrology. Events are processed instantly and never stored.</Text>
            <TouchableOpacity style={s.syncBtn} onPress={syncCalendar} disabled={calendarLoading}>
              {calendarLoading
                ? <ActivityIndicator color="#fff" />
                : <Text style={s.syncBtnText}>Sync Calendar</Text>}
            </TouchableOpacity>
            {calendarEvents.length > 0 && (
              <>
                <Text style={s.eventsTitle}>{calendarEvents.length} events labelled</Text>
                {calendarEvents.map(ev => (
                  <View key={ev.id} style={s.eventRow}>
                    <Text style={[s.eventEmoji, { color: LABEL_COLOR[ev.label] }]}>{ev.emoji}</Text>
                    <View style={{ flex: 1 }}>
                      <Text style={s.eventTitle}>{ev.title}</Text>
                      <Text style={s.eventReason}>{ev.reason}</Text>
                    </View>
                    <Text style={[s.eventLabel, { color: LABEL_COLOR[ev.label] }]}>{ev.label}</Text>
                  </View>
                ))}
              </>
            )}
          </>
        )}
      </View>

      {/* Birth details */}
      {profile && (
        <View style={s.section}>
          <Text style={s.sectionTitle}>Your Birth Details</Text>
          <View style={s.card}>
            {[['Date', profile.birthDate], ['Time', profile.birthTime + (profile.isApproximateTime ? ' (approx)' : '')],
              ['Place', profile.placeName], ['Timezone', profile.timezone],
              ['Coordinates', `${profile.latitude}, ${profile.longitude}`]].map(([k, v]) => (
              <View key={k} style={s.row}>
                <Text style={s.rowLabel}>{k}</Text>
                <Text style={s.rowVal}>{v}</Text>
              </View>
            ))}
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const s = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.cream },
  container: { padding: 24, paddingTop: 56, paddingBottom: 48 },
  title: { fontSize: 26, fontWeight: '300', color: C.ink, marginBottom: 24 },
  section: { marginBottom: 28 },
  sectionTitle: { fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', color: C.inkLight, marginBottom: 12 },
  planCard: { backgroundColor: C.card, borderRadius: 12, padding: 16 },
  planName: { fontSize: 18, color: C.ink, fontWeight: '400', marginBottom: 8 },
  planDesc: { fontSize: 13, color: C.inkLight, marginBottom: 8 },
  planFeature: { fontSize: 12, color: C.ink, marginBottom: 4 },
  upgradeBtn: { backgroundColor: C.gold, borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginTop: 14 },
  upgradeBtnText: { color: '#fff', fontSize: 14, fontWeight: '600' },
  proBtn: { borderWidth: 1.5, borderColor: C.gold, borderRadius: 10, paddingVertical: 12, alignItems: 'center', marginTop: 8 },
  proBtnText: { color: C.gold, fontSize: 13 },
  card: { backgroundColor: C.card, borderRadius: 12, padding: 16 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.goldLight },
  rowLabel: { fontSize: 13, color: C.ink, flex: 1 },
  rowSub: { fontSize: 11, color: C.inkLight },
  rowVal: { fontSize: 13, color: C.inkLight, textAlign: 'right', flex: 1 },
  tokenText: { fontSize: 10, color: '#52B788', marginTop: 8 },
  gatedBanner: { backgroundColor: '#FDF5E6', borderRadius: 10, padding: 14, borderLeftWidth: 3, borderLeftColor: C.gold },
  gatedText: { fontSize: 13, color: C.inkLight, lineHeight: 19 },
  calDesc: { fontSize: 13, color: C.inkLight, marginBottom: 12, lineHeight: 19 },
  syncBtn: { backgroundColor: C.ink, borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginBottom: 16 },
  syncBtnText: { color: '#fff', fontSize: 14 },
  eventsTitle: { fontSize: 11, letterSpacing: 1.5, textTransform: 'uppercase', color: C.inkLight, marginBottom: 10 },
  eventRow: { flexDirection: 'row', alignItems: 'flex-start', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.goldLight, gap: 10 },
  eventEmoji: { fontSize: 18, width: 24 },
  eventTitle: { fontSize: 13, color: C.ink, marginBottom: 2 },
  eventReason: { fontSize: 11, color: C.inkLight },
  eventLabel: { fontSize: 12, fontWeight: '500' },
});
