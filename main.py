from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser

### import modulos das funcoes
import textwrap, srt, os, time, subprocess
from datetime import timedelta


### usar Lib/shutil.py e/ou Lib/tempfile.py para controlar arquivos temporários de SRT.
### Assim dá pra criar o arquivo em uma pasta escondida, e só disponibilizar ela quando e se
### o arquivo for gerado corretamente. Por exemplo, para contornar erros quando txt tenta ser gerado
### com a nota musical e avisar que um erro aconteceu.

##### TODO
### 2 - [ ] box para selecionar tipo de quebra de linha, se por ponto ou padrão
###         útil para quando tem mais de uma pessoa falando. Reconstruir o texto todo, e onde houver
###         nova linha dupla ou tripla pula para a próxima letra ou palavra.
### 3 - [X] criar novo método de gerar tempos dos CCs: por quantidade de caracteres. v2
### 4 - [ ] aba que exibe último CC gerado? pode gerar confusão por não poder ser editado.
### 5 - [ ] novo método/formato (EBU STL) de export para ser compativel com Media Composer.
### 6 - [ ] CTRL + Z  ??? como fazer? uma matriz que salve todas as ações. As variáveis serão globais?
### 7 - [ ] criar tooltips para todos os botoes - https://github.com/PedroHenriques/Tkinter_ToolTips
### 8 - [X] adicionar sempre um espaco apos cada pontuacao -  ele não saberia diferenciar sites
### 9 - [ ] corrigir divisao por em 'zero duracao_cc = (duracao_video - (4 * segundo)) / (len_lista - 3)'
### 10- [ ] opcao para já receber o texto quebrado em linhas sempre que outra pessoa falar.

programa_nome = 'CC Fácil' 
programa_versao = "v0.99.2.4"

## funcoes do SRT output ###################################################

fps = 29.97
frame = timedelta(seconds=1/fps) # ou 29.97
segundo = timedelta(seconds = 1) #facilita fazer contas com tempo timedelta
duracao_video = timedelta(seconds = 15)
nome_arquivo = "CH BDRG JUL_30 15 CH30N5s"

texto = """

No Globo esporte desse sábado,

tudo sobre a final do Gauchão Raiz!

01234567890123456789012345678901234567890123456789012345678901234567890123456789

Nós vamos estar na Arena, onde Grêmio e Caxias disputam o título de campeão!

E tem também a final do Prêmio Bucha!

Os nossos jurados vão escolher os melhores gols do campeonato!

E ainda: o Inter vai ao Rio de Janeiro pra segurar a liderança do Brasileirão!

Tudo isso nesse sábado, logo depois do Jornal do Almoço.
"""

def lista_timecode(lista_texto):
    
    lista_tc_start_ccs = []
    lista_tc_end_ccs = []

    len_lista = len(lista_texto)
    duracao_cc = (duracao_video - (4 * segundo)) / (len_lista - 3)
    indice = 1
    
    for item_tc in lista_texto[0]:   #primeiro item "_'
        lista_tc_start_ccs.append(timedelta(milliseconds = 0))
        lista_tc_end_ccs.append(timedelta(milliseconds = 500))
        #print(item_tc)


    for item_tc in lista_texto[1:3]:
        lista_tc_start_ccs.append(timedelta(seconds = indice))
        lista_tc_end_ccs.append(timedelta(seconds = indice + 1.5 - 0.1))
        indice =  indice + 1.5
        #print(item_tc) 

    indice = 1 # 1 pq é mais fácil criar todos como se começassem no início e somar 4 segundos das linhas de cima
    for item_tc in lista_texto[3:]:
        fun_cc_start = (duracao_cc * indice) - duracao_cc + (segundo * 4)  #+ (frame*2)
        fun_cc_end = (duracao_cc * indice)  + (segundo * 4) - (frame*2)
        lista_tc_start_ccs.append(fun_cc_start)
        lista_tc_end_ccs.append(fun_cc_end)
        indice = indice + 1
        
    return lista_tc_start_ccs, lista_tc_end_ccs

