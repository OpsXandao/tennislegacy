# TennisLegacy — Design System (Arcade Retro Neon)

Este documento define os tokens visuais, componentes e diretrizes para o frontend do TennisLegacy.

## Paleta de Cores (Neon Tokens)

| Nome | Hex | Uso |
|---|---|---|
| **Background** | `#0a0a0a` | Fundo principal da aplicação |
| **Card Bg** | `#1a1a2e` | Fundo de containers e cards |
| **Neon Primary** | `#00ff88` | Ações principais, sucesso, ATP |
| **Neon Danger** | `#ff0055` | Ações destrutivas, erro, WTA |
| **Neon Gold** | `#ffe600` | Destaques, rankings top, GS |
| **Neon Info** | `#00e5ff` | Informações, detalhes técnicos |
| **Neon Muted** | `#4a4e69` | Textos secundários, bordas inativas |

## Tipografia

- **Títulos:** `Press Start 2P` (Pixel art style)
- **Corpo / Stats:** `Share Tech Mono` (Monospace futurista)

## Efeitos Visuais

### Scanlines (Overlay)
Um gradiente linear repetitivo para simular monitores CRT.
```css
.scanlines {
  background: linear-gradient(
    rgba(18, 16, 16, 0) 50%,
    rgba(0, 0, 0, 0.25) 50%
  );
  background-size: 100% 4px;
  z-index: 10;
  pointer-events: none;
}
```

### Neon Glow
Todas as cores neon devem ter um `box-shadow` ou `text-shadow`.
```css
.glow-primary {
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
  border: 1px solid #00ff88;
}
```

## Componentes (Tailwind Class Examples)

### NeonButton
```html
<button class="bg-transparent border-2 border-neon-primary text-neon-primary px-4 py-2 font-pixel hover:bg-neon-primary hover:text-black transition-all shadow-[0_0_10px_rgba(0,255,136,0.3)]">
  START GAME
</button>
```

### NeonCard
```html
<div class="bg-card-bg border border-neon-muted p-4 rounded-sm shadow-[0_0_15px_rgba(0,0,0,0.5)]">
  <!-- Content -->
</div>
```

### PixelBar (Health/Energy)
Barra composta por pequenos blocos de 4px ou 8px.
- `[####------]` (60% energia)

## Hierarquia de Torneios (Tiers)

| Tier | Cor Neon |
|---|---|
| Grand Slam | Gold |
| Masters 1000 | Info (Cyan) |
| ATP 500 / WTA 500 | Primary (Green) |
| ATP 250 / WTA 250 | Muted |
| Challengers / ITFs | Danger (Pink/Muted) |

## Assets

- Logos e ícones devem seguir estilo pixel-art ou outline neon.
- Bandeiras de países em 8-bit ou 16-bit.
