import { createFileRoute } from "@tanstack/react-router"

import TenantManagement from "../../components/Tenant/TenantManagement"

function Tenants() {
  return <TenantManagement />
}

export const Route = createFileRoute("/_layout/tenants")({
  component: Tenants,
}) 