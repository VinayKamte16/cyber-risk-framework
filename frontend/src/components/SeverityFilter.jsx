import React from 'react';

const SeverityFilter = ({ selectedSeverity, onSeverityChange }) => {
  const severities = [
    { value: 'all', label: 'All', color: 'gray' },
    { value: 'high', label: 'High', color: 'danger' },
    { value: 'medium', label: 'Medium', color: 'warning' },
    { value: 'low', label: 'Low', color: 'success' }
  ];

  return (
    <div className="flex space-x-2">
      {severities.map((severity) => (
        <button
          key={severity.value}
          onClick={() => onSeverityChange(severity.value)}
          className={`px-3 py-1 rounded-full text-sm font-medium
            ${selectedSeverity === severity.value
              ? `bg-${severity.color}-500 text-white`
              : `bg-${severity.color}-100 text-${severity.color}-800 hover:bg-${severity.color}-200`
            }`}
        >
          {severity.label}
        </button>
      ))}
    </div>
  );
};

export default SeverityFilter; 