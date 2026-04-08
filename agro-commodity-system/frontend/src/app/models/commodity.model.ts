export type CommodityType =
  | 'GRAOS'
  | 'FIBRAS'
  | 'ACUCAR_ALCOOL'
  | 'CARNES'
  | 'CAFE'
  | 'FRUTAS'
  | 'OLEOS'
  | 'OUTROS';

export const COMMODITY_TYPE_LABELS: Record<CommodityType, string> = {
  GRAOS: 'Grãos',
  FIBRAS: 'Fibras',
  ACUCAR_ALCOOL: 'Açúcar e Álcool',
  CARNES: 'Carnes',
  CAFE: 'Café',
  FRUTAS: 'Frutas e Vegetais',
  OLEOS: 'Óleos Vegetais',
  OUTROS: 'Outros'
};

export interface Commodity {
  id?: number;
  name: string;
  code: string;
  type: CommodityType;
  currentPrice: number;
  previousPrice?: number;
  unit: string;
  currency: string;
  description?: string;
  originRegion?: string;
  lastUpdated?: string;
  createdAt?: string;
  priceVariation?: number;
  priceVariationFormatted?: string;
}

export interface PriceHistory {
  id: number;
  commodityId: number;
  commodityName: string;
  price: number;
  recordedAt: string;
  source: string;
  notes?: string;
}

export interface AIAnalysisRequest {
  question: string;
  commodityId?: number;
  analysisType?: 'CHAT' | 'MARKET_ANALYSIS' | 'PRICE_PREDICTION' | 'RECOMMENDATION';
}

export interface WorkflowStep {
  stepName: string;
  description: string;
  status: 'COMPLETED' | 'SKIPPED' | 'ERROR';
  output: string;
}

export interface AIAnalysisResponse {
  answer: string;
  analysisType: string;
  insights: string[];
  recommendations: string[];
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidenceScore: number;
  generatedAt: string;
  modelUsed: string;
  workflowSteps: WorkflowStep[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  analysis?: AIAnalysisResponse;
}
