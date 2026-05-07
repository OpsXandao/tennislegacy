# Auditoria de Segurança — TennisLegacy
> Data: 2026-03-19
> Auditor: Security Engineer Agent
> Escopo: Backend FastAPI (`api/`, `src/dados.py`, `src/save.py`, `src/json_utils.py`) + Frontend React (`Front/src/`)

---

## Sumário Executivo

A auditoria identificou **8 vulnerabilidades** distribuídas entre severidades Crítica (1), Alta (3), Média (3) e Baixa (1). O risco mais grave é a ausência de sanitização do parâmetro `nome_save` antes de seu uso em `os.path.join()`, o que permite a qualquer cliente enviar o header `X-Save-Name: ../../../etc/passwd` e fazer o servidor ler — ou escrever — arquivos fora do diretório `saves/`. O segundo maior risco é a política CORS permissiva (`allow_origins=["*"]` combinada com `allow_credentials=True`), que viola a especificação do navegador e expõe todos os endpoints autenticados. As demais vulnerabilidades dizem respeito a validação insuficiente de campos de entrada (nome de save sem restrição de charset), ausência de autenticação real nas rotas, informações internas nos logs do frontend, e um uso de `dangerouslySetInnerHTML` que, embora não seja diretamente explorável hoje, representa uma superfície que merece controle.

Nenhum segredo ou credencial foi encontrado no código-fonte. A biblioteca `json_utils.salvar_json_seguro` protege corretamente contra corrupção por escrita parcial (write-tmp-then-rename). O frontend usa React com JSX e não apresenta XSS por concatenação de strings.

---

## Vulnerabilidades Encontradas

### [CRITICO] Path Traversal no nome_save — leitura e escrita arbitrária de arquivos

- **Arquivo:** `api/session.py:97-102`, `src/dados.py:64-324`, `src/save.py:16-17`
- **Vetor de ataque:**
  O header `X-Save-Name` é lido diretamente do request HTTP e passado, sem nenhuma sanitização, para `Session(x_save_name)`, que o armazena em `self.nome_save_ativo`. Todas as funções de path em `src/dados.py` fazem `os.path.join(SAVES_DIR, nome_save, ...)`. Como `os.path.join()` respeita componentes `..`, um atacante pode enviar:
  ```
  X-Save-Name: ../../../../etc/passwd
  ```
  e a função `get_caminho_jogador_save` retornará `/etc/passwd`. O endpoint `GET /api/save/{nome}/preview` aceita o nome como path parameter sem validação de existência no filesystem antes de chamar `carregar_jogador(nome)`, o que também é afetado.

  Para **escrita**, o endpoint `POST /api/save/salvar` usa `session.nome_save_ativo` para determinar onde persistir `jogador.json` — um atacante autenticado com sessão ativa pode escrever JSON arbitrário fora de `saves/`.

  O mesmo padrão inseguro existe em:
  - `src/dados.py:get_caminho_ranking_save()` (linha 64-67)
  - `src/dados.py:get_caminho_npc_save()` (linha 288-303) — o `nome_jogador` também é usado em `os.path.join` após transformação parcial com `.replace()`, mas sem bloquear `..`
  - `src/dados.py:excluir_save()` (linha 322-332) — `shutil.rmtree()` sobre caminho derivado de `nome_save` pode excluir diretórios arbitrários se `../` for injetado

- **Impacto:**
  - Leitura de qualquer arquivo legível pelo processo do servidor (ex.: arquivos de configuração, chaves SSH em `~/.ssh/`, outros saves de outros usuários)
  - Escrita arbitrária de JSON em qualquer caminho (sobrescrever arquivos de sistema ou de outros saves)
  - Deleção recursiva de diretórios arbitrários via `DELETE /api/save/{nome}` → `shutil.rmtree()`

