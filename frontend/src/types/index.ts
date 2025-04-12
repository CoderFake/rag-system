// User types
export interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;
  refreshToken: string | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  password: string;
  name?: string;
  email?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  type: 'query' | 'response';
  content: string;
  created_at: string;
  query_id?: string;
  user_id?: number;
  sources?: DocumentSource[];
}

export interface ChatHistory {
  history: ChatMessage[];
}

export interface ChatQuery {
  query: string;
  session_id: string;
  language: string;
}

export interface ChatResponse {
  response: string;
  source_documents: DocumentSource[];
  route_type: string;
  query_id: string;
  response_id: string;
}

export interface FeedbackData {
  response_id: string;
  type: 'thumbs_up' | 'thumbs_down' | 'comment';
  value: string;
}

// Document types
export interface Document {
  id: string;
  title: string;
  file_path?: string;
  file_type: string;
  category: string;
  tags: string[];
  user_id?: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentSource {
  id: string;
  title: string;
  category: string;
  relevance_score?: number;
}

export interface DocumentUpload {
  file: File;
  title: string;
  category: string;
  tags: string;
  description: string;
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
  page: number;
  limit: number;
}

// Settings types
export interface Settings {
  chunk_size: number;
  chunk_overlap: number;
  embedding_model: string;
  supported_languages: string[];
}

// Theme types
export type ThemeMode = 'light' | 'dark';

// Language types
export type Language = 'en' | 'vi';
