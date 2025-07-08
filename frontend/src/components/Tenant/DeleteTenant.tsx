import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"

import { type TenantPublic, TenantsService } from "../../client"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
} from "../ui/dialog"
import useCustomToast from "../../hooks/useCustomToast"

interface DeleteTenantProps {
  tenant: TenantPublic
  isOpen: boolean
  onClose: () => void
}

const DeleteTenant = ({ tenant, isOpen, onClose }: DeleteTenantProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteTenant = async (tenantId: string) => {
    await TenantsService.deleteTenant({ tenantId })
  }

  const mutation = useMutation({
    mutationFn: deleteTenant,
    onSuccess: () => {
      showSuccessToast("The tenant was deleted successfully")
      onClose()
    },
    onError: () => {
      showErrorToast("An error occurred while deleting the tenant")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tenants"] })
    },
  })

  const onSubmit = async () => {
    mutation.mutate(tenant.id)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      role="alertdialog"
      open={isOpen}
      onOpenChange={({ open }) => !open && onClose()}
    >
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Delete Tenant</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              Are you sure you want to delete tenant <strong>"{tenant.name}"</strong> (Code: {tenant.code})?
            </Text>
            <Text mb={4} color="red.600" fontWeight="medium">
              This action cannot be undone. All data associated with this tenant will be permanently deleted.
            </Text>
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
              colorPalette="red"
              type="submit"
              loading={isSubmitting}
            >
              Delete
            </Button>
          </DialogFooter>
          <DialogCloseTrigger />
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default DeleteTenant 