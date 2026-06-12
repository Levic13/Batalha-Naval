import random

LINHAS = 5
COLUNAS = 10

NAVIOS = [
    ("Porta-avioes", 5),
    ("Navio-tanque", 4),
    ("Contratorpedeiro", 3),
    ("Submarino", 2),
    ("Lancha", 1),
]

# 0=agua, 1=navio, 2=acerto, 3=erro
SIMBOLOS = [" . ", " # ", " X ", " O "]


def criar_tabuleiro():
    tabuleiro = []

    for i in range(LINHAS):
        linha = []
        for j in range(COLUNAS):
            linha.append(0)      # 0 = agua
        tabuleiro.append(linha)

    return tabuleiro


tab_jogador = criar_tabuleiro()  # navios do jogador
tab_maquina = criar_tabuleiro()  # navios da maquina
tab_ataques = criar_tabuleiro()  # o que o jogador ve do inimigo

navios_jogador = []
navios_maquina = []


def mostrar_tabuleiro(tabuleiro, titulo):
    print(f"\n--- {titulo} ---")
    cabecalho = "    "

    for c in range(COLUNAS):
        cabecalho += f"{c}  "
    print(cabecalho)

    for l in range(LINHAS):
        linha_str = f"{l}  "
        for c in range(COLUNAS):
            linha_str += SIMBOLOS[tabuleiro[l][c]]
        print(linha_str)
    print()


def ler_uma_coordenada(texto):
    partes = texto.strip().split(",")

    if len(partes) != 2:
        return -1, -1
    parte0 = partes[0].strip()
    parte1 = partes[1].strip()

    if not parte0.isdigit() or not parte1.isdigit():
        return -1, -1
    return int(parte0), int(parte1)


def calcular_celulas(l1, c1, l2, c2):
    celulas = []

    if l1 == l2:  # mesma linha -> navio horizontal
        if c1 <= c2:
            inicio = c1
            fim = c2

        else:
            inicio = c2
            fim = c1

        for c in range(inicio, fim + 1):
            celulas.append([l1, c])
        return celulas

    elif c1 == c2:  # mesma coluna -> navio vertical
        if l1 <= l2:
            inicio = l1
            fim = l2

        else:
            inicio = l2
            fim = l1

        for l in range(inicio, fim + 1):
            celulas.append([l, c1])
        return celulas
    return None  # linhas e colunas diferentes = diagonal


def posicionamento_valido(tabuleiro, celulas, tamanho, silencioso=False):
    # celulas == None significa que o jogador digitou uma diagonal
    if celulas is None:
        if not silencioso:
            print("  Erro: O navio deve ser reto (horizontal ou vertical)!")
        return False
    
    # o numero de celulas calculadas deve bater exatamente com o tamanho do navio
    if len(celulas) != tamanho:
        if not silencioso:
            print(f"  Erro: O navio precisa de exatamente {tamanho} casas.")
        return False
    
    # verifica cada celula individualmente: limites do tabuleiro e sobreposicao
    for i in range(len(celulas)):
        l = celulas[i][0]
        c = celulas[i][1]
        if l < 0 or l >= LINHAS or c < 0 or c >= COLUNAS:
            if not silencioso:
                print(f"  Erro: Fora do campo! Linhas 0-{LINHAS-1}, Colunas 0-{COLUNAS-1}.")
            return False
        if tabuleiro[l][c] != 0:  # != 0 significa que ja tem algo nessa celula
            if not silencioso:
                print("  Erro: Ja tem um navio nessa posicao!")
            return False
    return True


def posicionar_navio_jogador(nome, tamanho):
    while True:
        print(f"Posicione seu {nome} (tamanho {tamanho}): ", end="")
        entrada = input()

        partes = entrada.strip().split()
        if len(partes) != 2:
            print("  Use: linha,coluna linha,coluna  (ex: 0,0 0,4)")
            continue

        l1, c1 = ler_uma_coordenada(partes[0])
        l2, c2 = ler_uma_coordenada(partes[1])
        if l1 == -1 or l2 == -1:
            print("  Coordenadas invalidas!")
            continue

        celulas = calcular_celulas(l1, c1, l2, c2)
        if not posicionamento_valido(tab_jogador, celulas, tamanho):
            continue

        for i in range(len(celulas)):
            l = celulas[i][0]
            c = celulas[i][1]
            tab_jogador[l][c] = 1
        navios_jogador.append(celulas)
        break


def posicionar_navios_maquina():
    for i in range(len(NAVIOS)):
        tamanho = NAVIOS[i][1]

        while True:
            horizontal = random.choice([True, False])
            celulas = []
            if horizontal:
                l = random.randint(0, LINHAS - 1)
                # limita a coluna inicial para o navio nao ultrapassar a borda direita
                c = random.randint(0, COLUNAS - tamanho)
                for j in range(tamanho):
                    celulas.append([l, c + j])

            else:
                # limita a linha inicial para o navio nao ultrapassar a borda inferior
                l = random.randint(0, LINHAS - tamanho)
                c = random.randint(0, COLUNAS - 1)
                for j in range(tamanho):
                    celulas.append([l + j, c])

            # tenta de novo se a posicao sortear conflito com outro navio
            if posicionamento_valido(tab_maquina, celulas, tamanho, silencioso=True):
                for j in range(len(celulas)):
                    ll = celulas[j][0]
                    cc = celulas[j][1]
                    tab_maquina[ll][cc] = 1
                navios_maquina.append(celulas)
                break


