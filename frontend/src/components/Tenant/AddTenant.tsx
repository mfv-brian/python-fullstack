import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type TenantCreate, TenantsService } from "../../client"
import type { ApiError } from "../../client/core/ApiError"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"
import { useAuditLogger, createTenantAuditLog } from "../../utils/auditLog"
import useAuth from "../../hooks/useAuth"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"
import { NativeSelectField, NativeSelectRoot } from "../ui/native-select"

const AddTenant = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const { user: currentUser } = useAuth()
  const { logAction } = useAuditLogger()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<TenantCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      description: "",
      code: "",
      status: "active",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: TenantCreate) =>
      TenantsService.createTenant({ requestBody: data }),
    onSuccess: async (createdTenant) => {
      showSuccessToast("Tenant created successfully.")
      
      // Create audit log entry
      if (currentUser) {
        const auditData = createTenantAuditLog(
          "CREATE",
          createdTenant.id,
          currentUser.id,
          undefined, // No before state for creation
          {
            name: createdTenant.name,
            code: createdTenant.code,
            description: createdTenant.description,
            status: createdTenant.status,
            max_users: createdTenant.max_users,
            max_storage_gb: createdTenant.max_storage_gb,
          },
          "INFO"
        )
        await logAction(auditData)
      }
      
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] })
    },
  })

  const onSubmit: SubmitHandler<TenantCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-tenant" my={0}>
          <FaPlus fontSize="16px" />
          Add Tenant
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add Tenant</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new tenant.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Tenant Name"
              >
                <Input
                  id="name"
                  {...register("name", {
                    required: "Tenant name is required.",
                    minLength: {
                      value: 2,
                      message: "Name must be at least 2 characters",
                    },
                  })}
                  placeholder="Enter tenant name"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.code}
                errorText={errors.code?.message}
                label="Tenant Code"
                helperText="Unique identifier for the tenant (uppercase letters, numbers, and underscores only)"
              >
                <Input
                  id="code"
                  {...register("code", {
                    required: "Tenant code is required.",
                    pattern: {
                      value: /^[A-Z0-9_]+$/,
                      message: "Code must contain only uppercase letters, numbers, and underscores",
                    },
                    minLength: {
                      value: 2,
                      message: "Code must be at least 2 characters",
                    },
                    maxLength: {
                      value: 20,
                      message: "Code must be at most 20 characters",
                    },
                  })}
                  placeholder="TENANT_CODE"
                  type="text"
                  style={{ textTransform: "uppercase" }}
                />
              </Field>

              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  id="description"
                  {...register("description")}
                  placeholder="Brief description of the tenant"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.status}
                errorText={errors.status?.message}
                label="Status"
              >
                <NativeSelectRoot>
                  <NativeSelectField
                    {...register("status", {
                      required: "Status is required",
                    })}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </NativeSelectField>
                </NativeSelectRoot>
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddTenant 