import json
from pymongo import MongoClient
from pathlib import Path
from bson import json_util
from pymongo.errors import BulkWriteError

MONGO_URI = "mongodb://localhost:27017/"
NOME_BANCO = "Projetos_Daniel_Arthur"
PASTA_DUMP = Path(__file__).parent

ARQUIVOS_JSON = [
    "atividades.json",
    "departamentos.json",
    "funcionarios.json",
    "projetos.json",
    "projetosrelacionamentos.json"
]

def parse_json(content):
    try:
        return json_util.loads(content)
    except:
        return json.loads(content)

def importar_dados():
    client = MongoClient(MONGO_URI)
    db = client[NOME_BANCO]
    
    for nome_arquivo in ARQUIVOS_JSON:
        caminho_arquivo = PASTA_DUMP / nome_arquivo
        nome_colecao = nome_arquivo.split('.')[0]
        
        print(f"\nProcessando: {nome_arquivo}...")
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if content.startswith('['):
                    dados = parse_json(content)
                else:
                    dados = [parse_json(line) for line in content.splitlines() if line.strip()]
                
                if not dados:
                    print("ℹArquivo vazio")
                    continue
                
                if isinstance(dados, list):
                    for doc in dados:
                        if '_id' in doc and isinstance(doc['_id'], dict) and '$oid' in doc['_id']:
                            doc['_id'] = json_util.ObjectId(doc['_id']['$oid'])
                
                try:
                    result = db[nome_colecao].insert_many(dados)
                    print(f"{len(result.inserted_ids)} documentos inseridos")
                except BulkWriteError as e:
                    print(f"Alguns erros ocorreram, mas alguns documentos foram inseridos")
                    print(f"Documentos inseridos: {e.details['nInserted']}")
                    
        except Exception as e:
            print(f"ERRO: {type(e).__name__}: {str(e)}")
            if hasattr(e, 'args') and e.args:
                print(f"Detalhes: {e.args[0]}")

    print("\nColeções criadas:", db.list_collection_names())
    client.close()

if __name__ == "__main__":
    print("Iniciando importação corrigida...")
    importar_dados()