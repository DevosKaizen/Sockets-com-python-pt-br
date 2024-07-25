import socket
import time

endereco_servidor = ('127.0.0.1', 65432)
id_cliente = None
contatos = {}

def registrar():
    global id_cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(endereco_servidor)
        s.sendall(b'01')
        dados = s.recv(1024)
        id_cliente = dados.decode('utf-8')[2:]
        print(f"Registrado com ID: {id_cliente}")

def conectar():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(endereco_servidor)
        s.sendall(f"03{id_cliente}".encode('utf-8'))
        while True:
            dados = s.recv(1024)
            if not dados:
                break
            print(f"Recebido: {dados.decode('utf-8')}")

def enviar_mensagem(destino, mensagem):
    timestamp = str(int(time.time()))
    msg = f"05{id_cliente}{destino}{timestamp}{mensagem}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(endereco_servidor)
        s.sendall(msg.encode('utf-8'))

def confirmacao_leitura(origem, timestamp):
    msg = f"08{origem}{timestamp}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(endereco_servidor)
        s.sendall(msg.encode('utf-8'))

def criar_grupo(membros):
    timestamp = str(int(time.time()))
    membros_str = ''.join(membros)
    msg = f"10{id_cliente}{timestamp}{membros_str}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(endereco_servidor)
        s.sendall(msg.encode('utf-8'))

def adicionar_contato(id_contato, nome):
    contatos[nome] = id_contato
    print(f"Contato {nome} adicionado com ID {id_contato}")

def ver_contatos():
    print("Contatos disponíveis:")
    for nome, id_contato in contatos.items():
        print(f"{nome}: {id_contato}")

def menu():
    print("\nMenu:")
    print("1. Criar contato")
    print("2. Ver contatos disponíveis")
    print("3. Criar grupo")
    print("4. Enviar mensagem")
    print("5. Sair")
    escolha = input("Escolha uma opção: ")
    return escolha

def main():
    registrar()
    while True:
        escolha = menu()
        if escolha == '1':
            nome = input("Digite o nome do contato: ")
            id_contato = input("Digite o ID do contato: ")
            adicionar_contato(id_contato, nome)
        elif escolha == '2':
            ver_contatos()
        elif escolha == '3':
            membros = []
            while True:
                nome = input("Digite o nome do membro (ou 'sair' para terminar): ")
                if nome == 'sair':
                    break
                if nome in contatos:
                    membros.append(contatos[nome])
                else:
                    print("Contato não encontrado.")
            criar_grupo(membros)
        elif escolha == '4':
            nome = input("Digite o nome do contato: ")
            if nome in contatos:
                mensagem = input("Digite a mensagem: ")
                enviar_mensagem(contatos[nome], mensagem)
            else:
                print("Contato não encontrado.")
        elif escolha == '5':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
