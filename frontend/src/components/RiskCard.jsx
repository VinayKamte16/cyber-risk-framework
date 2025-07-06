import React from 'react';

const RiskCard = ({ title, count, color }) => {
  return (
    <div className={`bg-white p-6 rounded-lg shadow border-t-4 border-${color}-500`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{count}</p>
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <svg
            className={`w-6 h-6 text-${color}-500`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default RiskCard; 