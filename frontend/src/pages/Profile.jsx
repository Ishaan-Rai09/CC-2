import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Calendar, Loader2 } from 'lucide-react';
import { formatDate } from '../utils/helpers';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [formData, setFormData] = useState({
    fullName: user?.full_name || '',
    email: user?.email || '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await updateProfile({
        full_name: formData.fullName,
        email: formData.email
      });
      setSuccess('Profile updated successfully.');
      setIsEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-3xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">Profile Settings</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">Manage your account details and preferences.</p>
      </header>

      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
        <div className="p-8 border-b border-[var(--color-border)] bg-[var(--color-surface-raised)]/30 flex items-center gap-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-[var(--color-accent)] to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white text-3xl font-bold">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-[var(--color-text-primary)]">{user?.full_name}</h2>
            <p className="text-[var(--color-text-secondary)]">{user?.email}</p>
          </div>
        </div>

        <div className="p-8">
          {error && (
             <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-lg mb-6">
               {error}
             </div>
          )}
          {success && (
             <div className="bg-green-500/10 border border-green-500/20 text-green-400 text-sm px-4 py-3 rounded-lg mb-6">
               {success}
             </div>
          )}

          {!isEditing ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm text-[var(--color-text-tertiary)] flex items-center gap-2 mb-1">
                    <User className="w-4 h-4" /> Full Name
                  </label>
                  <p className="text-[var(--color-text-primary)] font-medium">{user?.full_name}</p>
                </div>
                <div>
                  <label className="text-sm text-[var(--color-text-tertiary)] flex items-center gap-2 mb-1">
                    <Mail className="w-4 h-4" /> Email Address
                  </label>
                  <p className="text-[var(--color-text-primary)] font-medium">{user?.email}</p>
                </div>
                <div>
                  <label className="text-sm text-[var(--color-text-tertiary)] flex items-center gap-2 mb-1">
                    <Calendar className="w-4 h-4" /> Joined
                  </label>
                  <p className="text-[var(--color-text-primary)] font-medium">{formatDate(user?.created_at)}</p>
                </div>
              </div>
              <div className="pt-6">
                <button 
                  onClick={() => setIsEditing(true)}
                  className="bg-[var(--color-surface-raised)] text-[var(--color-text-primary)] border border-[var(--color-border)] px-4 py-2 rounded-lg font-medium hover:bg-[var(--color-border)] transition-colors"
                >
                  Edit Profile
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">Full Name</label>
                  <input
                    type="text"
                    required
                    value={formData.fullName}
                    onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                    className="w-full bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">Email Address</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-[var(--color-text-primary)] focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-[var(--color-accent)] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[var(--color-accent-hover)] transition-all flex items-center disabled:opacity-50"
                >
                  {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="bg-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] px-4 py-2.5 rounded-lg font-medium transition-all"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
