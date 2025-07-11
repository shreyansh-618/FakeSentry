import mongoose, { type Document, Schema } from "mongoose";

export interface INewsAnalysis extends Document {
  userId: string;
  content: string;
  prediction: "real" | "fake";
  confidence: number;
  modelUsed: string;
  processingTime: number;
  createdAt: Date;
}
const NewsAnalysisSchema = new Schema<INewsAnalysis>(
  {
    userId: {
      type: String,
      required: true,
      index: true,
    },
    content: {
      type: String,
      enum: ["real", "fake"],
      required: true,
    },
    confidence: {
      type: Number,
      required: true,
      min: 0,
      max: 1,
    },
    modelUsed: {
      type: String,
      required: true,
    },
    processingTime: {
      type: Number,
      required: true,
    },
  },
  {
    timestamps: true,
  }
);

NewsAnalysisSchema.index({ userId: 1, createdAt: -1 });
export const NewsAnalysis = mongoose.model<INewsAnalysis>(
  "NewsAnalysis",
  NewsAnalysisSchema
);
