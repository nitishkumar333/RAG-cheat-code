// Based on Langchain's Document structure
export interface DocumentMetadata {
    source: string;
    page: number;
    [key: string]: any; // Allow other metadata properties
  }
  
  export interface LangchainDocument {
    id: string; // We will add this on the frontend for list management
    page_content: string;
    metadata: DocumentMetadata;
  }
  
  // API response from /pdf-chunks will be this, without the frontend-id
  export type ApiDocument = Omit<LangchainDocument, 'id'>;