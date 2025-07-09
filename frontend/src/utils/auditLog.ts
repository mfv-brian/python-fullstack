import { useCreateUserAuditLog } from "../hooks/useAuditLogs"
import type { AuditAction, AuditSeverity } from "../client/types.gen"

export interface AuditLogData {
  action: AuditAction
  resource_type: string
  resource_id: string
  before_state?: Record<string, any>
  after_state?: Record<string, any>
  custom_metadata?: Record<string, any>
  severity?: AuditSeverity
  tenant_id: string
  user_id: string
}

export const useAuditLogger = () => {
  const createAuditLog = useCreateUserAuditLog()

  const logAction = async (data: AuditLogData) => {
    try {
      console.log("Creating audit log:", data)
      
      // Get user agent from browser
      const userAgent = navigator.userAgent
      
      // Get client IP (this will be handled by the backend)
      const auditLogData = {
        user_id: data.user_id,
        action: data.action,
        resource_type: data.resource_type,
        resource_id: data.resource_id,
        before_state: data.before_state,
        after_state: data.after_state,
        custom_metadata: {
          ...data.custom_metadata,
          user_agent: userAgent,
          frontend_timestamp: new Date().toISOString(),
        },
        severity: data.severity || "INFO",
        tenant_id: data.tenant_id,
      }

      console.log("Sending audit log data:", auditLogData)
      const result = await createAuditLog.mutateAsync(auditLogData)
      console.log("Audit log created successfully:", result)
    } catch (error) {
      console.error("Failed to create audit log:", error)
      console.error("Error details:", {
        message: error instanceof Error ? error.message : "Unknown error",
        status: error instanceof Error && 'status' in error ? (error as any).status : "Unknown",
        data: error instanceof Error && 'data' in error ? (error as any).data : "Unknown",
      })
      // Don't throw error to avoid breaking the main operation
    }
  }

  return { logAction }
}

// Helper functions for common audit log scenarios
export const createUserAuditLog = (
  action: AuditAction,
  userId: string,
  tenantId: string,
  currentUserId: string,
  beforeState?: Record<string, any>,
  afterState?: Record<string, any>,
  severity: AuditSeverity = "INFO"
) => ({
  action,
  resource_type: "user",
  resource_id: userId,
  before_state: beforeState,
  after_state: afterState,
  severity,
  tenant_id: tenantId,
  user_id: currentUserId,
})

export const createTenantAuditLog = (
  action: AuditAction,
  tenantId: string,
  currentUserId: string,
  beforeState?: Record<string, any>,
  afterState?: Record<string, any>,
  severity: AuditSeverity = "INFO"
) => ({
  action,
  resource_type: "tenant",
  resource_id: tenantId,
  before_state: beforeState,
  after_state: afterState,
  severity,
  tenant_id: tenantId,
  user_id: currentUserId,
}) 