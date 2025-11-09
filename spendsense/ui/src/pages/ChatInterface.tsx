/**
 * Chat Interface Page
 * Full-screen chat with SpendSense AI coach
 * NOTE: Backend chat API (POST /api/chat/message) needs to be implemented
 */

import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import DashboardLayout from '../components/dashboard/DashboardLayout';

interface Message {
  id: string;
  type: 'user' | 'ai';
  text: string;
  timestamp: Date;
  quickReplies?: string[];
}

const ChatInterface: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const context = searchParams.get('context');

  const [messages, setMessages] = useState<Message[]>(() => {
    // Welcome message with quick start options
    const welcomeMessage: Message = {
      id: '1',
      type: 'ai',
      text: context
        ? `Hi! I see you're interested in learning more about ${context.replace(/-/g, ' ')}. How can I help you with that?`
        : "Hi! I'm your SpendSense coach. I'm here to help you understand your financial patterns and make better money decisions. What would you like to explore today?",
      timestamp: new Date(),
      quickReplies: context
        ? ['Tell me more', 'Show recommendations', 'What should I do?']
        : ['Explain my persona', 'Why is my utilization high?', 'How can I save more?', 'What are these signals?'],
    };
    return [welcomeMessage];
  });

  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: inputText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // TODO: Replace with actual API call
    // const response = await fetch('/api/chat/message', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     user_id: localStorage.getItem('spendsense_user_id'),
    //     message: inputText,
    //     context: context || 'general',
    //   }),
    // });
    // const data = await response.json();

    // Mock AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        text: "I understand you're interested in that topic. While I'm still learning to provide personalized advice, I can connect you with relevant resources from your dashboard. Would you like me to show you related recommendations?",
        timestamp: new Date(),
        quickReplies: ['Yes, show recommendations', 'Tell me more', 'Go back to dashboard'],
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleQuickReply = (reply: string) => {
    setInputText(reply);
    handleSend();
  };

  return (
    <DashboardLayout showBottomNav={false} showFloatingChat={false}>
      <div className="fixed inset-0 bg-white flex flex-col md:relative md:rounded-lg md:shadow-md md:border md:border-gray-100">
        {/* Chat Header */}
        <div className="bg-cyan-600 text-white px-4 py-4 md:rounded-t-lg flex items-center gap-3 shadow-md">
          <button
            onClick={() => navigate('/dashboard')}
            className="md:hidden text-white hover:bg-cyan-700 rounded p-1 focus:outline-none focus:ring-2 focus:ring-white"
          >
            ←
          </button>
          <div className="flex-1">
            <h1 className="text-lg font-semibold">SpendSense Coach</h1>
            <p className="text-cyan-100 text-sm">● Online</p>
          </div>
          <button
            className="text-white hover:bg-cyan-700 rounded p-2 focus:outline-none focus:ring-2 focus:ring-white"
            aria-label="Chat settings"
          >
            ⚙️
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message) => (
            <div key={message.id}>
              {/* Message Bubble */}
              <div
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] md:max-w-[70%] rounded-lg px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-cyan-600 text-white'
                      : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                </div>
              </div>

              {/* Quick Replies */}
              {message.type === 'ai' && message.quickReplies && (
                <div className="flex flex-wrap gap-2 mt-2 ml-0">
                  {message.quickReplies.map((reply, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickReply(reply)}
                      className="px-3 py-2 bg-white border border-cyan-300 text-cyan-700 rounded-full text-sm font-medium hover:bg-cyan-50 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    >
                      {reply}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 rounded-lg px-4 py-3 shadow-sm border border-gray-200">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4 md:rounded-b-lg">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type a message..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isTyping}
              className="px-6 py-3 bg-cyan-600 text-white rounded-lg font-medium hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              →
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            💡 Tip: Ask specific questions about your signals, persona, or financial goals
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ChatInterface;
