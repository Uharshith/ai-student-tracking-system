import React, { useState } from 'react';
const { GoogleGenerativeAI } = require("@google/generative-ai");

// USE YOUR KEY HERE
const genAI = new GoogleGenerativeAI("AIzaSyAAXoLV_trXJATPb0UrbLt16HIQtQJiDek");
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const AcademicBot = () => {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input) return;
    setLoading(true);
    
    // Add user message to UI
    const newHistory = [...chatHistory, { role: "user", text: input }];
    setChatHistory(newHistory);

    try {
      const result = await model.generateContent(`You are an Academic Advisor. Answer this based on student tracking logic: ${input}`);
      const response = await result.response;
      setChatHistory([...newHistory, { role: "bot", text: response.text() }]);
    } catch (error) {
      console.error("AI Error:", error);
    }
    
    setInput("");
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', width: '300px', background: '#fff', border: '1px solid #ddd', borderRadius: '10px', boxShadow: '0px 0px 10px rgba(0,0,0,0.1)' }}>
      <div style={{ background: '#007bff', color: '#fff', padding: '10px', borderRadius: '10px 10px 0 0' }}>Academic Assistant</div>
      <div style={{ height: '300px', overflowY: 'auto', padding: '10px' }}>
        {chatHistory.map((msg, i) => (
          <div key={i} style={{ textAlign: msg.role === 'user' ? 'right' : 'left', margin: '5px 0' }}>
            <span style={{ background: msg.role === 'user' ? '#e1ffc7' : '#f1f1f1', padding: '5px 10px', borderRadius: '5px', display: 'inline-block' }}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', borderTop: '1px solid #ddd' }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} style={{ flex: 1, border: 'none', padding: '10px' }} placeholder="Ask something..." />
        <button onClick={handleSend} disabled={loading} style={{ background: '#007bff', color: '#fff', border: 'none', padding: '10px' }}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default AcademicBot;