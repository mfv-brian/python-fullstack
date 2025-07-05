import { createFileRoute } from "@tanstack/react-router"

import AuditLogManagement from "../../components/AuditLog/AuditLogManagement"

export const Route = createFileRoute("/_layout/audit-logs")({
  component: AuditLogs,
})

function AuditLogs() {
  return <AuditLogManagement />
} 