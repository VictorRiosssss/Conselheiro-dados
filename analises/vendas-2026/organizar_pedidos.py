import re,csv,json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from collections import defaultdict,Counter

P=Path('/opt/data/conselheiro-dados/analises/vendas-2026')
source=P/'pedidos-fonte-telegram.txt'
customers='''DIEGO RIOS SILVA
SEBASTIÃO E JULIANA
CRISTIANO FRAGOSO DE OLIVEIRA
DILERMANDO LAJE RIBEIRO PESSOA SOBRINHO
PHMC REPRESENTACAO E PARTICIPACAO LTDA
ALEX SENA MACEDO E SILVA
RENATO MARQUES DE OLIVEIRA
ELCYDES PIAGGIO DE OLIVEIRA JÚNIOR
APX NET SERVICOS E COMERCIO LTDA
TARCISIO ANDRADE BERNARDO
EDER CARLOS DOS SANTOS
JULIANA DE ALMEIDA LACERDA
ICL FARMACIA LTDA
CRISTHIANO PAULO TEIXEIRA DE CASTRO
Karina Freire Araújo de Carvalho
SIPEL CONSTRUCOES LTDA
CARLOS WASHIGTON LEITE DOS SANTOS
Larissa Beatriz Bernardo de Oliveira
LAIANE SILVA DE SOUZA
HÉLIO CATHARINO DA SILVA NETO
Márcio Pinheiro de Souza
JOANITA MERCES RAMOS SILVA
DUNAX LUBRIFICANTES LTDA
GILVANDO BARBOSA LIMA
LUIZA SELIS SANTOS SANTANA
Ygor Veloso Gomes Silva
LUIZA ADRIANA DA SILVA ODIZO
SARA DA SILVA SERRA
BRARLON MACEDO FARIAS
BIBIANE CARNEIRO FERREIRA BRAGA
LUIZ CARLOS DE CARVALHO BAHIA NETO
GEOVANA NERES ALVES GUIMARÂES
G6 TRANSPORTE
TAYRONE BRANDÃO MALAQUIAS
VIVIANE DE JESUS SOUZA
TOMAZ FIGUEREDO COSTA JUNIOR
RISOMAR FRANCO DE ALBUQUERQUE
Fernanda Oliveira Gobatto
BRUNO SOUZA BASTOS
ANA PAULA
CAIO CEZAR REBOUÇAS CERQUEIRA
SANDRO GONZAGA SANTANA
ELOFILO CINTRA SILVA
CIRE - CLINICA INTEGRADA DE REABILITACAO ESTETICA LTDA'''.splitlines()
statuses=['Pré conferência','Enviado a fábrica','Pendente assinatura do caderno técnico','Em conferência','ENTREGUE','Aguardando cadastro','Em montagem']
pattern=re.compile(r'^(PV-LP-\d+)\s+(.+?)\s+('+ '|'.join(map(re.escape,statuses))+r')\s+(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s*(.*?)\s*R\$\s*([\d.,]+)$')
raw=[s for s in source.read_text().splitlines() if s.startswith('PV-')]
rows=[]
for line in raw:
 m=pattern.fullmatch(line)
 assert m,line
 code,clients,status,date,owner,delivery,nfs,amount=m.groups()
 candidates=[c for c in customers if clients==c or clients.startswith(c+' ')]
 assert len(candidates)==1,(code,candidates)
 customer=candidates[0]; final=clients[len(customer):].strip()
 value=Decimal(amount.replace('.','').replace(',','.'))
 dt=datetime.strptime(date,'%d/%m/%Y').date(); dd=datetime.strptime(delivery,'%d/%m/%Y').date()
 assert re.fullmatch(r'PV-LP-\d+',code) and dt.year==2026
 rows.append({'codigo':code,'cliente':customer,'cliente_final':final,'status':status,'data_venda':dt.isoformat(),'responsavel':owner,'previsao_entrega':dd.isoformat(),'notas_fiscais_informadas':nfs,'valor':str(value),'linha_fonte':line})
assert len(rows)==len(raw)==len(set(r['codigo'] for r in rows))
assert set(r['cliente'] for r in rows)==set(customers)
rows.sort(key=lambda r:(r['data_venda'],r['codigo']))
total=sum((Decimal(r['valor']) for r in rows),Decimal(0))
by=defaultdict(lambda:{'valor':Decimal(0),'pedidos':[],'nomes_finais':set()})
monthly=defaultdict(lambda:Decimal(0))
for r in rows:
 b=by[r['cliente']]; b['valor']+=Decimal(r['valor']);b['pedidos'].append(r['codigo'])
 if r['cliente_final']:b['nomes_finais'].add(r['cliente_final'])
 monthly[r['data_venda'][:7]]+=Decimal(r['valor'])
