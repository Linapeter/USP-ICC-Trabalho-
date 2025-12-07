
import sys
from datetime import datetime
import time
import random
import pyttsx3
import unicodedata

try:
    from docx import Document
except ImportError:
    Document = None

from colorama import init as colorama_init, Fore, Style

colorama_init()


# ALFABETO BRAILLE


braille_map = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    ' ': ' ',

    ',': '⠂', ';': '⠆', ':': '⠒', '.': '⠲',
    '?': '⠦', '!': '⠖', '-': '⠤', "'": '⠄', '"': '⠶'
}

reverse_braille_map = {v: k for k, v in braille_map.items()}


# BRAILLE POR PONTOS


braille_por_pontos = {
    (1,): "⠁", (1,2): "⠃", (1,4): "⠉", (1,4,5): "⠙",
    (1,5): "⠑", (1,2,4): "⠋", (1,2,4,5): "⠛", (1,2,5): "⠓",
    (2,4): "⠊", (2,4,5): "⠚", (1,3): "⠅", (1,2,3): "⠇",
    (1,3,4): "⠍", (1,3,4,5): "⠝", (1,3,5): "⠕",
    (1,2,3,4): "⠏", (1,2,3,4,5): "⠟",
    (1,2,3,5): "⠗", (2,3,4): "⠎",
    (2,3,4,5): "⠞", (1,3,6): "⠥", (1,2,3,6): "⠧",
    (2,4,5,6): "⠺", (1,3,4,6): "⠭",
    (1,3,4,5,6): "⠽", (1,3,5,6): "⠵"
}

reverse_pontos = {v: k for k, v in braille_por_pontos.items()}

pontos_para_letra = {}

for pontos, simbolo in braille_por_pontos.items():
    letra = reverse_braille_map.get(simbolo)
    if letra:
        pontos_para_letra[pontos] = letra


# HISTÓRICO


historico = []

def registrar_historico(tipo, conteudo):
    historico.append({
        'datahora': datetime.now(),
        'tipo': tipo,
        'conteudo': conteudo
    })

def salvar_historico_em_arquivo(nome_arquivo='historico.txt'):
    with open(nome_arquivo, 'a', encoding='utf-8') as f:
        for item in historico:
            dt = item['datahora'].strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{dt} | {item['tipo']} | {item['conteudo']}\n")
    print(f"Histórico salvo em {nome_arquivo}.")


# TRADUÇÃO TEXTO <-> BRAILLE

import unicodedata

# Texto -> Braille
def traduzir_texto_para_braille(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_limpo = ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])

    resultado = []
    for ch in texto_limpo:
        low = ch.lower()
        if low in braille_map:
            resultado.append(braille_map[low])
        else:
            if ch.strip() == '':
                resultado.append(' ')
            else:
                resultado.append('?')

    traducao = ''.join(resultado)
    registrar_historico('Texto → Braille', f"{texto} => {traducao}")
    return traducao

# Braille -> Texto
def traduzir_braille_para_texto(braille_texto):
    resultado = []
    for ch in braille_texto:
        if ch in reverse_braille_map:
            resultado.append(reverse_braille_map[ch])
        elif ch == ' ':
            resultado.append(' ')
        else:
            resultado.append('?')

    traducao = ''.join(resultado)
    registrar_historico('Braille → Texto', f"{braille_texto} => {traducao}")
    return traducao


# LEITOR DE VOZ


def configurar_voz_portugues(engine):
    for voice in engine.getProperty('voices'):
        if ("portuguese" in voice.name.lower()
            or "português" in voice.name.lower()
            or "pt" in voice.id.lower()
            or "br" in voice.id.lower()):
            engine.setProperty('voice', voice.id)
            return True
    return False

def falar_texto(texto, piscar=False):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    if not voices:
        print("⚠ Nenhuma voz instalada no sistema.")
        return

    if not configurar_voz_portugues(engine):
        print("⚠ Voz PT-BR não encontrada, usando voz padrão.")

    if piscar:
        for letra in texto:
            engine.say(letra)
            engine.runAndWait()
            piscar_braille_por_letra(letra)
    else:
        engine.say(texto)
        engine.runAndWait()


