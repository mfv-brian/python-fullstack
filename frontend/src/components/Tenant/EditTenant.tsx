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
import { useEffect } from "react"

import { type TenantPublic, type TenantUpdate, TenantsService } from "../../client"
import type { ApiError } from "../../client/core/ApiError"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
} from "../ui/dialog"
import { Field } from "../ui/field"
import { NativeSelectField, NativeSelectRoot } from "../ui/native-select"

interface EditTenantProps {
  tenant: TenantPublic
  isOpen: boolean
  onClose: () => void
}

const EditTenant = ({ tenant, isOpen, onClose }: EditTenantProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TenantUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  useEffect(() => {
    if (isOpen && tenant) {
      reset({
        name: tenant.name,
        description: tenant.description,
        code: tenant.code,
        status: tenant.status,
      })
    }
  }, [isOpen, tenant, reset])

  const mutation = useMutation({
    mutationFn: (data: TenantUpdate) =>
      TenantsService.updateTenant({ tenantId: tenant.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Tenant updated successfully.")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] })
    },
  })

  const onSubmit: SubmitHandler<TenantUpdate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
    >
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Tenant</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the tenant details below.</Text>
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
                onClick={onClose}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              loading={isSubmitting}
            >
              Update
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditTenant 