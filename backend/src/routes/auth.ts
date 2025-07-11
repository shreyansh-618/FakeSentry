import express from "express";
import { User } from "../models/User";
import {
  authenticateToken,
  type AuthenticatedRequest,
} from "../middleware/auth";
const router = express.Router();

router.post(
  "/profile",
  authenticateToken,
  async (req: AuthenticatedRequest, res) => {
    try {
      const { displayName, photoURL } = req.body;

      const user = await User.findOneAndUpdate(
        { firebaseUid: req.user!.uid },
        {
          firebaseUid: req.user!.uid,
          email: req.user!.email,
          displayName,
          photoURL,
        },
        {
          upsert: true,
          new: true,
          runValidators: true,
        }
      );
      res.json({
        id: user._id,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        createdAt: user.createdAt,
      });
    } catch (error) {
      console.error("Profile update error:", error);
      res.status(500).json({ error: "Failed to update profile " });
    }
  }
);

router.get(
  "/profile",
  authenticateToken,
  async (req: AuthenticatedRequest, res) => {
    try {
      const user = await User.findOne({ firebaseUid: req.user!.uid });

      if (!user) {
        return res.status(404).json({ error: "uSER NOT Found" });
      }
      res.json({
        id: user._id,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        createdAt: user.createdAt,
      });
    } catch (error) {
      console.error("Profile fetch error:", error);
      res.status(500).json({ error: "Failed to fetch profile" });
    }
  }
);
export default router;
