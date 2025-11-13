# 🔍 Comandos Básicos de Validação - Integração Sophos + Wazuh

Comandos essenciais para verificar se os logs da Sophos API estão sendo coletados.

---

## ✅ 1. Verificar se os Wodles Estão Executando

```bash
sudo tail -50 /var/ossec/logs/ossec.log | grep -i sophos
```

**Você deve ver:**
```
INFO: wazuh-modulesd:command: INFO: Starting command 'sophos_events'.
INFO: wazuh-modulesd:command: INFO: Starting command 'sophos_alerts'.
```

Se aparecer a cada 5 minutos = **✅ Funcionando!**

---

## ✅ 2. Verificar Coleta de Dados

```bash
# Ver se o arquivo de log existe e tem conteúdo
ls -lh /var/log/sophos-api.log

# Contar quantas linhas (eventos) foram coletadas
sudo wc -l /var/log/sophos-api.log

# Ver últimos 10 eventos coletados
sudo tail -10 /var/log/sophos-api.log

# Ver coleta em tempo real (Ctrl+C para sair)
sudo tail -f /var/log/sophos-api.log
```

**Se o arquivo tiver linhas JSON** = **✅ Coletando dados!**

---

## ✅ 3. Verificar Estado dos Cursores

```bash
# Cursor de eventos
cat /var/ossec/wodles/sophos_cursor_events.txt

# Cursor de alertas
cat /var/ossec/wodles/sophos_cursor_alerts.txt
```

**Se tiver conteúdo (string longa)** = **✅ Sistema de cursor funcionando!**

---

## ✅ 4. Verificar Processamento das Regras

```bash
# Testar se uma linha do log está sendo processada corretamente
sudo head -1 /var/log/sophos-api.log | sudo /var/ossec/bin/wazuh-logtest
```

**Você deve ver:**
```
**Phase 1: Completed pre-decoding.
**Phase 2: Completed decoding.
       decoder: 'json'
       
**Phase 3: Completed filtering (rules).
       Rule id: '110001'  ← Regra Sophos!
       Level: '3'
       Description: 'Sophos Central API - Evento recebido'
       groups: 'sophos','api_events'
```

**Se aparecer Rule id 110001 ou similar** = **✅ Regras funcionando!**

---

## ✅ 5. Verificar no Wazuh Dashboard

1. Acesse o **Wazuh Dashboard** no navegador
2. Vá em **"Security Events"** ou **"Threat Hunting"**
3. Adicione filtro: `rule.groups: sophos`
4. Você verá eventos da Sophos!

**Filtros úteis:**
```
rule.groups: sophos                          # Todos os eventos Sophos
rule.groups: sophos AND rule.level >= 7      # Apenas eventos importantes
data.severity: high                          # Apenas eventos de alta severidade
data.type: Event::Endpoint::Threat*          # Apenas detecções de ameaças
```

---

## ✅ 6. Verificar Última Atualização

```bash
# Ver quando foi a última coleta
stat /var/log/sophos-api.log
```

**Se "Modify" for recente (últimos 5-10 min)** = **✅ Coleta ativa!**

---

## 🔄 7. Forçar Execução Manual (Teste)

```bash
# Executar coleta manualmente (como usuário wazuh)
sudo -u wazuh bash -c "cd /var/ossec/wodles && python3 get_sophos_data.py events"

# Ou se seu sistema usa 'ossec':
sudo -u ossec bash -c "cd /var/ossec/wodles && python3 get_sophos_data.py events"
```

**Você deve ver:**
```
INFO: Buscando dados de: https://api-br01.central.sophos.com/siem/v1/events?limit=1000
SUCESSO: Total de X items do tipo 'events' coletados.
```

---

## 📊 8. Estatísticas Rápidas

```bash
# Total de eventos
echo "Total de eventos: $(sudo wc -l < /var/log/sophos-api.log)"

# Tamanho do arquivo
echo "Tamanho: $(sudo du -h /var/log/sophos-api.log | cut -f1)"

# Última modificação
echo "Última coleta: $(sudo stat -c %y /var/log/sophos-api.log | cut -d'.' -f1)"
```

---

## 🆘 Troubleshooting Rápido

### Nenhum evento coletado?

```bash
# Ver erros nos logs
sudo grep -i error /var/ossec/logs/ossec.log | tail -20

# Testar credenciais
sudo cat /var/ossec/wodles/.env

# Executar manualmente para ver erros
sudo -u wazuh bash -c "cd /var/ossec/wodles && python3 get_sophos_data.py events"
```

### Wodles não estão executando?

```bash
# Verificar configuração
sudo grep -A 10 "sophos_events" /var/ossec/etc/ossec.conf

# Validar configuração do Wazuh
sudo /var/ossec/bin/wazuh-control configtest

# Reiniciar Wazuh Manager
sudo systemctl restart wazuh-manager
```

### Eventos não aparecem no Dashboard?

```bash
# Verificar se o Wazuh está lendo o arquivo
sudo grep "sophos-api.log" /var/ossec/logs/ossec.log

# Verificar se as regras existem
sudo grep "110001" /var/ossec/etc/rules/local_rules.xml
```

---

## ✅ Checklist de Validação

Marque cada item após verificar:

- [ ] Wodles executando a cada 5 minutos
- [ ] Arquivo `/var/log/sophos-api.log` existe e tem conteúdo
- [ ] Arquivos de cursor atualizados
- [ ] Regras Sophos no `local_rules.xml`
- [ ] `wazuh-logtest` processa eventos corretamente
- [ ] Eventos aparecem no Dashboard
- [ ] Sem erros em `/var/ossec/logs/ossec.log`

**Se todos marcados** = **🎉 Integração 100% funcional!**

---

**Referência rápida para validação diária da integração Sophos + Wazuh.**

