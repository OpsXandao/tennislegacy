type FrontendErrorPayload = {
  kind: string
  message: string
  stack?: string | null
  url?: string
  user_agent?: string
  component_stack?: string | null
  extra?: Record<string, unknown>
}

let lastSentAt = 0

export async function reportError(payload: FrontendErrorPayload): Promise<void> {
  const now = Date.now()
  if (now - lastSentAt < 300) return
  lastSentAt = now

  try {
    await fetch('/api/logs/frontend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...payload,
        url: payload.url ?? window.location.href,
        user_agent: payload.user_agent ?? window.navigator.userAgent,
      }),
    })
  } catch {
    // Evita loop de erro ao falhar o envio do proprio log.
  }
}
