import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface LeadAnalysis {
  investment_score: number;
  recommendation: string;
  strengths: string[];
  risks: string[];
  action_items: string[];
}

interface GenerateLeadsResponse {
  lead_analysis: LeadAnalysis;
  message: string;
}

interface SendEmailResponse {
  message: string;
  recipient: string;
}

const emailService = {
  async generateLeads(reportId: number): Promise<GenerateLeadsResponse> {
    const token = localStorage.getItem('access_token');  // Fixed: was 'token', should be 'access_token'
    const response = await axios.post(
      `${API_URL}/report/leads/${reportId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  },

  async sendEmail(reportId: number, recipient: string): Promise<SendEmailResponse> {
    const token = localStorage.getItem('access_token');  // Fixed: was 'token', should be 'access_token'
    const response = await axios.post(
      `${API_URL}/report/email/${reportId}`,
      { 
        to_emails: [recipient],
        include_lead_analysis: false
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  },
};

export { emailService };
export type { GenerateLeadsResponse, LeadAnalysis, SendEmailResponse };

