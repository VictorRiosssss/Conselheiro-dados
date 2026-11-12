BEGIN TRANSACTION;
CREATE TABLE decisao (
  id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL, area TEXT, titulo TEXT NOT NULL,
  contexto TEXT, opcoes TEXT, escolha TEXT, motivo TEXT, numeros TEXT, revisar_em TEXT,
  resultado TEXT, resultado_em TEXT);
CREATE TABLE memoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, texto TEXT NOT NULL,
  criada_em TEXT NOT NULL, ativa INTEGER NOT NULL DEFAULT 1);
CREATE TABLE numero (
  id INTEGER PRIMARY KEY AUTOINCREMENT, chave TEXT NOT NULL, valor REAL NOT NULL,
  ref TEXT NOT NULL, fonte TEXT NOT NULL, registrado_em TEXT NOT NULL);
CREATE TABLE pendencia (
  id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL, quando TEXT NOT NULL,
  origem TEXT, concluida_em TEXT, criada_em TEXT NOT NULL);
CREATE TABLE problema (
  id INTEGER PRIMARY KEY AUTOINCREMENT, area TEXT NOT NULL, titulo TEXT NOT NULL,
  descricao TEXT, impacto INTEGER NOT NULL DEFAULT 3, responsavel TEXT, desde TEXT,
  tentado TEXT, proximo_passo TEXT, status TEXT NOT NULL DEFAULT 'aberto',
  criado_em TEXT NOT NULL, atualizado_em TEXT NOT NULL);
CREATE TABLE relatorio (
  id INTEGER PRIMARY KEY AUTOINCREMENT, fonte TEXT NOT NULL, ref TEXT, caminho TEXT NOT NULL,
  recebido_em TEXT NOT NULL, obs TEXT);
DELETE FROM "sqlite_sequence";
COMMIT;