# PISCAR BRAILLE

def piscar_braille_por_letra(letra, duracao=0.35):
    """
    Pisca a célula braille 2x3 da letra, com cada ponto aceso colorido
    conforme sua numeração.
    ● colorido = ponto aceso
    ○ cinza    = ponto apagado
    """
    letra = letra.lower()
    if letra not in braille_map:
        return

    simbolo = braille_map[letra]
    pontos_acesos = reverse_pontos.get(simbolo, ())

    # Cores individuais para os 6 pontos do Braille
    cor = {
        1: Fore.RED,
        2: Fore.YELLOW,
        3: Fore.BLUE,
        4: Fore.GREEN,
        5: Fore.MAGENTA,
        6: Fore.CYAN
    }

    def ponto(n, aceso=True):
        if aceso and n in pontos_acesos:
            return cor[n] + "●" + Style.RESET_ALL
        else:
            return Fore.WHITE + "○" + Style.RESET_ALL

    def desenhar(aceso):
        print()
        print(f"   {ponto(1, aceso)} {ponto(4, aceso)}")
        print(f"   {ponto(2, aceso)} {ponto(5, aceso)}")
        print(f"   {ponto(3, aceso)} {ponto(6, aceso)}")
        print()

    desenhar(True)
    time.sleep(duracao)

    desenhar(False)
    time.sleep(duracao * 0.55)


# QUIZ


def quiz_braille(qtd=5):
    letras = [l for l in braille_map.keys() if l.isalpha()]
    score = 0

    for i in range(qtd):
        letra = random.choice(letras)
        symbol = braille_map[letra]

        if random.choice([True, False]):
            resposta = input(f"Pergunta {i+1}/{qtd}: Que letra é '{symbol}'? ").lower()
            if resposta == letra:
                print("Correto!")
                score += 1
            else:
                print(f"Errado. Resposta certa: {letra}")
        else:
            resposta = input(f"Pergunta {i+1}/{qtd}: Qual o símbolo da letra '{letra}'? ").strip()
            if resposta == symbol:
                print("Correto!")
                score += 1
            else:
                print(f"Errado. Símbolo correto: {symbol}")

    print(f"Pontuação final: {score}/{qtd}")


# TECLADO BRAILLE NUMÉRICO


def teclado_braille_numerico(traduzir=True):
    print("Digite números de pontos (ex: 1 24 145)")
    entrada = input("Sequência: ").strip()
    if not entrada:
        print("Nenhuma entrada.")
        return ""

    tokens = entrada.split()
    letras = []

    for tok in tokens:
        try:
            pts = tuple(sorted(int(d) for d in tok))
        except:
            letras.append('?')
            continue

        simbolo = braille_por_pontos.get(pts)
        letra = reverse_braille_map.get(simbolo, '?') if simbolo else '?'
        letras.append(letra)

    texto = ''.join(letras)
    print("Resultado:", texto)
    registrar_historico('Teclado Braille (num) → Texto', f"{entrada} => {texto}")

    if traduzir:
        braille = ''.join(braille_por_pontos.get(tuple(sorted(int(d) for d in tok)), '?') for tok in tokens)
        print("Braille:", braille)
        registrar_historico('Teclado Braille (num) → Braille', f"{entrada} => {braille}")

    return texto


# MOSTRAR ALFABETO


def exibir_alfabeto_braille():
    print("Alfabeto Braille (letra : símbolo)")
    items = [k for k in braille_map.keys() if k.isalpha()] + [',', ';', ':', '.', '?', '!', '-', "'", '"']
    for ch in items:
        print(f"{ch} : {braille_map[ch]}", end='  ')
    print("\n")


# TRADUÇÃO DE ARQUIVOS


