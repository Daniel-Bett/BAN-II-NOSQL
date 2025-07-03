from conector import db
from id_generator import get_next_id_projeto
from datetime import date
from pprint import pprint

class Projeto:
    def __init__(self, idprojeto=None, nome=None, descricao=None, datainicio=None, datafim=None, situacao=None, idresponsavel=None):
        self.idprojeto = idprojeto
        self.nome = nome
        self.descricao = descricao
        self.datainicio = datainicio
        self.datafim = datafim
        self.situacao = situacao
        self.idresponsavel = idresponsavel

    def inserir(self):
        self.idprojeto = get_next_id_projeto()
        doc = {
            "idprojeto": self.idprojeto,
            "nome": self.nome,
            "descricao": self.descricao,
            "datainicio": self.datainicio,
            "datafim": self.datafim,
            "situacao": self.situacao,
            "idresponsavel": self.idresponsavel
        }
        db['projetos'].insert_one(doc)
        print(f"Projeto inserido com ID: {self.idprojeto}")

    @staticmethod
    def listar():
        projetos = list(db['projetos'].find({}, {"_id": 0}))
        pprint(projetos)
        return projetos

    @staticmethod
    def buscar_por_id(idprojeto):
        projeto = db['projetos'].find_one({"idprojeto": idprojeto}, {"_id": 0})
        if projeto:
            print("Projeto encontrado:")
            pprint(projeto)
            return projeto
        else:
            print(f"Projeto com ID {idprojeto} não encontrado.")
            return None

    def atualizar(self):
        if not self.idprojeto:
            print("ID do projeto não fornecido.")
            return
        filtro = {"idprojeto": self.idprojeto}
        novos_dados = {
            "$set": {
                "nome": self.nome,
                "descricao": self.descricao,
                "datainicio": self.datainicio,
                "datafim": self.datafim,
                "situacao": self.situacao,
                "idresponsavel": self.idresponsavel
            }
        }
        resultado = db['projetos'].update_one(filtro, novos_dados)
        if resultado.matched_count:
            print("Projeto atualizado com sucesso.")
        else:
            print("Projeto não encontrado.")

    def deletar(self):
        if not self.idprojeto:
            print("ID do projeto não fornecido.")
            return
        resultado = db['projetos'].delete_one({"idprojeto": self.idprojeto})
        if resultado.deleted_count:
            print("Projeto deletado com sucesso.")
        else:
            print("Projeto não encontrado.")

    def atualizar_situacao(self):
        if self.situacao != "Ativo":
            print("Apenas projetos com situação 'Ativo' podem ser encerrados.")
            return
        self.situacao = "Encerrado"
        self.datafim = date.today().strftime("%Y-%m-%d")
        db['projetos'].update_one(
            {"idprojeto": self.idprojeto},
            {"$set": {"situacao": self.situacao, "datafim": self.datafim}}
        )
        print("Situação do projeto atualizada para 'Encerrado'.")

    def atualizar_situacao_suspensa(self):
        if self.situacao != 'Ativo':
            print("O projeto precisa estar 'Ativo' para ser suspenso.")
            return
        self.situacao = 'Suspenso'
        db['projetos'].update_one(
            {"idprojeto": self.idprojeto},
            {"$set": {"situacao": self.situacao}}
        )
        print(f"Projeto {self.idprojeto} agora está 'Suspenso'.")

    def atualizar_situacao_reativar(self):
        if self.situacao != 'Suspenso':
            print("O projeto precisa estar 'Suspenso' para ser reativado.")
            return
        self.situacao = 'Ativo'
        db['projetos'].update_one(
            {"idprojeto": self.idprojeto},
            {"$set": {"situacao": self.situacao}}
        )
        print(f"Projeto {self.idprojeto} agora está 'Ativo'.")

    @staticmethod
    def existe_projeto(nome, datainicio):
        resultado = db['projetos'].find_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}, "datainicio": datainicio}
        )
        return resultado is not None

    @staticmethod
    def existe_nome(nome):
        resultado = db['projetos'].find_one(
            {"nome": {"$regex": f"^{nome}$", "$options": "i"}}
        )
        return resultado is not None
