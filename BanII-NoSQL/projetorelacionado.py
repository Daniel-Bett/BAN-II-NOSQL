from conector import db
from id_generator import get_next_id_projetorelacionamento
from pprint import pprint

class ProjetoRelacionado:
    def __init__(self, idprojeto=None, idprojetorelacionado=None, idrelacionamento=None):
        self.idprojeto = idprojeto
        self.idprojetorelacionado = idprojetorelacionado
        self.idrelacionamento = idrelacionamento

    def inserir(self):
        if not self.idprojeto or not self.idprojetorelacionado:
            print("IDs de projeto e projeto relacionado são obrigatórios.")
            return

        self.idrelacionamento = get_next_id_projetorelacionamento()

        doc = {
            "idrelacionamento": self.idrelacionamento,
            "idprojeto": self.idprojeto,
            "idprojetorelacionado": self.idprojetorelacionado
        }

        db['projetosrelacionamentos'].insert_one(doc)
        print(f"Relacionamento inserido com ID: {self.idrelacionamento}")

    @staticmethod
    def listar():
        try:
            relacionamentos = list(
                db['projetosrelacionamentos']
                .find({}, {"_id": 0})
                .sort([("idprojeto", 1), ("idprojetorelacionado", 1)])
            )
            pprint(relacionamentos)
            return relacionamentos
        except Exception as e:
            print(f"Erro ao listar: {e}")
            return []

    @staticmethod
    def buscar_por_id(idrelacionamento):
        relacionamento = db['projetosrelacionamentos'].find_one(
            {"idrelacionamento": idrelacionamento}, {"_id": 0}
        )
        if relacionamento:
            print("Relacionamento encontrado:")
            pprint(relacionamento)
            return relacionamento
        else:
            print(f"Nenhum relacionamento encontrado com id {idrelacionamento}")
            return None

    @staticmethod
    def deletar(idrelacionamento):
        if not idrelacionamento:
            print("ID do relacionamento é obrigatório para exclusão.")
            return

        resultado = db['projetosrelacionamentos'].delete_one(
            {"idrelacionamento": idrelacionamento}
        )
        if resultado.deleted_count:
            print("Relacionamento deletado com sucesso.")
        else:
            print("Relacionamento não encontrado.")

    def atualizar(self, novo_idprojetorelacionado):
        if not self.idrelacionamento:
            print("ID do relacionamento é obrigatório para atualização.")
            return

        relacionamento = db['projetosrelacionamentos'].find_one({"idrelacionamento": self.idrelacionamento})
        if not relacionamento:
            print("❌ Relacionamento não encontrado.")
            return

        projeto_existe = db['projetos'].find_one({"idprojeto": novo_idprojetorelacionado})
        if not projeto_existe:
            print(f"❌ Projeto relacionado com ID {novo_idprojetorelacionado} não encontrado.")
            return

        db['projetosrelacionamentos'].update_one(
            {"idrelacionamento": self.idrelacionamento},
            {"$set": {"idprojetorelacionado": novo_idprojetorelacionado}}
        )
        self.idprojetorelacionado = novo_idprojetorelacionado
        print("Projeto relacionado atualizado com sucesso.")
