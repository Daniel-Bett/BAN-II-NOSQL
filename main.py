from atividade import Atividade
from departamento import Departamento
from funcionario import Funcionario
from projeto import Projeto
from projetorelacionado import ProjetoRelacionado
from datetime import datetime
from conector import listar_projetos, listar_atividades, listar_funcionarios, listar_departamentos, listar_projetos_relacionados
from conector import db


def buscar_nome_funcionario(idfunc):
    funcionario = db['funcionarios'].find_one({"idfuncionario": idfunc})
    return funcionario['nmfuncionario'] if funcionario else "Desconhecido"

def relatorio_macroprojetos():
    relacionamentos = list(db['projetosrelacionamentos'].find())
    macros_ids = {rel['idprojeto'] for rel in relacionamentos}
    macro_docs = list(db['projetos'].find({"idprojeto": {"$in": list(macros_ids)}}))

    resultados = []
    for macro in macro_docs:
        id_macro = macro.get("idprojeto")
        nome_macro = macro.get("nmprojeto", "Sem nome")
        responsavel = buscar_nome_funcionario(macro.get("idresponsavel"))

        atividades_macro = list(db['atividades'].find({"idprojeto": id_macro}))
        total_macro = len(atividades_macro)
        encerradas_macro = sum(1 for a in atividades_macro if a.get("situacao") == "Encerrado")

        relacionados = [rel['idprojetorelacionado'] for rel in relacionamentos if rel['idprojeto'] == id_macro]
        total_sub = 0
        encerradas_sub = 0
        for id_sub in relacionados:
            atividades_sub = list(db['atividades'].find({"idprojeto": id_sub}))
            total_sub += len(atividades_sub)
            encerradas_sub += sum(1 for a in atividades_sub if a.get("situacao") == "Encerrado")

        total_geral = total_macro + total_sub
        encerradas_geral = encerradas_macro + encerradas_sub
        percentual = round((encerradas_geral / total_geral * 100), 2) if total_geral else 0.0

        resultados.append({
            "idprojetomacro": id_macro,
            "macroprojeto": nome_macro,
            "responsavel_geral": responsavel,
            "quantidade_subprojetos": len(relacionados),
            "perc_macro_projeto": f"{percentual}%"
        })

    return resultados

def menu():
    print("==== Menu de Opções ====")
    print("1 - CRUD")
    print("2 - Operações do Sistema")
    print("3 - Relatórios")
    print("0 - Sair")
    return input("Escolha uma opção: ")

def incluir():
    print("\nEscolha uma tabela para incluir:")
    print("1 - Departamento")
    print("2 - Funcionário")
    print("3 - Atividade")
    print("4 - Projeto Relacionado")
    print("5 - Projeto")
    opcao = input("Escolha a opção: ").strip()

    if opcao == '1':
        op = input("Deseja visualizar os departamentos existentes? (1-Sim 2-Não): ").strip()
        if op == '1':
            departamentos = Departamento.listar()
            for dep in departamentos:
                print(dep)
        nome = input("Digite o nome do novo departamento: ").strip()
        if nome:
            departamento = Departamento(nmdepartamento=nome)
            departamento.inserir()
        else:
            print("Nome inválido.")

    elif opcao == '2':
        nome = input("Digite o nome do novo funcionário: ").strip()
        if not nome:
            print("Erro: O nome do funcionário não pode estar vazio.")
            return
        op = input("Deseja visualizar os departamentos existentes? (1-Sim 2-Não): ").strip()
        if op == '1':
            departamentos = Departamento.listar()
            for dep in departamentos:
                print(dep)
        try:
            iddepartamento = int(input("Digite o ID do departamento: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        departamentos_existentes = Departamento.listar()
        ids_validos = [dep.get('iddepartamento') for dep in departamentos_existentes]
        if iddepartamento not in ids_validos:
            print("Erro: ID de departamento inválido. Nenhum funcionário foi cadastrado.")
        else:
            funcionario = Funcionario(nmfuncionario=nome, iddepartamento=iddepartamento)
            funcionario.inserir()
            print("Funcionário incluído com sucesso!")

    elif opcao == '3':
        nome = input("Digite o nome da atividade: ").strip()
        descricao = input("Digite a descrição da atividade: ").strip()
        while True:
            datainicio = input("Digite a data de início (AAAA-MM-DD): ").strip()
            try:
                datetime.datetime.strptime(datainicio, "%Y-%m-%d")
                break
            except ValueError:
                print("Formato de data inválido. Use o formato AAAA-MM-DD.")
        datafim = None
        situacao = 'Pendente'
        op = input("Deseja visualizar os projetos existentes? (1-Sim 2-Não): ").strip()
        if op == '1':
            projetos = Projeto.listar()
            for proj in projetos:
                print(proj)
        try:
            idprojeto = int(input("Digite o ID do projeto: ").strip())
        except ValueError:
            print("ID de projeto inválido.")
            return
        op = input("Deseja visualizar os funcionários existentes? (1-Sim 2-Não): ").strip()
        if op == '1':
            funcionarios = Funcionario.listar()
            for fun in funcionarios:
                print(fun)
        try:
            idresponsavel = int(input("Digite o ID do responsável: ").strip())
        except ValueError:
            print("ID do responsável inválido.")
            return

        atividades_existentes = Atividade.listar()
        atividade_ja_existe = any(
            a.get('nmatividade', '').strip().lower() == nome.lower() and
            str(a.get('datainicio')) == datainicio and
            a.get('idprojeto') == idprojeto
            for a in atividades_existentes
        )
        if atividade_ja_existe:
            print("Já existe uma atividade com esse nome, data e projeto.")
        else:
            atividade = Atividade(
                nmatividade=nome,
                descricao=descricao,
                datainicio=datainicio,
                datafim=datafim,
                situacao=situacao,
                idprojeto=idprojeto,
                idresponsavel=idresponsavel
            )
            atividade.inserir()
            print("Atividade incluída com sucesso!")

    elif opcao == '4':
        op = input("Deseja visualizar os projetos existentes? (1-Sim 2-Não): ").strip()
        if op == '1':
            projetos = Projeto.listar()
            for proj in projetos:
                print(proj)
        try:
            idprojeto = int(input("Digite o ID do projeto principal: ").strip())
            idprojetorelacionado = int(input("Digite o ID do projeto relacionado: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        projetos_dados = Projeto.listar()
        projetos_ids = [p.get('idprojeto') for p in projetos_dados]

        if idprojeto not in projetos_ids or idprojetorelacionado not in projetos_ids:
            print("Um ou ambos os projetos informados não existem.")
        else:
            situacao_principal = next((p.get('situacao') for p in projetos_dados if p.get('idprojeto') == idprojeto), None)
            if situacao_principal != 'Ativo':
                print("O projeto principal não está ativo.")
            else:
                projeto_relacionado = ProjetoRelacionado(
                    idprojeto=idprojeto,
                    idprojetorelacionado=idprojetorelacionado
                )
                projeto_relacionado.inserir()
                print("Projeto relacionado incluído com sucesso!")

    elif opcao == '5':
        def validar_data(data):
            try:
                datetime.datetime.strptime(data, "%Y-%m-%d")
                return True
            except ValueError:
                return False

        def verificar_funcionario_existente(idfuncionario):
            funcionarios = Funcionario.listar()
            return any(f.get('idfuncionario') == idfuncionario for f in funcionarios)

        nome = input("Digite o nome do projeto: ").strip()
        descricao = input("Digite a descrição do projeto: ").strip()
        while True:
            datainicio = input("Digite a data de início (AAAA-MM-DD): ").strip()
            if validar_data(datainicio):
                break
            else:
                print("Data inválida! Use o formato AAAA-MM-DD.")
        datafim = None
        situacao = 'Ativo'
        while True:
            try:
                idresponsavel = int(input("Digite o ID do responsável: ").strip())
                if verificar_funcionario_existente(idresponsavel):
                    break
                else:
                    print("ID de responsável não encontrado!")
            except ValueError:
                print("ID inválido!")

        if Projeto.existe_projeto(nome, datainicio):
            data_formatada = datetime.datetime.strptime(datainicio, "%Y-%m-%d").strftime("%m/%y")
            novo_nome = f"{nome} ({data_formatada})"
            if Projeto.existe_nome(novo_nome):
                print("Já existe um projeto com esse nome adaptado. Inclusão cancelada.")
                return
            print(f"Projeto já existe com esse nome e data. Nome alterado para: {novo_nome}")
        else:
            novo_nome = nome

        projeto = Projeto(
            nome=novo_nome,
            descricao=descricao,
            datainicio=datainicio,
            datafim=datafim,
            situacao=situacao,
            idresponsavel=idresponsavel
        )
        projeto.inserir()
        print("Projeto incluído com sucesso!")

def remover():
    print("\nEscolha uma tabela para remover:")
    print("1 - Departamento")
    print("2 - Funcionário")
    print("3 - Atividade")
    print("4 - Projeto Relacionado")
    print("5 - Projeto")
    opcao = input("Escolha a opção: ").strip()

    if opcao == '1':
        try:
            iddepartamento = int(input("Digite o ID do departamento a ser removido: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        funcionarios = Funcionario.listar()
        existe_funcionario = any(f.get("iddepartamento") == iddepartamento for f in funcionarios)
        if existe_funcionario:
            print("Não é possível remover o departamento: há funcionários associados.")
        else:
            departamento = Departamento(iddepartamento=iddepartamento)
            departamento.deletar()
            print("Departamento removido com sucesso!")

def remover():
    print("\nEscolha uma tabela para remover:")
    print("1 - Departamento")
    print("2 - Funcionário")
    print("3 - Atividade")
    print("4 - Projeto Relacionado")
    print("5 - Projeto")
    opcao = input("Escolha a opção: ").strip()

    if opcao == '1':
        try:
            iddepartamento = int(input("Digite o ID do departamento a ser removido: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        funcionarios = Funcionario.listar()
        bloqueado = False
        for f in funcionarios:
            if f.get("iddepartamento") == iddepartamento:
                print(f"Funcionário associado ao departamento: {f.get('nmfuncionario')} (ID: {f.get('idfuncionario')})")
                bloqueado = True
        if bloqueado:
            print("Não é possível remover o departamento: há funcionários associados.")
        else:
            departamento = Departamento(iddepartamento=iddepartamento)
            departamento.deletar()
            print("Departamento removido com sucesso!")

    elif opcao == '2':
        try:
            idfuncionario = int(input("Digite o ID do funcionário a ser removido: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        atividades = Atividade.listar()
        projetos = Projeto.listar()
        tem_atividade = any(a.get("idresponsavel") == idfuncionario for a in atividades)
        tem_projeto = any(p.get("idresponsavel") == idfuncionario for p in projetos)

        if tem_atividade or tem_projeto:
            print("Não é possível remover o funcionário: há atividades ou projetos associados.")
        else:
            funcionario = Funcionario(idfuncionario=idfuncionario)
            funcionario.deletar()
            print("Funcionário removido com sucesso!")

    elif opcao == '3':
        try:
            idatividade = int(input("Digite o ID da atividade a ser removida: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        atividade = Atividade(idatividade=idatividade)
        atividade.deletar()
        print("Atividade removida com sucesso!")

    elif opcao == '4':
        try:
            idrelacionamento = int(input("Digite o ID do relacionamento a ser removido: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        relacionados = ProjetoRelacionado.listar()
        existe = any(r.get("idrelacionamento") == idrelacionamento for r in relacionados)
        if not existe:
            print("Relacionamento não encontrado.")
            return

        projeto_relacionado = ProjetoRelacionado()
        projeto_relacionado.deletar(idrelacionamento)
        print("Projeto Relacionado removido com sucesso!")

    elif opcao == '5':
        try:
            idprojeto = int(input("Digite o ID do projeto a ser removido: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        atividades = Atividade.listar()
        relacionados = ProjetoRelacionado.listar()
        tem_atividade = any(a.get("idprojeto") == idprojeto for a in atividades)
        tem_relacionamento = any(
            r.get("idprojeto") == idprojeto or r.get("idprojetorelacionado") == idprojeto for r in relacionados
        )

        if tem_atividade or tem_relacionamento:
            print("Não é possível remover o projeto: há atividades ou relacionamentos associados.")
        else:
            projeto = Projeto(idprojeto=idprojeto)
            projeto.deletar()
            print("Projeto removido com sucesso!")

def consultar():
    print("\nEscolha uma tabela para consultar:")
    print("1 - Departamento")
    print("2 - Funcionário")
    print("3 - Atividade")
    print("4 - Projeto Relacionado")
    print("5 - Projeto")
    opcao = input("Escolha a opção: ")

    if opcao == '1':
        departamentos = Departamento.listar()
    elif opcao == '2':
        funcionarios = Funcionario.listar()
    elif opcao == '3':
        atividades = Atividade.listar()
        
    elif opcao == '4':
        projetos_relacionados = ProjetoRelacionado.listar()
        
    elif opcao == '5':
        projetos = Projeto.listar()
        
def atualizar():
    print("\nEscolha uma tabela para atualizar:")
    print("1 - Departamento")
    print("2 - Funcionário")
    print("3 - Atividade")
    print("4 - Projeto Relacionado")
    print("5 - Projeto")
    opcao = input("Escolha a opção: ").strip()

    if opcao == '1':
        try:
            iddepartamento = int(input("Digite o ID do departamento a ser atualizado: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        nome = input("Digite o novo nome do departamento: ").strip()
        departamento = Departamento(iddepartamento=iddepartamento, nmdepartamento=nome)
        departamento.atualizar()
        print("Departamento atualizado com sucesso!")

    elif opcao == '2':
        try:
            idfuncionario = int(input("Digite o ID do funcionário a ser atualizado: ").strip())
            iddepartamento = int(input("Digite o novo ID do departamento: ").strip())
        except ValueError:
            print("ID inválido.")
            return
        nome = input("Digite o novo nome do funcionário: ").strip()
        funcionario = Funcionario(idfuncionario=idfuncionario, nmfuncionario=nome, iddepartamento=iddepartamento)
        funcionario.atualizar()
        print("Funcionário atualizado com sucesso!")

    elif opcao == '3':
        try:
            idatividade = int(input("Digite o ID da atividade a ser atualizada: ").strip())
            idprojeto = int(input("Digite o novo ID do projeto: ").strip())
            idresponsavel = int(input("Digite o novo ID do responsável: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        nome = input("Digite o novo nome da atividade: ").strip()
        descricao = input("Digite a nova descrição: ").strip()
        datainicio = input("Digite a nova data de início (AAAA-MM-DD): ").strip()
        datafim = input("Digite a nova data de fim (AAAA-MM-DD): ").strip()
        situacao = input("Digite a nova situação da atividade: ").strip()

        atividade = Atividade(idatividade=idatividade, nmatividade=nome, descricao=descricao,
                              datainicio=datainicio, datafim=datafim, situacao=situacao,
                              idprojeto=idprojeto, idresponsavel=idresponsavel)
        atividade.atualizar()
        print("Atividade atualizada com sucesso!")

    elif opcao == '4':
        try:
            idrelacionamento = int(input("Digite o ID do relacionamento a ser atualizado: ").strip())
            idprojeto = int(input("Digite o ID do projeto principal: ").strip())
            idprojetorelacionado = int(input("Digite o novo ID do projeto relacionado: ").strip())
        except ValueError:
            print("ID inválido. Todos os IDs devem ser números inteiros.")
            return

        projetos = Projeto.listar()
        ids_projetos = [p.get('idprojeto') for p in projetos]

        if idprojeto not in ids_projetos or idprojetorelacionado not in ids_projetos:
            print("Um ou ambos os projetos não existem.")
            return

        situacao_principal = next((p.get('situacao') for p in projetos if p.get('idprojeto') == idprojeto), None)
        if situacao_principal != 'Ativo':
            print("O projeto principal não está ativo.")
            return

        projeto_relacionado = ProjetoRelacionado(idprojeto=idprojeto, idprojetorelacionado=idprojetorelacionado, idrelacionamento=idrelacionamento)
        projeto_relacionado.atualizar(idrelacionamento)
        print("Projeto Relacionado atualizado com sucesso!")

    elif opcao == '5':
        try:
            idprojeto = int(input("Digite o ID do projeto a ser atualizado: ").strip())
            idresponsavel = int(input("Digite o novo ID do responsável: ").strip())
        except ValueError:
            print("ID inválido.")
            return

        nome = input("Digite o novo nome do projeto: ").strip()
        descricao = input("Digite a nova descrição do projeto: ").strip()
        datainicio = input("Digite a nova data de início (AAAA-MM-DD): ").strip()
        datafim = input("Digite a nova data de fim (AAAA-MM-DD): ").strip()
        situacao = input("Digite a nova situação do projeto: ").strip()

        projeto = Projeto(idprojeto=idprojeto, nome=nome, descricao=descricao,
                        datainicio=datainicio, datafim=datafim, situacao=situacao,
                        idresponsavel=idresponsavel)
        projeto.atualizar()
        print("Projeto atualizado com sucesso!")

def menu_crud():
    print("\n==== Menu CRUD ====")
    print("1 - Incluir")
    print("2 - Remover")
    print("3 - Consultar")
    print("4 - Atualizar")
    print("0 - Voltar")
    return input("Escolha uma opção: ").strip()

def operacoes_especiais():
    while True:
        print("\n==== Operações Especiais ====")
        print("1 - Transferir Funcionário de Departamento")
        print("2 - Criar Atividade com Estado Inicial")
        print("3 - Executar Atividade")
        print("4 - Criar Projeto com Situação 'Ativo'")
        print("5 - Executar Projeto")
        print("6 - Suspender Projeto")
        print("7 - Reativar Projeto")
        print("8 - Relacionar Projetos")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha a opção: ").strip()

        if opcao == '1':
            try:
                idfuncionario = int(input("ID do funcionário a ser transferido: ").strip())
                funcionarios = Funcionario.listar()
                if not any(f.get('idfuncionario') == idfuncionario for f in funcionarios):
                    print("Funcionário não encontrado.")
                    continue
                idnovo_departamento = int(input("Novo ID de departamento: ").strip())
                funcionario = Funcionario(idfuncionario=idfuncionario)
                funcionario.transferir(idnovo_departamento)
                print("Funcionário transferido com sucesso!")
            except ValueError:
                print("Entrada inválida. Use apenas números inteiros.")

        elif opcao == '2':
            while True:
                nome = input("Digite o nome da atividade: ").strip()
                descricao = input("Digite a descrição da atividade: ").strip()
                while True:
                    datainicio = input("Digite a data de início (AAAA-MM-DD): ").strip()
                    try:
                        datetime.strptime(datainicio, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Formato de data inválido. Use o formato AAAA-MM-DD.")

                datafim = None
                situacao = input("Situação inicial (Pendente ou Em Andamento): ").strip()
                if situacao not in ["Pendente", "Em Andamento"]:
                    print("Situação inválida.")
                    continue

                if input("Deseja visualizar os projetos existentes? 1-Sim 2-Nao: ").strip() == '1':
                    Projeto.listar()
                        
                try:
                    idprojeto = int(input("Digite o ID do projeto: ").strip())
                except ValueError:
                    print("ID de projeto inválido.")
                    continue

                if input("Deseja visualizar os funcionários existentes? 1-Sim 2-Nao: ").strip() == '1':
                    Funcionario.listar()
                try:
                    idresponsavel = int(input("Digite o ID do responsável: ").strip())
                except ValueError:
                    print("ID do responsável inválido.")
                    continue

                if any(
                    a.get('nmatividade', '').strip().lower() == nome.lower() and
                    str(a.get('datainicio')) == datainicio and
                    a.get('idprojeto') == idprojeto
                    for a in Atividade.listar()
                ):
                    print("Já existe uma atividade com esse nome, data e projeto.")
                    continue
                else:
                    atividade = Atividade(
                        nmatividade=nome,
                        descricao=descricao,
                        datainicio=datainicio,
                        datafim=datafim,
                        situacao=situacao,
                        idprojeto=idprojeto,
                        idresponsavel=idresponsavel
                    )
                    atividade.inserir()
                    print("Atividade incluída com sucesso!")
                    break  

        elif opcao == '3':
            atividades = Atividade.listar()
            for a in atividades:
                print(a)
            try:
                idatividade = int(input("ID da atividade: ").strip())
                if not any(a.get('idatividade') == idatividade for a in atividades):
                    print("Atividade não encontrada.")
                    continue
                atividade = Atividade(idatividade=idatividade)
                atividade.atualizar_situacao()
                print("Situação da atividade atualizada com sucesso!")
            except ValueError:
                print("ID inválido.")

        elif opcao == '4':
            def validar_data(data):
                try:
                    datetime.strptime(data, "%Y-%m-%d")
                    return True
                except ValueError:
                    return False
            def verificar_funcionario_existente(idfuncionario):
                return any(f.get('idfuncionario') == idfuncionario for f in Funcionario.listar())

            nome = input("Digite o nome do projeto: ").strip()
            descricao = input("Digite a descrição do projeto: ").strip()
            while True:
                datainicio = input("Digite a data de início (AAAA-MM-DD): ").strip()
                if validar_data(datainicio):
                    break
                else:
                    print("Data inválida! Use o formato AAAA-MM-DD.")
            datafim = None
            situacao = 'Ativo'
            while True:
                try:
                    idresponsavel = int(input("Digite o ID do responsável: ").strip())
                    if verificar_funcionario_existente(idresponsavel):
                        break
                    else:
                        print("ID de responsável inválido!")
                except ValueError:
                    print("ID inválido!")

            if Projeto.existe_projeto(nome, datainicio):
                data_formatada = datetime.datetime.strptime(datainicio, "%Y-%m-%d").strftime("%m/%y")
                novo_nome = f"{nome} ({data_formatada})"
                if Projeto.existe_nome(novo_nome):
                    print("Já existe um projeto com esse nome adaptado. Inclusão cancelada.")
                    return
                print(f"Projeto já existe com esse nome e data. Nome alterado para: {novo_nome}")
            else:
                novo_nome = nome

            projeto = Projeto(nome=novo_nome, descricao=descricao, datainicio=datainicio, datafim=datafim, situacao=situacao, idresponsavel=idresponsavel)
            projeto.inserir()
            print("Projeto incluído com sucesso!")

        elif opcao == '5':
            try:
                idprojeto = int(input("Digite o ID do projeto a ser encerrado: ").strip())
            except ValueError:
                print("ID inválido.")
                return

            dados = Projeto.buscar_por_id(idprojeto)
            if not dados:
                print("❌ Projeto não encontrado.")
                return

            projeto = Projeto(
                idprojeto=dados.get("idprojeto"),
                nome=dados.get("nome"),
                descricao=dados.get("descricao"),
                datainicio=dados.get("datainicio"),
                datafim=dados.get("datafim"),
                situacao=dados.get("situacao"),
                idresponsavel=dados.get("idresponsavel")
            )

            projeto.atualizar_situacao()

        elif opcao == '6':
            Projeto.listar()

            try:
                idprojeto = int(input("ID do projeto: ").strip())
            except ValueError:
                print("ID inválido.")
                return

            dados = Projeto.buscar_por_id(idprojeto)
            if not dados:
                print("Projeto não encontrado.")
                return

            projeto = Projeto(
                idprojeto=dados.get("idprojeto"),
                nome=dados.get("nome") or dados.get("nmprojeto"),
                descricao=dados.get("descricao"),
                datainicio=dados.get("datainicio"),
                datafim=dados.get("datafim"),
                situacao=dados.get("situacao"),
                idresponsavel=dados.get("idresponsavel")
            )

            projeto.atualizar_situacao_suspensa()
    
        elif opcao == '7':
            for p in Projeto.listar():
                print(p)
            try:
                idprojeto = int(input("ID do projeto: ").strip())
            except ValueError:
                print("ID inválido.")
                return

            dados = Projeto.buscar_por_id(idprojeto)
            if not dados:
                print("Projeto não encontrado.")
                return

            projeto = Projeto(
                idprojeto=dados.get("idprojeto"),
                nome=dados.get("nome") or dados.get("nmprojeto"),
                descricao=dados.get("descricao"),
                datainicio=dados.get("datainicio"),
                datafim=dados.get("datafim"),
                situacao=dados.get("situacao"),
                idresponsavel=dados.get("idresponsavel")
            )

            projeto.atualizar_situacao_reativar()

        elif opcao == '8':
            for proj in Projeto.listar():
                print(proj)
            try:
                idprojeto = int(input("Digite o ID do projeto principal: ").strip())
                idprojetorelacionado = int(input("Digite o ID do projeto a ser relacionado: ").strip())
            except ValueError:
                print("ID inválido.")
                continue

            projetos_dados = Projeto.listar()
            ids_projetos = [p.get('idprojeto') for p in projetos_dados]

            if idprojeto not in ids_projetos or idprojetorelacionado not in ids_projetos:
                print("Um ou ambos os projetos informados não existem.")
                continue

            situacao_principal = next((p.get('situacao') for p in projetos_dados if p.get('idprojeto') == idprojeto), None)
            if situacao_principal not in ['Ativo', 'Pendente']:
                print("O projeto principal não está em execução.")
                continue

            projeto_relacionado = ProjetoRelacionado(idprojeto=idprojeto, idprojetorelacionado=idprojetorelacionado)
            projeto_relacionado.inserir()
            print("Projeto Relacionado incluído com sucesso!")

        elif opcao == '0':
            break
        else:
            print("Opção inválida.")

def menu_relatorios():
    while True:
        print("\n====== Submenu: Relatórios ======")
        print("1 - Percentual de conclusão do Projeto por responsável")
        print("2 - Projetos sem atividades associadas")
        print("3 - Departamento, Funcionários, projetos e atividades")
        print("4 - Atividades em período determinado")
        print("5 - Percentual de atividades concluídas por departamento")
        print("6 - Responsáveis por projetos com percentual de conclusão")
        print("7 - Percentual de conclusão de macroprojetos")
        print("8 - Percentual de atividades por responsável")
        print("9 - Percentual de conclusão de atividades por funcionário")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\n--- Percentual de conclusão do Projeto por responsável ---")
            projetos = listar_projetos()
            atividades = listar_atividades()
            funcionarios = {f['idfuncionario']: f['nmfuncionario'] for f in listar_funcionarios()}

            for p in projetos:
                idprojeto = p['idprojeto']
                nome_projeto = p.get('nmprojeto', p.get('nome', ''))
                responsavel = funcionarios.get(p['idresponsavel'], 'Desconhecido')
                atvs = [a for a in atividades if a['idprojeto'] == idprojeto]
                total = len(atvs)
                finalizadas = len([a for a in atvs if a['situacao'] == 'Encerrado'])
                percentual = f"{(finalizadas / total * 100):.2f}%" if total else "0%"
                print(f"Projeto: {nome_projeto} | Responsável: {responsavel} | Total: {total} | Finalizadas: {finalizadas} | %: {percentual}")

        elif opcao == '2':
            print("\n--- Projetos sem atividades associadas ---")
            projetos = listar_projetos()
            atividades = listar_atividades()
            atividades_ids = {a['idprojeto'] for a in atividades}
            funcionarios = {f['idfuncionario']: f['nmfuncionario'] for f in listar_funcionarios()}

            for p in projetos:
                if p['idprojeto'] not in atividades_ids:
                    nome_projeto = p.get('nmprojeto', p.get('nome', ''))
                    responsavel = funcionarios.get(p['idresponsavel'], 'Desconhecido')
                    print(f"Projeto: {nome_projeto} | Responsável: {responsavel} | Nenhuma atividade")

        elif opcao == '3':
            print("\n--- Departamento, Funcionários, projetos e atividades ---")
            departamentos = {d['iddepartamento']: d['nmdepartamento'] for d in listar_departamentos()}
            funcionarios = {f['idfuncionario']: f for f in listar_funcionarios()}
            projetos = listar_projetos()
            atividades = listar_atividades()

            for a in atividades:
                projeto = next((p for p in projetos if p['idprojeto'] == a['idprojeto']), {})
                resp_proj = funcionarios.get(projeto.get('idresponsavel'), {})
                executor = funcionarios.get(a['idresponsavel'], {})
                print(f"Projeto: {projeto.get('nmprojeto', projeto.get('nome', ''))} | Resp.Projeto: {resp_proj.get('nmfuncionario')} ({departamentos.get(resp_proj.get('iddepartamento'))}) | Atividade: {a.get('nmatividade')} | Executor: {executor.get('nmfuncionario')} ({departamentos.get(executor.get('iddepartamento'))}) | Data: {a.get('datainicio')} - {a.get('datafim')} | Situação: {a.get('situacao')}")

        elif opcao == '4':
            def validar_data(data):
                try:
                    return datetime.strptime(data, "%Y-%m-%d")
                except ValueError:
                    return None
            
            while True:
                data_inicio = input("Informe a data inicial (AAAA-MM-DD): ").strip()
                inicio = validar_data(data_inicio)
                if inicio:
                    break
                print("Data inicial inválida. Use o formato AAAA-MM-DD.")

            while True:
                data_fim = input("Informe a data final (AAAA-MM-DD): ").strip()
                fim = validar_data(data_fim)
                if fim:
                    break
                print("Data final inválida. Use o formato AAAA-MM-DD.")

            atividades = listar_atividades()
            funcionarios = listar_funcionarios()
            departamentos = listar_departamentos()
            projetos = listar_projetos()

            encontrados = []
            for a in atividades:
                if isinstance(a.get("datainicio"), str):
                    try:
                        a["datainicio"] = datetime.strptime(a["datainicio"], "%Y-%m-%d")
                    except Exception:
                        continue
                if isinstance(a.get("datafim"), str):
                    try:
                        a["datafim"] = datetime.strptime(a["datafim"], "%Y-%m-%d")
                    except Exception:
                        continue

                if not a.get("datainicio") or not a.get("datafim"):
                    continue
                if not (inicio <= a["datainicio"] <= fim and inicio <= a["datafim"] <= fim):
                    continue

                projeto = next((p for p in projetos if p["idprojeto"] == a["idprojeto"]), None)
                executor = next((f for f in funcionarios if f["idfuncionario"] == a["idresponsavel"]), None)
                dept_executor = next((d for d in departamentos if d["iddepartamento"] == executor["iddepartamento"]), {}) if executor else {}

                encontrados.append({
                    "idprojeto": projeto["idprojeto"] if projeto else None,
                    "nmprojeto": projeto.get("nmprojeto") or projeto.get("nome"),
                    "nmatividade": a["nmatividade"],
                    "executor": executor["nmfuncionario"] if executor else "Desconhecido",
                    "departamento_executor": dept_executor.get("nmdepartamento", "Desconhecido"),
                    "datainicio": a["datainicio"].strftime("%Y-%m-%d"),
                    "datafim": a["datafim"].strftime("%Y-%m-%d"),
                    "situacao_atividade": a["situacao"],
                    "situacao_projeto": projeto["situacao"] if projeto else "Desconhecida"
                })

            if encontrados:
                print("\nAtividades executadas no período:")
                print("Projeto | Atividade | Executor | Departamento | Início | Fim | Situação Atividade | Situação Projeto")
                for r in encontrados:
                    print(f"{r['nmprojeto']} | {r['nmatividade']} | {r['executor']} | {r['departamento_executor']} | {r['datainicio']} | {r['datafim']} | {r['situacao_atividade']} | {r['situacao_projeto']}")
            else:
                print("Nenhuma atividade encontrada no período.")
        elif opcao == '5':
            atividades = listar_atividades()
            funcionarios = listar_funcionarios()
            departamentos = listar_departamentos()
            projetos = listar_projetos()
            resultado = {}
            for a in atividades:
                idprojeto = a.get("idprojeto")
                projeto = next((p for p in projetos if p["idprojeto"] == idprojeto), None)
                if not projeto:
                    continue

                responsavel = next((f for f in funcionarios if f["idfuncionario"] == projeto.get("idresponsavel")), None)
                if not responsavel:
                    continue

                departamento = next((d for d in departamentos if d["iddepartamento"] == responsavel["iddepartamento"]), None)
                if not departamento:
                    continue

                nome = departamento["nmdepartamento"]

                if nome not in resultado:
                    resultado[nome] = {"total": 0, "finalizado": 0}

                resultado[nome]["total"] += 1
                if a["situacao"] == "Encerrado":
                    resultado[nome]["finalizado"] += 1

            print("Departamento | Atividades Totais | Finalizadas | Percentual")
            print("-" * 80)
            for nome, dados in resultado.items():
                percentual = round((dados["finalizado"] / dados["total"] * 100), 2) if dados["total"] > 0 else 0
                print(f"{nome} | {dados['total']} | {dados['finalizado']} | {percentual}%")

        elif opcao == '6':
            atividades = listar_atividades()
            funcionarios = listar_funcionarios()
            projetos = listar_projetos()

            resultado = {}

            for projeto in projetos:
                idresponsavel = projeto.get("idresponsavel")
                if not idresponsavel:
                    continue

                funcionario = next((f for f in funcionarios if f["idfuncionario"] == idresponsavel), None)
                if not funcionario:
                    continue

                nome = funcionario["nmfuncionario"]

                atividades_do_projeto = [a for a in atividades if a["idprojeto"] == projeto["idprojeto"]]

                total = len(atividades_do_projeto)
                finalizadas = len([a for a in atividades_do_projeto if a["situacao"] == "Encerrado"])

                if nome not in resultado:
                    resultado[nome] = {"total": 0, "finalizado": 0}

                resultado[nome]["total"] += total
                resultado[nome]["finalizado"] += finalizadas

            print("Responsável | Atividades Totais | Finalizadas | Percentual")
            print("-" * 80)
            for nome, dados in resultado.items():
                percentual = round((dados["finalizado"] / dados["total"] * 100), 2) if dados["total"] > 0 else 0
                print(f"{nome} | {dados['total']} | {dados['finalizado']} | {percentual}%")

        elif opcao == '7':
            try:
                resultados = relatorio_macroprojetos()
                if resultados:
                    print("idprojetomacro | macroprojeto | responsavel_geral | quantidade_subprojetos | perc_macro_projeto")
                    print("-" * 100)
                    for r in resultados:
                        print(f"{r['idprojetomacro']} | {r['macroprojeto']} | {r['responsavel_geral']} | {r['quantidade_subprojetos']} | {r['perc_macro_projeto']}")
                else:
                    print("Nenhum macroprojeto encontrado.")
            except Exception as e:
                print(f"Erro ao gerar relatório: {e}")

        elif opcao == '8':
            atividades = listar_atividades()
            funcionarios = listar_funcionarios()

            resultado = {}
            for a in atividades:
                executor = next((f for f in funcionarios if f["idfuncionario"] == a["idresponsavel"]), None)
                if not executor:
                    continue

                nome = executor["nmfuncionario"]
                if nome not in resultado:
                    resultado[nome] = {"total": 0, "finalizado": 0}

                resultado[nome]["total"] += 1
                if a["situacao"] == "Encerrado":
                    resultado[nome]["finalizado"] += 1

            print("Executor | Atividades Totais | Finalizadas | Pendentes | Percentual")
            print("-" * 80)
            for nome, dados in resultado.items():
                pendentes = dados["total"] - dados["finalizado"]
                percentual = round((dados["finalizado"] / dados["total"] * 100), 2) if dados["total"] > 0 else 0
                print(f"{nome} | {dados['total']} | {dados['finalizado']} | {pendentes} | {percentual}%")

        elif opcao == '9':
            atividades = listar_atividades()
            funcionarios = listar_funcionarios()
            departamentos = listar_departamentos()

            resultado = []

            for f in funcionarios:
                nome = f["nmfuncionario"]
                departamento = next((d for d in departamentos if d["iddepartamento"] == f["iddepartamento"]), {})

                atividades_f = [a for a in atividades if a["idresponsavel"] == f["idfuncionario"]]
                total = len(atividades_f)
                finalizado = len([a for a in atividades_f if a["situacao"] == "Encerrado"])

                percentual = round((finalizado / total * 100), 2) if total > 0 else 0

                resultado.append({
                    "departamento": departamento.get("nmdepartamento", "Desconhecido"),
                    "funcionario": nome,
                    "percentual": percentual
                })

            print("Departamento | Funcionário | Percentual")
            print("-" * 50)
            for r in resultado:
                print(f"{r['departamento']} | {r['funcionario']} | {r['percentual']}%")


        elif opcao == '0':
            break
        else:
            print("Opção inválida.")


def main():
    while True:
        print("\n==== Menu Principal ====")
        print("1 - CRUD")
        print("2 - Operações do Sistema")  
        print("3 - Relatórios")             
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            while True:
                opcao_crud = menu_crud()
                if opcao_crud == '1':
                    incluir()
                elif opcao_crud == '2':
                    remover()
                elif opcao_crud == '3':
                    consultar()
                elif opcao_crud == '4':
                    atualizar()
                elif opcao_crud == '0':
                    break  
                else:
                    print("Opção inválida. Tente novamente.")
        elif opcao == '2':
            operacoes_especiais()
        elif opcao == '3':
            menu_relatorios()
        elif opcao == '0':
            print("Saindo do programa. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