def traduzir_arquivo(caminho, direcao='t2b'):
    try:
        if caminho.lower().endswith('.txt'):
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
        elif caminho.lower().endswith('.docx'):
            if Document is None:
                print("python-docx não está instalado.")
                return
            doc = Document(caminho)
            conteudo = "\n".join(p.text for p in doc.paragraphs)
        else:
            print("Formato não suportado.")
            return
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        return

    if direcao == 't2b':
        traducao = traduzir_texto_para_braille(conteudo)
    else:
        traducao = traduzir_braille_para_texto(conteudo)

    print("\n=== Tradução ===")
    print(traducao)


# HISTÓRICO


def mostrar_historico():
    if not historico:
        print("Histórico vazio.")
        return

    print("Histórico:")
    for item in historico:
        dt = item['datahora'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"{dt} | {item['tipo']} | {item['conteudo']}")

    if input("Salvar em arquivo? (s/n) ").lower() == 's':
        salvar_historico_em_arquivo()


# MENU


def menu_principal():
    piscar_ativado_global = False

    while True:
        print("\n" + "="*50)
        print("          🌟 TRADUTOR BRAILLE — MENU 🌟")
        print("="*50)
        print("1) Texto → Braille")
        print("2) Braille → Texto")
        print("3) Leitor de voz")
        print("4) Ativar/desativar piscadas automáticas")
        print("5) Quiz de treino")
        print("6) Modo Digitação Braille (numérico)")
        print("7) Histórico")
        print("8) Tradutor de arquivos")
        print("0) Sair")
        print("="*50)

        exibir_alfabeto_braille()
        escolha = input("Escolha uma opção: ").strip()

        # 1) Texto → Braille
        if escolha == '1':
            texto = input("Digite o texto: ")
            traducao = traduzir_texto_para_braille(texto)
            print("\n→ Braille:", traducao)

            op = input("Quer ouvir? (s/n) ").lower()
            if op == 's':
                falar_texto(texto, piscar=piscar_ativado_global)

            if input("Piscar braille visual? (s/n) ").lower() == 's':
                for letra in texto:
                    piscar_braille_por_letra(letra)

        # 2) Braille → Texto
        elif escolha == '2':
            braille = input("Digite Braille: ")
            traducao = traduzir_braille_para_texto(braille)
            print("→ Texto:", traducao)

            op = input("Ouvir leitura? (s/n) ").strip().lower()
            if op == 's':
                falar_texto(traducao, piscar=piscar_ativado_global)

            if input("Piscar braille? (s/n) ").lower() == 's':
                for letra in traducao:
                    piscar_braille_por_letra(letra)

        # 3) Leitor de voz
        elif escolha == '3':
            print("1) Ler texto")
            print("2) Ler Braille")
            sub = input("Opção: ").strip()

            if sub == '1':
                texto = input("Digite texto: ")
                falar_texto(texto, piscar=piscar_ativado_global)

            elif sub == '2':
                braille = input("Digite Braille: ")
                texto = traduzir_braille_para_texto(braille)
                print("Texto:", texto)
                falar_texto(texto, piscar=piscar_ativado_global)

        # 4) Ativar/desativar piscar
        elif escolha == '4':
            piscar_ativado_global = not piscar_ativado_global
            print("Piscar automático agora está:", 
                  "ATIVADO" if piscar_ativado_global else "DESATIVADO")

        # 5) Quiz
        elif escolha == '5':
            try:
                qtd = int(input("Quantas perguntas? ").strip())
            except:
                qtd = 5
            quiz_braille(qtd)

        # 6) Teclado braille numérico
        elif escolha == '6':
            print("1) Apenas digitar")
            print("2) Digitar e traduzir")
            sub = input("Opção: ")
            teclado_braille_numerico(traduzir=(sub != '1'))

        # 7) Histórico
        elif escolha == '7':
            mostrar_historico()

        # 8) Arquivos
        elif escolha == '8':
            caminho = input("Caminho: ").strip()
            print("1) Texto → Braille")
            print("2) Braille → Texto")
            sub = input("Opção: ").strip()
            traduzir_arquivo(caminho, direcao=('t2b' if sub == '1' else 'b2t'))

        # 0) Sair
        elif escolha == '0':
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


menu_principal()
