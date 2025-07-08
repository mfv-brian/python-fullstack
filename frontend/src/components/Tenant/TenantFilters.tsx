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

import { Field } from "../ui/field"
import { InputGroup } from "../ui/input-group"
import { NativeSelectField, NativeSelectRoot } from "../ui/native-select"

interface TenantFilters {
  search?: string
  status?: string
}

interface TenantFiltersProps {
  onFiltersChange: (filters: TenantFilters) => void
  onReset: () => void
  loading?: boolean
}

const TenantFilters = ({ onFiltersChange, onReset, loading }: TenantFiltersProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const { register, handleSubmit, reset } = useForm<TenantFilters>()

  const onSubmit = (data: TenantFilters) => {
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
                placeholder="Search tenants by name, code, or description..."
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
              <GridItem>
                <Field label="Status">
                  <NativeSelectRoot size="sm">
                    <NativeSelectField
                      {...register("status")}
                    >
                      <option value="">All Status</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </NativeSelectField>
                  </NativeSelectRoot>
                </Field>
              </GridItem>
            </Grid>
          )}
        </VStack>
      </form>
    </Box>
  )
}

export default TenantFilters 