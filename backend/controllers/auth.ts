import { type RequestHandler } from 'express';
import { prisma } from '../lib/db';
import bcrypt from 'bcrypt';

export const registerHandler: RequestHandler = async (req, res) => {
    const { fullName, email, password } = req.body
    try {
        if (!fullName || !email || !password) {
            return res.status(400).send("Missing required fields")
        }

        const existingUser = await prisma.user.findUnique({
            where: { email }
        })

        if (existingUser) {
            return res.status(400).send("User with this email already exists")
        }

        const hashedPassword = await bcrypt.hash(password, 10)

        const newUser = await prisma.user.create({
            data: {
                email,
                fullName,
                password: hashedPassword,
            }
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

        const user = await prisma.user.findUnique({
            where: { email }
        })

        if (!user) {
            return res.status(400).send("Invalid email or password")
        }

        const isPasswordValid = await bcrypt.compare(password, user.password)

        if (!isPasswordValid) {
            return res.status(400).send("Invalid email or password")
        }

        res.status(200).send("Login successful")

    } catch (error) {
        console.log("Login endpoint failed with error: ", error)
        res.status(500).send("Internal Server Error")
    }
}