import api from "./axios";

const predictionService = {

  // ===============================
  // SUBJECT RISK PREDICTION
  // ===============================
  getSubjectRisk: async (semester) => {
    try {

      const response = await api.get("/subject-risk/", {
        params: { semester }   // ✅ FIX
      });

      console.log("Subject Risk API:", response.data);

      return response.data;

    } catch (error) {
      console.error("Subject Risk API Error:", error);
      throw error;
    }
  },


  // ===============================
  // AI RECOMMENDATION + TREND
  // ===============================
  getRecommendation: async (semester) => {
    try {

      const response = await api.get("/recommendation/", {
        params: { semester }   // ✅ FIX
      });

      console.log("Recommendation API:", response.data);

      return response.data;

    } catch (error) {
      console.error("Recommendation API Error:", error);
      throw error;
    }
  }

};

export default predictionService;