import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, X, File, Loader2, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { notesService } from '../services/notes';
import { formatBytes } from '../utils/helpers';
import { cn } from '../utils/helpers';

const Upload = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      if (!title) {
        setTitle(e.dataTransfer.files[0].name.split('.')[0]);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      if (!title) {
        setTitle(e.target.files[0].name.split('.')[0]);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !subject || !file) {
      setError('Please fill in all required fields and select a file.');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('title', title);
    formData.append('subject', subject);
    if (description) formData.append('description', description);
    formData.append('file', file);

    try {
      await notesService.createNote(formData);
      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">Upload Material</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">Add new notes, assignments, or study guides.</p>
      </header>

      {success ? (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-green-500/10 border border-green-500/20 rounded-2xl p-12 text-center"
        >
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <h2 className="text-2xl font-bold text-green-400 mb-2">Upload Successful!</h2>
          <p className="text-[var(--color-text-secondary)]">Redirecting to dashboard...</p>
        </motion.div>
      ) : (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                Title <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Chapter 4 Summary"
                className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                Subject <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. CS101, Data Structures"
                className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                Description <span className="text-[var(--color-text-tertiary)]">(Optional)</span>
              </label>
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of the material..."
                className="w-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all resize-none"
              />
            </div>
          </div>

          <div className="space-y-6">
            <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
              File <span className="text-red-400">*</span>
            </label>
            
            {!file ? (
              <div 
                className={cn(
                  "border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center transition-all h-[300px]",
                  dragActive ? "border-[var(--color-accent)] bg-[var(--color-accent)]/5" : "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-text-secondary)]"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <UploadCloud className="w-12 h-12 text-[var(--color-text-tertiary)] mb-4" />
                <p className="text-[var(--color-text-primary)] font-medium mb-1">Drag & drop your file here</p>
                <p className="text-[var(--color-text-secondary)] text-sm mb-6">PDF, DOCX, PPT, JPG up to 50MB</p>
                
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <label 
                  htmlFor="file-upload"
                  className="cursor-pointer bg-[var(--color-background)] border border-[var(--color-border)] text-[var(--color-text-primary)] px-6 py-2.5 rounded-full font-medium hover:bg-[var(--color-surface-raised)] transition-all"
                >
                  Browse Files
                </label>
              </div>
            ) : (
              <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 h-[300px] flex flex-col items-center justify-center relative">
                <button 
                  type="button"
                  onClick={() => setFile(null)}
                  className="absolute top-4 right-4 p-2 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] bg-[var(--color-background)] rounded-full"
                >
                  <X className="w-4 h-4" />
                </button>
                <File className="w-16 h-16 text-[var(--color-accent)] mb-4" />
                <p className="font-medium text-[var(--color-text-primary)] text-center break-all px-4">{file.name}</p>
                <p className="text-[var(--color-text-secondary)] text-sm mt-2">{formatBytes(file.size)}</p>
              </div>
            )}

            {error && (
              <p className="text-red-400 text-sm mt-2">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              className="w-full bg-[var(--color-accent)] text-white rounded-xl px-4 py-3.5 font-medium hover:bg-[var(--color-accent-hover)] transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/25"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Upload Material'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default Upload;
