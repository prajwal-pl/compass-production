import { type RequestHandler } from 'express'
import { db } from '../db/db'
import { services } from '../db/schema'
import { eq } from 'drizzle-orm'

export const listServices: RequestHandler = async (req, res) => {
    try {
        const userId = req.userId as string
        const userServices = await db.select().from(services).where(eq(services.userId, userId))

        if (!userServices) {
            return res.status(404).json({ message: "No services found for this user" })
        }

        res.status(200).json({ message: "Services retrieved successfully", services: userServices })
    } catch (error) {
        console.log("List services endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}

export const getServiceById: RequestHandler = async (req, res) => {
    const { id } = req.params
    try {
        if (!id) {
            return res.status(400).json({ message: "Service ID is required" })
        }

        const service = await db.select().from(services).where(eq(services.id, id as string)).limit(1)

        if (!service || service.length === 0) {
            return res.status(404).json({ message: "Service not found" })
        }

        res.status(200).json({ message: "Service retrieved successfully", service: service[0] })
    } catch (error) {
        console.log("Get service by ID endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}

export const createService: RequestHandler = async (req, res) => {
    try {
        const userId = req.userId as string
        const { name, description, repositoryUrl } = req.body

        if (!name) {
            return res.status(400).json({ message: "Service name is required" })
        }

        const [newService] = await db.insert(services).values({
            name,
            description,
            repositoryUrl,
            userId: userId,
        }).returning()

        if (!newService) {
            return res.status(500).json({ message: "Failed to create service" })
        }

        res.status(201).json({ message: "Service created successfully", service: newService })
    } catch (error) {
        console.log("Create service endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}

export const updateService: RequestHandler = async (req, res) => {
    const { id } = req.params
    const { name, description, repositoryUrl, status } = req.body
    try {
        if (!id) {
            return res.status(400).json({ message: "Service ID is required" })
        }

        const [service] = await db.select().from(services).where(eq(services.id, id as string)).limit(1)

        if (!service) {
            return res.status(404).json({ message: "Service not found" })
        }

        const [updatedService] = await db.update(services).set({
            name: name || service.name,
            description: description || service.description,
            repositoryUrl: repositoryUrl || service.repositoryUrl,
            status: status || service.status,
        }).where(eq(services.id, id as string)).returning()

        if (!updatedService) {
            return res.status(500).json({ message: "Failed to update service" })
        }

        res.status(200).json({ message: "Service updated successfully", service: updatedService })
    } catch (error) {
        console.log("Update service endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}

export const deleteService: RequestHandler = async (req, res) => {
    const { id } = req.params
    try {
        if (!id) {
            return res.status(400).json({ message: "Service ID is required" })
        }

        const [service] = await db.select().from(services).where(eq(services.id, id as string)).limit(1)

        if (!service) {
            return res.status(404).json({ message: "Service not found" })
        }

        await db.delete(services).where(eq(services.id, id as string))

        res.status(200).json({ message: "Service deleted successfully" })

    } catch (error) {
        console.log("Delete Service endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}

export const getServiceLogs: RequestHandler = async (req, res) => {
    const { id } = req.params
    try {
        if (!id) {
            return res.status(400).json({ message: "Service ID is required" })
        }

        const [service] = await db.select().from(services).where(eq(services.id, id as string)).limit(1)

        if (!service) {
            return res.status(404).json({ message: "Service not found" })
        }

        // WIP: Integrate with logging system to fetch real logs for the service

    } catch (error) {
        console.log("Get service logs endpoint failed with error: ", error)
        res.status(500).json({ message: "Internal Server Error", error })
    }
}