def lista_timecode_v2(lista_texto):
    global texto
    
    lista_tc_start_ccs = []
    lista_tc_end_ccs = []
    
    total_caracteres = 0
    porcentagem_cc = 0
    
    print("lista v2: ")

    #calcula o total de caracteres excluindo os 3 primeiros blocos: 1 bloco vazio, e 2 blocos de uma linha só
    #onde o tempo é calculado/imposto por outra parte do código
    for bloco in texto[3:]:
        total_caracteres = total_caracteres + len(bloco)
    

    len_lista = len(lista_texto)
    duracao_cc = (duracao_video - (4 * segundo)) / (len_lista - 3)
    duracao_ccs = (duracao_video - (4 * segundo))
    indice = 1
    
    for item_tc in lista_texto[0]:   #primeiro item '_' #primeira imposição
        lista_tc_start_ccs.append(timedelta(milliseconds = 0))
        lista_tc_end_ccs.append(timedelta(milliseconds = 500))
        #print(item_tc)


    for item_tc in lista_texto[1:3]:  #segunda imposição
        lista_tc_start_ccs.append(timedelta(seconds = indice))
        lista_tc_end_ccs.append(timedelta(seconds = indice + 1.5 - 0.1))
        indice =  indice + 1.5
        #print(item_tc) 

    indice = 1 # 1 pq é mais fácil criar todos como se começassem no início e somar 4 segundos das linhas de cima
    for item_tc in lista_texto[3:]:
        
        porcentagem_cc_em_segundos = ((duracao_ccs * len(item_tc)) / total_caracteres)        #calcula a porcentagem do CC atual já em segundos
        fun_cc_start = lista_tc_end_ccs[-1] + (frame*2)
        fun_cc_end   = fun_cc_start + (porcentagem_cc_em_segundos) - (frame*2)
        
        
#         fun_cc_start = (duracao_cc * indice) - duracao_cc + (segundo * 4)  #+ (frame*2)
#         fun_cc_end = (duracao_cc * indice)  + (segundo * 4) - (frame*2)
        
        lista_tc_start_ccs.append(fun_cc_start)
        lista_tc_end_ccs.append(fun_cc_end)
        indice = indice + 1
        
    return lista_tc_start_ccs, lista_tc_end_ccs


def _limpa_texto():
    global texto
    texto_2 = texto.split()  #limpa o texto e espacos e linhas vazias
     
    texto = texto_2[0]       #reutilizando a variavel - aqui texto comeca a ser reescrito do zero
                                  #com a primeira palavra, para poder usar o espaco no ELSE abaixo
                                  #usar if para adicionar nota musical no inicio e mudar o 1 do range abaixo
    
    
    #não usei join() pois preciso tirar alguns espaços
    for palavra in range(1, len(texto_2)):              # corrige espacos antes das pontuacoes
        palavra_2 = texto_2[palavra]     #palavra_2 vira a palavra em questao, acho que foi para encurtar ou para poder mexer nela se necessario
        if palavra_2 == "." or palavra_2 == "," or palavra_2 == ";"  or palavra_2 == ":" or palavra_2 == ")" or palavra_2 == "!" or palavra_2 == "?":
            texto = texto + texto_2[palavra]  #se for pontuacao cola direto

        else:
            texto = texto + " " + texto_2[palavra] # se nao for pontuacao, espaco + palavra
    
    return texto

def _quebra_texto():
    global texto
    wrapper = textwrap.TextWrapper(width=32, break_long_words = True)
    texto = wrapper.wrap(text=texto)         # reutilizando a variavel "texto" - acho que nao precisa do text
    
    return texto