def ja_atirou_aqui(lista_tiros, l, c):
    for i in range(len(lista_tiros)):
        if lista_tiros[i][0] == l and lista_tiros[i][1] == c:
            return True
    return False


def contar_navios_vivos(navios, tabuleiro):
    vivos = 0

    for i in range(len(navios)):
        navio = navios[i]
        navio_vivo = False

        # percorre cada celula do navio; se alguma ainda nao foi acertada (!=2), ele continua vivo
        for j in range(len(navio)):
            l = navio[j][0]
            c = navio[j][1]
            if tabuleiro[l][c] != 2:
                navio_vivo = True
                break  # basta uma celula intacta para o navio estar vivo

        if navio_vivo:
            vivos = vivos + 1
    return vivos


def ataque_jogador(ja_atirou):
    while True:
        print("Seu ataque (linha,coluna): ", end="")
        entrada = input()
        l, c = ler_uma_coordenada(entrada)
        if l == -1:
            print("  Use: linha,coluna  (ex: 2,5)")
            continue

        if l < 0 or l >= LINHAS or c < 0 or c >= COLUNAS:
            print(f"  Fora do campo! Linhas 0-{LINHAS-1}, Colunas 0-{COLUNAS-1}.")
            continue
        if ja_atirou_aqui(ja_atirou, l, c):
            print("  Voce ja atirou aqui! Escolha outra posicao.")
            continue

        ja_atirou.append([l, c])
        if tab_maquina[l][c] == 1:
            tab_maquina[l][c] = 2
            tab_ataques[l][c] = 2
            print("  >>> ACERTOU! <<<")
        else:
            tab_ataques[l][c] = 3
            print("  Agua...")
        break


def ataque_maquina(ja_atirou):
    # sorteia posicoes ate encontrar uma que ainda nao foi atacada
    while True:
        l = random.randint(0, LINHAS - 1)
        c = random.randint(0, COLUNAS - 1)

        if not ja_atirou_aqui(ja_atirou, l, c):
            ja_atirou.append([l, c])

            if tab_jogador[l][c] == 1:  # acertou navio do jogador
                tab_jogador[l][c] = 2
                print(f"  Maquina atirou em {l},{c} --- ACERTOU seu navio!")

            else:
                # so marca como erro se a celula era agua (evita sobrescrever acerto anterior)
                if tab_jogador[l][c] == 0:
                    tab_jogador[l][c] = 3
                print(f"  Maquina atirou em {l},{c} --- Agua.")
            break


def main():
    print("Legenda: . = agua   # = navio   X = acerto   O = erro")
    print()
    print("Para posicionar: linha,coluna linha,coluna")
    print("Exemplo: 0,0 0,4  -> navio horizontal na linha 0, colunas 0 a 4")
    print(f"Grade: {LINHAS} linhas (0-{LINHAS - 1})  x  {COLUNAS} colunas (0-{COLUNAS - 1})")
    print()

    for i in range(len(NAVIOS)):
        nome = NAVIOS[i][0]
        tamanho = NAVIOS[i][1]
        posicionar_navio_jogador(nome, tamanho)
        mostrar_tabuleiro(tab_jogador, "Seu tabuleiro")

    posicionar_navios_maquina()
    print("Maquina posicionou seus navios. Que o jogo comece!\n")

    tiros_jogador = []
    tiros_maquina = []

    while True:
        print("=" * 45)
        print("SUA VEZ")
        mostrar_tabuleiro(tab_ataques, "Tabuleiro inimigo (suas tentativas)")
        ataque_jogador(tiros_jogador)

        vivos_maquina = contar_navios_vivos(navios_maquina, tab_maquina)
        print(f"  Navios inimigos restantes: {vivos_maquina}")
        mostrar_tabuleiro(tab_ataques, "Tabuleiro inimigo")

        if vivos_maquina == 0:
            print("=" * 45)
            print("  VOCE VENCEU! Todos os navios inimigos foram destruidos!")
            print("=" * 45)
            print("  Obrigado por jogar!")
            print("  Grupo 23: Leandro Cardoso Vieira, Murilo Bornemann Bonamigo")
            break

        print("=" * 45)
        print("VEZ DA MAQUINA")
        ataque_maquina(tiros_maquina)

        vivos_jogador = contar_navios_vivos(navios_jogador, tab_jogador)
        print(f"  Seus navios restantes: {vivos_jogador}")
        mostrar_tabuleiro(tab_jogador, "Seu tabuleiro")

        if vivos_jogador == 0:
            print("=" * 45)
            print("  VOCE PERDEU! Todos os seus navios foram destruidos!")
            print("=" * 45)
            print("  Obrigado por jogar!")
            print("  Grupo 23: Leandro Cardoso Vieira, Murilo Bornemann Bonamigo")
            break


main()
