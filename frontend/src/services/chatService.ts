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
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;

    if (user && user.id) {
      let userSessionId = localStorage.getItem(`chatSessionId_${user.id}`);
      if (!userSessionId) {
        userSessionId = this.generateSessionId();
        localStorage.setItem(`chatSessionId_${user.id}`, userSessionId);
      }
      return userSessionId;
    } else {
      let anonSessionId = localStorage.getItem('anonChatSessionId');
      if (!anonSessionId) {
        anonSessionId = this.generateSessionId();
        localStorage.setItem('anonChatSessionId', anonSessionId);
      }
      return anonSessionId;
    }
  }

  setSessionId(sessionId: string): void {
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    if (user && user.id) {
      localStorage.setItem(`chatSessionId_${user.id}`, sessionId);
    } else {
      localStorage.setItem('anonChatSessionId', sessionId);
    }
  }

  clearSessionId(): void {
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (user && user.id) {
      localStorage.removeItem(`chatSessionId_${user.id}`);
    } else {
      localStorage.removeItem('anonChatSessionId');
    }
  }
}

export const chatService = new ChatService();
export default chatService;
