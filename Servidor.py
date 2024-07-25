import socket
import threading
import time

clientes = {}
mensagens_pendentes = {}

def tratar_cliente(conn, addr):
    print(f"Conectado por {addr}")
    with conn:
        while True:
            dados = conn.recv(1024)
            if not dados:
                break
            mensagem = dados.decode('utf-8')
            tratar_mensagem(mensagem, conn)

def tratar_mensagem(mensagem, conn):
    codigo = mensagem[:2]
    if codigo == '01':
        registrar_cliente(conn)
    elif codigo == '03':
        id_cliente = mensagem[2:15]
        conectar_cliente(id_cliente, conn)
    elif codigo == '05':
        tratar_envio_mensagem(mensagem, conn)
    elif codigo == '08':
        tratar_confirmacao_leitura(mensagem, conn)
    elif codigo == '10':
        tratar_criacao_grupo(mensagem, conn)

def registrar_cliente(conn):
    id_cliente = gerar_id_unico()
    clientes[id_cliente] = conn
    conn.sendall(f"02{id_cliente}".encode('utf-8'))

def gerar_id_unico():
    return str(int(time.time() * 1000000))[-13:]

def conectar_cliente(id_cliente, conn):
    clientes[id_cliente] = conn
    if id_cliente in mensagens_pendentes:
        for mensagem in mensagens_pendentes[id_cliente]:
            conn.sendall(mensagem.encode('utf-8'))
        del mensagens_pendentes[id_cliente]

def tratar_envio_mensagem(mensagem, conn):
    origem = mensagem[2:15]
    destino = mensagem[15:28]
    timestamp = mensagem[28:38]
    dados = mensagem[38:]
    if destino in clientes:
        clientes[destino].sendall(f"06{mensagem}".encode('utf-8'))
        conn.sendall(f"07{destino}{timestamp}".encode('utf-8'))
    else:
        if destino not in mensagens_pendentes:
            mensagens_pendentes[destino] = []
        mensagens_pendentes[destino].append(mensagem)
        conn.sendall(f"07{destino}{timestamp}".encode('utf-8'))

def tratar_confirmacao_leitura(mensagem, conn):
    origem = mensagem[2:15]
    timestamp = mensagem[15:25]
    for id_cliente, mensagens in mensagens_pendentes.items():
        mensagens[:] = [msg for msg in mensagens if msg[2:15] != origem or msg[28:38] > timestamp]
    conn.sendall(f"09{origem}{timestamp}".encode('utf-8'))

def tratar_criacao_grupo(mensagem, conn):
    id_grupo = gerar_id_unico()
    criador = mensagem[2:15]
    timestamp = mensagem[15:25]
    membros = [mensagem[i:i+13] for i in range(25, len(mensagem), 13)]
    mensagem_grupo = f"11{id_grupo}{timestamp}{''.join(membros + [criador])}"
    for membro in membros + [criador]:
        if membro in clientes:
            clientes[membro].sendall(mensagem_grupo.encode('utf-8'))
        else:
            if membro not in mensagens_pendentes:
                mensagens_pendentes[membro] = []
            mensagens_pendentes[membro].append(mensagem_grupo)
    
def iniciar_servidor():
    host = '127.0.0.1'
    port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Servidor iniciado, esperando conexões...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor()