def _quebra_texto_v2():
    #não funcionou pois o sistema de quebra de linhas já as vezes deixava um ponto e uma letra no fim do item
    #então as vezes ficaria um CC com uma letra sozinho. o v3 tenta contornar esse problema reescrevendo
    #mais uma vez o CC
    global texto
    wrapper = textwrap.TextWrapper(width=32, break_long_words = True)
    texto = wrapper.wrap(text=texto)         # reutilizando a variavel "texto" - acho que nao precisa do text
    
    if True:   # só executa se True, mudar para BOX depois
        print("quebrando linhas nos pontos")
        
        linha_tmp = ""
        letra_tmp = ""
        texto_tmp = []
        
        for item in texto:
            indice = -1
            if "." not in item and "!" not in item and "?" not in item:
                #não tendo nenhua pontuacao, coloca o item na lista
                texto_tmp.append(item)
            else:
                #tem alguma pontuacao entao...
                for letra_tmp in item:
                    #criar linha temporaria e ir adicionando as letras, quando encontrar pontuacao fecha e comeca nova linha
                    indice = indice + 1
                    if letra_tmp != "." and letra_tmp != "!" and letra_tmp != "?":
                        #nao sendo pontuacao
                        linha_tmp = linha_tmp + letra_tmp
                    
                    elif item[indice+1:indice+2] == " ":
                        #sendo pontuacao e o proximo indice sendo espaço (não é site, por exemplo)
                        linha_tmp = linha_tmp + letra_tmp
                        texto_tmp.append(linha_tmp)
                        linha_tmp = ""
                    
                    elif item[indice+1:indice+2] != " ":
                        #sendo pontuacao e o proximo indice sendo diferente de espaco (um site, por exemplo)
                        linha_tmp = linha_tmp + letra_tmp
               
                texto_tmp.append(linha_tmp)
                linha_tmp = ""
               
        #print(texto)
        print(texto_tmp)
    texto = texto_tmp
    return texto

def _quebra_texto_v3():
    global texto
    
    #remonta o texto mas agora com palavras longas corrigidas e quebras de linha em pontuações
    
    texto_tmp = [""] #inicializa o primeiro item vazio para n poder acessar abaixo
    linha_tmp = ''
    linha_tmp2 = ''
    n = 0 #controla o indice do texto_tmp
    texto = texto.split()

    for i in range(len(texto)):
               
        linha_tmp2 = linha_tmp + " " + texto[i]   #cria uma linha temporaria para testar o tamanho
        linha_tmp2 = linha_tmp2.strip() #tira os espaços antes e depois se tiver
    
        if len(linha_tmp2) <= 32:
            #sendo menor o valor tmp2 vai para tmp que é a linha que é inserida no texto
            linha_tmp =  linha_tmp2
            
            if texto[i][-1] == "." or texto[i][-1] == "!" or texto [i][-1] == "?":
                texto_tmp[n] = linha_tmp.strip()  #aplica a linha_tmp construída
                linha_tmp = ""    #limpa a linha temporaria
                texto_tmp.append(linha_tmp)   #cria uma nova linha vazia 
                n = n + 1  #atualiza o indice para poder acesar a informação criadoa na linha acima
            
        else:
            #sendo maior
            texto_tmp[n] = linha_tmp.strip()  #aplica a linha_tmp construída antes no item atual n
            linha_tmp = texto[i]    #inicializa uma nova linha com a palavra que não coube
            texto_tmp.append(linha_tmp)   #cria uma nova linha com a palavra que nao coube, se for a última palavra garante que mesmo que o IF acima não ocorra, ele vá para o texto
            n = n + 1  #atualiza o indice para poder acesar a informação criadoa na linha acima
            
    print(texto_tmp)
    texto = texto_tmp
        #tem que retornar lista
    return texto

def _quebra_texto_v4():
    global texto
    
    #remonta o texto mas agora com palavras longas corrigidas e quebras de linha em pontuações
    
    texto_tmp = "" 
    linha_tmp = ""
    linha_tmp2 = ""
    texto = texto.split()
    
    for i in texto:
        
        linha_tmp2 = linha_tmp2 + " " + i #linha temporaria para testar tamanho
        linha_tmp2 = linha_tmp2.strip() #tira espaços antes e depois
        
        if i == "Raiz!":
            print(i)
      
        if i[-1] == "." or i[-1] == "!" or i[-1] == "?":
            if len(linha_tmp2) <= 32:
                linha_tmp = texto_tmp + " " + i
                texto_tmp = linha_tmp.lstrip() + "\n"
                linha_tmp2 = ""
            
            else:
                linha_tmp = texto_tmp + "\n" + i
                texto_tmp = linha_tmp.lstrip() + "\n"
                linha_tmp2 = i
        
        else:
            if len(linha_tmp2) <=  32:
                texto_tmp = texto_tmp.lstrip() + " " + i
            
            else:
                texto_tmp = texto_tmp.lstrip() + "\n" + i
                linha_tmp2 = i
                
    print(texto_tmp)        
    texto = texto_tmp.strip().split("\n")
    return texto

