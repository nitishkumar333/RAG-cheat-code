import React, { useState } from 'react';
import type { LangchainDocument } from '../types';
import { PdfUploader } from './PdfUploader';
import { ChunkList } from './ChunkList';
import { ProcessingView } from './ProcessingView';
import { generateEmbeddings } from '../services/api';
import { toast } from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid'; // Need to install uuid: npm install uuid && npm install -D @types/uuid

type AppState = 'uploading' | 'reviewing' | 'processing';

export const KnowledgeBaseManager: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('uploading');
  const [documents, setDocuments] = useState<LangchainDocument[]>([]);
  const [sourceFileName, setSourceFileName] = useState('');

  const handleUploadSuccess = (apiDocs: any, fileName: string) => {
    const docsWithIds = apiDocs.map((doc) => ({
      ...doc,
      id: uuidv4(), // Add a unique frontend ID for CRUD
    }));
    setDocuments(docsWithIds);
    setSourceFileName(fileName);
    setAppState('reviewing');
  };

  const handleUpdateDocument = (id: string, newContent: string) => {
    setDocuments((prevDocs) =>
      prevDocs.map((doc) =>
        doc.id === id ? { ...doc, page_content: newContent } : doc
      )
    );
    toast.success('Chunk updated!');
  };

  const handleDeleteDocument = (id: string) => {
    setDocuments((prevDocs) => prevDocs.filter((doc) => doc.id !== id));
    toast.error('Chunk deleted!');
  };

  const handleProcess = async () => {
    setAppState('processing');
    toast.loading('Starting embedding generation...');
    try {
      // Note: We use a simulated progress view, but the API call is real.
      // In a real app, you'd use polling or websockets to get progress.
      await generateEmbeddings(documents);
      toast.dismiss();
      // The ProcessingView will handle the "success" message
    } catch (error) {
      console.error(error);
      toast.dismiss();
      toast.error('Failed to generate embeddings.');
      setAppState('reviewing'); // Go back to review on error
    }
  };

  const handleReset = () => {
    setDocuments([]);
    setSourceFileName('');
    setAppState('uploading');
  };

  const renderState = () => {
    switch (appState) {
      case 'uploading':
        return <PdfUploader onUploadSuccess={handleUploadSuccess} />;
      case 'reviewing':
        return (
          <ChunkList
            documents={documents}
            fileName={sourceFileName}
            onUpdateDocument={handleUpdateDocument}
            onDeleteDocument={handleDeleteDocument}
            onProcess={handleProcess}
            onReset={handleReset}
          />
        );
      case 'processing':
        return <ProcessingView onProcessingComplete={handleReset} />;
      default:
        return null;
    }
  };

  return (
    <div className="flex w-full flex-grow items-center justify-center p-4">
      {renderState()}
    </div>
  );
};