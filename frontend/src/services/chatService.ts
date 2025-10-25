import api from './api';

export interface ChatResponse {
  answer: string;
  chat_history?: Array<{ role: string; content: string }>;
  context?: any;
  report_id?: number;
}

const chatService = {
  async chat(reportId: number, message: string): Promise<ChatResponse> {
    const response = await api.post(`/chatbot/chat/${reportId}`, { message });
    return response.data;
  },

  async agenticQuery(reportId: number, query: string): Promise<any> {
    const response = await api.post(`/chatbot/agentic/${reportId}`, { query });
    return response.data;
  },
};

export { chatService };
export default chatService;
