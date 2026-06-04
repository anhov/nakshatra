import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { ActivityIndicator, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { UserProvider, useUser } from './src/context/UserContext';
import TodayScreen       from './src/screens/TodayScreen';
import CalendarScreen    from './src/screens/CalendarScreen';
import FindBestDayScreen from './src/screens/FindBestDayScreen';
import MyChartScreen     from './src/screens/MyChartScreen';
import OnboardingScreen  from './src/screens/OnboardingScreen';
import SettingsScreen    from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const C = { cream: '#F6F0E6', ink: '#221A10', inkLight: '#6B5D4F', gold: '#C4963A' };

function AppNavigator() {
  const { profile, isLoading } = useUser();

  if (isLoading) {
    return <View style={{ flex: 1, backgroundColor: C.cream, alignItems: 'center', justifyContent: 'center' }}>
      <ActivityIndicator color={C.gold} size="large" />
    </View>;
  }

  if (!profile) {
    return (
      <NavigationContainer>
        <StatusBar style="dark" />
        <OnboardingScreen />
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarStyle: { backgroundColor: C.cream, borderTopColor: '#E8D5A3', height: 80, paddingBottom: 16 },
          tabBarActiveTintColor: C.gold,
          tabBarInactiveTintColor: C.inkLight,
          tabBarLabelStyle: { fontSize: 10, letterSpacing: 0.5 },
          tabBarIcon: ({ color, size }) => {
            const icons: Record<string, string> = {
              Today: 'sunny-outline', Calendar: 'calendar-outline',
              'Best Day': 'search-outline', 'My Chart': 'star-outline',
              Settings: 'settings-outline',
            };
            return <Ionicons name={(icons[route.name] ?? 'ellipse-outline') as any} size={size} color={color} />;
          },
        })}
      >
        <Tab.Screen name="Today"    component={TodayScreen} />
        <Tab.Screen name="Calendar" component={CalendarScreen} />
        <Tab.Screen name="Best Day" component={FindBestDayScreen} />
        <Tab.Screen name="My Chart" component={MyChartScreen} />
        <Tab.Screen name="Settings" component={SettingsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <UserProvider>
      <AppNavigator />
    </UserProvider>
  );
}
