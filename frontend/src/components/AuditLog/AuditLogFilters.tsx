import {
  Box,
  Button,
  Grid,
  GridItem,
  HStack,
  Input,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiFilter, FiSearch, FiX } from "react-icons/fi"

import type { AuditLogFilters } from "../../client/types.gen"
import { Field } from "../ui/field"
import { InputGroup } from "../ui/input-group"
import { NativeSelectField, NativeSelectRoot } from "../ui/native-select"

interface AuditLogFiltersProps {
  onFiltersChange: (filters: AuditLogFilters) => void
  onReset: () => void
  loading?: boolean
}

const AuditLogFilters = ({ onFiltersChange, onReset, loading }: AuditLogFiltersProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const { register, handleSubmit, reset } = useForm<AuditLogFilters>()

  const onSubmit = (data: AuditLogFilters) => {
    // Clean up empty values
    const cleanData = Object.fromEntries(
      Object.entries(data).filter(([_, value]) => value !== "" && value !== undefined)
    )
    onFiltersChange(cleanData)
  }

  const handleReset = () => {
    reset()
    onReset()
  }

  return (
    <Box p={4} bg="bg.subtle" borderRadius="md" mb={4}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <VStack gap={4} align="stretch">
          {/* Search Bar */}
          <Field>
            <InputGroup startElement={<FiSearch />}>
              <Input
                placeholder="Search logs (message, user, resource, etc.)"
                {...register("search")}
                size="lg"
              />
            </InputGroup>
          </Field>

          {/* Toggle Advanced Filters */}
          <HStack justify="space-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              <FiFilter />
              Advanced Filters
            </Button>
            <HStack>
              <Button
                type="submit"
                size="sm"
                loading={loading}
              >
                <FiSearch />
                Search
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleReset}
              >
                <FiX />
                Reset
              </Button>
            </HStack>
          </HStack>

          {/* Advanced Filters */}
          {isExpanded && (
            <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
              <GridItem colSpan={2}>
                <Field label="Date Range">
                  <HStack>
                    <Input
                      type="datetime-local"
                      {...register("start_date")}
                      placeholder="Start date"
                      size="sm"
                    />
                    <Box px={2} color="gray.500">
                      to
                    </Box>
                    <Input
                      type="datetime-local"
                      {...register("end_date")}
                      placeholder="End date"
                      size="sm"
                    />
                  </HStack>
                </Field>
              </GridItem>

              <GridItem>
                <Field label="Action">
                  <NativeSelectRoot size="sm">
                    <NativeSelectField
                      {...register("action")}
                    >
                      <option value="">All Actions</option>
                      <option value="CREATE">Create</option>
                      <option value="UPDATE">Update</option>
                      <option value="DELETE">Delete</option>
                      <option value="VIEW">View</option>
                      <option value="LOGIN">Login</option>
                      <option value="LOGOUT">Logout</option>
                      <option value="EXPORT">Export</option>
                      <option value="IMPORT">Import</option>
                    </NativeSelectField>
                  </NativeSelectRoot>
                </Field>
              </GridItem>

              <GridItem>
                <Field label="Resource Type">
                  <NativeSelectRoot size="sm">
                    <NativeSelectField
                      {...register("resource_type")}
                    >
                      <option value="">All Resources</option>
                      <option value="user">User</option>
                      <option value="item">Item</option>
                      <option value="order">Order</option>
                      <option value="product">Product</option>
                      <option value="setting">Setting</option>
                    </NativeSelectField>
                  </NativeSelectRoot>
                </Field>
              </GridItem>

              <GridItem>
                <Field label="Severity">
                  <NativeSelectRoot size="sm">
                    <NativeSelectField
                      {...register("severity")}
                    >
                      <option value="">All Severities</option>
                      <option value="INFO">Info</option>
                      <option value="WARNING">Warning</option>
                      <option value="ERROR">Error</option>
                      <option value="CRITICAL">Critical</option>
                    </NativeSelectField>
                  </NativeSelectRoot>
                </Field>
              </GridItem>

              <GridItem>
                <Field label="User ID">
                  <Input
                    {...register("user_id")}
                    placeholder="Enter user ID"
                    size="sm"
                  />
                </Field>
              </GridItem>

              <GridItem>
                <Field label="Tenant ID">
                  <Input
                    {...register("tenant_id")}
                    placeholder="Enter tenant ID"
                    size="sm"
                  />
                </Field>
              </GridItem>
            </Grid>
          )}
        </VStack>
      </form>
    </Box>
  )
}

export default AuditLogFilters 