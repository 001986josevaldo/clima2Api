from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from ClimaController import *

controller = ClimaController()


load_dotenv()
# para executar
# python3.10 app.py

app = Flask(__name__)
CORS(app)  # <-- habilita CORS para todos os domínios


@app.route('/clima')
def clima_por_cep():
    cep = request.args.get('cep')
    print("CEP recebido:", cep)

    if not cep:
        return jsonify({"erro": "CEP não informado"}), 400

    cep = cep.replace("-", "").strip()

    
    try:
        # Etapa única: Endereço via ViaCEP
        res_cep = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        #print("Resposta do ViaCEP:", res_cep.text)

        if res_cep.status_code != 200:
            return jsonify({"erro": "Erro ao buscar CEP"}), 500

        endereco = res_cep.json()
        if "erro" in endereco:
            return jsonify({"erro": "CEP inválido"}), 400

        # Criar retorno somente com os dados que chegaram
        resultado = {
            "endereco":{
            "cep": endereco.get("cep"),
            "logradouro": endereco.get("logradouro"),
            "bairro": endereco.get("bairro"),
            "localidade": endereco.get("localidade"),
            "uf": endereco.get("uf"),
            "ddd": endereco.get("ddd"),
            "siafi": endereco.get("siafi"),
            "ibge": endereco.get("ibge")}
        }
        #print("retorno:", resultado)
        
        # Montando o endereço completo para geocodificação
        endereco = f"{resultado['endereco'].get('logradouro')}, {resultado['endereco'].get('bairro')},{resultado['endereco'].get('localidade')}, {resultado['endereco'].get('uf')}"
        # Obter as coordenadas via geocodificação
        latlon = controller.geocodificar_endereco(endereco)
        
        # Adicionando as coordenadas ao dicionário de resultado
        resultado["geolocalizacao"]={
            "lat": latlon['lat'],
            "lon": latlon['lon']
        }
        #print("Coordenadas:", latlon)

        #print("Dados do endereço:", resultado)
        
        # Obtendo os dados do clima usando as coordenadas
        clima = controller.obter_clima(latlon['lat'], latlon['lon'])
        #print("Dados do clima:", clima)

        # Adicionando os dados do clima ao resultado
        resultado["clima"]= {
            "temperatura": clima["current_weather"]["temperature"],  # Temperatura
            "windspeed": clima["current_weather"]["windspeed"],  # Velocidade do vento
            "winddirection": clima["current_weather"]["winddirection"],  # Direção do vento
            "is_day": clima["current_weather"]["is_day"],  # Se é dia ou noite
            "weathercode": clima["current_weather"]["weathercode"],  # Código do clima
            "elevation": clima["elevation"],  # Altitude
            "timezone": clima["timezone"],  # Fuso horário
        }
        # Retornando os dados combinados
        return jsonify(resultado)


    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", str(e))
        return jsonify({"erro": "Erro na requisição ao ViaCEP"}), 500

    except Exception as e:
        print("Erro inesperado:", str(e))
        return jsonify({"erro": "Erro no processamento", "detalhes": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)