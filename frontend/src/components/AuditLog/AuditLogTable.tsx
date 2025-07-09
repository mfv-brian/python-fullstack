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
import { useState } from "react"
import { FiDownload, FiEye, FiSearch } from "react-icons/fi"

import type { AuditAction, AuditSeverity } from "../../client/types.gen"
import { useAuditLogs } from "../../hooks/useAuditLogs"
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

const PER_PAGE = 10

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
  const [filters, setFilters] = useState<AuditLogFilterOptions>({})
  const [selectedLog, setSelectedLog] = useState<any>(null)
  const [showExport, setShowExport] = useState(false)

  const { data, isLoading, isPlaceholderData, error } = useAuditLogs(page, filters)

  const logs = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  const handleFiltersChange = (newFilters: AuditLogFilterOptions) => {
    setFilters(newFilters)
    setPage(1)
  }

  const handleFiltersReset = () => {
    setFilters({})
    setPage(1)
  }

  if (error) {
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
              <EmptyState.Title>Error loading audit logs</EmptyState.Title>
              <EmptyState.Description>
                {error instanceof Error ? error.message : "An error occurred while loading audit logs"}
              </EmptyState.Description>
            </VStack>
          </EmptyState.Content>
        </EmptyState.Root>
      </Box>
    )
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