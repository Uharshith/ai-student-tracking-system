// src/api/aiService.js
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI("YOUR_API_KEY");
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

export const getAIResponse = async (prompt) => {
  const result = await model.generateContent(prompt);
  const response = await result.response;
  return response.text();
};