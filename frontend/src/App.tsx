import { Toaster } from 'react-hot-toast';
import { Header } from './components/Header';
import { KnowledgeBaseManager } from './components/KnowledgeBaseManager';

function App() {
  return (
    <div className="flex h-screen w-full flex-col bg-background">
      <Header />
      <main className="flex flex-grow flex-col items-center p-4 sm:p-8">
        <KnowledgeBaseManager />
      </main>
      <Toaster 
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#333',
            color: '#fff',
          },
        }}
      />
    </div>
  );
}

export default App;