def _quebra_texto_v5(): #talvez o v5 só faça sentido quando tiver futuramente a separacao das linhas para cada CC
    # se for uma pessoa só falando, o V1 faz mais sentido
    global texto
    
    t = ""
    tt = []
    
    #monta novo texto com quebras de linhas em todas as pontuações
    for i in texto.split():
        if not i.endswith((".","!","?")):
            #nao terminando com pontuação
            t = t + " " + i
            t = t.strip() #tira os espacos iniciais
        else:
            #terminando com pontuacao cola e bota nova linha
            t = t + " " + i + "\n"
    
    t = t.splitlines() #retorna lista com cada linha em um
    
    
    #tira espaços que possam ter sobrado no início e fim
    for i in range(len(t)):
        t[i] = t[i].strip()
    
    wrapper = textwrap.TextWrapper(width=32, break_long_words = True)
   
    for i in t:
        
        linha_quebrada = wrapper.wrap(text=i)
        
        # TODO
        # Testar aqui uma quebra de linha que distribua melhor as palavras. Para não sobrar um CC com uma palavra só quando
        # estiver configurado para quebra de linha em pontuacoes.
        # Ainda não sei bem como.
                  
        for ii in linha_quebrada:
            tt.append(ii.strip())
                       
            
            
    texto =  tt
    return texto
    

def _lista_cc_bk():
    global texto            #usar a variavel global mesmo por praticidade
    texto_temp_2 = texto    #inverte texto e texto_temp_2 para usar texto_temp_2 como temporario abaixo
    texto = []
    linha_temp = ""

    ################ CRIA AQUI O PRIMEIRO ITEM VAZIO DO TEXTO ######################
    texto.append("_")  #texto.append("\u266A")


    for texto_linha in texto_temp_2[:2]:  #apenas as duas primeiras "linhas" (itens na lista "texto_temp_2")
        texto.append(texto_linha)
    
    # TODO - aqui, caso a quebra de linha esteja configurada para PONTUAÇÕES fazer testar o último item, se for ponto
    # testa se vai ficar em um CC sozinho, caso positivo, gera um item vazio (linha vazia), caso negativo (termina na
    # ultima linha do CC) nao precisa adicionar nada diferente.
    
    for texto_linha in range(2, len(texto_temp_2), 2):                 #exceto as duas primeiras linhas *de dois em dois*<<<<
        for texto_linha_2 in texto_temp_2[texto_linha:texto_linha+2]:  #só por conveniencia o 2 aqui, no futuro dá pra alterar quantas linhas cada CC tem aqui
            linha_temp = linha_temp + "\n" + texto_linha_2             #melhorar com uma lista temporaria de linhas?
        texto.append(linha_temp.strip())                               #strip tira os espacos iniciais e finais e novas linhas
        linha_temp = ""                                        #reinicia a linha_temp antes de ser usada de novo
    print(texto)
    pass


#não é possível adicionar a nova linha em todas as interações para criar novo CC em caso de pontuação.

def _lista_cc():
    global texto            #usar a variavel global mesmo por praticidade
    texto_temp_2 = texto    #inverte texto e texto_temp_2 para usar texto_temp_2 como temporario abaixo
    texto = []
    linha_temp = ""
    linhas_por_cc = 0       #vai contar quantas linhas já tem na linha temp
    ################ CRIA AQUI O PRIMEIRO ITEM VAZIO DO TEXTO ######################
    texto.append("♪")  # alterado para ter a nota musical - testar em outros sistemas #texto.append("\u266A")


    for texto_linha in texto_temp_2[:2]:  #apenas as duas primeiras "linhas" (itens na lista "texto_temp_2")
        texto.append(texto_linha)
    
