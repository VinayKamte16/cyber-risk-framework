import React, { createContext, useContext, useState } from 'react';

function getRandomScore() {
  return Math.floor(Math.random() * 100);
}
function getRandomLevel(score) {
  if (score < 30) return 'Low';
  if (score < 70) return 'Medium';
  return 'High';
}
function getRandomSeverity() {
  return ['High', 'Medium', 'Low'][Math.floor(Math.random() * 3)];
}
function getRandomStatus() {
  return ['compliant', 'non-compliant', 'partial'][Math.floor(Math.random() * 3)];
}

const frameworksList = ['NIST', 'ISO 27001', 'GDPR', 'PCI DSS'];

function generateMockData() {
  // Dashboard
  const now = new Date();
  const riskScores = Array.from({ length: 14 }, (_, i) => ({
    timestamp: new Date(now.getTime() - i * 86400000).toISOString(),
    score: getRandomScore(),
  })).reverse();
  const threats = Array.from({ length: Math.floor(Math.random() * 5) + 3 }, (_, i) => ({
    title: `Threat #${i + 1}`,
    description: `Description for threat #${i + 1}`,
    severity: getRandomSeverity(),
    timestamp: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
  }));
  const assets = Array.from({ length: 6 }, (_, i) => ({
    name: `Asset-${i + 1}`,
    type: ['server', 'cloud', 'workstation'][Math.floor(Math.random() * 3)],
    ip_address: `192.168.1.${i + 10}`,
    health: getRandomScore(),
    last_updated: new Date(now.getTime() - Math.random() * 86400000).toISOString(),
  }));
  const compliance = {
    overallScore: getRandomScore(),
    frameworks: frameworksList.map((name) => ({
      name,
      score: getRandomScore(),
      requirements: [
        { title: 'Access Control', status: getRandomStatus() },
        { title: 'Incident Response', status: getRandomStatus() },
        { title: 'Risk Assessment', status: getRandomStatus() },
      ],
    })),
  };
  // Risk Assessment
  const riskCategories = ['Network', 'System', 'Application'].map((name) => {
    const score = getRandomScore();
    return {
      name,
      score,
      level: getRandomLevel(score),
    };
  });
  // Threat Intelligence
  const threatDescriptions = [
    'Suspicious login attempt detected from an unknown IP address.',
    'Malware signature identified in email attachment.',
    'Unusual outbound network traffic detected.',
    'Multiple failed login attempts detected.',
    'Potential data exfiltration activity observed.',
    'Phishing email reported by user.',
    'Unauthorized access to sensitive file detected.',
    'Ransomware activity detected on endpoint.',
    'Zero-day vulnerability exploit attempt blocked.',
    'Abnormal increase in privileged account activity.'
  ];
  const threatIntel = Array.from({ length: Math.floor(Math.random() * 5) + 5 }, (_, i) => ({
    title: `Threat Event #${i + 1}`,
    description: threatDescriptions[Math.floor(Math.random() * threatDescriptions.length)],
    severity: getRandomSeverity(),
    timestamp: new Date(Date.now() - Math.random() * 86400000).toLocaleString(),
  }));
  return {
    dashboard: {
      currentRiskScore: getRandomScore(),
      threats,
      riskScores,
      assets,
      compliance,
    },
    riskAssessment: riskCategories,
    threatIntelligence: threatIntel,
    compliance: compliance,
  };
}

const MockDataContext = createContext();

export function MockDataProvider({ children }) {
  const [mockData, setMockData] = useState(null);
  const generate = () => setMockData(generateMockData());
  const reset = () => setMockData(null);
  return (
    <MockDataContext.Provider value={{ mockData, generate, reset }}>
      {children}
    </MockDataContext.Provider>
  );
}

export function useMockData() {
  return useContext(MockDataContext);
} 