import {
  Badge,
  Box,
  Code,
  Grid,
  GridItem,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { FiCalendar, FiGlobe, FiMonitor, FiUser } from "react-icons/fi"

import type { AuditLogEntry } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../ui/dialog"

interface AuditLogDetailsProps {
  log: AuditLogEntry
  isOpen: boolean
  onClose: () => void
}

const AuditLogDetails = ({ log, isOpen, onClose }: AuditLogDetailsProps) => {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
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

  const getActionColor = (action: string) => {
    switch (action) {
      case "CREATE":
        return "green"
      case "UPDATE":
        return "blue"
      case "DELETE":
        return "red"
      case "VIEW":
        return "gray"
      default:
        return "blue"
    }
  }

  return (
    <DialogRoot
      size={{ base: "md", md: "lg" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Audit Log Details</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <VStack gap={6} align="stretch">
            {/* Basic Information */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                Basic Information
              </Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiCalendar />
                      <Text fontSize="sm" fontWeight="medium">
                        Timestamp
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {formatTimestamp(log.timestamp)}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Log ID
                    </Text>
                    <Code fontSize="sm">{log.id}</Code>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Action
                    </Text>
                    <Badge colorScheme={getActionColor(log.action)} size="sm">
                      {log.action}
                    </Badge>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Severity
                    </Text>
                    <Badge colorScheme={getSeverityColor(log.severity)} size="sm">
                      {log.severity}
                    </Badge>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* User Information */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                User Information
              </Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiUser />
                      <Text fontSize="sm" fontWeight="medium">
                        User Name
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {log.user_name || "Unknown"}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Email
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {log.user_email || "N/A"}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      User ID
                    </Text>
                    <Code fontSize="sm">{log.user_id || "N/A"}</Code>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Session ID
                    </Text>
                    <Code fontSize="sm">{log.session_id || "N/A"}</Code>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* Resource Information */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                Resource Information
              </Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Resource Type
                    </Text>
                    <Badge variant="outline" size="sm">
                      {log.resource_type}
                    </Badge>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Resource ID
                    </Text>
                    <Code fontSize="sm">{log.resource_id || "N/A"}</Code>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* Technical Information */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                Technical Information
              </Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiGlobe />
                      <Text fontSize="sm" fontWeight="medium">
                        IP Address
                      </Text>
                    </HStack>
                    <Code fontSize="sm">{log.ip_address || "N/A"}</Code>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiMonitor />
                      <Text fontSize="sm" fontWeight="medium">
                        User Agent
                      </Text>
                    </HStack>
                    <Text fontSize="xs" color="gray.600" truncate maxW="300px">
                      {log.user_agent || "N/A"}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Tenant ID
                    </Text>
                    <Code fontSize="sm">{log.tenant_id || "N/A"}</Code>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* Message */}
            {log.message && (
              <Box>
                <Text fontSize="lg" fontWeight="bold" mb={4}>
                  Message
                </Text>
                <Box p={3} bg="gray.50" borderRadius="md">
                  <Text fontSize="sm">{log.message}</Text>
                </Box>
              </Box>
            )}

            {/* State Changes */}
            {(log.before_state || log.after_state) && (
              <Box>
                <Text fontSize="lg" fontWeight="bold" mb={4}>
                  State Changes
                </Text>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  <GridItem>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                      Before State
                    </Text>
                    <Box p={3} bg="red.50" borderRadius="md" maxH="200px" overflowY="auto">
                      <Code fontSize="xs" whiteSpace="pre-wrap">
                        {log.before_state ? JSON.stringify(log.before_state, null, 2) : "N/A"}
                      </Code>
                    </Box>
                  </GridItem>
                  <GridItem>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                      After State
                    </Text>
                    <Box p={3} bg="green.50" borderRadius="md" maxH="200px" overflowY="auto">
                      <Code fontSize="xs" whiteSpace="pre-wrap">
                        {log.after_state ? JSON.stringify(log.after_state, null, 2) : "N/A"}
                      </Code>
                    </Box>
                  </GridItem>
                </Grid>
              </Box>
            )}

            {/* Metadata */}
            {log.metadata && Object.keys(log.metadata).length > 0 && (
              <Box>
                <Text fontSize="lg" fontWeight="bold" mb={4}>
                  Metadata
                </Text>
                <Box p={3} bg="blue.50" borderRadius="md" maxH="200px" overflowY="auto">
                  <Code fontSize="xs" whiteSpace="pre-wrap">
                    {JSON.stringify(log.metadata, null, 2)}
                  </Code>
                </Box>
              </Box>
            )}
          </VStack>
        </DialogBody>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AuditLogDetails 