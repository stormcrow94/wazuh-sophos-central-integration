#!/usr/bin/env python3
"""
Script Auxiliar para Configurar Credenciais da Sophos Central API
Este script ajuda a criar o arquivo .env obtendo automaticamente o Tenant ID
"""
import json
from urllib import request, parse
import sys

print("=" * 60)
print("🔧 Configuração de Credenciais - Sophos Central API")
print("=" * 60)
print()

# Solicitar credenciais ao usuário
print("📋 Obtenha estas informações em:")
print("   Sophos Central > Global Settings > API Credentials")
print("   (Crie uma credencial com papel 'Service Principal SIEM')")
print()

client_id = input("Digite o Client ID: ").strip()
client_secret = input("Digite o Client Secret: ").strip()

if not client_id or not client_secret:
    print("\n❌ Client ID e Client Secret são obrigatórios!")
    sys.exit(1)

print()
print("🔍 Obtendo Tenant ID e região automaticamente...")
print()

# Passo 1: Autenticar
auth_url = "https://id.sophos.com/api/v2/oauth2/token"
try:
    auth_data = parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "token"
    }).encode("utf-8")
    
    req = request.Request(auth_url, data=auth_data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    with request.urlopen(req, timeout=30) as response:
        if response.status == 200:
            token = json.loads(response.read().decode("utf-8")).get("access_token")
            print("✅ Autenticação bem-sucedida!")
        else:
            print(f"❌ Erro na autenticação: Status {response.status}")
            sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao autenticar: {e}")
    print("\n⚠️  Verifique se o Client ID e Client Secret estão corretos")
    sys.exit(1)

# Passo 2: Obter Tenant ID via whoami
whoami_url = "https://api.central.sophos.com/whoami/v1"
try:
    req_whoami = request.Request(whoami_url)
    req_whoami.add_header("Authorization", f"Bearer {token}")
    
    with request.urlopen(req_whoami, timeout=30) as response:
        if response.status == 200:
            whoami_data = json.loads(response.read().decode("utf-8"))
            tenant_id = whoami_data.get("id")
            api_hosts = whoami_data.get("apiHosts", {})
            data_region = api_hosts.get("dataRegion", "https://api.central.sophos.com")
            
            # Remover https:// do data_region
            data_host = data_region.replace("https://", "").replace("http://", "")
            
            print("✅ Informações obtidas com sucesso!")
            print()
            print("📊 Informações do Tenant:")
            print(f"   Tenant ID: {tenant_id}")
            print(f"   Região: {data_host}")
            print()
        else:
            print(f"❌ Erro ao obter tenant info: Status {response.status}")
            sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao obter informações do tenant: {e}")
    sys.exit(1)

# Passo 3: Criar arquivo .env
env_content = f"""# Credenciais da API Sophos Central
# Gerado automaticamente em {import_datetime()}
SOPHOS_CLIENT_ID="{client_id}"
SOPHOS_CLIENT_SECRET="{client_secret}"
SOPHOS_TENANT_ID="{tenant_id}"

# API Hosts
SOPHOS_API_AUTH_HOST="id.sophos.com"
SOPHOS_API_DATA_HOST="{data_host}"
"""

# Função auxiliar para data
def import_datetime():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

env_content = f"""# Credenciais da API Sophos Central
# Gerado automaticamente
SOPHOS_CLIENT_ID="{client_id}"
SOPHOS_CLIENT_SECRET="{client_secret}"
SOPHOS_TENANT_ID="{tenant_id}"

# API Hosts
SOPHOS_API_AUTH_HOST="id.sophos.com"
SOPHOS_API_DATA_HOST="{data_host}"
"""

try:
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✅ Arquivo .env criado com sucesso!")
    print()
    print("📁 Localização: .env (diretório atual)")
    print()
    print("📋 Conteúdo gerado:")
    print("-" * 60)
    # Mascarar o client_secret ao mostrar
    masked_secret = f"{client_secret[:15]}...{client_secret[-10:]}"
    print(f"SOPHOS_CLIENT_ID=\"{client_id}\"")
    print(f"SOPHOS_CLIENT_SECRET=\"{masked_secret}\"")
    print(f"SOPHOS_TENANT_ID=\"{tenant_id}\"")
    print(f"SOPHOS_API_AUTH_HOST=\"id.sophos.com\"")
    print(f"SOPHOS_API_DATA_HOST=\"{data_host}\"")
    print("-" * 60)
    print()
    print("🎯 Próximos passos:")
    print("   1. Copie o arquivo .env para o Wazuh Manager")
    print("   2. Coloque em /var/ossec/wodles/.env")
    print("   3. Ajuste permissões: sudo chmod 600 /var/ossec/wodles/.env")
    print()
    print("✅ Configuração completa!")
    
except Exception as e:
    print(f"❌ Erro ao criar arquivo .env: {e}")
    sys.exit(1)

