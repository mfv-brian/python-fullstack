import {
  Badge,
  Box,
  Button,
  Card,
  Grid,
  GridItem,
  HStack,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import {
  FiArchive,
  FiDatabase,
  FiHardDrive,
  FiRefreshCw,
  FiSave,
  FiSettings,
  FiTrash2,
} from "react-icons/fi"

import type { AuditSeverity } from "../../client/types.gen"
import { Checkbox } from "../ui/checkbox"
import { Field } from "../ui/field"
import { NativeSelectField, NativeSelectRoot } from "../ui/native-select"

// Define the settings type
interface AuditLogSettings {
  retention_days: number;
  enable_archival: boolean;
  archival_threshold_days: number;
  enable_compression: boolean;
  backup_frequency: 'daily' | 'weekly' | 'monthly';
  enable_real_time_monitoring: boolean;
  log_level: AuditSeverity;
  enable_export: boolean;
  max_export_records: number;
  enable_data_masking: boolean;
  tenant_isolation: boolean;
}

const AuditLogSettings = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty },
  } = useForm<AuditLogSettings>({
    defaultValues: {
      retention_days: 90,
      enable_archival: true,
      archival_threshold_days: 30,
      enable_compression: true,
      backup_frequency: "weekly",
      enable_real_time_monitoring: true,
      log_level: "INFO",
      enable_export: true,
      max_export_records: 10000,
      enable_data_masking: false,
      tenant_isolation: true,
    },
  })

  const archivalEnabled = watch("enable_archival")
  const compressionEnabled = watch("enable_compression")

  const onSubmit = async (data: AuditLogSettings) => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      console.log("Settings saved:", data)
      setLastUpdated(new Date().toLocaleString())
    } catch (error) {
      console.error("Failed to save settings:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleArchiveNow = async () => {
    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      console.log("Manual archival triggered")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCleanupOldLogs = async () => {
    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      console.log("Old logs cleanup triggered")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box>
      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack gap={6} align="stretch">
          {/* Data Retention Settings */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiDatabase />
                <Text fontSize="lg" fontWeight="bold">
                  Data Retention
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                  <GridItem>
                    <Field
                      label="Retention Period (Days)"
                      helperText="How long to keep logs before deletion"
                      invalid={!!errors.retention_days}
                      errorText={errors.retention_days?.message}
                    >
                      <Input
                        type="number"
                        {...register("retention_days", {
                          required: "Retention days is required",
                          min: { value: 1, message: "Must be at least 1 day" },
                          max: { value: 3650, message: "Cannot exceed 3650 days (10 years)" },
                        })}
                        placeholder="90"
                      />
                    </Field>
                  </GridItem>
                </Grid>

                <HStack p={3} bg="yellow.50" borderRadius="md">
                  <Text fontSize="sm" color="yellow.800">
                    <strong>Warning:</strong> Logs older than the retention period will be permanently deleted.
                    This action cannot be undone.
                  </Text>
                </HStack>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Archival Settings */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiArchive />
                <Text fontSize="lg" fontWeight="bold">
                  Data Archival
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Field>
                  <Checkbox
                    checked={archivalEnabled}
                    onCheckedChange={({ checked }) => setValue("enable_archival", !!checked)}
                  >
                    Enable automatic archival
                  </Checkbox>
                </Field>

                {archivalEnabled && (
                  <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                    <GridItem>
                      <Field
                        label="Archive After (Days)"
                        helperText="Move logs to cold storage after this period"
                        invalid={!!errors.archival_threshold_days}
                        errorText={errors.archival_threshold_days?.message}
                      >
                        <Input
                          type="number"
                          {...register("archival_threshold_days", {
                            required: archivalEnabled ? "Archival days is required" : false,
                            min: { value: 1, message: "Must be at least 1 day" },
                          })}
                          placeholder="30"
                        />
                      </Field>
                    </GridItem>
                  </Grid>
                )}

                <HStack p={3} bg="blue.50" borderRadius="md">
                  <Text fontSize="sm" color="blue.800">
                    Archived logs are moved to cold storage for cost-effective long-term retention.
                    They can still be accessed but with higher latency.
                  </Text>
                </HStack>

                <HStack>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleArchiveNow}
                    loading={isLoading}
                  >
                    <FiArchive />
                    Archive Now
                  </Button>
                </HStack>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Storage Optimization */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiHardDrive />
                <Text fontSize="lg" fontWeight="bold">
                  Storage Optimization
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Field>
                  <Checkbox
                    checked={compressionEnabled}
                    onCheckedChange={({ checked }) => setValue("enable_compression", !!checked)}
                  >
                    Enable data compression
                  </Checkbox>
                </Field>

                <HStack p={3} bg="green.50" borderRadius="md">
                  <Text fontSize="sm" color="green.800">
                    Compression reduces storage costs by up to 70% with minimal impact on performance.
                  </Text>
                </HStack>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Backup Settings */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiRefreshCw />
                <Text fontSize="lg" fontWeight="bold">
                  Backup & Recovery
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                  <GridItem>
                    <Field label="Backup Frequency">
                      <NativeSelectRoot>
                        <NativeSelectField
                          {...register("backup_frequency")}
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                        </NativeSelectField>
                      </NativeSelectRoot>
                    </Field>
                  </GridItem>
                </Grid>

                <HStack p={3} bg="purple.50" borderRadius="md">
                  <Text fontSize="sm" color="purple.800">
                    Automated backups ensure data recovery in case of system failures.
                    Backups are encrypted and stored in geographically distributed locations.
                  </Text>
                </HStack>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Additional Settings */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiSettings />
                <Text fontSize="lg" fontWeight="bold">
                  Additional Settings
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                  <GridItem>
                    <Field>
                      <Checkbox
                        checked={watch("enable_real_time_monitoring")}
                        onCheckedChange={({ checked }) => setValue("enable_real_time_monitoring", !!checked)}
                      >
                        Enable real-time monitoring
                      </Checkbox>
                    </Field>
                  </GridItem>
                  <GridItem>
                    <Field>
                      <Checkbox
                        checked={watch("enable_export")}
                        onCheckedChange={({ checked }) => setValue("enable_export", !!checked)}
                      >
                        Enable data export
                      </Checkbox>
                    </Field>
                  </GridItem>
                  <GridItem>
                    <Field>
                      <Checkbox
                        checked={watch("enable_data_masking")}
                        onCheckedChange={({ checked }) => setValue("enable_data_masking", !!checked)}
                      >
                        Enable data masking
                      </Checkbox>
                    </Field>
                  </GridItem>
                  <GridItem>
                    <Field>
                      <Checkbox
                        checked={watch("tenant_isolation")}
                        onCheckedChange={({ checked }) => setValue("tenant_isolation", !!checked)}
                      >
                        Enable tenant isolation
                      </Checkbox>
                    </Field>
                  </GridItem>
                </Grid>

                <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                  <GridItem>
                    <Field
                      label="Log Level"
                      helperText="Minimum severity level to log"
                    >
                      <NativeSelectRoot>
                        <NativeSelectField
                          {...register("log_level")}
                        >
                          <option value="INFO">Info</option>
                          <option value="WARNING">Warning</option>
                          <option value="ERROR">Error</option>
                          <option value="CRITICAL">Critical</option>
                        </NativeSelectField>
                      </NativeSelectRoot>
                    </Field>
                  </GridItem>
                  <GridItem>
                    <Field
                      label="Max Export Records"
                      helperText="Maximum number of records for export"
                      invalid={!!errors.max_export_records}
                      errorText={errors.max_export_records?.message}
                    >
                      <Input
                        type="number"
                        {...register("max_export_records", {
                          required: "Max export records is required",
                          min: { value: 1, message: "Must be at least 1" },
                          max: { value: 1000000, message: "Cannot exceed 1,000,000 records" },
                        })}
                        placeholder="10000"
                      />
                    </Field>
                  </GridItem>
                </Grid>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Data Management Actions */}
          <Card.Root>
            <Card.Header>
              <HStack>
                <FiSettings />
                <Text fontSize="lg" fontWeight="bold">
                  Data Management
                </Text>
              </HStack>
            </Card.Header>
            <Card.Body>
              <VStack gap={4} align="stretch">
                <Text fontSize="sm" color="gray.600">
                  Perform immediate data management operations:
                </Text>

                <HStack wrap="wrap" gap={3}>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCleanupOldLogs}
                    loading={isLoading}
                    colorPalette="red"
                  >
                    <FiTrash2 />
                    Cleanup Old Logs
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    loading={isLoading}
                  >
                    <FiRefreshCw />
                    Optimize Storage
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    loading={isLoading}
                  >
                    <FiDatabase />
                    Rebuild Indexes
                  </Button>
                </HStack>

                <HStack p={3} bg="red.50" borderRadius="md">
                  <Text fontSize="sm" color="red.800">
                    <strong>Caution:</strong> Data management operations may temporarily impact system performance.
                    It's recommended to run these during maintenance windows.
                  </Text>
                </HStack>
              </VStack>
            </Card.Body>
          </Card.Root>

          {/* Save Settings */}
          <Card.Root>
            <Card.Body>
              <HStack justify="space-between" align="center">
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" fontWeight="medium">
                    Settings Status
                  </Text>
                  {lastUpdated ? (
                    <Text fontSize="xs" color="gray.600">
                      Last updated: {lastUpdated}
                    </Text>
                  ) : (
                    <Text fontSize="xs" color="gray.600">
                      No changes saved yet
                    </Text>
                  )}
                  {isDirty && (
                    <Badge colorScheme="yellow" size="sm">
                      Unsaved Changes
                    </Badge>
                  )}
                </VStack>

                <Button
                  type="submit"
                  variant="solid"
                  loading={isLoading}
                  disabled={!isDirty}
                >
                  <FiSave />
                  Save Settings
                </Button>
              </HStack>
            </Card.Body>
          </Card.Root>
        </VStack>
      </form>
    </Box>
  )
}

export default AuditLogSettings 