# Esse for roda por todas as linhas em texto_temp_2, testa se o final é uma pontuação (ou qualquer outra coisa que gere uma nova linha) e
# vai montando uma linha_temp (já com as quebras de texto para o CC) enquanto armazenda em linhas_por_cc quantas linhas já estão na linha temp.
# Caso o final seja pontuação adiciona o que tem montado no texto, se nao ele testa o número de linhas se for igual ou maior que 2 ele coloca
# a linha temp no texto, se for menor ele só continua montando a linha temp para ser adicionada depois. Assim esse limite de 2 pode ser alterado
# futuramente por uma variavel.
    
    
    for texto_linha in texto_temp_2[2:]:                 #exceto as duas primeiras linhas *de dois em dois*<<<<
        if texto_linha.endswith((".","!","?")):          #se terminar com pontuação
            linha_temp = linha_temp + "\n" + texto_linha  #cria a linha temporaria com o que já tinha antes (pode ser que seja vazia)
            texto.append(linha_temp.strip())              #adiciona no texto                 #strip tira os espacos iniciais e finais e novas linhas
            linhas_por_cc = 0                             #reseta o número de linhas na linha temp
            linha_temp = ""                               #reseta/esvazia a linha temp
            
        else:
            if linhas_por_cc < 2:                               #se a linha for menor que 2
                linha_temp = linha_temp + "\n" + texto_linha    #adiciona na linha temp com o que já tinha antes (pode ser que seja vazia)
                linhas_por_cc = linhas_por_cc + 1               #atualiza o número de linhas na linha temp
                
                                                            #um if se parado pois a soma anterior pode já ter chegado no limite (2)
            if linhas_por_cc >= 2:                          #se for maior ou igual a 2 (esse dois pode ser alterado por uma variável futuramente)
                texto.append(linha_temp.strip())            #adiciona a linha temp no texto
                linhas_por_cc = 0                           #seseta o número de linhas na linha temp, pois essa linha temp nao vale mais 
                linha_temp = ""                             #reseta para iniciar um novo ciclo
                
    pass



def _aplica_timecode():
    global texto
    #aqui texto já é uma lista onde cada item é um bloco de CC
    #chama a funcao e recebe duas listas de timecodes
    starts_ccs, ends_ccs = lista_timecode_v2(texto)

    # colocar timecodes
    cc_lista = []
    item = 0

    for cc_linhas in texto:
        
        cc_start = starts_ccs[item] #cc inicial baseado na linha/item
        cc_end = ends_ccs[item] #cc final um segundo apos     
        cc_lista.append(srt.Subtitle(index=item, start=cc_start, end=cc_end, content=cc_linhas))
        item = item + 1
    return cc_lista
    
    
def _salva_cc():
    global nome_arquivo     #acho que nao precisa

    pasta_salvar = nome_dir.get()
    
    cc_final = srt.compose(_aplica_timecode())

    #nome_arquivo_comformato = r"H:\CHAMADAS FINALIZADAS\\" + nome_arquivo + ".srt"
    nome_arquivo_comformato = nome_arquivo + ".srt"
    caminho_nome_arquivo_comformato = pasta_salvar + "\\" + nome_arquivo_comformato
    
#     while os.path.exists(nome_arquivo_comformato):
#         nome_arquivo_comformato = (nome_arquivo_comformato[:-4]) + " extra" + ".srt"
#         print("mais extra")
    
    if os.path.exists(caminho_nome_arquivo_comformato): #se arquivo já existe adiciona data no nome
        t = time.localtime()
        current_time = time.strftime("_%Y_%m_%d_%H_%M_%S", t)
        print(current_time)
        #nome_arquivo_comformato = (nome_arquivo_comformato[:-4]) + current_time + ".srt"
        nome_arquivo = nome_arquivo + current_time
        nome_arquivo_comformato =  nome_arquivo + ".srt"
        caminho_nome_arquivo_comformato = pasta_salvar + "\\" + nome_arquivo_comformato
        
            
    file1 = open(caminho_nome_arquivo_comformato,"w", encoding = 'utf-16')
    file1.write(cc_final)
    file1.close()
    
    var_feedback_ui.set(" " + nome_arquivo_comformato)
    label_feedback.configure(cursor="hand2", foreground="blue")
    label_feedback.bind("<Button-1>", lambda a: selecionar_no_explorer(caminho_nome_arquivo_comformato))
    var_feedback_ui_msg.set("Legenda Salva:")
        ### esse lambda permite enviar algum atributo para a função que nao seja o botão pressionado
        
#     label_feedback()
    

### Funcoes da UI ###################################################


