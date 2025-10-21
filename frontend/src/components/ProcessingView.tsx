import React, { useEffect, useState } from 'react';
import { Progress } from './ui/Progress';
import { CheckCircle, Loader2 } from 'lucide-react';

interface ProcessingViewProps {
  onProcessingComplete: () => void;
}

export const ProcessingView: React.FC<ProcessingViewProps> = ({
  onProcessingComplete,
}) => {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Generating embeddings...');

  useEffect(() => {
    // Simulate processing time
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) {
          return prev;
        }
        return prev + 5;
      });
    }, 200);

    // Simulate API call completion
    const timeout = setTimeout(() => {
      clearInterval(interval);
      setProgress(100);
      setMessage('Embeddings generated successfully!');
      
      // Notify parent component after a short delay
      setTimeout(() => {
        onProcessingComplete();
      }, 1500);

    }, 5000); // 5-second simulated processing

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [onProcessingComplete]);

  return (
    <div className="w-full max-w-lg space-y-4">
      <div className="flex items-center justify-center gap-2">
        {progress < 100 ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <CheckCircle className="h-5 w-5 text-green-500" />
        )}
        <p className="text-lg font-medium">{message}</p>
      </div>
      <Progress value={progress} />
    </div>
  );
};