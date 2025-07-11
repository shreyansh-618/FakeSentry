import express from "express";
import axios from "axios";
import { z } from "zod";
import {
  authenticateToken,
  type AuthenticatedRequest,
} from "../middleware/auth";
import { NewsAnalysis } from "../models/NewsAnalysis";

const router = express.Router();

// Validation schema
const analyzeNewsSchema = z.object({
  content: z.string().min(10).max(10000, "Content too long"),
});

// Analyze news endpoint
router.post(
  "/analyze",
  authenticateToken,
  async (req: AuthenticatedRequest, res) => {
    try {
      // Validate input
      const { content } = analyzeNewsSchema.parse(req.body);

      // Call ML service
      const mlServiceUrl =
        process.env.ML_SERVICE_URL || "http://localhost:5000";
      const mlResponse = await axios.post(
        `${mlServiceUrl}/predict`,
        {
          text: content,
        },
        {
          timeout: 30000, // 30 second timeout
        }
      );

      const prediction = mlResponse.data;

      // Save analysis to database
      const analysis = new NewsAnalysis({
        userId: req.user!.uid,
        content,
        prediction: prediction.prediction,
        confidence: prediction.confidence,
        modelUsed: prediction.model_used,
        processingTime: prediction.processing_time,
      });

      await analysis.save();

      res.json({
        id: analysis._id,
        prediction: prediction.prediction,
        confidence: prediction.confidence,
        modelUsed: prediction.model_used,
        processingTime: prediction.processing_time,
        timestamp: analysis.createdAt,
      });
    } catch (error) {
      console.error("News analysis error:", error);

      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: "Invalid input",
          details: error.errors,
        });
      }

      if (axios.isAxiosError(error)) {
        return res.status(503).json({
          error: "ML service unavailable",
          message: "Please try again later",
        });
      }

      res.status(500).json({ error: "Internal server error" });
    }
  }
);

// Get user's analysis history
router.get(
  "/history",
  authenticateToken,
  async (req: AuthenticatedRequest, res) => {
    try {
      const page = Number.parseInt(req.query.page as string) || 1;
      const limit = Number.parseInt(req.query.limit as string) || 10;
      const skip = (page - 1) * limit;

      const analyses = await NewsAnalysis.find({ userId: req.user!.uid })
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .select("-content"); // Exclude full content for performance

      const total = await NewsAnalysis.countDocuments({
        userId: req.user!.uid,
      });

      res.json({
        analyses,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
        },
      });
    } catch (error) {
      console.error("History fetch error:", error);
      res.status(500).json({ error: "Failed to fetch history" });
    }
  }
);

// Get specific analysis details
router.get(
  "/analysis/:id",
  authenticateToken,
  async (req: AuthenticatedRequest, res) => {
    try {
      const analysis = await NewsAnalysis.findOne({
        _id: req.params.id,
        userId: req.user!.uid,
      });

      if (!analysis) {
        return res.status(404).json({ error: "Analysis not found" });
      }

      res.json(analysis);
    } catch (error) {
      console.error("Analysis fetch error:", error);
      res.status(500).json({ error: "Failed to fetch analysis" });
    }
  }
);

export default router;
