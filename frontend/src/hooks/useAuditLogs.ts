import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { AuditLogsService } from "../client/sdk.gen"
import type { AuditAction, AuditSeverity, AuditLogPublic } from "../client/types.gen"

// Define the filters type
interface AuditLogFilterOptions {
  search?: string;
  action?: AuditAction;
  severity?: AuditSeverity;
  resource_type?: string;
  resource_id?: string;
  start_date?: string;
  end_date?: string;
  user_id?: string;
  tenant_id?: string;
}

// Extended type with UI-specific fields
interface ExtendedAuditLog extends AuditLogPublic {
  user_name?: string;
  user_email?: string;
  message?: string;
  severity: AuditSeverity;
  action: AuditAction;
  timestamp: string;
}

const PER_PAGE = 10

export const useAuditLogs = (page: number, filters?: AuditLogFilterOptions) => {
  return useQuery({
    queryKey: ["auditLogs", { page, filters }],
    queryFn: async () => {
      const skip = (page - 1) * PER_PAGE
      
      // Convert frontend filters to API parameters
      const apiParams: any = {
        skip,
        limit: PER_PAGE,
      }
      
      if (filters?.action) apiParams.action = filters.action
      if (filters?.severity) apiParams.severity = filters.severity
      if (filters?.resource_type) apiParams.resourceType = filters.resource_type
      if (filters?.resource_id) apiParams.resourceId = filters.resource_id
      if (filters?.user_id) apiParams.userId = filters.user_id
      if (filters?.tenant_id) apiParams.tenantId = filters.tenant_id
      if (filters?.start_date) apiParams.startDate = filters.start_date
      if (filters?.end_date) apiParams.endDate = filters.end_date
      
      const response = await AuditLogsService.readAuditLogs(apiParams)
      
      // Transform API response to include user information and messages
      const extendedData = response.data.map((log): ExtendedAuditLog => ({
        ...log,
        user_name: `User ${log.user_id.slice(0, 8)}`, // Mock user name - in real app, you'd fetch user details
        user_email: `user-${log.user_id.slice(0, 8)}@example.com`, // Mock email
        message: `${log.action} operation on ${log.resource_type} ${log.resource_id}`,
        severity: log.severity || "INFO",
        action: log.action,
        timestamp: log.timestamp || new Date().toISOString(),
      }))
      
      return {
        data: extendedData,
        count: response.count,
      }
    },
    placeholderData: (prevData) => prevData,
  })
}

export const useAuditLogExport = () => {
  return useMutation({
    mutationFn: async ({ format, filters }: { format: 'JSON' | 'CSV'; filters?: AuditLogFilterOptions }) => {
      if (format === "CSV") {
        // Use the backend CSV export endpoint
        const apiParams: any = {}
        
        if (filters?.action) apiParams.action = filters.action
        if (filters?.severity) apiParams.severity = filters.severity
        if (filters?.resource_type) apiParams.resourceType = filters.resource_type
        if (filters?.resource_id) apiParams.resourceId = filters.resource_id
        if (filters?.user_id) apiParams.userId = filters.user_id
        if (filters?.tenant_id) apiParams.tenantId = filters.tenant_id
        if (filters?.start_date) apiParams.startDate = filters.start_date
        if (filters?.end_date) apiParams.endDate = filters.end_date
        
        const response = await AuditLogsService.exportAuditLogsCsv(apiParams)
        
        // Create and download file
        const blob = new Blob([response.csv_data], { type: "text/csv" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = response.filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        return response
      } else {
        // For JSON, fetch the data and convert to JSON format
        const apiParams: any = {
          limit: 10000, // Get a large number of records for export
        }
        
        if (filters?.action) apiParams.action = filters.action
        if (filters?.severity) apiParams.severity = filters.severity
        if (filters?.resource_type) apiParams.resourceType = filters.resource_type
        if (filters?.resource_id) apiParams.resourceId = filters.resource_id
        if (filters?.user_id) apiParams.userId = filters.user_id
        if (filters?.tenant_id) apiParams.tenantId = filters.tenant_id
        if (filters?.start_date) apiParams.startDate = filters.start_date
        if (filters?.end_date) apiParams.endDate = filters.end_date
        
        const response = await AuditLogsService.readAuditLogs(apiParams)
        
        // Create and download file
        const content = JSON.stringify(response.data, null, 2)
        const blob = new Blob([content], { type: "application/json" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        return response
      }
    },
  })
}

export const useAuditLogDetails = (auditLogId: string) => {
  return useQuery({
    queryKey: ["auditLog", auditLogId],
    queryFn: async () => {
      const response = await AuditLogsService.readAuditLog({ auditLogId })
      
      // Transform to extended format
      const extendedLog: ExtendedAuditLog = {
        ...response,
        user_name: `User ${response.user_id.slice(0, 8)}`,
        user_email: `user-${response.user_id.slice(0, 8)}@example.com`,
        message: `${response.action} operation on ${response.resource_type} ${response.resource_id}`,
        severity: response.severity || "INFO",
        action: response.action,
        timestamp: response.timestamp || new Date().toISOString(),
      }
      
      return extendedLog
    },
    enabled: !!auditLogId,
  })
}

export const useCreateAuditLog = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (auditLogData: any) => {
      return await AuditLogsService.createAuditLog({ requestBody: auditLogData })
    },
    onSuccess: () => {
      // Invalidate and refetch audit logs
      queryClient.invalidateQueries({ queryKey: ["auditLogs"] })
    },
  })
}

export const useUpdateAuditLog = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ auditLogId, updateData }: { auditLogId: string; updateData: any }) => {
      return await AuditLogsService.updateAuditLog({ 
        auditLogId, 
        requestBody: updateData 
      })
    },
    onSuccess: () => {
      // Invalidate and refetch audit logs
      queryClient.invalidateQueries({ queryKey: ["auditLogs"] })
    },
  })
}

export const useDeleteAuditLog = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (auditLogId: string) => {
      return await AuditLogsService.deleteAuditLog({ auditLogId })
    },
    onSuccess: () => {
      // Invalidate and refetch audit logs
      queryClient.invalidateQueries({ queryKey: ["auditLogs"] })
    },
  })
} 