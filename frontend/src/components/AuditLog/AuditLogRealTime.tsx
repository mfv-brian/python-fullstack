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
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const websocketRef = useRef<WebSocket | null>(null)

  // WebSocket connection
  const connect = () => {
    try {
      // Get the base URL from the current window location
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/v1/audit-logs/ws`
      
      const ws = new WebSocket(wsUrl)
      websocketRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setConnectionError(null)
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        if (!isPaused) {
          try {
            const data = JSON.parse(event.data)
            
            // Handle different message types
            if (data.type === 'audit_log') {
              const log: ExtendedAuditLog = {
                ...data.log,
                user_name: `User ${data.log.user_id?.slice(0, 8) || 'Unknown'}`,
                user_email: `user-${data.log.user_id?.slice(0, 8) || 'unknown'}@example.com`,
                message: `${data.log.action} operation on ${data.log.resource_type} ${data.log.resource_id}`,
                severity: data.log.severity || "INFO",
                action: data.log.action,
                timestamp: data.log.timestamp || new Date().toISOString(),
              }

              setLogs(prevLogs => {
                const newLogs = [log, ...prevLogs].slice(0, 100) // Keep only last 100 logs
                return newLogs
              })
            } else if (data.type === 'ping') {
              // Respond to ping with pong
              ws.send(JSON.stringify({ type: 'pong' }))
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionError('Connection error occurred')
        setIsConnected(false)
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        if (event.code !== 1000) { // Not a normal closure
          setConnectionError('Connection lost. Click Connect to retry.')
        }
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionError('Failed to establish connection')
    }
  }

  const disconnect = () => {
    if (websocketRef.current) {
      websocketRef.current.close(1000, 'User disconnected')
      websocketRef.current = null
    }
    setIsConnected(false)
    setConnectionError(null)
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
      if (websocketRef.current) {
        websocketRef.current.close()
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

        {/* Error Message */}
        {connectionError && (
          <Box mt={2} p={2} bg="red.50" borderRadius="md">
            <Text fontSize="sm" color="red.600">
              {connectionError}
            </Text>
          </Box>
        )}

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
                        IP: {log.ip_address || "N/A"}
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