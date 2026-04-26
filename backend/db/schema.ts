import { relations } from "drizzle-orm";
import { boolean, pgEnum, pgTable, text, timestamp, uniqueIndex, uuid, vector } from "drizzle-orm/pg-core";

export const AuthProviders = pgEnum("auth_providers", ["EMAIL", "GOOGLE"])

export const UserRole = pgEnum("user_role", ["OWNER", "ADMIN", "MEMBER"])

export const ServiceStatus = pgEnum("service_status", ["ACTIVE", "INACTIVE", "DEPRECATED", "MAINTENANCE"])

export const Environment = pgEnum("environment", ["DEVELOPMENT", "STAGING", "PRODUCTION"])

export const DeploymentStatus = pgEnum("deployment_status", ["PENDING", "IN_PROGRESS", "SUCCESS", "FAILED", "ROLLED_BACK"])

export const users = pgTable("users", {
    id: uuid("id").defaultRandom().primaryKey(),
    email: text("email").notNull().unique(),
    password: text("password"),
    fullName: text("full_name"),
    provider: AuthProviders().default("EMAIL").notNull(),
    role: UserRole().default("MEMBER").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
});

export const teams = pgTable("teams", {
    id: uuid("id").defaultRandom().primaryKey(),
    name: text("name").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
})

export const services = pgTable("services", {
    id: uuid("id").defaultRandom().primaryKey(),
    name: text("name").notNull(),
    description: text("description"),
    userId: uuid("user_id").notNull().references(() => users.id),
    status: ServiceStatus().default("ACTIVE").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
})

export const deployments = pgTable("deployments", {
    id: uuid("id").defaultRandom().primaryKey(),
    serviceId: uuid("service_id").notNull().references(() => services.id),
    version: text("version").notNull(),
    commitSha: text("commit_sha").notNull(),
    commitMessage: text("commit_message").notNull(),
    environment: Environment().default("DEVELOPMENT").notNull(),
    status: DeploymentStatus().default("PENDING").notNull(),
    rolledBack: boolean("rolled_back").default(false).notNull(),
    startedAt: timestamp("started_at").defaultNow(),
    completedAt: timestamp("completed_at"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
})

export const documentation = pgTable("documentation", {
    id: uuid("id").defaultRandom().primaryKey(),
    serviceId: uuid("service_id").notNull().references(() => services.id),
    title: text("title").notNull(),
    content: text("content").notNull(),
    version: text("version").notNull(),
    isAiGenerated: boolean("is_ai_generated").default(false).notNull(),
    embedding: vector("embedding", { dimensions: 1536 }),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
})

export const teamMembers = pgTable("team_members", {
    id: uuid("id").defaultRandom().primaryKey(),
    teamId: uuid("team_id").notNull().references(() => teams.id),
    userId: uuid("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
    role: UserRole().default("MEMBER").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().$onUpdateFn(() => new Date()).notNull(),
}, (table) => ({
    teamUserUnique: uniqueIndex("team_members_team_user_unique").on(table.teamId, table.userId),
}))

export const userRelations = relations(users, ({ many }) => ({
    services: many(services),
    teamMembers: many(teamMembers)
}))

export const teamRelations = relations(teams, ({ many }) => ({
    teamMembers: many(teamMembers)
}))

export const serviceRelations = relations(services, ({ one, many }) => ({
    deployments: many(deployments),
    documentation: many(documentation),
    user: one(users, { fields: [services.userId], references: [users.id] })
}))

export const deploymentRelations = relations(deployments, ({ one }) => ({
    service: one(services, { fields: [deployments.serviceId], references: [services.id] })
}))

export const documentationRelations = relations(documentation, ({ one }) => ({
    service: one(services, { fields: [documentation.serviceId], references: [services.id] })
}))

export const teamMemberRelations = relations(teamMembers, ({ one }) => ({
    user: one(users, { fields: [teamMembers.userId], references: [users.id] }),
    team: one(teams, { fields: [teamMembers.teamId], references: [teams.id] })
}))