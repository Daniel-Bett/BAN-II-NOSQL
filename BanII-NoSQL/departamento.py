from conector import db
from id_generator import get_next_id_departamento
from pprint import pprint

class Departamento:
    def __init__(self, iddepartamento=None, nmdepartamento=None):
        self.iddepartamento = iddepartamento
        self.nmdepartamento = nmdepartamento

    def inserir(self):
        existe = db['departamentos'].find_one(
            {"nmdepartamento": {"$regex": f"^{self.nmdepartamento}$", "$options": "i"}}
        )
        if existe:
            print("Já existe um departamento com esse nome. Operação cancelada.")
            return

        self.iddepartamento = get_next_id_departamento()

        doc = {
            "iddepartamento": self.iddepartamento,
            "nmdepartamento": self.nmdepartamento
        }
        db['departamentos'].insert_one(doc)
        print(f"Departamento inserido com ID: {self.iddepartamento}")

    @staticmethod
    def listar():
        try:
            departamentos = list(db['departamentos'].find({}, {"_id": 0}))
            pprint(departamentos)
            return departamentos
        except Exception as e:
            print(f"Erro ao listar departamentos: {e}")
            return []

    def atualizar(self):
        if not self.iddepartamento:
            print("ID do departamento não fornecido.")
            return

        filtro = {"iddepartamento": self.iddepartamento}

        existe = db['departamentos'].find_one(
            {"nmdepartamento": {"$regex": f"^{self.nmdepartamento}$", "$options": "i"},
             "iddepartamento": {"$ne": self.iddepartamento}}
        )
        if existe:
            print("Já existe outro departamento com esse nome. Operação cancelada.")
            return

        atualizacao = {"$set": {"nmdepartamento": self.nmdepartamento}}

        resultado = db['departamentos'].update_one(filtro, atualizacao)
        if resultado.matched_count:
            print("Departamento atualizado com sucesso.")
        else:
            print("Departamento não encontrado.")

    def deletar(self):
        if not self.iddepartamento:
            print("ID do departamento não fornecido.")
            return

        resultado = db['departamentos'].delete_one({"iddepartamento": self.iddepartamento})
        if resultado.deleted_count:
            print("Departamento deletado com sucesso.")
        else:
            print("Departamento não encontrado.")
    
    @staticmethod
    def buscar_por_id(iddepartamento):
        departamento = db['departamentos'].find_one({"iddepartamento": iddepartamento}, {"_id": 0})
        if departamento:
            print("Departamento encontrado:")
            from pprint import pprint
            pprint(departamento)
            return departamento
        else:
            print(f"Nenhum departamento encontrado com iddepartamento = {iddepartamento}")
            return None

