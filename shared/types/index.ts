export interface BabyProfile {
  id: number;
  name: string;
  birthDate: string;
  sex: string;
}

export interface CareEntry {
  id: string;
  babyId: string;
  category: 'feeding' | 'sleep' | 'diaper' | 'note';
  occurredAt: string;
  notes?: string;
}

export type ContentType = 'rhyme' | 'video' | 'sound' | 'activity';

export interface ContentItem {
  id: number;
  type: ContentType;
  title: string;
  url: string;
  ageMinMonths: number;
  ageMaxMonths: number;
  config?: Record<string, unknown> | null;
}

export type AlertLevel = 'low' | 'medium' | 'high';

export interface SymptomCheckResult {
  possibleCauses: string[];
  homeCare: string[];
  redFlags: string[];
  alertLevel: AlertLevel;
  disclaimer: string;
}

export type PrescriptionStatus = 'pending_review' | 'reviewed' | 'flagged';

export interface PrescriptionExtraction {
  id: number;
  babyId: number;
  medicineNames: string[];
  dosageText: string[];
  frequencyText: string[];
  rawOcrText: string;
  status: PrescriptionStatus;
  aiDisclaimer: string;
}

export interface ProductRecommendation {
  id: number;
  name: string;
  category: string;
  ageMinMonths: number;
  ageMaxMonths: number;
  price: string;
  tags: string[];
  score: number;
  matchedTags: string[];
  explanation?: string;
}

export interface ConsultationSlot {
  id: number;
  pediatricianName: string;
  slotTime: string;
  status: 'available' | 'booked';
}

export interface BookingConfirmation {
  confirmationId: string;
  slotId: number;
  pediatricianName: string;
  slotTime: string;
  status: 'booked';
  message: string;
}
