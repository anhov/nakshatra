export interface TithiInfo {
  number: number;
  name: string;
  paksha: string;
  elapsed_pct: number;
}

export interface VaraInfo {
  number: number;
  english: string;
  ruler: string;
  sanskrit: string;
}

export interface NakshatraInfo {
  number: number;
  name: string;
  pada: number;
  elapsed_pct: number;
}

export interface YogaInfo {
  number: number;
  name: string;
  elapsed_pct: number;
}

export interface KaranaInfo {
  number: number;
  name: string;
  is_fixed: boolean;
  elapsed_pct: number;
}

export interface PanchangaData {
  date: string;
  local_time: string;
  julian_day: number;
  sun_longitude: number;
  moon_longitude: number;
  tithi: TithiInfo;
  vara: VaraInfo;
  nakshatra: NakshatraInfo;
  yoga: YogaInfo;
  karana: KaranaInfo;
}