assert sum((x['valor'] for x in by.values()),Decimal(0))==total
assert sum(monthly.values(),Decimal(0))==total
rank=[]; accum=Decimal(0)
for name,data in sorted(by.items(),key=lambda item:item[1]['valor'],reverse=True):
 accum+=data['valor']; rank.append({'cliente':name,'valor':str(data['valor']),'quantidade_pedidos':len(data['pedidos']),'participacao_pct':str(data['valor']/total*100),'acumulado_pct':str(accum/total*100),'pedidos':data['pedidos'],'nomes_finais_informados':sorted(data['nomes_finais'])})

def br(n,decimals=2):
 return f'{Decimal(n):,.{decimals}f}'.replace(',','X').replace('.',',').replace('X','.')
def datebr(s):return datetime.strptime(s,'%Y-%m-%d').strftime('%d/%m/%Y')

with (P/'vendas-2026.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Código','Cliente','Cliente final','Status','Data da venda','Responsável','Previsão de entrega','Notas fiscais informadas','Valor (R$)'])
 for r in rows:w.writerow([r['codigo'],r['cliente'],r['cliente_final'],r['status'],datebr(r['data_venda']),r['responsavel'],datebr(r['previsao_entrega']),r['notas_fiscais_informadas'],r['valor'].replace('.',',')])
with (P/'clientes-2026.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Cliente (nome literal no Pontta)','Valor de pedidos (R$)','Quantidade de pedidos','Participação nas vendas (%)','Participação acumulada (%)','Pedidos'])
 for r in rank:w.writerow([r['cliente'],r['valor'].replace('.',','),r['quantidade_pedidos'],br(r['participacao_pct']),br(r['acumulado_pct']),', '.join(r['pedidos'])])

top={str(n):{'valor':str(sum((Decimal(r['valor']) for r in rank[:n]),Decimal(0))),'percentual':str(sum((Decimal(r['valor']) for r in rank[:n]),Decimal(0))/total*100)} for n in [1,3,5,10]}
summary={'fonte':'Pedidos de venda do Pontta colados por Victor no Telegram, em duas mensagens. Sem acesso direto ao Pontta e sem total geral de controle fornecido.','criterio':'Soma dos valores de todos os pedidos recebidos com data de venda em 2026. Mantém pedido de valor zero e todos os status recebidos. Não equivale a faturamento fiscal, recebimentos ou entregas. Agrupamento apenas por igualdade literal do campo Cliente, sem CPF/CNPJ disponível. Não une clientes por nomes finais semelhantes.','quantidade_pedidos':len(rows),'quantidade_clientes_nomes_literais':len(rank),'total_valor_pedidos':str(total),'data_minima_informada':rows[0]['data_venda'],'data_maxima_informada':rows[-1]['data_venda'],'valor_zero':[r['codigo'] for r in rows if Decimal(r['valor'])==0],'status':dict(Counter(r['status'] for r in rows)),'meses':{m:str(v) for m,v in sorted(monthly.items())},'maiores':top,'ranking':rank}
(P/'pedidos-estruturados.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(P/'resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
lines=['# Vendas de 2026 — relação enviada por Victor','',summary['fonte'],summary['criterio'],'',f"Pedidos: {len(rows)} | Clientes por nome literal: {len(rank)} | Total: R$ {br(total)}",'', '## Pedidos por data','']
for r in rows:lines.append(f"- {datebr(r['data_venda'])} · {r['codigo']} · {r['cliente']} · R$ {br(r['valor'])} · {r['status']}")
lines+=['','## Concentração por cliente','']
for r in rank:lines.append(f"- {r['cliente']}: R$ {br(r['valor'])} · {br(r['participacao_pct'])}% · pedidos: {', '.join(r['pedidos'])}")
(P/'vendas-2026.md').write_text('\n'.join(lines)+'\n')
# Reabertura dos CSVs e reconciliação com os dados estruturados.
with (P/'vendas-2026.csv').open(encoding='utf-8-sig',newline='') as f: check=list(csv.DictReader(f,delimiter=';'))
assert len(check)==len(rows)
assert sum((Decimal(r['Valor (R$)'].replace(',','.')) for r in check),Decimal(0))==total
assert {r['Código'] for r in check}=={r['codigo'] for r in rows}
with (P/'clientes-2026.csv').open(encoding='utf-8-sig',newline='') as f: checkrank=list(csv.DictReader(f,delimiter=';'))
assert sum((Decimal(r['Valor de pedidos (R$)'].replace(',','.')) for r in checkrank),Decimal(0))==total
print(json.dumps({k:v for k,v in summary.items() if k!='ranking'},ensure_ascii=False,indent=2))
print('MAIORES CLIENTES')
for r in rank[:10]:print(r['cliente'],'R$',br(r['valor']),br(r['participacao_pct'])+'%')
print('VALIDAÇÃO: códigos únicos, datas em 2026, somas por cliente/mês e CSVs reconciliados com a fonte transcrita.')
