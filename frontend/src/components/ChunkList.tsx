import React from 'react';
import type { LangchainDocument } from '../types';
import { ChunkItem } from './ChunkItem';
import { Button } from './ui/Button';
import { FileText, Rocket, RotateCcw } from 'lucide-react';

interface ChunkListProps {
  documents: LangchainDocument[];
  fileName: string;
  onUpdateDocument: (id: string, newContent: string) => void;
  onDeleteDocument: (id: string) => void;
  onProcess: () => void;
  onReset: () => void;
}

export const ChunkList: React.FC<ChunkListProps> = ({
  documents,
  fileName,
  onUpdateDocument,
  onDeleteDocument,
  onProcess,
  onReset
}) => {
  return (
    <div className="w-full max-w-4xl space-y-6">
      <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Review Documents</h2>
          <p className="flex items-center text-muted-foreground">
            <FileText className="mr-2 h-4 w-4" />
            {fileName} ({documents.length} chunks)
          </p>
        </div>
        <div className="flex w-full gap-2 sm:w-auto">
          <Button variant="outline" onClick={onReset} className="w-1/2 sm:w-auto">
            <RotateCcw className="mr-2 h-4 w-4" />
            Start Over
          </Button>
          <Button onClick={onProcess} className="w-1/2 sm:w-auto">
            <Rocket className="mr-2 h-4 w-4" />
            Start Processing
          </Button>
        </div>
      </div>
      
      <div className="space-y-4">
        {documents.map((doc) => (
          <ChunkItem
            key={doc.id}
            doc={doc}
            onDelete={onDeleteDocument}
            onUpdate={onUpdateDocument}
          />
        ))}
      </div>
    </div>
  );
};