import { DatabaseZap } from 'lucide-react';

export const Header = () => {
  return (
    <header className="border-b border-border p-4">
      <div className="container mx-auto flex items-center">
        <DatabaseZap className="h-6 w-6 text-primary" />
        <h1 className="ml-2 text-xl font-bold">RAG Pipeline Manager</h1>
      </div>
    </header>
  );
};