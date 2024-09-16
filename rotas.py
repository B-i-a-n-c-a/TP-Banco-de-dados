from app import app
from flask import render_template, request, session, redirect, url_for
import sqlite3, re, base64

app.secret_key = 'supersecretkey' # 'corta' a execução de uma funcao em algumas partes

def valida_cpf(cpf):
    return bool(re.match(r'^\d{11}$', cpf))

def valida_cep(cep):
    return bool(re.match(r'^\d{8}$', cep))

def valida_rg(rg):
    return bool(re.match(r'^\d{10}$', rg))

def valida_telefone(telefone):
    return bool(re.match(r'^\d{11}$', telefone))

def verifica_existencia_funcionario():
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()
    cursor.execute("SELECT COUNT(*) FROM funcionario")
    quantidade_funcionarios = cursor.fetchone()[0]
    banco.close()
    return quantidade_funcionarios > 0

@app.route('/')
def index():
    return render_template('inicial_funcionario.html')

@app.route('/cadastro_funcionario')
def cadastro_funcionario():
    return render_template('funcionario_form.html')

@app.route('/cadastraF', methods=['POST'])
def cadastraF():
    if verifica_existencia_funcionario():
        erros = "Já existe um funcionario cadastrado!"
        return  render_template('funcionario_form.html', erros=erros)
    
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    cpf = request.form.get('cpf')
    cargo = request.form.get('cargo')
    login = request.form.get('login')
    senha = request.form.get('senha')

    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()

    erros = ""
    if not valida_cpf(cpf):
        erros = "Dado inválido!"

    if erros:
        return render_template('funcionario_form.html', erros=erros)

    else:
        cursor.execute('INSERT INTO funcionario (nome, idade, cpf, cargo, login, senha) VALUES (?, ?, ?, ?, ?, ?)', (nome, idade, cpf, cargo, login, senha))

        banco.commit()
        banco.close()

        return render_template('inicial_funcionario.html')

@app.route('/login')
def login_funcionario():
    return render_template('login_form.html')

@app.route('/verifica_login', methods=['GET', 'POST'])
def verifica_login():
    login = request.form.get('login')
    senha = request.form.get('senha')
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM funcionario WHERE login=? AND senha=?", (login, senha))
    resultado = cursor.fetchone()   
    banco.close()
    erros = ""
    if resultado:    
        return render_template('inicial_funcionario.html')
    else: 
        erros = "Login ou senha incorretos, tonho!!!"
        return render_template('login_form.html', erros=erros)
    
@app.route('/cadastro_cliente')
def cadastro_cliente():
    return render_template('cliente_form.html')

