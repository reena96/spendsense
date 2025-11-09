/**
 * Floating Chat Button Component
 * Shows on tablet/desktop when chat sidebar is collapsed
 * Bottom-right corner with notification badge support
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

interface FloatingChatButtonProps {
  unreadCount?: number;
  onClick?: () => void;
}

const FloatingChatButton: React.FC<FloatingChatButtonProps> = ({ unreadCount = 0, onClick }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate('/dashboard/chat');
    }
  };

  return (
    <button
      onClick={handleClick}
      className="
        fixed bottom-4 right-4 z-30
        w-14 h-14 md:w-16 md:h-16
        bg-cyan-600 text-white
        rounded-full shadow-lg
        flex items-center justify-center
        hover:bg-cyan-700 active:scale-95
        transition-all duration-200
        focus:outline-none focus:ring-4 focus:ring-cyan-300
        md:hidden lg:flex
      "
      aria-label={`Open chat${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
    >
      <span className="text-3xl" aria-hidden="true">💬</span>

      {/* Notification Badge */}
      {unreadCount > 0 && (
        <span
          className="
            absolute -top-1 -right-1
            bg-red-500 text-white text-xs font-bold
            rounded-full w-6 h-6
            flex items-center justify-center
            border-2 border-white
            shadow-sm
          "
          aria-label={`${unreadCount} unread messages`}
        >
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  );
};

export default FloatingChatButton;
