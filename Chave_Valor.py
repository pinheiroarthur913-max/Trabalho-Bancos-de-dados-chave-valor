
import json
import sys

import redis

PREFIXO = "aluno:"


def conectar():
    """Cria a conexão com o Redis e testa se o servidor está no ar."""
    cliente = redis.Redis(host="localhost", port=6379,
                          db=0, decode_responses=True)
    try:
        cliente.ping()
    except redis.exceptions.ConnectionError:
        print("Erro: não foi possível conectar ao Redis em localhost:6379.")
        print("Verifique se o servidor está em execução e tente novamente.")
        sys.exit(1)
    return cliente


def montar_chave(matricula):
    return f"{PREFIXO}{matricula.strip()}"


def cadastrar(db):
    """Cadastra (PUT/SET) um registro. Se a chave já existe, pergunta se atualiza."""
    matricula = input("Matrícula (chave): ").strip()
    if not matricula:
        print("A chave não pode ser vazia.")
        return

    chave = montar_chave(matricula)
    if db.exists(chave):
        resp = input(
            "Essa chave já existe. Deseja sobrescrever? (s/n): ").strip().lower()
        if resp != "s":
            print("Operação cancelada.")
            return

    nome = input("Nome: ").strip()
    curso = input("Curso: ").strip()
    email = input("E-mail: ").strip()

    valor = json.dumps({"nome": nome, "curso": curso,
                       "email": email}, ensure_ascii=False)
    db.set(chave, valor)  # operação PUT/SET
    print(f"Registro '{chave}' salvo com sucesso.")


def consultar(db):
    """Consulta (GET) um registro pela chave."""
    matricula = input("Matrícula (chave): ").strip()
    chave = montar_chave(matricula)

    valor = db.get(chave)  # operação GET
    if valor is None:
        print("Nenhum registro encontrado para essa chave.")
        return

    dados = json.loads(valor)
    print(f"\nChave: {chave}")
    print(f"  Nome : {dados.get('nome')}")
    print(f"  Curso: {dados.get('curso')}")
    print(f"  Email: {dados.get('email')}")


def listar(db):
    """Lista todas as chaves cadastradas usando SCAN (não bloqueia o servidor)."""
    chaves = sorted(db.scan_iter(match=f"{PREFIXO}*"))
    if not chaves:
        print("Nenhum registro cadastrado.")
        return

    print(f"\n{len(chaves)} registro(s) encontrado(s):")
    for chave in chaves:
        dados = json.loads(db.get(chave))
        print(f"  {chave} -> {dados.get('nome')} ({dados.get('curso')})")


def excluir(db):
    """Exclui (DELETE) um registro pela chave."""
    matricula = input("Matrícula (chave): ").strip()
    chave = montar_chave(matricula)

    if not db.exists(chave):
        print("Nenhum registro encontrado para essa chave.")
        return

    resp = input(f"Confirma a exclusão de '{chave}'? (s/n): ").strip().lower()
    if resp != "s":
        print("Operação cancelada.")
        return

    db.delete(chave)  # operação DELETE
    print("Registro excluído com sucesso.")


def menu():
    print("\n=== Banco chave-valor (Redis) ===")
    print("1 - Cadastrar")
    print("2 - Consultar")
    print("3 - Listar chaves")
    print("4 - Excluir")
    print("0 - Sair")
    return input("Escolha uma opção: ").strip()


def main():
    db = conectar()
    acoes = {"1": cadastrar, "2": consultar, "3": listar, "4": excluir}

    while True:
        opcao = menu()
        if opcao == "0":
            print("Encerrando.")
            break
        acao = acoes.get(opcao)
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            acao(db)
        except redis.exceptions.RedisError as erro:
            print(f"Erro no banco de dados: {erro}")


if __name__ == "__main__":
    main()
