import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Download, Trash2, FileText, File, Image, FileSpreadsheet, MoreVertical } from 'lucide-react';
import { notesService } from '../services/notes';
import { formatBytes, formatDate } from '../utils/helpers';
import StatCard from '../components/StatCard';

const getFileIcon = (type) => {
  if (!type) return File;
  const t = type.toLowerCase();
  if (t === 'pdf') return FileText;
  if (t.includes('doc')) return FileText;
  if (t.includes('ppt') || t.includes('xls')) return FileSpreadsheet;
  if (t === 'image') return Image;
  return File;
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  const fetchData = async () => {
    try {
      const [statsData, notesData] = await Promise.all([
        notesService.getStats(),
        notesService.getNotes(searchQuery)
      ]);
      setStats(statsData);
      setNotes(notesData.notes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchData();
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const handleDownload = async (id) => {
    try {
      const url = await notesService.getDownloadUrl(id);
      window.open(url, '_blank');
    } catch (err) {
      console.error('Download failed', err);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await notesService.deleteNote(id);
        fetchData();
      } catch (err) {
        console.error('Delete failed', err);
      }
    }
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-4 border-[var(--color-accent)] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">Dashboard</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">Overview of your academic materials.</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Total Notes" value={stats?.total_notes || 0} />
        <StatCard title="Subjects" value={stats?.subjects_count || 0} />
        <StatCard title="Storage Used" value="Optimized" />
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            placeholder="Search notes or subjects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full pl-10 pr-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
          />
        </div>
      </div>

      {/* Notes List */}
      <div>
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-6">Recent Files</h2>
        {notes.length === 0 ? (
          <div className="text-center py-20 bg-[var(--color-surface)] rounded-2xl border border-[var(--color-border)] border-dashed">
            <FileText className="w-12 h-12 text-[var(--color-border)] mx-auto mb-4" />
            <h3 className="text-lg font-medium text-[var(--color-text-primary)]">No notes found</h3>
            <p className="text-[var(--color-text-secondary)] mt-1">Upload some notes to get started.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {notes.map((note, i) => {
              const Icon = getFileIcon(note.file_type);
              return (
                <motion.div
                  key={note.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                  className="bg-[var(--color-surface)] rounded-2xl border border-[var(--color-border)] p-5 hover:border-[var(--color-accent)]/50 transition-colors group flex flex-col"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-center">
                      <Icon className="w-5 h-5 text-[var(--color-text-secondary)]" />
                    </div>
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {note.file_key && (
                        <button onClick={() => handleDownload(note.id)} className="p-1.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-background)] hover:text-[var(--color-text-primary)]">
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                      <button onClick={() => handleDelete(note.id)} className="p-1.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-red-500/10 hover:text-red-400">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-medium text-[var(--color-text-primary)] line-clamp-1" title={note.title}>{note.title}</h3>
                    <p className="text-xs text-[var(--color-text-tertiary)] mt-1">{note.subject}</p>
                    {note.description && (
                      <p className="text-sm text-[var(--color-text-secondary)] mt-3 line-clamp-2">{note.description}</p>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-[var(--color-border)] text-xs text-[var(--color-text-tertiary)]">
                    <span>{formatDate(note.created_at)}</span>
                    <span className="uppercase">{note.file_type || 'Unknown'} {note.file_size ? `• ${formatBytes(note.file_size)}` : ''}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
