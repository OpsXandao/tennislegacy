---
name: tennis-save-restructuring
description: Restructures the tennis game save system to use a dedicated doubles ranking, optimized match history, and a fragmented calendar (one file per tournament). Use this skill when the user requests a more scalable and organized save architecture or when tournament data becomes too large for a single file.
---

# Tennis Save Restructuring

## Overview
This skill guides the restructuring of the save system to improve performance, data integrity, and ease of management.

## New Save Architecture

### 1. Dedicated Doubles Ranking
Separate the doubles ranking from the singles ranking into its own JSON files.
- `saves/<perfil>/ranking_atp_duplas.json`
- `saves/<perfil>/ranking_wta_duplas.json`

### 2. Optimized Match History
Store match history in a separate file to keep ranking files lean.
- `saves/<perfil>/historico_partidas.json`
- Schema: `[{"id_partida": "uuid", "data": "YYYY-WW", "torneio": "id", "jogadores": [id1, id2], "resultado": "score", "vencedor": id}]`

### 3. Fragmented Calendar
Move from a single large calendar file to a directory-based structure.
- `saves/<perfil>/calendario/atp/`
- `saves/<perfil>/calendario/wta/`
- Each tournament is a file: `saves/<perfil>/calendario/atp/dallas_open_2026.json`

## Implementation Workflow

### Step 1: Directory Preparation
Create the necessary folder structure within the save directory.
```python
os.makedirs(f"saves/{perfil}/calendario/atp", exist_ok=True)
os.makedirs(f"saves/{perfil}/calendario/wta", exist_ok=True)
```

### Step 2: Data Migration
1. **Split Rankings:** Extract `pontos_detalhados_duplas` and `pontos_ranking_duplas` from the main ranking and move to the new doubles ranking file.
2. **Shard Calendar:** Read the current `world_tournaments_*.json` and save each key as a separate file in the new `calendario/` subdirectories.

### Step 3: Code Update
Update `src/dados.py`, `src/tournament_manager.py`, and `src/ranking.py` to support the new paths and fragmented loading.

## Verification
- Ensure `Ranking ATP Duplas` displays correctly in the menu.
- Verify that finishing a tournament only updates the specific tournament file in `calendario/atp/`.
- Confirm that `log.txt` no longer shows "File too large" errors for world tour updates.
