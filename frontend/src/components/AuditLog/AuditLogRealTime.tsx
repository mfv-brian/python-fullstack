import {
  Badge,
  Box,
  Button,
  Card,
  Flex,
  HStack,
  IconButton,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FiActivity, FiPause, FiPlay, FiTrash2 } from "react-icons/fi"

import type { AuditLogPublic, AuditAction, AuditSeverity } from "../../client/types.gen"

// Define an extended type with the additional fields needed for this component
interface ExtendedAuditLog extends AuditLogPublic {
  user_name?: string;
  user_email?: string;
  message?: string;
  severity: AuditSeverity;
  action: AuditAction;
  timestamp: string; // Make timestamp required
}

const AuditLogRealTime = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [logs, setLogs] = useState<ExtendedAuditLog[]>([])
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const intervalRef = useRef<number | null>(null)

  // Mock WebSocket connection
  const connect = () => {
    setIsConnected(true)
    
    // Simulate receiving real-time logs
    intervalRef.current = window.setInterval(() => {
      if (!isPaused) {
        const mockLog: ExtendedAuditLog = {
          id: Date.now().toString(),
          user_id: `user${Math.floor(Math.random() * 100)}`,
          user_email: `user${Math.floor(Math.random() * 100)}@example.com`,
          user_name: `User ${Math.floor(Math.random() * 100)}`,
          action: ["CREATE", "UPDATE", "DELETE", "VIEW", "LOGIN"][Math.floor(Math.random() * 5)] as any,
          resource_type: ["user", "item", "order", "product"][Math.floor(Math.random() * 4)],
          resource_id: `resource${Math.floor(Math.random() * 1000)}`,
          timestamp: new Date().toISOString(),
          ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
          severity: ["INFO", "WARNING", "ERROR", "CRITICAL"][Math.floor(Math.random() * 4)] as any,
          message: [
            "User logged in successfully",
            "Item created",
            "Order updated",
            "Product deleted",
            "Configuration changed",
            "Access granted",
            "System error occurred",
            "Critical failure detected"
          ][Math.floor(Math.random() * 8)],
          tenant_id: `tenant${Math.floor(Math.random() * 3) + 1}`,
        }

        setLogs(prevLogs => {
          const newLogs = [mockLog, ...prevLogs].slice(0, 100) // Keep only last 100 logs
          return newLogs
        })
      }
    }, 2000 + Math.random() * 3000) // Random interval between 2-5 seconds
  }

  const disconnect = () => {
    setIsConnected(false)
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current)
    }
  }

  const togglePause = () => {
    setIsPaused(!isPaused)
  }

  const clearLogs = () => {
    setLogs([])
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

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  // Auto scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [logs, autoScroll])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current)
      }
    }
  }, [])

  return (
    <Box>
      {/* Header Controls */}
      <Card.Root p={4} mb={4}>
        <Flex justify="space-between" align="center">
          <HStack>
            <HStack>
              <FiActivity color={isConnected ? "green" : "gray"} />
              <Text fontSize="sm" fontWeight="medium">
                Status: {isConnected ? "Connected" : "Disconnected"}
              </Text>
            </HStack>
            {isConnected && (
              <Badge colorScheme={isPaused ? "yellow" : "green"} size="sm">
                {isPaused ? "Paused" : "Live"}
              </Badge>
            )}
          </HStack>

          <HStack>
            {isConnected ? (
              <>
                <IconButton
                  variant="ghost"
                  size="sm"
                  onClick={togglePause}
                  aria-label={isPaused ? "Resume" : "Pause"}
                  title={isPaused ? "Resume monitoring" : "Pause monitoring"}
                >
                  {isPaused ? <FiPlay /> : <FiPause />}
                </IconButton>
                <IconButton
                  variant="ghost"
                  size="sm"
                  onClick={clearLogs}
                  aria-label="Clear logs"
                  title="Clear all logs"
                >
                  <FiTrash2 />
                </IconButton>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={disconnect}
                  colorPalette="red"
                >
                  Disconnect
                </Button>
              </>
            ) : (
              <Button
                variant="solid"
                size="sm"
                onClick={connect}
                colorPalette="green"
              >
                Connect
              </Button>
            )}
          </HStack>
        </Flex>

        {/* Stats */}
        {isConnected && (
          <HStack mt={4} gap={6}>
            <Text fontSize="sm" color="gray.600">
              Total Logs: {logs.length}
            </Text>
            <Text fontSize="sm" color="gray.600">
              Last Updated: {logs.length > 0 ? formatTimestamp(logs[0].timestamp) : "Never"}
            </Text>
          </HStack>
        )}
      </Card.Root>

      {/* Real-time Log Feed */}
      <Box
        maxH="600px"
        overflowY="auto"
        border="1px solid"
        borderColor="gray.200"
        borderRadius="md"
        bg="gray.50"
      >
        {logs.length === 0 ? (
          <Box p={8} textAlign="center">
            <Text color="gray.500">
              {isConnected 
                ? "Waiting for logs..." 
                : "Connect to start monitoring real-time audit logs"
              }
            </Text>
          </Box>
        ) : (
          <VStack gap={0} align="stretch">
            {logs.map((log, index) => (
              <Box
                key={log.id}
                p={3}
                borderBottom={index < logs.length - 1 ? "1px solid" : "none"}
                borderColor="gray.200"
                bg={index === 0 ? "green.50" : "white"}
                transition="background-color 0.3s"
              >
                <Flex justify="space-between" align="start" gap={3}>
                  <VStack align="start" gap={1} flex={1}>
                    <HStack wrap="wrap" gap={2}>
                      <Badge
                        colorScheme={getSeverityColor(log.severity)}
                        size="sm"
                      >
                        {log.severity}
                      </Badge>
                      <Badge
                        colorScheme={getActionColor(log.action)}
                        size="sm"
                        variant="outline"
                      >
                        {log.action}
                      </Badge>
                      <Text fontSize="xs" color="gray.500">
                        {log.resource_type}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {formatTimestamp(log.timestamp)}
                      </Text>
                    </HStack>
                    
                    <Text fontSize="sm" fontWeight="medium">
                      {log.message}
                    </Text>
                    
                    <HStack>
                      <Text fontSize="xs" color="gray.600">
                        User: {log.user_name} ({log.user_email})
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        •
                      </Text>
                      <Text fontSize="xs" color="gray.600">
                        IP: {log.ip_address}
                      </Text>
                      {log.tenant_id && (
                        <>
                          <Text fontSize="xs" color="gray.500">
                            •
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            Tenant: {log.tenant_id}
                          </Text>
                        </>
                      )}
                    </HStack>
                  </VStack>
                </Flex>
              </Box>
            ))}
            <div ref={logsEndRef} />
          </VStack>
        )}
      </Box>

      {/* Footer Controls */}
      {logs.length > 0 && (
        <Card.Root p={3} mt={4}>
          <Flex justify="space-between" align="center">
            <Text fontSize="sm" color="gray.600">
              Showing latest {logs.length} logs (max 100)
            </Text>
            <HStack>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAutoScroll(!autoScroll)}
                colorPalette={autoScroll ? "green" : "gray"}
              >
                Auto-scroll: {autoScroll ? "On" : "Off"}
              </Button>
            </HStack>
          </Flex>
        </Card.Root>
      )}
    </Box>
  )
}

export default AuditLogRealTime 