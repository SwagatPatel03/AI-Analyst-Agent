import type { AgenticAnalysisResult, ChatMessage, LeadAnalysis, Predictions, Report } from '../types';
import api from './api';

export const reportService = {
  // ==================== UPLOAD ENDPOINTS ====================
  
  uploadReport: async (file: File, companyName: string, reportYear?: number): Promise<unknown> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', companyName);
    if (reportYear) {
      formData.append('report_year', reportYear.toString());
    }

    const response = await api.post('/upload/report', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getReports: async (): Promise<{ reports: Report[] }> => {
    const response = await api.get('/upload/reports');
    return response.data;
  },

  // ==================== VISUALIZATION ENDPOINTS ====================
  
  generateVisualizations: async (reportId: number): Promise<unknown> => {
    const response = await api.post(`/analysis/visualize/report/${reportId}`);
    return response.data;
  },

  getVisualizations: async (reportId: number): Promise<{ visualizations: string[] }> => {
    const response = await api.get(`/analysis/visualizations/${reportId}`);
    return response.data;
  },

  getVisualizationFile: async (filePath: string): Promise<string> => {
    const response = await api.get(`/analysis/visualization/file`, {
      params: { file_path: filePath },
    });
    return response.data;
  },

  downloadExcel: async (reportId: number): Promise<Blob> => {
    const response = await api.get(`/analysis/excel/${reportId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // ==================== PREDICTION ENDPOINTS ====================
  
  generatePredictions: async (reportId: number): Promise<{ predictions: Predictions }> => {
    const response = await api.post(`/report/predict/${reportId}`);
    return response.data;
  },

  getPredictions: async (reportId: number): Promise<{ predictions: Predictions }> => {
    const response = await api.get(`/report/predictions/${reportId}`);
    return response.data;
  },

  // ==================== REPORT GENERATION ENDPOINTS ====================
  
  generateReport: async (reportId: number): Promise<unknown> => {
    const response = await api.post(`/report/generate/${reportId}`);
    return response.data;
  },

  getReportSummary: async (reportId: number): Promise<{ report_summary: string }> => {
    const response = await api.get(`/report/summary/${reportId}`);
    return response.data;
  },

  downloadReportPDF: async (reportId: number): Promise<Blob> => {
    // Add timestamp to prevent browser caching of old PDF
    const timestamp = new Date().getTime();
    const response = await api.get(`/report/pdf/${reportId}?t=${timestamp}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // ==================== EMAIL ENDPOINTS ====================
  
  sendEmail: async (
    reportId: number, 
    emails: string[], 
    includeLeadAnalysis: boolean
  ): Promise<{ status?: string } | { success?: boolean }> => {
    const response = await api.post(`/report/email/${reportId}`, {
      to_emails: emails,
      include_lead_analysis: includeLeadAnalysis,
    });
    return response.data;
  },

  generateLeads: async (reportId: number): Promise<{ lead_analysis: LeadAnalysis }> => {
    const response = await api.post(`/report/leads/${reportId}`);
    return response.data;
  },

  // ==================== INVESTMENT LEADS ENDPOINTS (NEW) ====================
  
  generateInvestmentLeads: async (reportId: number): Promise<{
    company: string;
    summary: string;
    rating: string;
    opportunities: Array<{
      title: string;
      evidence: string;
      potential: string;
      timeframe: string;
    }>;
    risks: Array<{
      title: string;
      severity: string;
      evidence: string;
      mitigation?: string;
    }>;
    catalysts: Array<{
      title: string;
      impact: string;
      evidence: string;
    }>;
    key_metrics: Record<string, unknown>;
  }> => {
    const response = await api.post('/leads/generate', { report_id: reportId });
    return response.data;
  },

  emailInvestmentLeads: async (
    reportId: number,
    recipients: string[],
    previewOnly: boolean = false
  ): Promise<{
    status: string;
    recipients?: string[];
    leads_data: Record<string, unknown>;
    html_preview: string;
  }> => {
    const response = await api.post('/leads/email', {
      report_id: reportId,
      recipients,
      preview_only: previewOnly,
    });
    return response.data;
  },

  previewLeadEmail: async (reportId: number): Promise<{
    html: string;
    leads_data: Record<string, unknown>;
  }> => {
    const response = await api.get(`/leads/preview/${reportId}`);
    return response.data;
  },

  // ==================== CHATBOT ENDPOINTS ====================
  
  sendChatMessage: async (reportId: number, message: string): Promise<{ answer: string }> => {
    const response = await api.post(`/chatbot/chat/${reportId}`, { message });
    return response.data;
  },

  getChatHistory: async (reportId: number): Promise<{ chat_history: ChatMessage[] }> => {
    const response = await api.get(`/chatbot/chat/history/${reportId}`);
    return response.data;
  },

  clearChatHistory: async (reportId: number): Promise<void> => {
    await api.delete(`/chatbot/chat/history/${reportId}`);
  },

  // ==================== AGENTIC ANALYST ENDPOINTS ====================
  
  agenticAnalysis: async (reportId: number, query: string): Promise<AgenticAnalysisResult> => {
    const response = await api.post(`/chatbot/agent/analyze/${reportId}`, { query });
    return response.data;
  },

  executeCustomCode: async (reportId: number, code: string): Promise<unknown> => {
    const response = await api.post(`/chatbot/agent/execute-code/${reportId}`, { code });
    return response.data;
  },

  // ==================== DEPARTMENT LEADS ENDPOINTS ====================
  
  extractDepartmentLeads: async (reportId: number, sendEmail: boolean = true): Promise<{
    success: boolean;
    leads: {
      departments: Array<{
        name: string;
        growth: string;
        status: string;
        work_items: string[];
        concerns: string;
      }>;
      summary: string;
    };
    email_sent: boolean;
    message: string;
  }> => {
    const response = await api.post('/api/department-leads/extract-and-email', {
      report_id: reportId,
      send_email: sendEmail
    });
    return response.data;
  },

  previewDepartmentLeads: async (reportId: number): Promise<unknown> => {
    const response = await api.post(`/api/department-leads/preview-leads/${reportId}`);
    return response.data;
  },

  getDepartmentLeadsEmail: async (): Promise<{ email: string; description: string }> => {
    const response = await api.get('/api/department-leads/default-email');
    return response.data;
  },
};