@app.route('/cadastraC', methods=['GET','POST'])
def cadastraC():
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    cpf = request.form.get('cpf')
    rg = request.form.get('rg')
    telefone = request.form.get('telefone')
    banco = request.form.get('banco')
    agencia = request.form.get('agencia')
    numero_conta = request.form.get('numero_conta')
    tipo_conta = request.form.get('tipo_conta')
                
    conexao_banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = conexao_banco.cursor()

    erros = ""
    
    if not valida_cpf(cpf):
        erros = "Dado inválido!"
    if not valida_rg(rg):
        erros = "Dado inválido!"
    if not valida_telefone(telefone):
        erros = "Dado inválido!"

    if erros:
        return render_template('cliente_form.html', erros=erros)
    else:       
        
        cursor.execute('INSERT INTO cliente (nome, idade, cpf, rg, telefone, banco, agencia, numero_conta, tipo_conta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (nome, idade, cpf, rg, telefone, banco, agencia, numero_conta, tipo_conta))
                    
        conexao_banco.commit()
        conexao_banco.close()

        return render_template('inicial_funcionario.html')

@app.route('/cadastro_imovel')
def cadastro_imovel():
    return render_template('imovel_form.html')

@app.route('/cadastraI', methods=['POST'])
def cadastraI():
    end_numero = request.form.get('end_numero')
    end_bairro = request.form.get('end_bairro')
    end_cidade = request.form.get('end_cidade')
    end_estado = request.form.get('end_estado')
    end_cep = request.form.get('end_cep')
    area_total = request.form.get('area_total')
    qtd_comodo = request.form.get('qtd_comodo')
    preco = request.form.get('preco')
    status = request.form.get('status')
    imagem = request.files.getlist('imagem')

    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()
        
    erros = ""

    if not valida_cep(end_cep):
        erros = "Dado inválido!"
    if erros:
        return render_template('imovel_form.html', erros=erros)
    else: 
       cursor.execute('INSERT INTO imovel (end_numero, end_bairro, end_cidade, end_estado, end_cep, area_total, qtd_comodo, preco, status) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (end_numero, end_bairro, end_cidade, end_estado, end_cep, area_total, qtd_comodo, preco, status))
       banco.commit()
       
    id_imovel = cursor.lastrowid

    for img in imagem:
        dados_imagem = img.read()
        cursor.execute('INSERT INTO imagens(id_imovel, imagem) VALUES (?, ?)', (id_imovel, sqlite3.Binary(dados_imagem)))
    banco.commit()
    banco.close()

    return render_template('inicial_funcionario.html')

@app.route('/imprime_imovel')
def imprime_imovel():
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()

    cursor.execute("SELECT id, end_numero, end_bairro, end_cidade, end_estado, end_cep, area_total, qtd_comodo, preco, status FROM imovel")
    dados = cursor.fetchall()

    for imovel in dados:
        imovel_completo = list(imovel)
        id_imovel = imovel[0] #id_imovel recebe os dados da coluna 0 da tabela imovel

        cursor.execute("SELECT imagem FROM imagens WHERE id_imovel = ?", (id_imovel,))
        imagem = cursor.fetchone()
        
        img = imagem[0]
        for img in imagem:
            imagem_codificada = base64.b64encode(img).decode('utf-8')
        imovel_completo.append(imagem_codificada)

    banco.close()
    return render_template('imprime_imovel.html',imovel_completo=imovel_completo)
    #return render_template('imprime_imovel.html', dados=dados)

@app.route('/imprime_cliente')
def imprime_cliente():
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()

    cursor.execute("SELECT nome, idade, cpf, rg, telefone, banco FROM cliente")
    dados = cursor.fetchall()

    banco.close()
    return render_template('imprime_cliente.html', dados=dados)

def exclui_cadastro(tabela, chave, valor):
    erros = ""
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()

    cursor.execute("SELECT COUNT(1) FROM cliente WHERE cpf = ?", (chave,))
    resultado = cursor.fetchone()
    if resultado is None:
        erros = "Dado não encontrado!!"
        return render_template('inicial_funcionario.html', erros=erros)
    else:
        sql = f"DELETE FROM {tabela} WHERE {chave} = ?"
        cursor.execute(sql, (valor,))
        banco.commit()
        banco.close()
        erros = "Excluído com sucesso!!"
        return render_template('inicial_funcionario.html', erros=erros)
    
@app.route('/exclui_imovel')
def exclui_imovel():
    return render_template('exclui_imovel.html')

@app.route('/exclui_I', methods=['POST'])
def exclui_I():
    end_cep = request.form.get('end_cep')
    tabela_a_excluir = 'imovel'
    exclui_cadastro(tabela_a_excluir, 'end_cep', end_cep)

    return render_template('inicial_funcionario.html')

@app.route('/exclui_cliente')
def exclui_cliente():
    return render_template('exclui_cliente.html')

@app.route('/exclui_C', methods=['POST'])
def exclui_C():
    cpf = request.form.get('cpf')
    tabela_a_excluir = 'cliente'

    return  exclui_cadastro(tabela_a_excluir, 'cpf', cpf)

@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/verifica_dado', methods=['POST'])
def verifica_dado():
    dado = request.form.get('dado')
    cpf = r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$'
    cep = r'^\d{5}-?\d{3}$'
    session['dado'] = dado

    if re.fullmatch(cpf, dado):
        return render_template('verifica_cliente.html')
    elif re.fullmatch(cep, dado):
        return render_template('verifica_imovel.html')
    erros = "Dado  não encontrado."
    return render_template('update.html', erros=erros)

@app.route('/verifica_cliente', methods=['POST'])
def verifica_cliente():
    erros = ""
    cpf = session.get('dado') #redebe o dado que foi amarzenado a sessão na funcao 'update_cliente'

    conexao_banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = conexao_banco.cursor()
    dados = {
        'nome': request.form.get('nome'),
        'idade': request.form.get('idade'),
        'rg': request.form.get('rg'),
        'telefone': request.form.get('telefone'),
        'banco': request.form.get('banco'),
        'agencia': request.form.get('agencia'),
        'numero_conta': request.form.get('numero_conta'),
        'tipo_conta': request.form.get('tipo_conta'),
    }

    dados_final = {chave: valor for chave, valor in dados.items() if valor}

    if not dados_final:
        erros = "Não existe nenhum dado a ser atualizado"
        return render_template('verifica_cliente.html', erros=erros)
    else:
        campos = ", ".join([f"{k} = ?" for k in dados_final.keys()])
        valores = list(dados_final.values())
        valores.append(cpf)

        sql = f"UPDATE cliente SET {campos} WHERE cpf = ?"
        cursor.execute(sql, valores)
        conexao_banco.commit()
        erros = 'Dados atualizados com sucesso!'
        return render_template('inicial_funcionario.html', erros=erros)

@app.route('/verifica_imovel', methods=['POST'])
def verifica_imovel():
    erros = ""
    end_cep = session.get('dado')

    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()
    dados = {
        'end_numero':request.form.get('end_numero'),
        'end_bairro':request.form.get('end_bairro'),
        'end_cidade': request.form.get('end_cidade'),
        'end_estado':request.form.get('end_estado'),
        'area_total':request.form.get('area_total'),
        'qtd_comodo':request.form.get('qtd_comodo'),
        'preco':request.form.get('preco'),
        'status':request.form.get('status'),
    }

    dados_final = {chave: valor for chave, valor in dados.items() if valor}

    if not dados_final:
        erros = "Não existe nenhum dado a ser atualizado"
        return render_template('verifica_imovel.html', erros=erros)
    else:
        campos = ", ".join([f"{k} = ?" for k in dados_final.keys()])
        valores = list(dados_final.values())
        valores.append(end_cep)

        sql = f"UPDATE imovel SET {campos} WHERE end_cep = ?"
        cursor.execute(sql, valores)
        banco.commit()
        erros = 'Dados atualizados com sucesso!'
        return render_template('inicial_funcionario.html', erros=erros)


@app.route('/ordena', methods=['POST'])
def ordenar():
    atributo = request.form.get('atributo')  
    tabela = request.form.get('tabela')
    banco = sqlite3.connect('imobiliaria_banco.db')
    cursor = banco.cursor()
    sql = f"SELECT * FROM {tabela} ORDER BY {atributo} ASC"
    cursor.execute(sql)
    banco.commit()
    dados  = cursor.fetchall()

    if tabela == 'cliente':
        return render_template('imprime_cliente.html', dados=dados)
    elif tabela == 'imovel':
        return render_template('imprime_imovel.html', dados=dados)

@app.route('/ordenaM', methods=['POST'])
def ordenarM():
    atributo = request.form.get('atributo')  
    if atributo:
        banco = sqlite3.connect('imobiliaria_banco.db')
        cursor = banco.cursor()
        sql = f"SELECT * FROM imovel ORDER BY {atributo} ASC"
        cursor.execute(sql)
        dados  = cursor.fetchall()
        banco.close()
        return render_template('imprime_imovel.html', dados=dados)


#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#venv\Scripts\activate
#deactivate