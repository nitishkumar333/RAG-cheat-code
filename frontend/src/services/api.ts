import axios from 'axios';
import type { LangchainDocument } from '../types';

// IMPORTANT: Update this to your backend's URL
const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Uploads a PDF file to the /pdf-chunks endpoint.
 * @param file The PDF file to upload.
 * @param onUploadProgress A callback to track upload progress.
 * @returns A promise that resolves to an array of ApiDocument.
 */
export const uploadPdf = async (
  file: File,
  onUploadProgress: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('http://localhost:8000/pdf-chunks', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(progress);
      }
    },
  });
  return response.data;
};

/**
 * Sends the list of documents to the /generate-embeddings endpoint.
 * @param documents The list of documents to process.
 * @returns A promise that resolves when processing is complete.
 */
export const generateEmbeddings = async (documents: LangchainDocument[]): Promise<any> => {
  // We only send the original document structure, not our frontend-id
  const documentsToUpload = documents.map(({ id, ...doc }) => doc);
  
  const response = await apiClient.post('/generate-embeddings', documentsToUpload);
  return response.data;
};