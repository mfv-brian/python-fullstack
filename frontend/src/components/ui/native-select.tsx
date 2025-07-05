import * as React from "react"

export interface NativeSelectRootProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg"
}

export const NativeSelectRoot = React.forwardRef<
  HTMLDivElement,
  NativeSelectRootProps
>(function NativeSelectRoot(props, ref) {
  const { children, size, ...rest } = props
  return (
    <div ref={ref} {...rest}>
      {children}
    </div>
  )
})

export interface NativeSelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const NativeSelectField = React.forwardRef<
  HTMLSelectElement,
  NativeSelectFieldProps
>(function NativeSelectField(props, ref) {
  const { children, ...rest } = props
  return (
    <select
      ref={ref}
      style={{
        width: "100%",
        padding: "8px 12px",
        border: "1px solid #e2e8f0",
        borderRadius: "6px",
        backgroundColor: "white",
        fontSize: "14px",
        outline: "none",
        cursor: "pointer",
      }}
      {...rest}
    >
      {children}
    </select>
  )
}) 