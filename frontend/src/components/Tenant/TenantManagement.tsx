import { Container, Heading, Tabs } from "@chakra-ui/react"
import { useState } from "react"
import { FiHome } from "react-icons/fi"

import TenantTable from "./TenantTable"

const TenantManagement = () => {
  const [activeTab, setActiveTab] = useState("tenants")

  const handleTabChange = (details: any) => {
    setActiveTab(details.value)
  }

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12} mb={6}>
        Multi-Tenant Management
      </Heading>

      <Tabs.Root value={activeTab} onValueChange={handleTabChange}>
        <Tabs.List>
          <Tabs.Trigger value="tenants">
            <FiHome />
            Tenants
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="tenants">
          <TenantTable />
        </Tabs.Content>
      </Tabs.Root>
    </Container>
  )
}

export default TenantManagement 