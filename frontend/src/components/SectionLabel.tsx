import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

interface SectionLabelProps {
  children: ReactNode
  className?: string
}

export function SectionLabel({ children, className }: SectionLabelProps) {
  return (
    <h3
      className={cn(
        "font-mono text-[10px] font-medium tracking-[0.14em] text-muted-foreground uppercase",
        className
      )}
    >
      {children}
    </h3>
  )
}
