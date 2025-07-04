import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { FiBarChart2, FiFolder, FiLogIn } from 'react-icons/fi'
import { FaUserCircle } from 'react-icons/fa'
import UserProfileTab from './UserProfileTab'

export default function MobileBottomBar({ user, onLoginClick, setLogoutOpen, visibleTabs }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        width: '100%',
        height: '50px',
        backgroundColor: '#1f2937',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        zIndex: 1000,
        borderTop: '1px solid rgb(39, 46, 56)',
        fontFamily: '"Inter", system-ui, sans-serif',
      }}
    >
      {visibleTabs.map((tab, idx) => {
        const isActive = location.pathname === tab.route

        return (
          <button
            key={idx}
            onClick={() => navigate(tab.route)}
            style={{
              flex: 1,
              height: '100%',
              backgroundColor: 'transparent',
              border: 'none',
              outline: 'none',
              cursor: isActive ? 'default' : 'pointer',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '6px 10px',
                borderRadius: '8px',
                backgroundColor: isActive ? '#374151' : 'transparent',
                color: isActive ? '#ffffff' : '#9ca3af',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = '#d1d5db'
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = '#9ca3af'
              }}
            >
              {tab.icon}
            </div>
          </button>
        )
      })}
    </div>
  )
}
