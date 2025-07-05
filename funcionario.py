from conector import db
from id_generator import get_next_id_funcionario
from pprint import pprint

class Funcionario:
    def __init__(self, idfuncionario=None, nmfuncionario=None, iddepartamento=None):
        self.idfuncionario = idfuncionario
        self.nmfuncionario = nmfuncionario
        self.iddepartamento = iddepartamento

    def inserir(self):
        self.idfuncionario = get_next_id_funcionario()
        doc = {
            "idfuncionario": self.idfuncionario,
            "nmfuncionario": self.nmfuncionario,
            "iddepartamento": self.iddepartamento
        }
        db['funcionarios'].insert_one(doc)
        print(f"Funcionário inserido com ID: {self.idfuncionario}")

    @staticmethod
    def listar():
        try:
            funcionarios = list(db['funcionarios'].find({}, {"_id": 0}))
            pprint(funcionarios)
            return funcionarios
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []

    def atualizar(self):
        if not self.idfuncionario:
            print("ID do funcionário não fornecido.")
            return

        filtro = {"idfuncionario": self.idfuncionario}
        atualizacao = {
            "$set": {
                "nmfuncionario": self.nmfuncionario,
                "iddepartamento": self.iddepartamento
            }
        }
        resultado = db['funcionarios'].update_one(filtro, atualizacao)
        if resultado.matched_count:
            print("Funcionário atualizado com sucesso.")
        else:
            print("Funcionário não encontrado.")

    def deletar(self):
        if not self.idfuncionario:
            print("ID do funcionário não fornecido.")
            return

        resultado = db['funcionarios'].delete_one({"idfuncionario": self.idfuncionario})
        if resultado.deleted_count:
            print("Funcionário deletado com sucesso.")
        else:            print("❌ Funcionário não encontrado.")

    def transferir(self, novo_iddepartamento):
        if not self.idfuncionario:
            print("ID do funcionário não fornecido.")
            return

        resultado = db['funcionarios'].update_one(
            {"idfuncionario": self.idfuncionario},
            {"$set": {"iddepartamento": novo_iddepartamento}}
        )
        if resultado.matched_count:
            print("Funcionário transferido com sucesso.")
            self.iddepartamento = novo_iddepartamento  # atualiza o atributo também
        else:
            print("Funcionário não encontrado.")
    @staticmethod
    def buscar_por_id(idfuncionario):
        funcionario = db['funcionarios'].find_one(
            {"idfuncionario": idfuncionario},
            {"_id": 0}
        )
        if funcionario:
            print("Funcionário encontrado:")
            pprint(funcionario)
            return funcionario
        else:
            print(f"Nenhum funcionário encontrado com idfuncionario = {idfuncionario}")
            return None