- **Recomendação:**
  Implementar uma função centralizada de sanitização de `nome_save` que:
  1. Rejeite qualquer valor contendo `/`, `\`, `.`, ou `%` (após decodificação URL)
  2. Aplique um allowlist estrito de charset: apenas `[a-zA-Z0-9_-]`, tamanho máximo de 64 caracteres
  3. Após construir o caminho com `os.path.join`, verifique que o resultado começa com `SAVES_DIR` usando `os.path.realpath()`:
     ```python
     resolved = os.path.realpath(caminho)
     if not resolved.startswith(os.path.realpath(SAVES_DIR)):
         raise HTTPException(status_code=400, detail="Caminho inválido.")
     ```
  O mesmo controle deve ser aplicado a `nome_jogador` em `get_caminho_npc_save()` e a `nome_torneio` em `get_caminho_calendario_save()`.

---

### [ALTO] CORS mal configurado — allow_origins=* com allow_credentials=True

- **Arquivo:** `api/main.py:57-63`
- **Vetor de ataque:**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
  A combinação de `allow_origins=["*"]` com `allow_credentials=True` viola a especificação CORS (navegadores modernos rejeitam respostas com `Access-Control-Allow-Origin: *` quando `credentials: include` está presente). No entanto, o risco real é que a intenção do código é permitir credenciais de qualquer origem — se o wildcard for trocado por uma origem mal escolhida (ou se o desenvolvedor assumir que está protegido), qualquer site malicioso pode fazer requisições cross-origin com o contexto do usuário autenticado.

  Além disso, `allow_methods=["*"]` e `allow_headers=["*"]` expõem métodos como `DELETE` e headers arbitrários, ampliando a superfície de CSRF.

- **Impacto:**
  Confusão sobre o modelo de segurança real. Se a API for exposta na rede local ou internet, qualquer página web pode fazer chamadas autenticadas em nome do usuário (CSRF via fetch com credenciais) caso a origem seja posteriormente restringida de forma incorreta.

- **Recomendação:**
  Restringir `allow_origins` para a origem exata do frontend em produção (ex.: `["http://localhost:5173"]` em dev, `["https://meudominio.com"]` em prod). Nunca combinar `allow_origins=["*"]` com `allow_credentials=True`. Remover métodos desnecessários de `allow_methods`.

---

### [ALTO] Ausência de autenticação e autorização nas rotas da API

- **Arquivo:** Todos os arquivos em `api/routes/`
- **Vetor de ataque:**
  A única "autenticação" da API é a presença do header `X-Save-Name`. Qualquer cliente que envie esse header obtém acesso total às operações do save correspondente — ler dados do jogador, avançar semanas, assinar patrocínios, criar/deletar saves. Não existe mecanismo de sessão com token assinado, senha, ou qualquer verificação de que o cliente é o proprietário legítimo do save.

  Em `api/session.py:96-103`, a função `obter_sessao_ativa` aceita qualquer string no header e instancia ou reutiliza a sessão correspondente sem qualquer verificação:
  ```python
  def obter_sessao_ativa(
      x_save_name: str = Header(..., alias="X-Save-Name"),
  ) -> Session:
      sessao = _sessions_pool.pop(x_save_name, None)
      if sessao is None:
          sessao = Session(x_save_name)  # cria sessão para qualquer nome
      _sessions_pool[x_save_name] = sessao
      return sessao
  ```

- **Impacto:**
  Qualquer processo na mesma rede pode ler ou modificar o save de qualquer jogador simplesmente enviando o nome do save no header. Combinado com a vulnerabilidade de path traversal, o impacto escala para comprometimento total do sistema de arquivos.

- **Recomendação:**
  Para um jogo single-player local, o risco é aceitável em rede isolada. Para qualquer exposição de rede:
  1. Vincular o servidor a `127.0.0.1` (não `0.0.0.0`) no `uvicorn.run`
  2. Ou implementar autenticação por token de sessão assinado (JWT ou similar) emitido no momento de criar/carregar o save, validado a cada request

---

### [ALTO] Ausência de validação de charset em `nome` do save na criação

- **Arquivo:** `api/routes/save.py:40-48`, `api/routes/save.py:138-172`
- **Vetor de ataque:**
  O campo `nome` de `CreateSaveRequest` é definido como `str` puro sem restrição de charset ou tamanho máximo:
  ```python
  class CreateSaveRequest(BaseModel):
      nome: str = Field(..., description="Nome único do save/pasta")
  ```
  O Pydantic valida `idade` (com `ge=14, le=50`), mas não valida `nome`, `nome_jogador`, ou `nacionalidade`. Um atacante pode enviar:
  - `nome = "../etc"` — cria diretório fora de `saves/`
  - `nome = "a" * 10000` — nome excessivamente longo
  - `nome = "save\x00injection"` — null byte em sistemas que o suportam

  O endpoint `POST /api/save/criar` verifica apenas se o nome já existe (case-insensitive) antes de prosseguir com `_inicializar_arquivos_save(req.nome, ...)`, que cria o diretório diretamente.

- **Impacto:**
  Criação de diretórios fora de `saves/` (path traversal na criação). Sem a verificação de `realpath`, um nome como `../novo_dir` resulta em `os.makedirs(SAVES_DIR + "/../novo_dir")`.

- **Recomendação:**
  Adicionar validação ao campo `nome` do save com Pydantic:
  ```python
  nome: str = Field(..., min_length=1, max_length=64, pattern=r'^[a-zA-Z0-9_-]+$')
  nome_jogador: str = Field(..., min_length=1, max_length=100)
  ```

---

### [MEDIO] dangerouslySetInnerHTML com dados parcialmente controlados pelo usuário

- **Arquivo:** `Front/src/app/components/ui/chart.tsx:83-100`
- **Vetor de ataque:**
  ```tsx
  <style
    dangerouslySetInnerHTML={{
      __html: Object.entries(THEMES).map(([theme, prefix]) => `
  ${prefix} [data-chart=${id}] {
  ${colorConfig.map(([key, itemConfig]) => {
      const color = itemConfig.theme?.[...] || itemConfig.color;
      return color ? `  --color-${key}: ${color};` : null;
  }).join("\n")}
  }`)...
  ```
  O HTML injetado na tag `<style>` é construído a partir de `config` (prop `ChartConfig`) e do `id` gerado internamente. Se um componente pai passar um `ChartConfig` com valores de cor originados de dados da API (ex.: nomes de jogadores usados como rótulos de cores), um payload como `red; } body { display: none; } /*` no campo `color` pode injetar CSS arbitrário.

  Hoje, os valores de `ChartConfig` são todos definidos estaticamente no código frontend. O risco se materializa se dados da API forem usados como chaves ou valores de cor de gráficos futuramente.

- **Impacto:**
  CSS injection — modificação visual da interface. Não permite execução de JavaScript diretamente (é uma tag `<style>`, não `<script>`), mas pode ser usado para clickjacking visual ou extração de dados via CSS selectors em navegadores antigos.

- **Recomendação:**
  Sanitizar os valores de `color` com uma allowlist de formato CSS (`/^#[0-9a-fA-F]{3,8}$|^rgb\(|^hsl\(/`). Nunca usar valores originados da API como chaves ou values de `ChartConfig` sem sanitização.

---

### [MEDIO] Parâmetro de busca de duplas sem encoding no cliente

- **Arquivo:** `Front/src/api/client.ts:451-464`
- **Vetor de ataque:**
  ```typescript
  buscar: (params: { nome?: string; nacionalidade?: string }) => {
      let q = ''
      if (params.nome) q = `?nome=${params.nome}`          // sem encodeURIComponent
      else if (params.nacionalidade) q = `?nacionalidade=${params.nacionalidade}`
      return get<...>(`/duplas/buscar${q}`)
  }
  ```
  Os parâmetros `nome` e `nacionalidade` são concatenados na URL sem `encodeURIComponent`. Um nome com caracteres especiais (ex.: `Rafael Nadal & acao=deletar`) pode injetar parâmetros adicionais na query string. O backend usa FastAPI Query para ler esses parâmetros, o que isola o impacto a confusão de parâmetros — mas se o valor chegar a um sistema de logging que processa query strings, pode causar log injection.

- **Impacto:**
  Query string injection / parameter pollution. Impacto limitado no estado atual, mas representa má prática que pode escalar se a rota evoluir.

- **Recomendação:**
  Substituir a concatenação manual por `URLSearchParams`:
  ```typescript
  const params_obj = new URLSearchParams()
  if (params.nome) params_obj.set('nome', params.nome)
  else if (params.nacionalidade) params_obj.set('nacionalidade', params.nacionalidade)
  return get(`/duplas/buscar?${params_obj.toString()}`)
  ```

---

### [MEDIO] Ingestão de logs do frontend sem rate limiting e sem sanitização

- **Arquivo:** `api/routes/logs.py:25-42`
- **Vetor de ataque:**
  O endpoint `POST /api/logs/frontend` aceita payloads arbitrários do frontend sem autenticação (não requer `X-Save-Name` válido, apenas o header opcional), sem rate limiting e sem limite de tamanho para campos como `stack`, `message`, e `extra`. Um atacante pode:
  1. Enviar requisições em loop para saturar o disco com logs
  2. Injetar sequências de escape ou caracteres de controle nos campos de log para confundir sistemas de análise de log
  3. O campo `extra: dict[str, Any]` aceita qualquer estrutura JSON sem restrição de profundidade ou tamanho

- **Impacto:**
  Denial of service por saturação de log. Log injection caso o sistema de análise processe os campos sem escapamento.

- **Recomendação:**
  1. Adicionar rate limiting por IP (ex.: máximo 10 req/min por IP) usando `slowapi` ou middleware
  2. Limitar tamanho dos campos: `message: str = Field(..., max_length=2000)`, `stack: str = Field(None, max_length=5000)`
  3. Restringir `extra` a estruturas simples ou remover o campo

---

### [BAIXO] Servidor escutando em 0.0.0.0 por padrão

- **Arquivo:** `api/main.py:182-184`
- **Vetor de ataque:**
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8000)
  ```
  O servidor escuta em todas as interfaces de rede, expondo a API a toda a rede local (e, potencialmente, à internet se houver redirecionamento de porta no roteador). Combinado com a ausência de autenticação real, qualquer dispositivo na mesma rede pode acessar e modificar todos os saves.

- **Impacto:**
  Exposição da API não autenticada na rede local. Risco amplificado pela vulnerabilidade de path traversal.

- **Recomendação:**
  Alterar para `host="127.0.0.1"` para ambiente de desenvolvimento local. Documentar explicitamente que o servidor não deve ser exposto em redes não confiáveis.

---

## Superfície de Ataque Mapeada

### Entradas de dados externas

| Vetor | Onde chega | Validado? |
|---|---|---|
| `X-Save-Name` (header HTTP) | `api/session.py:97` → `src/dados.py` (todos os `get_caminho_*`) | NÃO |
| `nome` do save (path param e body) | `api/routes/save.py` | Parcialmente (apenas unicidade) |
| `nome_jogador` (body JSON) | `api/routes/save.py:CreateSaveRequest` | NÃO (tamanho/charset) |
| `nome_adversario` (path param) | `api/routes/partida.py:61` | Parcialmente (normalização) |
| Payload de log do frontend | `api/routes/logs.py` | NÃO (tamanho) |
| Query params `nome`, `nacionalidade` | `api/routes/duplas.py:84` | NÃO (no cliente) |
| `patrocinio_id` (body JSON) | `api/routes/jogador.py:400` | Sim (validado contra dict estático) |
| WebSocket payload `acao` | `api/ws/partida.py:48` | Parcialmente (strip + lower) |

### Pontos de escrita no filesystem

| Operação | Função | Proteção |
|---|---|---|
| Salvar jogador | `json_utils.salvar_json_seguro` | Escrita atômica via tmp (bom) |
| Criar diretório de save | `src/save.py:criar_pasta_save` | `os.makedirs` com path não sanitizado |
| Deletar save | `src/dados.py:excluir_save` / `api/routes/save.py:188` | `shutil.rmtree` com path não sanitizado |
| Salvar estado de torneio | `src/save.py:salvar_estado_atual_torneio` | Escrita atômica (bom), caminho não sanitizado |

### Armazenamento sensível

- Não foram encontrados segredos, tokens de API ou senhas no código-fonte
- Nenhum arquivo `.env` ou `credentials.json` identificado no escopo auditado
- Dados de save são puramente dados de jogo (não há PII real de usuários)

### Frontend

- React com JSX: strings de dados da API são escapadas automaticamente em renderização JSX normal
- Único uso de `dangerouslySetInnerHTML` localizado em `chart.tsx:83` — contexto de CSS, não HTML geral
- Nenhum uso de `eval()`, `innerHTML =`, ou `document.write()` encontrado
- `encodeURIComponent` ausente apenas nos parâmetros de busca de duplas (`client.ts:452-453`)

---

## Conclusão

O projeto possui uma arquitetura razoável para um jogo local single-player, com boas práticas de escrita atômica de JSON e separação de responsabilidades entre módulos. No entanto, a API foi construída assumindo um ambiente confiável (localhost) e exposta sem as salvaguardas necessárias para qualquer cenário de rede.

A vulnerabilidade de **path traversal em `nome_save`** é o problema mais urgente. Ela é trivial de explorar (basta mudar um header HTTP) e pode resultar em leitura e escrita arbitrária de arquivos no servidor. A correção requer uma única função de sanitização centralizada aplicada antes de qualquer `os.path.join(SAVES_DIR, nome_save)`.

**Prioridade de remediação:**

1. (Imediato) Implementar `_sanitizar_nome_save(nome: str) -> str` com allowlist `[a-zA-Z0-9_-]` e verificação de `os.path.realpath` — aplicar em `session.py`, `dados.py`, e `save.py`
2. (Imediato) Corrigir CORS: remover combinação `allow_origins=["*"]` + `allow_credentials=True`
3. (Sprint atual) Adicionar `pattern=r'^[a-zA-Z0-9_-]+$'` ao campo `nome` de `CreateSaveRequest`
4. (Sprint atual) Alterar `uvicorn.run` para `host="127.0.0.1"`
5. (Próximo sprint) Adicionar rate limiting ao endpoint de logs do frontend
6. (Próximo sprint) Usar `URLSearchParams` no cliente para parâmetros de busca de duplas
7. (Backlog) Adicionar sanitização de valores de cor em `ChartConfig` antes de injeção no `<style>`
