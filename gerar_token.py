import requests
import json

# --- PREENCHA COM SEUS DADOS ---
APP_ID = "6896781876999320"
SECRET_KEY = "DAhIpSQOWltBN3kNXye4aMWfXQcOUroW"
AUTHORIZATION_CODE = "TG-69d7ccb87c25700001344b7f-260875472" # Cole o código TG- que copiou da URL
REDIRECT_URI = "https://www.google.com"

def obter_primeiro_token():
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": SECRET_KEY,
        "code": AUTHORIZATION_CODE,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    print("Solicitando os tokens ao Mercado Livre...")
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        
        # Salva o resultado em um arquivo JSON na raiz do projeto
        with open("tokens.json", "w") as f:
            json.dump(dados, f, indent=4)
            
        print("Sucesso! Tokens gerados e salvos no arquivo 'tokens.json'.")
        print(f"Seu Access Token expira em: {dados.get('expires_in')} segundos.")
    else:
        print(f"Erro {response.status_code}: A autorização falhou.")
        print("Detalhes:", response.text)
        print("DICA: O código TG- expira muito rápido. Se der erro, gere outro link no navegador e tente novamente.")

if __name__ == "__main__":
    obter_primeiro_token()

