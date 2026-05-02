import express from "express"

import { authMiddleware } from "../middleware/auth-middleware"
import { createService, deleteService, getServiceById, getServiceLogs, listServices, updateService } from "../controllers/services"

const router = express.Router()

router.get("/", authMiddleware, listServices)
router.post("/", authMiddleware, createService)
router.get("/:id", authMiddleware, getServiceById)
router.put("/:id", authMiddleware, updateService)
router.delete("/:id", authMiddleware, deleteService)
router.get("/:id/logs", authMiddleware, getServiceLogs)

export default router