def imprime_texto():
    global texto
    global duracao_video
    global nome_arquivo
        
    texto = texto_box.get('1.0', 'end')
    
    # abre janela de alerta se estiver vazio
    if len(texto.split()) == 0:
        print("Box vazio...")
        messagebox.showinfo(message = "Cole o texto no Caixa de Texto...",
                            title = "Sem texto para formatar"                           
                            )
        texto_box.focus_set() #leva o foco para a caixa de texto      
        pass
    else:
        #transforma o conteudo dos spinboxs em segundos utilizaveis
        tempo_total_boxs_min = spinbox_min.get()
        tempo_total_boxs_min = int(tempo_total_boxs_min)
        tempo_total_boxs_seg = spinbox_seg.get()
        tempo_total_boxs_seg = int(tempo_total_boxs_seg)
        tempo_total_boxs = ((tempo_total_boxs_min * 60) + tempo_total_boxs_seg)
        duracao_video = timedelta(seconds = tempo_total_boxs)
     
        #pega o nome escrito na UI
        nome_arquivo = Nome_input.get()

        if os.path.exists(nome_dir.get()):
            print ("caminho existe")
            pass
        else:
            messagebox.showinfo(message = "Escolha um diretório existente para salvar sua legenda.",
                            title = "Caminho inválido!"                           
                            )
            _escolhe_dir()
            
        if os.path.exists(nome_dir.get()):  #só executa se o caminho existir
            #executa as ações/funções do programa
            _limpa_texto()
            _quebra_texto_v5()
            _lista_cc()
            _salva_cc()
        else:
            print("Diretorio não existia")
            
        

def _15s():
    var_min_ui.set(0)
    var_seg_ui.set(15)
    texto_box.focus_set()
    print("15s")

def _30s():
    var_min_ui.set(0)
    var_seg_ui.set(30)
    texto_box.focus_set()
    print("30s")

def _45s():
    var_min_ui.set(0)
    var_seg_ui.set(45)
    texto_box.focus_set()
    print("45s")

def _60s():
    var_min_ui.set(1)
    var_seg_ui.set(0)
    texto_box.focus_set()
    print("60s")

def _escolhe_dir():
    print("escolhe pasta")
    pasta_temp = var_nome_dir_ui.get()
    pasta_caminho = filedialog.askdirectory(initialdir = dir_inicial) #trocar caso MAC
    
    if len(pasta_caminho) == 0: #ZERO se foi cancelado
        pasta_caminho = pasta_temp
        var_nome_dir_ui.set(pasta_caminho) # o caminho volta a ser o caminho antigo
    else:
        print("pasta escolhida")
        print(pasta_caminho)
        var_nome_dir_ui.set(pasta_caminho) # o caminho é atualizado com o novo caminho

def _teste_numero(event): #só permite entrada de numeros no campo
    v = event.char
    print(v)
    try:
        v = int(v)
        return None
    except ValueError:
        if v!="\x08" and v!="":
            print('EEPAA')
            return "break"


def config_inicial():
    #algumas configurações iniciais
    #futuramente lerá um arquivo de configurações para sempre que iniciar o programa
    #começar com alguns valores setados como "formato padrao (srt, outros)", "tempo incial padrao"
    #caminho inicial padro
    
    #configura tempo inicial padrao para 30 segundos
    var_seg_ui.set(30)

def reseta_feedback_ui(evento):
    #pylint: disable=unused-argument
    
    var_feedback_ui.set("...")
    var_feedback_ui_msg.set("")
    var_abrindo_explorer.set("")
    label_feedback.configure(cursor="arrow", foreground="black")
    label_feedback.bind("<Button-1>", lambda reset:0) # lambda sem argumetos nao funciona então é só uma
                                                      # função que nao faz nada para nao chamar mais a função
                                                      # que abre o explorer  
    #label_feedback("<Button-1>", lambda a: var_feedback_ui.set("..."))
                                                      
def reseta_label_abrindo_explorer():
    var_abrindo_explorer.set('')
    pass
    
    
def selecionar_no_explorer(arquivo_caminho_salvo):
    
    if os.path.exists(arquivo_caminho_salvo):
        arquivo_caminho_salvo = os.path.realpath(arquivo_caminho_salvo)
        atributo_temp = r'explorer /select, '
        atributo_final = atributo_temp + arquivo_caminho_salvo
        subprocess.Popen(atributo_final)
        var_abrindo_explorer.set('Abrindo Explorer')
        #reseta_label_abrindo_explorer()
        #frame_feedback.update_idletasks()
        #time.sleep(3)
        label_abrindo_explorer.after(2000, reseta_label_abrindo_explorer)
        #reseta_feedback_ui("nada")
        
    else:
        var_feedback_ui_msg.set('Legenda')
        label_feedback.configure(foreground = "black")
        var_abrindo_explorer.set('não encontrada!')
        label_feedback.configure(cursor="arrow", foreground="red")
        label_feedback.bind("<Button-1>", lambda reset:0)


