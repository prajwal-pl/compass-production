import { type RequestHandler } from 'express';
import bcrypt from 'bcrypt';
import { db } from '../lib/utils';
import { users } from '../db/schema';
import { eq } from 'drizzle-orm';

export const registerHandler: RequestHandler = async (req, res) => {
    const { fullName, email, password } = req.body
    try {
        if (!fullName || !email || !password) {
            return res.status(400).send("Missing required fields")
        }

        const existingUser = await db.select().from(users).where(eq(users.email, email));
        if (existingUser) {
            return res.status(400).send("User with this email already exists")
        }

        const hashedPassword = await bcrypt.hash(password, 10)

        const newUser = await db.insert(users).values({
            fullName,
            email,
            password: hashedPassword,
        })

        console.log(newUser)

        res.status(201).send("User registered successfully")

    } catch (error) {
        console.log("Register endpoint failed with error: ", error)
        res.status(500).send("Internal Server Error")
    }
}

export const loginHandler: RequestHandler = async (req, res) => {
    const { email, password } = req.body
    try {
        if (!email || !password) {
            return res.status(400).send("Missing required fields")
        }

        const result = await db.select().from(users).where(eq(users.email, email)).limit(1)

        const user = result.flat()[0]

        if (!user) {
            return res.status(400).send("Invalid email or password")
        }

        const isPasswordValid = await bcrypt.compare(password, user.password || "")

        if (!isPasswordValid) {
            return res.status(400).send("Invalid email or password")
        }

        res.status(200).send("Login successful")

    } catch (error) {
        console.log("Login endpoint failed with error: ", error)
        res.status(500).send("Internal Server Error")
    }
}

export const profileHandler: RequestHandler = async (req, res) => {
    try {
        const userId = req.userId

        if (!userId) {
            return res.status(401).send("Unauthorized")
        }

        const result = await db.select().from(users).where(eq(users.id, userId)).limit(1)

        const user = result.flat()[0]

        if (!user) {
            return res.status(404).send("User not found")
        }

        res.status(200).json(user)
    } catch (error) {
        console.log("Profile endpoint failed with error: ", error)
        res.status(500).send("Internal Server Error")
    }
}

export const googleAuthHandler: RequestHandler = async (req, res) => { }