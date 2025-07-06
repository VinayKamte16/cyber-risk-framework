import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const getDashboardData = async () => {
  // Helper functions for random data
  const randomScore = () => Math.floor(Math.random() * 100);
  const randomHealth = () => Math.floor(Math.random() * 100);
  const randomSeverity = () => ['high', 'medium', 'low'][Math.floor(Math.random() * 3)];
  const randomType = () => ['server', 'cloud', 'workstation'][Math.floor(Math.random() * 3)];
  const now = new Date();

  // Generate random risk scores for the trend
  const riskScores = Array.from({ length: 14 }, (_, i) => ({
    timestamp: new Date(now.getTime() - i * 86400000).toISOString(),
    score: randomScore(),
  })).reverse();

  // Generate random threats
  const threats = Array.from({ length: Math.floor(Math.random() * 5) + 3 }, (_, i) => ({
    title: `Threat #${i + 1}`,
    description: `Description for threat #${i + 1}`,
    severity: randomSeverity(),
    timestamp: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
  }));

  // Generate random assets
  const assets = Array.from({ length: 6 }, (_, i) => ({
    name: `Asset-${i + 1}`,
    type: randomType(),
    ip_address: `192.168.1.${i + 10}`,
    health: randomHealth(),
    last_updated: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
  }));

  // Generate random compliance data
  const compliance = {
    overallScore: randomScore(),
    frameworks: [
      {
        name: 'NIST',
        score: randomScore(),
        requirements: [
          { title: 'Access Control', status: 'compliant' },
          { title: 'Incident Response', status: 'non-compliant', actionItems: 'Update response plan' },
          { title: 'Risk Assessment', status: 'partial', actionItems: 'Review risk register' },
        ],
      },
      {
        name: 'ISO 27001',
        score: randomScore(),
        requirements: [
          { title: 'Asset Management', status: 'compliant' },
          { title: 'Cryptography', status: 'compliant' },
          { title: 'Supplier Relationships', status: 'partial', actionItems: 'Review supplier contracts' },
        ],
      },
    ],
  };

  return {
    currentRiskScore: randomScore(),
    threats,
    riskScores,
    assets,
    compliance,
  };
};

export const fetchRiskData = async () => {
  try {
    const response = await api.get('/assess-risk');
    return response.data;
  } catch (error) {
    console.error('Error fetching risk data:', error);
    throw error;
  }
};

export const trainModel = async (trainingData, labels) => {
  try {
    const response = await api.post('/train-model', {
      training_data: trainingData,
      labels: labels,
    });
    return response.data;
  } catch (error) {
    console.error('Error training model:', error);
    throw error;
  }
};

export const getThreatIntelligence = async () => {
  try {
    const response = await api.get('/threat-intelligence');
    return response.data;
  } catch (error) {
    console.error('Error fetching threat intelligence:', error);
    throw error;
  }
};

export const getComplianceStatus = async () => {
  try {
    const response = await api.get('/compliance');
    return response.data;
  } catch (error) {
    console.error('Error fetching compliance status:', error);
    throw error;
  }
};

export default api; 