import apiService from './api';
import { DocumentsResponse, DocumentUpload } from '../types';

class DocumentService {
  async getDocuments(page: number = 1, limit: number = 10, category?: string): Promise<DocumentsResponse> {
    const params: Record<string, any> = {
      page,
      limit,
    };

    if (category) {
      params.category = category;
    }

    const response = await apiService.get<DocumentsResponse>('/admin/documents', {
      params,
    });
    return response.data;
  }

  async uploadDocument(documentData: DocumentUpload): Promise<{ status: string; document_id: string; num_chunks: number; filename: string }> {
    const formData = new FormData();
    formData.append('file', documentData.file);
    formData.append('title', documentData.title);
    formData.append('category', documentData.category);
    formData.append('tags', documentData.tags);
    formData.append('description', documentData.description);

    const response = await apiService.upload<{ status: string; document_id: string; num_chunks: number; filename: string }>(
      '/admin/upload',
      formData
    );
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<{ success: boolean }> {
    const response = await apiService.delete<{ success: boolean }>(`/admin/documents/${documentId}`);
    return response.data;
  }

  async reindexDocuments(): Promise<{ success: boolean }> {
    const response = await apiService.post<{ success: boolean }>('/admin/reindex');
    return response.data;
  }
}

export const documentService = new DocumentService();
export default documentService;
