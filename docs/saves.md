# Formato dos Arquivos de Save

Cada save fica em `saves/<perfil>/`. Toda escrita usa `salvar_json_seguro()` (backup + atomic replace).

## Nova Arquitetura Otimizada (2026-03)

Para garantir escalabilidade e performance, o sistema de save foi fragmentado (**sharding**):
1.  **Ranking Lean:** Os arquivos de ranking principal agora são apenas índices rápidos.
2.  **Jogadores Sharded:** Atributos detalhados e históricos de NPCs ficam em arquivos individuais.
3.  **Calendário Sharded:** Cada torneio da semana tem seu próprio JSON, carregado sob demanda.
4.  **Histórico Global:** As partidas são registradas em um arquivo central otimizado.

---

## Estrutura de Pastas do Save

```text
saves/<perfil>/
├── jogadores/              # Atributos completos de todos os NPCs
│   ├── atp/                # ex: carlos_alcaraz.json
│   └── wta/                # ex: iga_swiatek.json
├── calendario/             # Estado de todos os torneios simulados
│   ├── atp/                # ex: dallas_open.json
│   └── wta/                # ex: abu_dhabi_open.json
├── jogador.json            # Estado do jogador humano
├── ranking_atp.json        # Índice simples (Lean)
├── ranking_wta.json        # Índice simples (Lean)
├── ranking_atp_duplas.json # Ranking dedicado de duplas
├── ranking_wta_duplas.json # Ranking dedicado de duplas
├── historico_partidas.json # Registro otimizado de todos os confrontos
├── temporada.json          # Semana e Ano atual
└── log.txt                 # Logs de simulação e erros
```

---

## `jogador.json`

Origem: `src/jogador.py` → `to_dict()` / `src/save.py`

```json
{
  "nome": "string",
  "idade": 18,
  "nacionalidade": "[BR] Brasil",
  "genero": "masculino | feminino",
  "save_name": "string",

  "energia": 100,
  "fadiga": 0,
  "moral": 70,
  "ritmo_jogo": 50,

  "status_lesao": {
    "lesionado": false,
    "semanas_restantes": 0,
    "nivel": "saudavel | desconforto | limitado | lesionado",
    "penalidade_atributos": 0.0
  },

  "vinculos_dupla": {
    "Nome Parceiro": { "partidas": 12, "vitorias": 8 }
  },

  "modalidade_atual": "simples | duplas | ambos",
  "parceiro_duplas": { "nome": "...", "overall": 80 },
  "tipo_duplas_atual": "mesmo_genero | mista",

  "atributos": {
    "saque": 60, "forehand": 60, "backhand": 60,
    "topspin": 60, "voleio": 60, "slice": 60,
    "movimento": 60, "lob": 60, "winner": 60,
    "fisico": 60, "duplas": 60
  }
}
```

---

## `ranking_atp.json` (Versão Lean)

Este arquivo é um índice. Atributos detalhados devem ser carregados de `jogadores/atp/<nome>.json`.

```json
[
  {
    "nome": "Carlos Alcaraz",
    "nacionalidade": "[ES] España",
    "pontos": 13550,
    "pontos_ranking": 13550,
    "overall": 93,
    "is_lean": true
  }
]
```

---

## `historico_partidas.json`

Armazena os últimos 1000 confrontos de forma otimizada para estatísticas de carreira.

```json
[
  {
    "id": "a1b2c3d4",
    "torneio": "Dallas Open",
    "semana": 6,
    "ano": 2026,
    "modalidade": "simples | duplas",
    "jogadores": ["Alexandre Paiva", "Emilio Nava"],
    "vencedor": "Alexandre Paiva",
    "resultado": "6-4 6-3",
    "fase": "final"
  }
]
```

---

## `calendario/<tour>/<torneio>.json`

Estado individual de cada torneio da temporada. Substitui os antigos `world_tournaments_*.json`.

```json
{
  "torneio": "Dallas Open",
  "semana": 6,
  "fase_atual": "finalizado",
  "campeao_simples": "Emilio Nava",
  "campeao_duplas": "Paiva / Kecmanovic",
  "resultados": { ... },
  "resultados_duplas": { ... }
}
```

---

## Fluxo de Leitura/Escrita Otimizado

1.  **Carregamento de Ranking:** O `SistemaRanking` lê o arquivo lean.
2.  **Lazy Loading:** Quando o código chama `buscar_jogador_por_nome()`, o sistema verifica `is_lean`. Se `true`, ele busca o JSON individual em `jogadores/` e faz o merge dos dados.
3.  **Simulação Mundial:** O `WeekTournamentManager` lista arquivos no diretório `calendario/<tour>/` e carrega apenas os que possuem a `semana` igual à atual.
4.  **Escrita Atômica:** Todos os shards usam `salvar_json_seguro()` para evitar perda de dados em caso de crash.
