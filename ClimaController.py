# clima_controller.py
import os
import logging
import requests
from flask import request, jsonify

logging.basicConfig(level=logging.INFO)

class ClimaController:

    def buscar(self, cep):
        logging.info(f'Valor recebido: {cep}')

        dados_cep = {}
        coordenadas = {}
        clima = {}

        # 🔹 Consulta ViaCEP
        try:
            dados_cep = self.buscar_endereco_por_cep(cep)
        except Exception as e:
            logging.error(f"Erro ViaCEP: {str(e)}")

        # 🔹 Geocodificação (LocationIQ)
        try:
            if dados_cep:
                endereco = f"{dados_cep.get('logradouro')}, {dados_cep.get('localidade')}, {dados_cep.get('uf')}, Brasil"
                logging.info(f"Endereço para geocodificação: {endereco}")
                coordenadas = self.geocodificar_endereco(endereco)
        except Exception as e:
            logging.error(f"Erro LocationIQ: {str(e)}")

        # 🔹 Clima (Open-Meteo)
        try:
            if coordenadas:
                clima = self.obter_clima(coordenadas['lat'], coordenadas['lon'])
        except Exception as e:
            logging.error(f"Erro Open-Meteo: {str(e)}")

        # 🔹 Resposta final
        return {
            'dadosCep': dados_cep if dados_cep else 'Não encontrado',
            'coordenadas': {
                'latitude': coordenadas.get('lat'),
                'longitude': coordenadas.get('lon'),
                'elevation': clima.get('elevation', 'Não disponível')
            } if coordenadas else 'Não disponível',
            'clima': clima.get('current_weather', 'Clima não encontrado')
        }

    def buscar_endereco_por_cep(self, cep):
        res = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados = res.json()

        if 'erro' in dados:
            raise Exception("CEP inválido")

        return dados

    def geocodificar_endereco(self, endereco):
        api_key = os.getenv("LOCATIONIQ_KEY")

        res = requests.get("https://us1.locationiq.com/v1/search.php", params={
            'key': api_key,
            'q': endereco,
            'format': 'json'
        })

        dados = res.json()

        if 'error' in dados or not dados or 'lat' not in dados[0]:
            raise Exception("Falha na geocodificação")

        return {
            'lat': dados[0]['lat'],
            'lon': dados[0]['lon']
        }

    def obter_clima(self, lat, lon):
        res = requests.get("https://api.open-meteo.com/v1/forecast", params={
            'latitude': lat,
            'longitude': lon,
            'current_weather': True
        })

        return res.json()
