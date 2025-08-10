from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

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
        print("Resposta do ViaCEP:", res_cep.text)

        if res_cep.status_code != 200:
            return jsonify({"erro": "Erro ao buscar CEP"}), 500

        endereco = res_cep.json()
        if "erro" in endereco:
            return jsonify({"erro": "CEP inválido"}), 400

        # Criar retorno somente com os dados que chegaram
        resultado = {
            "cep": endereco.get("cep"),
            "logradouro": endereco.get("logradouro"),
            "bairro": endereco.get("bairro"),
            "cidade": endereco.get("localidade"),
            "uf": endereco.get("uf"),
            "ddd": endereco.get("ddd"),
            "siafi": endereco.get("siafi"),
            "ibge": endereco.get("ibge")
        }

        return jsonify(resultado)

    except Exception as e:
        print("Erro inesperado:", str(e))
        return jsonify({"erro": "Erro no processamento", "detalhes": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)