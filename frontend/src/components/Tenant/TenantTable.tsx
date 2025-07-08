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
import { FiEdit, FiEye, FiSearch, FiTrash2 } from "react-icons/fi"

import type { TenantPublic } from "../../client/types.gen"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "../ui/pagination"
import { SkeletonText } from "../ui/skeleton"
import TenantDetails from "./TenantDetails"
import TenantFilters from "./TenantFilters"
import AddTenant from "./AddTenant"
import EditTenant from "./EditTenant"
import DeleteTenant from "./DeleteTenant"

const PER_PAGE = 10

// Mock data for demo - replace with actual API call
const mockTenants = {
  data: [
    {
      id: "tenant-1",
      name: "Acme Corporation",
      description: "Leading provider of innovative solutions",
      code: "ACME",
      status: "active",
      created_at: "2024-01-15T10:30:00Z",
      updated_at: "2024-01-15T10:30:00Z",
    },
    {
      id: "tenant-2",
      name: "Global Tech Solutions",
      description: "Technology consulting and services",
      code: "GTS",
      status: "active",
      created_at: "2024-01-10T14:20:00Z",
      updated_at: "2024-01-20T09:15:00Z",
    },
    {
      id: "tenant-3",
      name: "StartupCo",
      description: "Innovative startup in the fintech space",
      code: "STARTUP",
      status: "inactive",
      created_at: "2024-01-05T08:45:00Z",
      updated_at: "2024-01-18T16:30:00Z",
    },
    {
      id: "tenant-4",
      name: "Enterprise Solutions Ltd",
      description: "Enterprise software solutions provider",
      code: "ESLLTD",
      status: "active",
      created_at: "2024-01-12T11:00:00Z",
      updated_at: "2024-01-22T13:45:00Z",
    },
    {
      id: "tenant-5",
      name: "Digital Innovations Inc",
      description: "Digital transformation consultancy",
      code: "DIGINC",
      status: "active",
      created_at: "2024-01-08T09:30:00Z",
      updated_at: "2024-01-19T10:20:00Z",
    },
  ],
  count: 5,
} as { data: TenantPublic[]; count: number }

interface TenantFiltersType {
  search?: string
  status?: string
}

