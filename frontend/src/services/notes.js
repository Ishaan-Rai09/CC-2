import api from './api';

export const notesService = {
  getNotes: async (search = '', subject = '') => {
    let url = '/notes/';
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (subject) params.append('subject', subject);
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    const response = await api.get(url);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/notes/stats');
    return response.data;
  },

  createNote: async (formData) => {
    const response = await api.post('/notes/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Increase timeout for large file uploads
      timeout: 30000, 
    });
    return response.data;
  },

  deleteNote: async (id) => {
    const response = await api.delete(`/notes/${id}`);
    return response.data;
  },

  getDownloadUrl: async (id) => {
    const response = await api.get(`/notes/${id}/download`);
    return response.data.download_url;
  }
};

export const analyticsService = {
  getAnalytics: async () => {
    const response = await api.get('/analytics/', {
      validateStatus: (status) => status === 200 || status === 202,
    });
    return {
      statusCode: response.status,
      ...response.data,
    };
  }
};
