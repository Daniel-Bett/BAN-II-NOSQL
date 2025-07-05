from pymongo import MongoClient
from pprint import pprint
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")

db = client['Projetos_Daniel_Arthur']

def verificar_conexao():
    try:
        client.server_info()
        print("Conexão com o MongoDB estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"Falha na conexão: {e}")
        return False

def listar_projetos_relacionados():
    try:
        registros = list(db['projetosrelacionamentos'].find())
        return registros
    except Exception as e:
        print(f"Erro ao listar projetos relacionados: {e}")
        return []

def listar_projetos():
    try:
        registros = list(db['projetos'].find())
        return registros
    except Exception as e:
        print(f"Erro ao listar projetos: {e}")
        return []

def listar_funcionarios():
    try:
        registros = list(db['funcionarios'].find())
        return registros
    except Exception as e:
        print(f"Erro ao listar funcionários: {e}")
        return []

def listar_departamentos():
    try:
        registros = list(db['departamentos'].find())
        return registros
    except Exception as e:
        print(f"Erro ao listar departamentos: {e}")
        return []

def listar_atividades():
    try:
        registros = list(db['atividades'].find())
        return registros
    except Exception as e:
        print(f"Erro ao listar atividades: {e}")
        return []
