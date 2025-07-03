import os
from pathlib import Path
from pymongo import MongoClient
from bson.json_util import loads

MONGO_URI = "mongodb://localhost:27017"
NOME_BANCO = "Projetos_Daniel_Arthur"
PASTA_DUMP = Path("projetos_daniel_arthur")

client = MongoClient(MONGO_URI)
db = client[NOME_BANCO]

for arquivo in PASTA_DUMP.glob("*.json"):
    nome_colecao = arquivo.stem
    print(f"Restaurando coleção: {nome_colecao}")

    with open(arquivo, "r", encoding="utf-8") as f:
        documentos = [loads(linha) for linha in f if linha.strip()]

    if documentos:
        db[nome_colecao].insert_many(documentos)

print(f"Banco '{NOME_BANCO}' criado")
