from conector import db
from id_generator import get_next_id_atividade
from datetime import date
from pprint import pprint

class Atividade:
    def __init__(self, idatividade=None, nmatividade=None, descricao=None, datainicio=None, datafim=None, situacao=None, idprojeto=None, idresponsavel=None):
        self.idatividade = idatividade
        self.nmatividade = nmatividade
        self.descricao = descricao
        self.datainicio = datainicio
        self.datafim = datafim
        self.situacao = situacao
        self.idprojeto = idprojeto
        self.idresponsavel = idresponsavel

    def inserir(self):
        self.idatividade = get_next_id_atividade()  

        doc = {
            "idatividade": self.idatividade,
            "nmatividade": self.nmatividade,
            "descricao": self.descricao,
            "datainicio": self.datainicio,
            "datafim": self.datafim,
            "situacao": self.situacao,
            "idprojeto": self.idprojeto,
            "idresponsavel": self.idresponsavel
        }

        db['atividades'].insert_one(doc)
        print(f"Atividade inserida com ID: {self.idatividade}")
    
    @staticmethod
    def listar():
        try:
            atividades = list(db['atividades'].find({}, {"_id": 0}))  # ocultar o _id do Mongo
            pprint(atividades)
            return atividades
        except Exception as e:
            print(f"Erro ao listar atividades: {e}")
            return []

    def atualizar(self):
        if not self.idatividade:
            print("ID da atividade não fornecido.")
            return

        filtro = {"idatividade": self.idatividade}
        nova_atividade = {
            "$set": {
                "nmatividade": self.nmatividade,
                "descricao": self.descricao,
                "datainicio": self.datainicio,
                "datafim": self.datafim,
                "situacao": self.situacao,
                "idprojeto": self.idprojeto,
                "idresponsavel": self.idresponsavel
            }
        }

        resultado = db['atividades'].update_one(filtro, nova_atividade)
        if resultado.matched_count:
            print("Atividade atualizada com sucesso.")
        else:
            print("Atividade não encontrada.")

    def deletar(self):
        if not self.idatividade:
            print("ID da atividade não fornecido.")
            return

        resultado = db['atividades'].delete_one({"idatividade": self.idatividade})
        if resultado.deleted_count:
            print("Atividade deletada com sucesso.")
        else:
            print("Atividade não encontrada.")

    def atualizar_situacao(self):
        if not self.idatividade:
            print("ID da atividade não fornecido.")
            return

        atividade = db['atividades'].find_one({"idatividade": self.idatividade})

        if not atividade:
            print("Atividade não encontrada.")
            return

        situacao_atual = atividade.get("situacao", "")
        if situacao_atual == "Encerrado":
            print("A atividade já está encerrada.")
        elif situacao_atual == "Pendente":
            nova_situacao = "Em Andamento"
            db['atividades'].update_one(
                {"idatividade": self.idatividade},
                {"$set": {"situacao": nova_situacao}}
            )
            print("Situação atualizada para Em Andamento.")
        elif situacao_atual == "Em Andamento":
            nova_situacao = "Encerrado"
            datafim = date.today().strftime("%Y-%m-%d")
            db['atividades'].update_one(
                {"idatividade": self.idatividade},
                {"$set": {"situacao": nova_situacao, "datafim": datafim}}
            )
            print("Situação atualizada para Encerrado.")
        else:
            print(f"Situação desconhecida: '{situacao_atual}'")
    
    @staticmethod
    def buscar_por_id(idatividade):
        atividade = db['atividades'].find_one({"idatividade": idatividade}, {"_id": 0})  # Oculta _id
        if atividade:
            print("Atividade encontrada:")
            from pprint import pprint
            pprint(atividade)
            return atividade
        else:
            print(f"Nenhuma atividade encontrada com idatividade = {idatividade}")
            return None

    
    
