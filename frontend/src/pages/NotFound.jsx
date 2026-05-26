import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col items-center justify-center p-6 text-center">
      <div className="text-[120px] font-bold text-[var(--color-border)] leading-none mb-4">404</div>
      <h1 className="text-2xl md:text-3xl font-bold text-[var(--color-text-primary)] mb-4">Page not found</h1>
      <p className="text-[var(--color-text-secondary)] mb-8 max-w-md">
        Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.
      </p>
      <Link 
        to="/"
        className="flex items-center gap-2 bg-[var(--color-surface-raised)] border border-[var(--color-border)] text-[var(--color-text-primary)] px-6 py-3 rounded-xl font-medium hover:bg-[var(--color-border)] transition-colors"
      >
        <Home className="w-5 h-5" />
        Back to Home
      </Link>
    </div>
  );
};

export default NotFound;