def abre_site():
    print("abrindo site")
    webbrowser.open_new("https://github.com/SamuelTell")
    print("abriu site")

################ UI ###################################################


root = Tk(baseName="CCFacil")
root_title = programa_nome + " " + programa_versao
root.title(root_title)
#root.resizable(FALSE,TRUE) # (horizontal, vertical)
root.minsize(400,400)
root.maxsize(800,800)

#define quais variaveis a UI vai usar
var_nome_dir_ui = StringVar() #pasta que vai salvar
var_nome_ch_ui = StringVar()
var_texto_box_ui = StringVar()
var_min_ui = StringVar()
var_seg_ui = StringVar()
var_feedback_ui = StringVar()
var_feedback_ui_msg = StringVar()
var_abrindo_explorer = StringVar()

#define variavaeis globais
#dir_inicial = 'H:\CHAMADAS FINALIZADAS\\'  # / CRIAR IF para criar esse valor diferente para Windows/MacOS/linux
dir_inicial = 'I:\SRT\\'  # / CRIAR IF para criar esse valor diferente para Windows/MacOS/linux


#cria um frame basico
frame_base = ttk.Frame(root, borderwidth=5, relief="solid", padding=(10,10,10,0)) # um quadrado base para colocar dentro
frame_feedback = ttk.Frame(root, borderwidth=5, padding=(10, 0,10, 0))

#cria a linha inicial Nome CH: [____] e outros textos
label_nome_ch = ttk.Label(frame_base, text='Nome CH:')
Nome_input = ttk.Entry(frame_base, textvariable = var_nome_ch_ui)
label_tempo = ttk.Label(frame_base, text='Tempo:')
label_pasta = ttk.Label(frame_base, text = 'Pasta:')
label_DoisPontos = ttk.Label(frame_base, text= ':')
label_Espaco = ttk.Label(frame_base, text= '  ')
label_min = ttk.Label(frame_base, text= 'min')
label_seg = ttk.Label(frame_base, text= 'seg')
label_feedback_msg = ttk.Label(frame_feedback, textvariable = var_feedback_ui_msg)
label_feedback = ttk.Label(frame_feedback, textvariable = var_feedback_ui, cursor="arrow", wraplength= 550)
label_abrindo_explorer = ttk.Label(frame_feedback, textvariable = var_abrindo_explorer)
nome_dir = ttk.Entry(frame_base, textvariable = var_nome_dir_ui)



#inicializa alguns valores na UI
var_nome_ch_ui.set('CH ')
var_nome_dir_ui.set(dir_inicial)
var_feedback_ui.set('https://github.com/SamuelTell')
var_feedback_ui_msg.set('Made by Samuel Telles')
var_abrindo_explorer.set('')


config_inicial()

#cria os botoes
botao_15s = ttk.Button(frame_base, text="15s", command = _15s)
botao_30s = ttk.Button(frame_base, text="30s", command = _30s)
botao_45s = ttk.Button(frame_base, text="45s", command = _45s)
botao_60s = ttk.Button(frame_base, text="60s", command = _60s)
botao_custom = ttk.Button(frame_base, text="Custom")
botao_escolhe_dir = ttk.Button(frame_base, text="Onde Salvar...", command = _escolhe_dir)
botao_gerar = ttk.Button(frame_base, text="Gerar .srt", command = imprime_texto)


#cria inputs spinbox
spinbox_min = Spinbox(frame_base,
                      from_=0,
                      to=59,
                      width=10,
                      textvariable = var_min_ui,
                      wrap = TRUE)
spinbox_seg = Spinbox(frame_base,
                      from_=0,
                      to=59,
                      width=10,
                      textvariable = var_seg_ui,
                      wrap = TRUE)


#cria caixa de texto
texto_box = Text(frame_base, wrap = "word")

#cria scroll text bar
scroll_y = ttk.Scrollbar(frame_base, orient=VERTICAL, command=texto_box.yview)
texto_box.configure(yscrollcommand = scroll_y.set)   #liga o scrool a caixa de texto

