# Inventário de prints em `src/torneio.py`

> Status: inventário histórico (criado antes do split para `src/torneio_core.py`).
> Para arquitetura atual, consultar `docs/refactoring_log.md`.

Documento preparatório para Fase 2 (desacoplamento UI/domínio).

| Linha | Função | Chamada atual | Retorno ideal (domínio) |
|---:|---|---|---|
| 25 | `(escopo de classe/metodo)` | `from src.io_utils import safe_input, print_blue, print_yellow` | Evento de aviso (`kind="warning"`) com payload de contexto. |
| 777 | `(escopo de classe/metodo)` | `print("🗞️ Você decidiu não conceder entrevista.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1392 | `(escopo de classe/metodo)` | `print("⚠️ Sem jogadores para a qualificação.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1505 | `(escopo de classe/metodo)` | `print(f"❌ Fase desconhecida: {fase}")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1667 | `(escopo de classe/metodo)` | `print_yellow(f"\n📢 {len(novos_ll)} Lucky Loser(s) entraram na chave principal: {', '.join([l['nome'] for l in novos_ll])}")` | Evento de aviso (`kind="warning"`) com payload de contexto. |
| 1841 | `(escopo de classe/metodo)` | `print("⚠️ Arquivo de torneio não encontrado.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1855 | `(escopo de classe/metodo)` | `print(f"🧹 Removendo confronto: {a_nome} vs {b_nome}")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1865 | `(escopo de classe/metodo)` | `print(f"✅ Confrontos removidos: {removidos} na fase '{fase}'")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1877 | `(escopo de classe/metodo)` | `print(f"\n--- Simulando {fase_nome} ---")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1889 | `(escopo de classe/metodo)` | `print(f"  {placar}")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 1929 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2653 | `(escopo de classe/metodo)` | `print_blue(f"🎾 Breve descanso entre partidas: +{rec}% de energia recuperada.")` | Evento informativo (`kind="info"`) com mensagem formatável. |
| 2655 | `(escopo de classe/metodo)` | `print_blue(f"\n👥 Duplas: {nome_par} vs {par_adversario.get('nome', '??')}")` | Evento informativo (`kind="info"`) com mensagem formatável. |
| 2718 | `(escopo de classe/metodo)` | `print_blue(` | Evento informativo (`kind="info"`) com mensagem formatável. |
| 2954 | `(escopo de classe/metodo)` | `print("\n📊 Resultados da Davis Cup (formato de equipes, em breve).")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2962 | `(escopo de classe/metodo)` | `print(f"\n📊 Resultados da fase {ultima_fase}:")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2973 | `(escopo de classe/metodo)` | `print(f"- {nome_a} vs {nome_b} \| 🏆 {nome_vencedor} ({placar})")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2975 | `(escopo de classe/metodo)` | `print("-", r)` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2977 | `(escopo de classe/metodo)` | `print("\n📊 Nenhum resultado disponível ainda.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 2982 | `(escopo de classe/metodo)` | `print(f"\n🗓️ Confrontos da fase {fase}:")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3005 | `(escopo de classe/metodo)` | `print_yellow(f"👉 {linha}  (SUA PARTIDA)")` | Evento de aviso (`kind="warning"`) com payload de contexto. |
| 3007 | `(escopo de classe/metodo)` | `print(linha)` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3024 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3032 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3035 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3050 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3055 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3060 | `(escopo de classe/metodo)` | `print("⚠️ Sem qualifying para este torneio.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3085 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3137 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3141 | `(escopo de classe/metodo)` | `print(f"❌ Erro ao iniciar torneio: {e}")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3374 | `(escopo de classe/metodo)` | `print("Você não tem confronto nesta fase ou já jogou sua partida.")` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3435 | `(escopo de classe/metodo)` | `print_red("\n🚨 WALKOVER (W/O) DETECTADO")` | Evento de erro/alerta estruturado (`kind="error"`, `message`). |
| 3437 | `(escopo de classe/metodo)` | `print_red(f"❌ Você está {motivo_h} e não pode entrar em quadra.")` | Evento de erro/alerta estruturado (`kind="error"`, `message`). |
| 3441 | `(escopo de classe/metodo)` | `print_green(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3495 | `(escopo de classe/metodo)` | `print_blue(f"🎾 Breve descanso entre partidas: +{rec}% de energia recuperada.")` | Evento informativo (`kind="info"`) com mensagem formatável. |
| 3568 | `(escopo de classe/metodo)` | `print_blue(` | Evento informativo (`kind="info"`) com mensagem formatável. |
| 3671 | `(escopo de classe/metodo)` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
| 3755 | `carregar_torneio` | `print(` | Retorno estruturado (resultado + lista de eventos), sem I/O direto. |