function getTenantsQueryOptions({ page, filters }: { page: number; filters?: TenantFiltersType }) {
  return {
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Apply filters to mock data
      let filteredData = [...mockTenants.data]
      
      if (filters?.search) {
        const searchTerm = filters.search.toLowerCase()
        filteredData = filteredData.filter(tenant =>
          tenant.name.toLowerCase().includes(searchTerm) ||
          tenant.code.toLowerCase().includes(searchTerm) ||
          tenant.description?.toLowerCase().includes(searchTerm)
        )
      }
      
      if (filters?.status && filters.status !== "all") {
        filteredData = filteredData.filter(tenant => tenant.status === filters.status)
      }
      
      // Pagination
      const start = (page - 1) * PER_PAGE
      const end = start + PER_PAGE
      const paginatedData = filteredData.slice(start, end)
      
      return {
        data: paginatedData,
        count: filteredData.length,
      }
    },
    queryKey: ["tenants", { page, filters }],
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "active":
      return "green"
    case "inactive":
      return "red"
    default:
      return "gray"
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

function TenantTable() {
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<TenantFiltersType>({})
  const [selectedTenant, setSelectedTenant] = useState<TenantPublic | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [editingTenant, setEditingTenant] = useState<TenantPublic | null>(null)
  const [deletingTenant, setDeletingTenant] = useState<TenantPublic | null>(null)

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getTenantsQueryOptions({ page, filters }),
    placeholderData: (prevData) => prevData,
  })

  const tenants = data?.data ?? []
  const count = data?.count ?? 0

  const handleFiltersChange = (newFilters: TenantFiltersType) => {
    setFilters(newFilters)
    setPage(1)
  }

  const handleFiltersReset = () => {
    setFilters({})
    setPage(1)
  }

  const handleViewDetails = (tenant: TenantPublic) => {
    setSelectedTenant(tenant)
    setShowDetails(true)
  }

  const handleEdit = (tenant: TenantPublic) => {
    setEditingTenant(tenant)
  }

  const handleDelete = (tenant: TenantPublic) => {
    setDeletingTenant(tenant)
  }

  if (isLoading && !data) {
    return (
      <Box>
        <TenantFilters
          onFiltersChange={handleFiltersChange}
          onReset={handleFiltersReset}
          loading={isLoading}
        />
        <Table.Root size={{ base: "sm", md: "md" }}>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Name</Table.ColumnHeader>
              <Table.ColumnHeader>Code</Table.ColumnHeader>
              <Table.ColumnHeader>Status</Table.ColumnHeader>
              <Table.ColumnHeader>Created</Table.ColumnHeader>
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
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Box>
    )
  }

  if (tenants.length === 0) {
    return (
      <Box>
        <TenantFilters
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
              <EmptyState.Title>No tenants found</EmptyState.Title>
              <EmptyState.Description>
                Try adjusting your search filters or add your first tenant
              </EmptyState.Description>
            </VStack>
          </EmptyState.Content>
        </EmptyState.Root>
      </Box>
    )
  }

  return (
    <Box>
      <TenantFilters
        onFiltersChange={handleFiltersChange}
        onReset={handleFiltersReset}
        loading={isLoading}
      />

      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="sm" color="gray.600">
          Showing {tenants.length} of {count} tenants
        </Text>
        <HStack>
          <AddTenant />
        </HStack>
      </Flex>

      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Name</Table.ColumnHeader>
            <Table.ColumnHeader>Code</Table.ColumnHeader>
            <Table.ColumnHeader>Description</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Created</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {tenants.map((tenant) => (
            <Table.Row key={tenant.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell>
                <VStack align="start" gap={1}>
                  <Text fontSize="sm" fontWeight="medium">
                    {tenant.name}
                  </Text>
                </VStack>
              </Table.Cell>
              <Table.Cell>
                <Badge variant="outline" size="sm">
                  {tenant.code}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <Tooltip.Root>
                  <Tooltip.Trigger>
                    <Text fontSize="sm" truncate maxW="200px">
                      {tenant.description || "No description"}
                    </Text>
                  </Tooltip.Trigger>
                  <Tooltip.Content>
                    {tenant.description || "No description"}
                  </Tooltip.Content>
                </Tooltip.Root>
              </Table.Cell>
              <Table.Cell>
                <Badge
                  colorScheme={getStatusColor(tenant.status || "inactive")}
                  size="sm"
                >
                  {tenant.status}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <Text fontSize="sm" color="gray.600">
                  {formatDate(tenant.created_at)}
                </Text>
              </Table.Cell>
              <Table.Cell>
                <HStack>
                  <Tooltip.Root>
                    <Tooltip.Trigger>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetails(tenant)}
                        aria-label="View details"
                      >
                        <FiEye />
                      </IconButton>
                    </Tooltip.Trigger>
                    <Tooltip.Content>
                      View details
                    </Tooltip.Content>
                  </Tooltip.Root>
                  <Tooltip.Root>
                    <Tooltip.Trigger>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(tenant)}
                        aria-label="Edit tenant"
                      >
                        <FiEdit />
                      </IconButton>
                    </Tooltip.Trigger>
                    <Tooltip.Content>
                      Edit tenant
                    </Tooltip.Content>
                  </Tooltip.Root>
                  <Tooltip.Root>
                    <Tooltip.Trigger>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        colorScheme="red"
                        onClick={() => handleDelete(tenant)}
                        aria-label="Delete tenant"
                      >
                        <FiTrash2 />
                      </IconButton>
                    </Tooltip.Trigger>
                    <Tooltip.Content>
                      Delete tenant
                    </Tooltip.Content>
                  </Tooltip.Root>
                </HStack>
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

      {selectedTenant && (
        <TenantDetails
          tenant={selectedTenant}
          isOpen={showDetails}
          onClose={() => {
            setShowDetails(false)
            setSelectedTenant(null)
          }}
        />
      )}

      {editingTenant && (
        <EditTenant
          tenant={editingTenant}
          isOpen={!!editingTenant}
          onClose={() => setEditingTenant(null)}
        />
      )}

      {deletingTenant && (
        <DeleteTenant
          tenant={deletingTenant}
          isOpen={!!deletingTenant}
          onClose={() => setDeletingTenant(null)}
        />
      )}
    </Box>
  )
}

export default TenantTable 