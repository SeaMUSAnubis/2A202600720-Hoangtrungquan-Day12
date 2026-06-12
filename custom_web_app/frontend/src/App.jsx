import React, { useState, useRef, useEffect } from 'react';
import { Send, Scale, BookOpen, ShieldCheck, Calculator, User, Search, Loader2, Settings, Key } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const agentIcons = {
  customer: <User className="agent-icon" />,
  law: <Scale className="agent-icon" />,
  tax: <Calculator className="agent-icon" />,
  compliance: <ShieldCheck className="agent-icon" />,
  summarizer: <BookOpen className="agent-icon" />,
  system: <Loader2 className="agent-icon animate-spin" />
};

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      agentType: 'customer',
      text: 'Xin chào! Tôi là Trợ lý Pháp lý ảo. Bạn cần tư vấn về vấn đề gì hôm nay?',
      citations: null
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeAgent, setActiveAgent] = useState('none');
  const [apiKey, setApiKey] = useState(localStorage.getItem('openrouter_key') || '');
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const saveApiKey = (key) => {
    setApiKey(key);
    localStorage.setItem('openrouter_key', key);
    setShowSettings(false);
  };

  const handleInput = (e) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    if (!apiKey) {
        setShowSettings(true);
        return;
    }

    const currentInput = inputValue.trim();
    const userMessage = { id: Date.now(), sender: 'user', text: currentInput };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    
    setIsTyping(true);
    setActiveAgent('system');
    
    try {
      // Gọi API Backend của chúng ta và truyền API Key qua Header
      const response = await axios.post('/api/chat', 
        { query: currentInput },
        { headers: { 'X-API-Key': apiKey } }
      );
      
      const { text, agentType, citations } = response.data;
      
      setActiveAgent('customer');
      setTimeout(() => {
          setIsTyping(false);
          setActiveAgent('none');
          setMessages(prev => [...prev, {
              id: Date.now() + 1,
              sender: 'agent',
              agentType: agentType || 'customer',
              text: text,
              citations: citations
          }]);
      }, 500);

    } catch (error) {
      console.error(error);
      setIsTyping(false);
      setActiveAgent('none');
      setMessages(prev => [...prev, {
          id: Date.now() + 1,
          sender: 'agent',
          agentType: 'system',
          text: "Lỗi kết nối Backend: " + (error.response?.data?.detail || error.message)
      }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app-container">
      <header>
        <div className="logo-container">
          <div className="logo-icon">
            <Scale size={24} />
          </div>
          <div className="logo-text">
            <h1>Legal AI Hub</h1>
            <p>Powered by Multi-Agent RAG</p>
          </div>
        </div>
        <div className="header-actions" style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button 
                onClick={() => setShowSettings(true)}
                style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '8px', borderRadius: '50%', cursor: 'pointer' }}
                title="Cài đặt API Key"
            >
                <Settings size={20} />
            </button>
            <div className="status-badge">
            <div className="status-dot"></div>
            System Online
            </div>
        </div>
      </header>

      {/* API Key Modal */}
      {showSettings && (
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', zIndex: 100, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <div style={{ background: 'var(--bg-secondary)', padding: '24px', borderRadius: '16px', width: '400px', border: '1px solid var(--border-color)' }}>
                  <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}><Key size={20} /> Cài đặt AI (OpenRouter)</h3>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>Nhập OpenRouter API Key để cấp quyền suy nghĩ cho Agent.</p>
                  <input 
                    type="password" 
                    defaultValue={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-or-v1-..."
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'white', marginBottom: '16px' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                      <button onClick={() => setShowSettings(false)} style={{ padding: '8px 16px', background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>Đóng</button>
                      <button onClick={() => saveApiKey(apiKey)} style={{ padding: '8px 16px', background: 'var(--gradient-accent)', border: 'none', color: 'white', borderRadius: '8px', cursor: 'pointer' }}>Lưu & Kích hoạt</button>
                  </div>
              </div>
          </div>
      )}

      <main>
        {/* Agent Workflow Indicator */}
        <AnimatePresence>
          {activeAgent !== 'none' && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="workflow-indicator"
            >
              <div className={`workflow-node ${activeAgent === 'system' ? 'active' : ''}`}>
                <Loader2 size={16} className={activeAgent === 'system' ? 'animate-spin' : ''} /> Supervisor
              </div>
              <div className={`workflow-node ${activeAgent === 'law' ? 'active' : ''}`}>
                <Scale size={16} /> Law
              </div>
              <div className={`workflow-node ${activeAgent === 'tax' ? 'active' : ''}`}>
                <Calculator size={16} /> Tax
              </div>
              <div className={`workflow-node ${activeAgent === 'compliance' ? 'active' : ''}`}>
                <ShieldCheck size={16} /> Compliance
              </div>
              <div className="workflow-arrow">→</div>
              <div className={`workflow-node ${activeAgent === 'summarizer' ? 'active' : ''}`}>
                <BookOpen size={16} /> Summarizer
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="chat-container">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`message-wrapper ${msg.sender}`}
              >
                <div className="message-bubble">
                  {msg.sender === 'agent' && (
                    <div className="agent-header">
                      {agentIcons[msg.agentType]}
                      <span style={{ textTransform: 'capitalize' }}>{msg.agentType} Agent</span>
                    </div>
                  )}
                  <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                  
                  {msg.citations && (
                    <div className="citations">
                      {msg.citations.map((cit) => (
                        <div key={cit.id} className="citation-card">
                          <div className="citation-header">
                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <BookOpen size={14} /> {cit.title}
                            </span>
                            <span className="relevance-score">Score: {cit.score}</span>
                          </div>
                          <div style={{ color: 'var(--text-secondary)' }}>
                            {cit.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            
            {isTyping && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="message-wrapper agent"
              >
                <div className="message-bubble">
                   <div className="agent-header">
                      {activeAgent === 'system' ? <Loader2 className="agent-icon animate-spin" /> : agentIcons[activeAgent]}
                      <span style={{ textTransform: 'capitalize' }}>{activeAgent === 'system' ? 'Supervisor' : activeAgent} Agent</span>
                    </div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-box">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={apiKey ? "Nhập câu hỏi pháp lý của bạn..." : "Vui lòng nhập API Key để chat..."}
              rows={1}
            />
            <button 
              className="send-button" 
              onClick={handleSend}
              disabled={!inputValue.trim() || isTyping}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
