import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useContext, useEffect, useState } from 'react';

export interface BirthProfile {
  name: string;
  birthDate: string;   // "YYYY-MM-DD"
  birthTime: string;   // "HH:MM"
  timezone: string;    // IANA
  latitude: number;
  longitude: number;
  placeName: string;
  isApproximateTime: boolean;
}

interface UserContextType {
  profile: BirthProfile | null;
  setProfile: (p: BirthProfile) => Promise<void>;
  isLoading: boolean;
}

const STORAGE_KEY = '@nakshatra_profile';

const UserContext = createContext<UserContextType>({
  profile: null,
  setProfile: async () => {},
  isLoading: true,
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfileState] = useState<BirthProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then(json => { if (json) setProfileState(JSON.parse(json)); })
      .finally(() => setIsLoading(false));
  }, []);

  const setProfile = async (p: BirthProfile) => {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(p));
    setProfileState(p);
  };

  return (
    <UserContext.Provider value={{ profile, setProfile, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export const useUser = () => useContext(UserContext);
