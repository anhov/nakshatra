import * as Calendar from 'expo-calendar';
import { BirthProfile } from '../context/UserContext';

const BASE = 'http://localhost:8000/api/v1';

export interface DeviceEvent {
  id: string;
  title: string;
  startDate: string;
  endDate: string;
}

export interface LabelledEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  label: 'Good' | 'Okay' | 'Reschedule';
  emoji: string;
  reason: string;
}

/** Request calendar permission and return whether it was granted. */
export async function requestCalendarPermission(): Promise<boolean> {
  const { status } = await Calendar.requestCalendarPermissionsAsync();
  return status === 'granted';
}

/** Read events for the next N days from the device calendar. */
export async function readUpcomingEvents(daysAhead = 14): Promise<DeviceEvent[]> {
  const { status } = await Calendar.getCalendarPermissionsAsync();
  if (status !== 'granted') return [];

  const calendars = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
  const calendarIds = calendars.map((c: any) => c.id);

  const start = new Date();
  const end   = new Date();
  end.setDate(end.getDate() + daysAhead);

  const events = await Calendar.getEventsAsync(calendarIds, start, end);
  return events as unknown as DeviceEvent[];
}

/** Send events to backend and get Good/Okay/Reschedule labels. */
export async function labelEvents(
  events: DeviceEvent[],
  profile: BirthProfile,
): Promise<LabelledEvent[]> {
  if (events.length === 0) return [];

  const payload = {
    events: events.map((e: DeviceEvent) => ({
      id: e.id,
      title: e.title ?? 'Untitled',
      start: e.startDate,
      end:   e.endDate,
    })),
    birth_date:  profile.birthDate,
    birth_time:  profile.birthTime,
    timezone:    profile.timezone,
    latitude:    profile.latitude,
    longitude:   profile.longitude,
  };

  const res = await fetch(`${BASE}/calendar/label`, {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Subscription-Tier': 'premium',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error('Calendar sync failed');
  const data = await res.json();
  return data.labelled_events;
}
