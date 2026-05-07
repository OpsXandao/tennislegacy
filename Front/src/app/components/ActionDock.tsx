interface ActionDockProps {
  children: React.ReactNode
  className?: string
}

export function ActionDock({ children, className = '' }: ActionDockProps) {
  return (
    <div className={`sticky bottom-0 z-20 mt-6 border-t app-divider app-overlay py-4 backdrop-blur-sm ${className}`}>
      <div className="mx-auto w-full max-w-7xl border app-divider app-panel-elevated p-3 shadow-[0_-8px_24px_rgba(0,0,0,0.18)]">
        {children}
      </div>
    </div>
  )
}
