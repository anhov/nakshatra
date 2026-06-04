import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.warn('Push notifications require a physical device.');
    return null;
  }

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Nakshatra',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
  }

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  const token = await Notifications.getExpoPushTokenAsync();
  return token.data;
}

export interface MorningPrefs {
  enabled: boolean;
  hour: number;
  minute: number;
}

/** Schedule (or cancel) the daily morning reading local notification. */
export async function scheduleMorningNotification(prefs: MorningPrefs): Promise<void> {
  // Cancel any existing daily schedule
  await Notifications.cancelAllScheduledNotificationsAsync();

  if (!prefs.enabled) return;

  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'Your daily reading is ready',
      body: 'Tap to see your score, favourable activities, and timing windows.',
      data: { screen: 'Today' },
      sound: 'default',
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes.DAILY,
      hour: prefs.hour,
      minute: prefs.minute,
    },
  });
}

/** Schedule an Ekadashi reminder for tomorrow at 8pm. */
export async function scheduleEkadashiReminder(ekadashiName: string, eveDate: Date): Promise<void> {
  const trigger = new Date(eveDate);
  trigger.setHours(20, 0, 0, 0);  // 8pm the eve before

  if (trigger <= new Date()) return;  // already past

  await Notifications.scheduleNotificationAsync({
    content: {
      title: `Tomorrow is ${ekadashiName}`,
      body: 'A sacred fasting day. Tap to prepare and see guidance.',
      data: { screen: 'Today' },
    },
    trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: trigger },
  });
}
