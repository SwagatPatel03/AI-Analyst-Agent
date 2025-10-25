/**
 * Type definitions for the application
 */

// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Report types
export interface Report {
  id: number;
  company_name: string;
  report_year: number | null;
  filename: string;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

export interface FinancialData {
  company_name: string;
  report_year: number;
  revenue: {
    current_year: number | null;
    previous_year: number | null;
    currency: string;
  };
  net_income: {
    current_year: number | null;
    previous_year: number | null;
  };
  total_assets: number | null;
  total_liabilities: number | null;
  shareholders_equity: number | null;
  cash_flow: {
    operating: number | null;
    investing: number | null;
    financing: number | null;
  };
  key_metrics: {
    eps: number | null;
    pe_ratio: number | null;
    roe: number | null;
    debt_to_equity: number | null;
  };
  segment_revenue: Array<{ segment: string; revenue: number }>;
  geographic_revenue: Array<{ region: string; revenue: number }>;
}

// Prediction types
export interface Predictions {
  success?: boolean;
  error?: string;
  report_id?: number;
  timestamp?: string;
  growth_rate?: {
    predicted: number;
    confidence_lower: number;
    confidence_upper: number;
    confidence_level: number;
  };
  sales_forecast?: Array<{
    year: number;
    predicted_revenue: number;
    growth_rate: number;
    currency: string;
  }>;
  segment_breakdown?: Array<{
    segment: string;
    current_revenue: number;
    proportion: number;
    predicted_growth: number;
  }>;
  recommendations?: Array<string | {
    category?: string;
    icon?: string;
    title?: string;
    description?: string;
    action?: string;
  }>;
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AgenticAnalysisResult {
  success: boolean;
  query: string;
  // Textual analysis from the agent (optional)
  analysis?: string;
  // Raw code the agent may have executed
  code_executed?: string;
  // Structured result block when code execution returns output/errors
  result?: { output?: string; errors?: string } | Record<string, unknown> | null;
  explanation?: string;
  error?: string;
}

// Visualization types
export interface Visualization {
  path: string;
  type: string;
}

// Lead Analysis types
export interface LeadAnalysis {
  investment_score: number;
  key_strengths: string[];
  risk_factors: string[];
  action_items: string[];
  recommendation: string;
}
