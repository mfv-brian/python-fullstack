import { Container, Heading, Tabs } from "@chakra-ui/react"
import { useState } from "react"
import { FiActivity, FiDatabase, FiSettings } from "react-icons/fi"

import AuditLogTable from "./AuditLogTable"
import AuditLogSettings from "./AuditLogSettings"
import AuditLogRealTime from "./AuditLogRealTime"

const AuditLogManagement = () => {
  const [activeTab, setActiveTab] = useState("logs")

  const handleTabChange = (details: any) => {
    setActiveTab(details.value)
  }

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12} mb={6}>
        Audit Log Management
      </Heading>

      <Tabs.Root value={activeTab} onValueChange={handleTabChange}>
        <Tabs.List>
          <Tabs.Trigger value="logs">
            <FiDatabase />
            Audit Logs
          </Tabs.Trigger>
          <Tabs.Trigger value="realtime">
            <FiActivity />
            Real-time Monitor
          </Tabs.Trigger>
          <Tabs.Trigger value="settings">
            <FiSettings />
            Settings
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="logs">
          <AuditLogTable />
        </Tabs.Content>

        <Tabs.Content value="realtime">
          <AuditLogRealTime />
        </Tabs.Content>

        <Tabs.Content value="settings">
          <AuditLogSettings />
        </Tabs.Content>
      </Tabs.Root>
    </Container>
  )
}

export default AuditLogManagement 