#acoes especificas BIND
spinbox_min.bind("<Key>", _teste_numero)
spinbox_seg.bind("<Key>", _teste_numero)

#BIND que dá RESET no feedback
texto_box.bind("<Key>", reseta_feedback_ui)  #poderia tudo ser feito com lambda a: var_feedback_ui.set("...")
Nome_input.bind("<Key>", reseta_feedback_ui)                   #caso fosse um só comando
spinbox_min.bind("<Button-1>", reseta_feedback_ui)
spinbox_seg.bind("<Button-1>", reseta_feedback_ui)
botao_15s.bind("<Button-1>", reseta_feedback_ui)
botao_30s.bind("<Button-1>", reseta_feedback_ui)
botao_45s.bind("<Button-1>", reseta_feedback_ui)
botao_60s.bind("<Button-1>", reseta_feedback_ui)
nome_dir.bind("<Key>", reseta_feedback_ui)
# label_feedback.bind("<Button-1>", reseta_feedback_ui)

#define o site clicável
label_feedback.configure(cursor="hand2", foreground="blue")
label_feedback.bind("<Button-1>", lambda e: abre_site())


#posiciona os items no grid

frame_base.grid(column = 0, row = 0, sticky = (N, S, E, W))
frame_feedback.grid(column = 0, row = 1, sticky = (E))

label_nome_ch.grid(column=0, row=0, sticky=(E))
Nome_input.grid(column=1, row=0, columnspan=9, sticky=(E, W), pady=5, padx=5)

label_tempo.grid(column = 0, row = 1, sticky=(E))
botao_15s.grid(column = 1, row = 1)
botao_30s.grid(column = 2, row = 1)
botao_45s.grid(column = 3, row = 1)
botao_60s.grid(column = 4, row = 1)
#botao_custom.grid(column = 4, row = 1)
#label_Espaco.grid(column = 5, row = 1)
spinbox_min.grid(column = 7, row = 1)
label_DoisPontos.grid(column = 8, row = 1)
spinbox_seg.grid(column = 9, row = 1)

label_min.grid(column = 7, row = 2, sticky = (N))
label_seg.grid(column = 9, row = 2, sticky = (N))

#TEXT BOX
texto_box.grid(column = 0, row = 3, columnspan = 10, sticky = (N, S, E, W))
scroll_y.grid(column = 10, row = 3, sticky=(N,S))

label_pasta.grid(column = 0, row = 4)
nome_dir.grid(column = 1, row = 4, columnspan=6, sticky=(E, W), pady=5, padx=5)
botao_escolhe_dir.grid(column = 7, row = 4)
botao_gerar.grid(column = 9, row = 4, pady=15, padx=5)

label_feedback_msg.grid(column = 0, row = 0, sticky=W)
label_feedback.grid(column = 1, row = 0, sticky=W, pady=5, padx=5)

label_abrindo_explorer.grid(column = 2, row =0)


#faz a UI ficar auto esticavel
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame_base.columnconfigure(0, weight=1, minsize = 35)
frame_base.columnconfigure(1, weight=1, minsize = 35)
frame_base.columnconfigure(2, weight=1, minsize = 35)
frame_base.columnconfigure(3, weight=1, minsize = 35)
frame_base.columnconfigure(4, weight=1, minsize = 35)
frame_base.columnconfigure(5, weight=1, minsize = 35)
frame_base.columnconfigure(6, weight=1, minsize = 35)
frame_base.columnconfigure(7, weight=1, minsize = 35)
#frame_base.columnconfigure(8, weight=1)
frame_base.columnconfigure(9, weight=1, minsize = 35)

frame_base.rowconfigure(0, weight=1, minsize = 35)
frame_base.rowconfigure(1, weight=1, minsize = 35)
frame_base.rowconfigure(2, weight=1, minsize = 35)
frame_base.rowconfigure(3, weight=1, minsize = 35)

root.mainloop()


# só rodar os comandos abaixos dentro da pasta
# nao precisa entrar em python
# -F cria um arquivo unico
# -w (--windowed, --noconsole) não abre o prompt e roda em janela
# set PYTHONOPTIMIZE=1 && pyinstaller -w -F CCFacil099_2_4.py
