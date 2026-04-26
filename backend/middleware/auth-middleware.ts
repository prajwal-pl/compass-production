import jwt from "jsonwebtoken"
import { type NextFunction, type Request, type Response } from "express"

declare global {
    namespace Express {
        interface Request {
            userId?: string
        }
    }
}

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization

    if (!authHeader) {
        return res.status(401).send("Authorization header missing")
    }

    const token = authHeader.split(" ")[1]

    if (!token) {
        return res.status(401).send("Token missing")
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET_KEY as string)
        req.userId = decoded as string
        next()
    } catch (error) {
        console.log("Auth middleware failed with error: ", error)
        res.status(401).send("Invalid token")
    }
}