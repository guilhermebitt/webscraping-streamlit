import streamlit as st
import matplotlib.pyplot
import pandas
from fpdf import FPDF
from requests import get as get_response
from bs4 import BeautifulSoup

def page1():
    elements = []
    for paragraph in site.find_all('p'):
        elements.append(paragraph.text)
    for num, element in enumerate(elements):
        if 'Item' in element:
            num = num
            item_text = element[:element.find(':')+1]
            item = element[element.find(':')+1:]
            classe_text = elements[num+1][:elements[num+1].find(':')+1]
            classe = elements[num+1][elements[num+1].find(':')+1:]
            coluna1 = [item_text, classe_text]
            coluna2 = [item, classe]
            texto = elements[num+2:-1]
    return coluna1, coluna2, texto


def texto_avaliacao(avaliacao):
    if int(avaliacao) > 100:
        text = f'{avaliacao} pontos, é um SCP muito famoso, a esse ponto, já deve ser um SCP bem conhecido na comunidade.'
    elif int(avaliacao) > 50:
        text = f'{avaliacao} pontos, caramba, é uma boa quantidade de pontos, talvez não seja tão famoso quanto SCP-173 ou SCP-002, mas com certeza é bem avaliado.'
    elif int(avaliacao) > 0:
        text = f'{avaliacao} pontos, nem abaixo do 0, nem muito acima, pode ser que algumas pessoas conheçam esse SCP, mas nem todo mundo consegue confirmar que ele é bom.'
    elif int(avaliacao) == 0:
        text = f'{avaliacao} pontos, bem, é um scp neutro, pode ser que ele seja recente na comunidade ou que a mesma ainda não possui uma posição muito concreta.'
    elif int(avaliacao) < 0:
        text = f'{avaliacao} pontos, bom, parece que a comunidade não gosta muito desse SCP.\nSabia que a partir do momento que uma criação SCP oficial do site fica com avaliação negativa, a página do scp é excluida ou então reescrita, se alguém além do autor original se dispor a reescreve-la?'
    return text


def create_pdf(chart, texto, avaliacao):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 25)

    # TABELA
    pdf.multi_cell(188, 10, 'SCP "WIKI"', ln=True)
    pdf.set_font('Arial', 'B', 15)
    for index, row in chart.iterrows():
        for data in row.values:
            pdf.cell(47, 10, str(data), border=True)
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 20, ln=True)

    # TEXTO
    for paragraph in texto:
        try:
            pdf.multi_cell(188, 10, '   ' + paragraph.replace('█', '*'), ln=True)
        except:
            pass

    # O QUE A COMUNIDADE ACHA
    pdf.add_page()
    pdf.set_font('Arial', 'B', 25)
    pdf.multi_cell(188, 10, 'O que a comunidade acha desse SCP?', ln=True)
    pdf.set_font('Arial', '', 16)
    pdf.multi_cell(188, 10, avaliacao, ln=True)

    # IMAGE
    pdf.image('Graphic.png', h=pdf.eph/2, w=pdf.epw)
    # DOWNLOAD
    pdf_bytes = bytes(pdf.output(dest='S'))
    return pdf_bytes

# STREAMLIT PÁGINA INICIAL
st.title('SCP "WIKI"')
st.text('Uma wiki alternativa para conhecer um pouco sobre os SCPs')
st.caption('SCP, ou "Secure, Contain, Protect", refere-se a uma comunidade de ficção colaborativa que cria e compartilha histórias sobre entidades, artefatos e fenômenos anômalos. Cada SCP é designado com um número único e descrito em um formato que simula um relatório científico ou arquivo de segurança, detalhando suas propriedades incomuns e os procedimentos necessários para mantê-lo seguro e fora do alcance do público. A comunidade SCP não apenas inventa esses elementos, mas também explora suas implicações narrativas, científicas e filosóficas, criando um universo rico e intrincado de mistério, horror e ficção científica.')
st.caption('Autor: Guilherme Bittencourt')
submitted = False
with st.form(key='input_scp', border=True):
    scp_num = st.text_input('SCP')
    if st.form_submit_button('Submit'):
        # DADOS DO SITE SCP
        url_scp = f'http://scp-pt-br.wikidot.com/scp-{scp_num}'
        response = get_response(url_scp)
        print(f'RESPOSTA DO SITE: {response.status_code}')

        error = False
        try:
            site = BeautifulSoup(response.content, 'html.parser')
            coluna1, coluna2, texto = page1()
        except:
            error = True
        if response.status_code != 404 and error == False:
            site = BeautifulSoup(response.content, 'html.parser')
            tab1, tab2 = st.tabs(["Página Inicial", "Avaliação da Comunidade"])
            submitted = True
        elif response.status_code != 404 and error == True:
            st.error('Página Bloqueada, você não tem autorização para acessar.')
        else:
            st.error('Código de SCP inválido, verifique e tente novamente.')
        
if submitted == True:
    # PÁGINA INICIAL
    with tab1:
        coluna1, coluna2, texto = page1()
        data = {
            'Atributo': coluna1,
            'Valor': coluna2
        }
        chart = pandas.DataFrame(data)
        st.dataframe(chart, hide_index=True)
        for i in texto:
            st.write(i)

    # AVALIAÇÃO DO SCP
    with tab2:
        avaliacao = site.find('span', class_='number prw54353').string
        # O QUE A COMUNIDADE ACHA DESSE SCP?
        st.subheader('O que a comunidade acha desse SCP?')
        texto_avaliacao = texto_avaliacao(avaliacao[0:])
        st.markdown(texto_avaliacao)
        # GRÁFICO COMPARANDO SCPS
        fig, ax = matplotlib.pyplot.subplots()
        SCPs = ['SCP-021-J (-10)', f'SCP-{scp_num} ({avaliacao})', 'SCP-002-PT (+152)']
        avaliacoes = [-10, int(avaliacao), 152]
        bar_labels = ['SCP Menos Avaliado', 'SCP Escolhido', 'SCP Mais Avaliado']
        bar_colors = ['tab:red', 'tab:blue', 'tab:green']
        ax.bar(SCPs, avaliacoes, label=bar_labels, color=bar_colors)
        ax.set_ylabel('Avaliação')
        ax.set_title('Avaliação da Comunidade')
        ax.legend(title='SCPs')
        st.subheader('Gráfico de pontuação:')
        with st.container(border=True):
            st.markdown('Considerando o SCP mais avaliado da comunidade e o menos avaliado da comunidade, podemos ver a sua posição.')
            st.pyplot(fig)
            st.caption('Dados Retirados do dia 11/07/2024.')
            matplotlib.pyplot.savefig('Graphic.png')
    # DONLOAD DO PDF
    pdf_bytes = create_pdf(chart, texto, texto_avaliacao)
    st.download_button('Baixar PDF', pdf_bytes, 'SCP "WIKI".pdf', 'application/pdf')
    
