import flask
from flask import Flask, render_template, request, flash, redirect, url_for
import fdb

secret_key = 'qualquercoisa'
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO.FDB'
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
    return render_template('novo.html')

@app.route('/criar', methods=['POST'])
def criar():
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
    cursor = con.cursor()
    try:
        cursor.execute("delete from livros where livros.id_livro = ?", (id,))
        return redirect(url_for('index'))
        con.commit()
    finally:
        cursor.close()
    flash('O Livro Foi Deletado Com Sucesso!')
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
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

@app.route('/novo_user')
def novo_user():
    return  render_template('cadastro_user.html')

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
            return redirect(url_for('novo'))
        cursor.execute("INSERT INTO USUARIOS(nome, email, senha) VALUES(?, ?, ?)",
                       (nome, email, senha))

        con.commit()
    finally:
        cursor.close()
    flash('O Usuário Foi Cadastrado Com Sucesso!')
    return redirect(url_for('index'))

if (__name__ == '__main__'):
    app.run(debug=True)