import api from './api';

export interface AgentResponse {
  query: string;
  generated_code?: string;
  execution_result?: any;
  explanation?: string;
  success: boolean;
  retry_count?: number;
}

const agentService = {
  async analyzeWithAgent(reportId: number, query: string): Promise<AgentResponse> {
    const response = await api.post(`/chatbot/agent/analyze/${reportId}`, { query });
    return response.data;
  },

  async executeCode(reportId: number, code: string): Promise<AgentResponse> {
    const response = await api.post(`/chatbot/agent/execute-code/${reportId}`, { code });
    return response.data;
  }
};

export { agentService };
export default agentService;
