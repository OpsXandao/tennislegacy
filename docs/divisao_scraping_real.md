# Plano de Extração de Dados Reais (Gemini, Claude, Codex)

**Objetivo:** O usuário solicitou que todos os 2461 arquivos JSON de jogadores (em `db/**Objetivo Principal:** Popular a lista `pontos_detalhados` de 2025 para expiração correta no jogo.
**Instruções para o Claude:**

1. Leia este arquivo para entender o contexto.
2. Adicione as dependências necessárias (ex: `requests`, `beautifulsoup4`, `lxml`, `pandas`) no `requirements.txt`.
3. Escreva um script (ou melhore `scripts/fetch_real_data.py`) focado em buscar os **resultados reais da temporada 2025** para os jogadores do Top 500 para as duplas (ATP e WTA).
4. Popule o campo `pontos_detalhados` e `pontos_detalhados_duplas` de cada JSON com a estrutura exigida pelo jogo:
   `{"pontos": <pontos>, "semana_expiracao": <semana_torneio>, "ano_expiracao": 2026, "torneio": "<nome>", "fase": "<fase>"}`.
5. Você pode usar os repositórios públicos (ex: Jeff Sackmann no GitHub), o site da ATP Tour, WTA Tour, ou a Wikipedia (seções de 2025) para extrair os pontos.

**Estratégia:** Dividir o trabalho entre as três IAs.

## 1. Gemini (Atual)

- **Feito:** Definição da arquitetura de colaboração e criação deste documento.
- **Feito:** Atualização da classe `Jogador` e da API para suportar e exibir atributos biográficos reais (Altura, Peso, Mão, Tipo de Backhand, Estilo).
- **Ação:** Criação do script base `scripts/fetch_real_data.py` (com suporte a requests e BeautifulSoup) para servir como template e scraping inicial dos dados biográficos do Top 100 da ATP.

## 2. Claude (Próxima IA)

**Objetivo Principal:** Popular a lista `pontos_detalhados` de 2025 para expiração correta no jogo.
**Instruções para o Claude:**

1. Leia este arquivo para entender o contexto.
2. Adicione as dependências necessárias (ex: `requests`, `beautifulsoup4`, `lxml`, `pandas`) no `requirements.txt`.
3. Escreva um script (ou melhore `scripts/fetch_real_data.py`) focado em buscar os **resultados reais da temporada 2025** para os jogadores do Top 500 (ATP e WTA).
4. Popule o campo `pontos_detalhados` e `pontos_detalhados_duplas` de cada JSON com a estrutura exigida pelo jogo:
   `{"pontos": <pontos>, "semana_expiracao": <semana_torneio>, "ano_expiracao": 2026, "torneio": "<nome>", "fase": "<fase>"}`.
5. Você pode usar os repositórios públicos (ex: Jeff Sackmann no GitHub), o site da ATP Tour, WTA Tour, ou a Wikipedia (seções de 2025) para extrair os pontos.

## 3. Codex (Próxima IA)

**Objetivo Principal:** Extrair Histórico de Troféus (`trofeus`) e finalizar dados Biográficos da WTA e posições menores.
**Instruções para o Codex:**

1. Leia este arquivo.
2. Expanda os scripts de scraping para buscar o histórico de títulos reais (Grand Slams, ATP/WTA 1000, 500, 250) para os jogadores e popule o array `trofeus` nos JSONs:
   `[{"nome": "Wimbledon", "ano": 2023, "categoria": "Grand Slam"}]`.
3. Certifique-se de que os dados biográficos reais de todas as jogadoras da **WTA** (Top 100+) sejam extraídos da Wikipedia ou WTA Tour, substituindo os dados aleatórios gerados anteriormente.
4. Execute o script e certifique-se de que o banco de dados mestre (`db/master/`) seja atualizado.
