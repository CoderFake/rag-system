import apiService from './api';
import { ChatHistory, ChatQuery, ChatResponse, FeedbackData } from '../types';

class ChatService {
  async sendMessage(query: string, sessionId: string, language: string): Promise<ChatResponse> {
    const data: ChatQuery = {
      query,
      session_id: sessionId,
      language,
    };
    
    const response = await apiService.post<ChatResponse>('/chat', data);
    return response.data;
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<ChatHistory> {
    const response = await apiService.get<ChatHistory>('/chat/history', {
      params: {
        session_id: sessionId,
        limit,
      },
    });
    return response.data;
  }

  async addFeedback(feedbackData: FeedbackData): Promise<{ message: string }> {
    const response = await apiService.post<{ message: string }>('/chat/feedback', feedbackData);
    return response.data;
  }

  generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  getSessionId(): string {
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = this.generateSessionId();
      localStorage.setItem('chatSessionId', sessionId);
    }
    return sessionId;
  }

  setSessionId(sessionId: string): void {
    localStorage.setItem('chatSessionId', sessionId);
  }

  clearSessionId(): void {
    localStorage.removeItem('chatSessionId');
  }
}

export const chatService = new ChatService();
export default chatService;
