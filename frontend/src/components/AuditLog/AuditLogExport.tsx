import {
  Button,
  ButtonGroup,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiDownload, FiFile, FiFileText } from "react-icons/fi"

import type { AuditAction, AuditSeverity } from "../../client/types.gen"
import { useAuditLogExport } from "../../hooks/useAuditLogs"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "../ui/dialog"

// Use the same interface as defined in AuditLogTable
interface AuditLogFilters {
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

interface AuditLogExportProps {
  isOpen: boolean
  onClose: () => void
  filters?: AuditLogFilters
}

const AuditLogExport = ({ isOpen, onClose, filters }: AuditLogExportProps) => {
  const [selectedFormat, setSelectedFormat] = useState<"JSON" | "CSV">("JSON")
  const exportMutation = useAuditLogExport()

  const handleExport = async () => {
    try {
      await exportMutation.mutateAsync({ format: selectedFormat, filters })
      onClose()
    } catch (error) {
      console.error("Export failed:", error)
      // You might want to show a toast notification here
    }
  }

  return (
    <DialogRoot
      size={{ base: "sm", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export Audit Logs</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <VStack gap={4} align="stretch">
            <Text fontSize="sm" color="gray.600">
              Choose the format for exporting your audit logs. The export will include
              all logs matching your current filter criteria.
            </Text>

            {/* Format Selection */}
            <VStack gap={3} align="stretch">
              <Text fontSize="sm" fontWeight="medium">
                Export Format
              </Text>
              <ButtonGroup size="sm" variant="outline" attached={false}>
                <Button
                  variant={selectedFormat === "JSON" ? "solid" : "outline"}
                  onClick={() => setSelectedFormat("JSON")}
                >
                  <FiFile />
                  JSON
                </Button>
                <Button
                  variant={selectedFormat === "CSV" ? "solid" : "outline"}
                  onClick={() => setSelectedFormat("CSV")}
                >
                  <FiFileText />
                  CSV
                </Button>
              </ButtonGroup>
            </VStack>

            {/* Format Description */}
            <VStack gap={2} align="stretch" p={3} bg="gray.50" borderRadius="md">
              <Text fontSize="sm" fontWeight="medium">
                {selectedFormat} Format
              </Text>
              <Text fontSize="xs" color="gray.600">
                {selectedFormat === "JSON" 
                  ? "Export as structured JSON format, ideal for programmatic processing and maintaining data relationships."
                  : "Export as comma-separated values, ideal for spreadsheet applications like Excel or Google Sheets."
                }
              </Text>
            </VStack>

            {/* Filter Summary */}
            {filters && Object.keys(filters).length > 0 && (
              <VStack gap={2} align="stretch" p={3} bg="blue.50" borderRadius="md">
                <Text fontSize="sm" fontWeight="medium">
                  Active Filters
                </Text>
                <VStack gap={1} align="stretch">
                  {filters.search && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">Search:</Text>
                      <Text fontSize="xs" fontWeight="medium">{filters.search}</Text>
                    </HStack>
                  )}
                  {filters.action && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">Action:</Text>
                      <Text fontSize="xs" fontWeight="medium">{filters.action}</Text>
                    </HStack>
                  )}
                  {filters.severity && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">Severity:</Text>
                      <Text fontSize="xs" fontWeight="medium">{filters.severity}</Text>
                    </HStack>
                  )}
                  {filters.resource_type && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">Resource:</Text>
                      <Text fontSize="xs" fontWeight="medium">{filters.resource_type}</Text>
                    </HStack>
                  )}
                  {filters.start_date && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">From:</Text>
                      <Text fontSize="xs" fontWeight="medium">
                        {new Date(filters.start_date).toLocaleDateString()}
                      </Text>
                    </HStack>
                  )}
                  {filters.end_date && (
                    <HStack justify="space-between">
                      <Text fontSize="xs" color="gray.600">To:</Text>
                      <Text fontSize="xs" fontWeight="medium">
                        {new Date(filters.end_date).toLocaleDateString()}
                      </Text>
                    </HStack>
                  )}
                </VStack>
              </VStack>
            )}
          </VStack>
        </DialogBody>
        <DialogFooter gap={2}>
          <DialogActionTrigger asChild>
            <Button
              variant="subtle"
              colorPalette="gray"
              disabled={exportMutation.isPending}
            >
              Cancel
            </Button>
          </DialogActionTrigger>
          <Button
            variant="solid"
            onClick={handleExport}
            loading={exportMutation.isPending}
          >
            <FiDownload />
            {exportMutation.isPending ? "Exporting..." : "Export"}
          </Button>
        </DialogFooter>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AuditLogExport 