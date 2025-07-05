import {
  Badge,
  Box,
  EmptyState,
  Flex,
  HStack,
  IconButton,
  Table,
  Text,
  Tooltip,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { FiDownload, FiEye, FiSearch } from "react-icons/fi"

import type { AuditLogEntry } from "../../client/types.gen"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "../ui/pagination"
import { SkeletonText } from "../ui/skeleton"
import AuditLogDetails from "./AuditLogDetails"
import AuditLogExport from "./AuditLogExport"
import AuditLogFilters from "./AuditLogFilters"

const PER_PAGE = 10

// Mock data for demo - replace with actual API call
const mockAuditLogs = {
  data: [
    {
      id: "1",
      user_id: "user123",
      user_email: "admin@example.com",
      user_name: "Admin User",
      action: "CREATE",
      resource_type: "user",
      resource_id: "user456",
      timestamp: "2024-01-15T10:30:00Z",
      ip_address: "192.168.1.100",
      severity: "INFO",
      message: "Created new user account",
      tenant_id: "tenant1",
    },
    {
      id: "2",
      user_id: "user789",
      user_email: "user@example.com",
      user_name: "John Doe",
      action: "UPDATE",
      resource_type: "item",
      resource_id: "item123",
      timestamp: "2024-01-15T09:15:00Z",
      ip_address: "192.168.1.101",
      severity: "WARNING",
      message: "Updated item configuration",
      tenant_id: "tenant1",
    },
    {
      id: "3",
      user_id: "user456",
      user_email: "manager@example.com",
      user_name: "Manager User",
      action: "DELETE",
      resource_type: "order",
      resource_id: "order789",
      timestamp: "2024-01-15T08:45:00Z",
      ip_address: "192.168.1.102",
      severity: "ERROR",
      message: "Deleted order permanently",
      tenant_id: "tenant2",
    },
  ],
  count: 3,
} as { data: AuditLogEntry[]; count: number }

function getAuditLogsQueryOptions({ page, filters }: { page: number; filters?: AuditLogFilters }) {
  return {
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      return mockAuditLogs
    },
    queryKey: ["auditLogs", { page, filters }],
  }
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "INFO":
      return "blue"
    case "WARNING":
      return "yellow"
    case "ERROR":
      return "red"
    case "CRITICAL":
      return "purple"
    default:
      return "gray"
  }
}

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

function AuditLogTable() {
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<AuditLogFilters>({})
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null)
  const [showExport, setShowExport] = useState(false)

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getAuditLogsQueryOptions({ page, filters }),
    placeholderData: (prevData) => prevData,
  })

  const logs = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  const handleFiltersChange = (newFilters: AuditLogFilters) => {
    setFilters(newFilters)
    setPage(1)
  }

  const handleFiltersReset = () => {
    setFilters({})
    setPage(1)
  }

  if (isLoading && !data) {
    return (
      <Box>
        <AuditLogFilters
          onFiltersChange={handleFiltersChange}
          onReset={handleFiltersReset}
          loading={isLoading}
        />
        <Table.Root size={{ base: "sm", md: "md" }}>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Timestamp</Table.ColumnHeader>
              <Table.ColumnHeader>User</Table.ColumnHeader>
              <Table.ColumnHeader>Action</Table.ColumnHeader>
              <Table.ColumnHeader>Resource</Table.ColumnHeader>
              <Table.ColumnHeader>Severity</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {[...Array(5)].map((_, index) => (
              <Table.Row key={index}>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
                <Table.Cell><SkeletonText noOfLines={1} /></Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Box>
    )
  }

  if (logs.length === 0) {
    return (
      <Box>
        <AuditLogFilters
          onFiltersChange={handleFiltersChange}
          onReset={handleFiltersReset}
          loading={isLoading}
        />
        <EmptyState.Root>
          <EmptyState.Content>
            <EmptyState.Indicator>
              <FiSearch />
            </EmptyState.Indicator>
            <VStack textAlign="center">
              <EmptyState.Title>No audit logs found</EmptyState.Title>
              <EmptyState.Description>
                Try adjusting your search filters or check back later
              </EmptyState.Description>
            </VStack>
          </EmptyState.Content>
        </EmptyState.Root>
      </Box>
    )
  }

  return (
    <Box>
      <AuditLogFilters
        onFiltersChange={handleFiltersChange}
        onReset={handleFiltersReset}
        loading={isLoading}
      />

      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="sm" color="gray.600">
          Showing {logs.length} of {count} logs
        </Text>
        <HStack>
          <AuditLogExport
            isOpen={showExport}
            onClose={() => setShowExport(false)}
            filters={filters}
          />
          <IconButton
            variant="ghost"
            size="sm"
            onClick={() => setShowExport(true)}
            aria-label="Export logs"
          >
            <FiDownload />
          </IconButton>
        </HStack>
      </Flex>

      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Timestamp</Table.ColumnHeader>
            <Table.ColumnHeader>User</Table.ColumnHeader>
            <Table.ColumnHeader>Action</Table.ColumnHeader>
            <Table.ColumnHeader>Resource</Table.ColumnHeader>
            <Table.ColumnHeader>Severity</Table.ColumnHeader>
            <Table.ColumnHeader>Message</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {logs.map((log) => (
            <Table.Row key={log.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Text fontSize="sm" truncate maxW="150px">
                      {formatTimestamp(log.timestamp)}
                    </Text>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    {formatTimestamp(log.timestamp)}
                  </Tooltip.Content>
                </Tooltip.Root>
              </Table.Cell>
              <Table.Cell>
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" fontWeight="medium">
                    {log.user_name || "Unknown"}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {log.user_email}
                  </Text>
                </VStack>
              </Table.Cell>
              <Table.Cell>
                <Badge
                  colorScheme={log.action === "DELETE" ? "red" : "blue"}
                  size="sm"
                >
                  {log.action}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" fontWeight="medium">
                    {log.resource_type}
                  </Text>
                  {log.resource_id && (
                    <Text fontSize="xs" color="gray.500" truncate maxW="100px">
                      {log.resource_id}
                    </Text>
                  )}
                </VStack>
              </Table.Cell>
              <Table.Cell>
                <Badge
                  colorScheme={getSeverityColor(log.severity)}
                  size="sm"
                >
                  {log.severity}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <Text fontSize="sm" truncate maxW="200px">
                  {log.message}
                </Text>
              </Table.Cell>
              <Table.Cell>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <IconButton
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedLog(log)}
                      aria-label="View log details"
                    >
                      <FiEye />
                    </IconButton>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    View details
                  </Tooltip.Content>
                </Tooltip.Root>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>

      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          page={page}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>

      {selectedLog && (
        <AuditLogDetails
          log={selectedLog}
          isOpen={!!selectedLog}
          onClose={() => setSelectedLog(null)}
        />
      )}
    </Box>
  )
}

export default AuditLogTable 