import flask
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
from flask_bcrypt import generate_password_hash, check_password_hash
import fdb
from fpdf import FPDF

secret_key = 'qualquercoisa'

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

host = 'localhost'
database = r'C:\Users\Aluno\PycharmProjects\PythonProject\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("select id_livro, titulo, autor, ano_publicado from livros")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('index.html', livros=livros)


@app.route('/novo')
def novo():
    if 'id_usuario'not in session:
        flash("Você precisa estar logado para acessar esta página")
        return redirect(url_for('index'))
    return render_template('novo.html')

@app.route('/criar', methods=['POST'])
def criar():
    if 'id_usuario'not in session:
        flash("Você precisa estar logado para acessar esta página")
    #pegar os dados do formulario
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM LIVROS WHERE livros.TITULO = ?', (titulo,))
        if cursor.fetchone(): #se existir
            flash('Esse livro já está cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("insert into livros(titulo, autor, ano_publicado) values (?, ?, ?)",
                       (titulo, autor, ano_publicado))

        con.commit()
    finally:
        cursor.close()
    flash('O Livro Foi Cadastrado Com Sucesso!')
    return redirect(url_for('index'))


@app.route('/atualizar')
def atualizar():
    return render_template('editar.html')



@app.route('/deletar/<int:id>', methods=['GET', 'POST'])
def deletar(id):
    if 'id_usuario'not in session:
        flash("Você precisa estar logado para deletar")
    cursor = con.cursor()
    try:
        cursor.execute("delete from livros where livros.id_livro = ?", (id,))
        return redirect(url_for('index'))
        con.commit()
    finally:
        cursor.close()
    flash('O Livro Foi Deletado Com Sucesso!')
    return redirect(url_for('index'))

@app.route('/deletar_user/<int:id>', methods=['GET', 'POST'])
def deletar_user(id):
    if 'id_usuario'not in session:
        flash("Você precisa estar logado para deletar")
    cursor = con.cursor()
    try:
        cursor.execute("delete from usuarios where id_usuario = ?", (id,))
        return redirect(url_for('perfil'))
        con.commit()
    finally:
        cursor.close()
    flash('O Usuário Foi Deletado Com Sucesso!')
    return redirect(url_for('perfil'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'id_usuario'not in session:
        flash("Você precisa estar logado para acessar esta página")
    cursor = con.cursor()
    cursor.execute("select id_livro, titulo, autor, ano_publicado from livros where id_livro = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash("Livro não foi encontrado")
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicado']

        cursor.execute("update livros set titulo = ?, autor = ?, ano_publicado = ? where id_livro = ?",
                       (titulo, autor, ano_publicado, id))
        con.commit()
        flash("Livro Atualizado Com Sucesso")
        return redirect(url_for('index'))
    cursor.close()
    return render_template('editar.html', livro=livro)

@app.route('/editar_user/<int:id>', methods=['GET', 'POST'])
def editar_user(id):
    cursor = con.cursor()
    cursor.execute("select id_usuario, nome, email, senha from usuarios where id_usuario = ?", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        flash("Usuário não foi encontrado")
        return redirect(url_for('perfil'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute("update usuarios set nome = ?, email = ?, senha = ? where id_usuario = ?",
                        (nome, email, senha, id))
        con.commit()
        cursor.close()
        flash("Usuário Atualizado Com Sucesso")
        return redirect(url_for('perfil'))

    return render_template('editar_user.html', usuario=usuario)

@app.route('/user')
def user():
    return render_template('cadastro_user.html')

@app.route('/login')
def login():
    return  render_template('login_user.html')

@app.route('/perfil')
def perfil():
    cursor = con.cursor()
    cursor.execute("select id_usuario, nome, email, senha from usuarios")
    usuarios = cursor.fetchall()
    id_usuario = usuarios[0]
    cursor.close()

    if "id_usuario" not in session:
        flash("Não está logado")
        return redirect(url_for('login'))
    return render_template('perfil.html', usuarios=usuarios)

@app.route('/cadastro_user', methods=['GET', 'POST'])
def cadastro_user():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM USUARIOS WHERE usuarios.EMAIL = ?', (email,))
        if cursor.fetchone():
            flash('Esse email já está cadastrado')
            return redirect(url_for('index'))
        senha_cripto = generate_password_hash(senha)
        cursor.execute("INSERT INTO USUARIOS(nome, email, senha) VALUES(?, ?, ?)",
                       (nome, email, senha_cripto))

        con.commit()
    finally:
        cursor.close()
    flash('O Usuário Foi Cadastrado Com Sucesso!')
    return redirect(url_for('index'))

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()
        cursor.execute("select id_usuario, nome, email, senha from usuarios where email = ?", (email,))
        usuario = cursor.fetchone()
        id_usuario = usuario[0]
        senha_cripto = usuario[3]
        cursor.close()

        if usuario:

            if check_password_hash(senha_cripto, senha):
                flash("Usuário Logado Com Sucesso")
                session['id_usuario'] = id_usuario
                return redirect(url_for('perfil'))
            flash("Falha ao logar")
            return redirect(url_for('login_user'))
    return render_template('login_user.html')

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('index'))

@app.route('/relatorio')
def relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicado FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha abaixo do título
    pdf.ln(5)  # Espaço após a linha
    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)
    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')
    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')


if (__name__ == '__main__'):
    app.run(debug=True)
