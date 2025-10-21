import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileUp } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { uploadPdf } from '../services/api';
// import { ApiDocument } from '../types';
import { Button } from './ui/Button';
import { Progress } from './ui/Progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';

interface PdfUploaderProps {
  onUploadSuccess: (documents: any, fileName: string) => void;
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error';

export const PdfUploader: React.FC<PdfUploaderProps> = ({ onUploadSuccess }) => {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState<string | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setFileName(file.name);
      setUploadState('uploading');
      setProgress(0);
      toast.loading('Uploading PDF...');

      try {
        const documents = await uploadPdf(file, setProgress);
        console.log(documents);
        setUploadState('success');
        toast.dismiss();
        toast.success('PDF processed successfully!');
        if(documents.status){
          onUploadSuccess(documents.chunks, file.name);
        }
      } catch (error) {
        setUploadState('error');
        setProgress(0);
        toast.dismiss();
        toast.error('Failed to process PDF. Please try again.');
        console.error(error);
      }
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
  });

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>Create Knowledge Base</CardTitle>
        <CardDescription>Upload a single PDF to create text chunks.</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed
          border-border p-8 text-center transition-colors
          ${isDragActive ? 'border-primary bg-accent' : 'hover:border-primary/70'}`}
        >
          <input {...getInputProps()} />
          <FileUp className="h-12 w-12 text-muted-foreground" />
          {isDragActive ? (
            <p className="mt-4 text-lg">Drop the PDF here...</p>
          ) : (
            <p className="mt-4 text-muted-foreground">
              Drag & drop a PDF here, or click to select
            </p>
          )}
        </div>
        
        {uploadState === 'uploading' && (
          <div className="mt-6 w-full space-y-2">
            <p className="text-sm text-muted-foreground">Uploading {fileName}...</p>
            <Progress value={progress} />
          </div>
        )}

        {uploadState === 'error' && (
           <Button variant="outline" className="mt-4" onClick={() => setUploadState('idle')}>
             Try Again
           </Button>
        )}
      </CardContent>
    </Card>
  );
};