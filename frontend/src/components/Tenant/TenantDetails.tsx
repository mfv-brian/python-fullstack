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
import { FiCalendar, FiCode, FiInfo, FiTag } from "react-icons/fi"

import type { TenantPublic } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../ui/dialog"

interface TenantDetailsProps {
  tenant: TenantPublic
  isOpen: boolean
  onClose: () => void
}

const TenantDetails = ({ tenant, isOpen, onClose }: TenantDetailsProps) => {
  const formatTimestamp = (timestamp: string | undefined) => {
    if (!timestamp) return "N/A";
    return new Date(timestamp).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "green"
      case "inactive":
        return "red"
      case "unknown":
        return "yellow"
      default:
        return "gray"
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
          <DialogTitle>Tenant Details</DialogTitle>
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
                      <FiTag />
                      <Text fontSize="sm" fontWeight="medium">
                        Name
                      </Text>
                    </HStack>
                    <Text fontSize="lg" fontWeight="semibold">
                      {tenant.name}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiCode />
                      <Text fontSize="sm" fontWeight="medium">
                        Code
                      </Text>
                    </HStack>
                    <Code fontSize="md" p={2} borderRadius="md">
                      {tenant.code}
                    </Code>
                  </VStack>
                </GridItem>
                <GridItem colSpan={2}>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiInfo />
                      <Text fontSize="sm" fontWeight="medium">
                        Description
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {tenant.description || "No description provided"}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Status
                    </Text>
                    <Badge
                      colorScheme={getStatusColor(tenant.status ?? "unknown")}
                      size="md"
                      px={3}
                      py={1}
                    >
                      {tenant.status ?? "unknown"}
                    </Badge>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <Text fontSize="sm" fontWeight="medium">
                      Tenant ID
                    </Text>
                    <Code fontSize="sm" p={2} borderRadius="md">
                      {tenant.id}
                    </Code>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* Timestamps */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                Timeline
              </Text>
              <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiCalendar />
                      <Text fontSize="sm" fontWeight="medium">
                        Created At
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {formatTimestamp(tenant.created_at)}
                    </Text>
                  </VStack>
                </GridItem>
                <GridItem>
                  <VStack align="start" gap={2}>
                    <HStack>
                      <FiCalendar />
                      <Text fontSize="sm" fontWeight="medium">
                        Last Updated
                      </Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {formatTimestamp(tenant.updated_at)}
                    </Text>
                  </VStack>
                </GridItem>
              </Grid>
            </Box>

            {/* Configuration Summary */}
            <Box>
              <Text fontSize="lg" fontWeight="bold" mb={4}>
                Configuration Summary
              </Text>
              <VStack align="stretch" gap={3}>
                <Box p={3} bg="blue.50" borderRadius="md">
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="medium">
                      Tenant Code
                    </Text>
                    <Badge variant="outline" size="sm">
                      {tenant.code}
                    </Badge>
                  </HStack>
                </Box>
                <Box p={3} bg="green.50" borderRadius="md">
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="medium">
                      Status
                    </Text>
                    <Badge
                      colorScheme={getStatusColor(tenant.status ?? "unknown")}
                      size="sm"
                    >
                      {tenant.status ?? "unknown"}
                    </Badge>
                  </HStack>
                </Box>
                <Box p={3} bg="purple.50" borderRadius="md">
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="medium">
                      Tenant Type
                    </Text>
                    <Badge variant="outline" size="sm">
                      Standard
                    </Badge>
                  </HStack>
                </Box>
              </VStack>
            </Box>
          </VStack>
        </DialogBody>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default TenantDetails 