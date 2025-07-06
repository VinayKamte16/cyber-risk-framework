import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ShieldExclamationIcon,
  GlobeAltIcon,
  DocumentCheckIcon,
  CogIcon,
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Risk Assessment', href: '/risk-assessment', icon: ShieldExclamationIcon },
    { name: 'Threat Intelligence', href: '/threat-intelligence', icon: GlobeAltIcon },
    { name: 'Compliance', href: '/compliance', icon: DocumentCheckIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  return (
    <aside
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        width: '256px',
        background: '#fff',
        borderRight: '1px solid #e5e7eb',
        zIndex: 40,
        color: '#222',
        fontWeight: 'bold',
        padding: '16px',
        boxShadow: '2px 0 8px rgba(0,0,0,0.03)',
      }}
    >
      <div style={{ height: 64 }} />
      <nav>
        {navigation.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '8px 0',
              color: location.pathname === item.href ? 'blue' : 'black',
              textDecoration: 'none',
              fontWeight: location.pathname === item.href ? 'bold' : 'normal',
            }}
          >
            <item.icon style={{marginRight: '8px', width: '24px', height: '24px'}} />
            {item.name}
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar; 