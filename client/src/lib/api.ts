import type {
  BookingConfirmation,
  ConsultationSlot,
  ContentItem,
  ContentType,
  PrescriptionExtraction,
  ProductRecommendation,
  SymptomCheckResult,
} from '@babycare/types';

const API_URL = import.meta.env.VITE_API_URL ?? '';

interface PrescriptionWire {
  id: number;
  baby_id: number;
  medicine_names: string[];
  dosage_text: string[];
  frequency_text: string[];
  raw_ocr_text: string;
  status: PrescriptionExtraction['status'];
  ai_disclaimer: string;
}
interface ProductWire {
  id: number;
  name: string;
  category: string;
  age_min_months: number;
  age_max_months: number;
  price: string | number;
  tags: string[];
  score: number;
  matched_tags: string[];
  explanation?: string;
}
interface ProductResponseWire {
  rule_based: ProductWire[];
  ai_explained: ProductWire[] | null;
}
interface ContentWire {
  id: number;
  type: ContentType;
  title: string;
  url: string;
  age_min_months: number;
  age_max_months: number;
  config?: Record<string, unknown> | null;
}
interface SlotWire {
  id: number;
  pediatrician_name: string;
  slot_time: string;
  status: ConsultationSlot['status'];
}
interface ConfirmationWire {
  confirmation_id: string;
  slot_id: number;
  pediatrician_name: string;
  slot_time: string;
  status: 'booked';
  message: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string;
    } | null;
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function checkSymptoms(
  babyId: number,
  ageMonths: number,
  symptoms: string,
): Promise<SymptomCheckResult> {
  const data = await request<{
    possible_causes: string[];
    home_care: string[];
    red_flags: string[];
    alert_level: SymptomCheckResult['alertLevel'];
    disclaimer: string;
  }>('/api/assistant/symptom-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ baby_id: babyId, age_months: ageMonths, symptoms }),
  });
  return {
    possibleCauses: data.possible_causes,
    homeCare: data.home_care,
    redFlags: data.red_flags,
    alertLevel: data.alert_level,
    disclaimer: data.disclaimer,
  };
}

export async function extractPrescription(
  babyId: number,
  file: File,
): Promise<PrescriptionExtraction> {
  const form = new FormData();
  form.append('baby_id', String(babyId));
  form.append('file', file);
  const d = await request<PrescriptionWire>('/api/prescriptions/extract', {
    method: 'POST',
    body: form,
  });
  return {
    id: d.id,
    babyId: d.baby_id,
    medicineNames: d.medicine_names,
    dosageText: d.dosage_text,
    frequencyText: d.frequency_text,
    rawOcrText: d.raw_ocr_text,
    status: d.status,
    aiDisclaimer: d.ai_disclaimer,
  };
}

export async function reviewPrescription(
  id: number,
  reviewerId: number,
  status: 'reviewed' | 'flagged',
  note: string,
): Promise<void> {
  await request(`/api/prescriptions/${id}/review`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': String(reviewerId),
    },
    body: JSON.stringify({ status, note }),
  });
}

export async function getProducts(
  babyId: number,
): Promise<ProductRecommendation[]> {
  const d = await request<ProductResponseWire>(
    `/api/products/recommend?baby_id=${babyId}`,
  );
  const products = d.ai_explained ?? d.rule_based;
  return products.map((p) => ({
    id: p.id,
    name: p.name,
    category: p.category,
    ageMinMonths: p.age_min_months,
    ageMaxMonths: p.age_max_months,
    price: String(p.price),
    tags: p.tags,
    score: p.score,
    matchedTags: p.matched_tags,
    explanation: p.explanation,
  }));
}

export async function getContent(
  age: number,
  type?: ContentType,
): Promise<ContentItem[]> {
  const query = new URLSearchParams({ age_months: String(age) });
  if (type) query.set('type', type);
  const data = await request<ContentWire[]>(`/api/content?${query}`);
  return data.map((d) => ({
    id: d.id,
    type: d.type,
    title: d.title,
    url: d.url,
    ageMinMonths: d.age_min_months,
    ageMaxMonths: d.age_max_months,
    config: d.config,
  }));
}

export async function getSlots(): Promise<ConsultationSlot[]> {
  const data = await request<SlotWire[]>('/api/consultations/slots');
  return data.map((d) => ({
    id: d.id,
    pediatricianName: d.pediatrician_name,
    slotTime: d.slot_time,
    status: d.status,
  }));
}

export async function bookSlot(slotId: number): Promise<BookingConfirmation> {
  const d = await request<ConfirmationWire>('/api/consultations/book', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ slot_id: slotId }),
  });
  return {
    confirmationId: d.confirmation_id,
    slotId: d.slot_id,
    pediatricianName: d.pediatrician_name,
    slotTime: d.slot_time,
    status: d.status,
    message: d.message,
  };
}
