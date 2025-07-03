from conector import db

def get_next_id_atividade():
    """
    Busca o maior idatividade na coleção 'atividades' e retorna +1.
    Se não houver nenhum, retorna 1.
    """
    atividade = db['atividades'].find_one(
        sort=[("idatividade", -1)],
        projection={"idatividade": 1}
    )

    if atividade and "idatividade" in atividade:
        return atividade["idatividade"] + 1
    else:
        return 1

def get_next_id_departamento():
    """
    Busca o maior iddepartamento na coleção 'departamentos' e retorna +1.
    Se não houver nenhum, retorna 1.
    """
    departamento = db['departamentos'].find_one(
        sort=[("iddepartamento", -1)],
        projection={"iddepartamento": 1}
    )
    if departamento and "iddepartamento" in departamento:
        return departamento["iddepartamento"] + 1
    else:
        return 1

def get_next_id_funcionario():
    funcionario = db['funcionarios'].find_one(
        sort=[("idfuncionario", -1)],
        projection={"idfuncionario": 1}
    )
    if funcionario and "idfuncionario" in funcionario:
        return funcionario["idfuncionario"] + 1
    else:
        return 1

def get_next_id_projeto():
    projeto = db['projetos'].find_one(
        sort=[("idprojeto", -1)],
        projection={"idprojeto": 1}
    )
    if projeto and "idprojeto" in projeto:
        return projeto["idprojeto"] + 1
    else:
        return 1
def get_next_id_projetorelacionamento():
    rel = db['projetosrelacionamentos'].find_one(
        sort=[("idrelacionamento", -1)],
        projection={"idrelacionamento": 1}
    )
    if rel and "idrelacionamento" in rel:
        return rel["idrelacionamento"] + 1
    else:
        return 1
