from flask import Flask, jsonify, request
import  psycopg2
from flask_jwt_extended import JWTManager, create_access_token 
from datetime import timedelta

app = Flask(__name__)  

app.config['JWT_SECRET_KEY'] = 'it\xb5u\xc3\xaf\xc1Q\xb9\n\x92W\tB\xe4\xfe__\x87\x8c}\xe9\x1e\xb8\x0f'
jwt = JWTManager(app)

def connection():
 return psycopg2.connect(
    dbname = "db2022139046",
    user = "a2022139046",
    password = "a202425",
    host="aid.estgoh.ipc.pt",
    port = 5432
)

@app.route('/login_utilizador', methods = ['POST'])
def login():
    dados = request.json
    username = dados.get('username')
    password = dados.get('password')
    if None in [username,password]:
        return jsonify({"mensagem": "Todos os campos são obrigatórios."}), 400
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT login(%s,%s)", (username,password))
            u_uid = cursor.fetchone()[0]
  
            if u_uid:
                access_token = create_access_token(
                   identity = str(u_uid),
                   expires_delta=timedelta(minutes=5)
                )
                return jsonify({"mensagem": "Login efetuado com sucesso",
                                "token": access_token,
                                "u_uid": u_uid
                               }), 200
            else: 
                return jsonify({"mensagem": "Credenciais invalidas"}), 401
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close() 


@app.route('/inserir_utilizador', methods=['POST'])
def criar_evento():
    dados = request.json
    username = dados.get('username')
    password = dados.get('password')
    if None in [username,password]:
        return jsonify({"mensagem": "Todos os campos são obrigatórios."}), 400

    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT inserir_utilizador(%s,%s)", (username,password))
            conn.commit()
            return jsonify({"mensagem": "Registo efetuado com sucesso!"}), 200
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/inserir_quiz', methods=['POST'])
def inserir_quiz():
    dados = request.json
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')
    tempo = int(dados.get('tempo_max'))
    u_uid = int(dados.get('utilizador_uid'))

    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.inserir_quiz(%s, %s, %s, %s)", 
                           (titulo, descricao, tempo, u_uid))
            novo_id = cursor.fetchone()[0]
            conn.commit()
            
            if novo_id != -1:
                return jsonify({"mensagem": "Quiz inserido com sucesso", "qid": novo_id}), 201
            else:
                return jsonify({"mensagem": "Erro ao inserir quiz"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/inserir_questao', methods=['POST'])
def inserir_questao():
    dados = request.json
    pergunta = dados.get('pergunta')
    respostas = dados.get('respostas') 
    num_r = dados.get('num_respostas')
    correta = dados.get('resposta_correta')
    url = dados.get('url_imagem')
    qid = dados.get('quiz_qid')

    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.inserir_questao(%s, %s, %s, %s, %s, %s)", 
                           (pergunta, respostas, num_r, correta, url, qid))
            novo_quid = cursor.fetchone()[0]
            conn.commit()
            if novo_quid != -1:
                return jsonify({
                    "mensagem": "Questão inserida com sucesso!",
                    "quid": novo_quid
                }), 201
            else:
                return jsonify({"mensagem": "Erro ao inserir na base de dados"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/listar_quizzes', methods=['GET'])
def listar_quizzes():
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT qid, titulo, descricao, tempo_max, utilizador_uid, username_criador FROM public.v_lista_quizzes")
            rows = cursor.fetchall()
            
            quizzes = []
            for r in rows:
                quizzes.append({
                    "qid": r[0],
                    "titulo": r[1],
                    "descricao": r[2],
                    "tempo_max": r[3],
                    "utilizador_uid": r[4],
                    "username_criador": r[5]
                })
            return jsonify(quizzes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/eliminar_quiz', methods=['POST'])
def eliminar_quiz():
    dados = request.json
    qid = dados.get('qid')
    u_uid = dados.get('u_uid') 

    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.eliminar_quiz(%s, %s)", (qid, u_uid))
            resultado = cursor.fetchone()[0]
            conn.commit()
            if resultado > 0:
                return jsonify({"mensagem": "Quiz eliminado com sucesso!"}), 200
            else:
                return jsonify({"mensagem": "Permissão negada ou Quiz inexistente"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
@app.route('/listar_questoes', methods=['POST'])
def listar_questoes_por_quiz():
    dados = request.json
    qid = dados.get('qid')
    if qid is None:
        return jsonify({"mensagem": "ID do quiz é obrigatório"}), 400
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM public.listar_questoes(%s)", (qid,))
            rows = cursor.fetchall()
            questoes = []
            for r in rows:
                questoes.append({
                    "quid": r[0],
                    "pergunta": r[1],
                    "num_respostas": r[2],
                    "respostas": r[3],
                    "resposta_correta": r[4],
                    "url_imagem": r[5],
                    "quiz_qid": r[6]
                })
            return jsonify(questoes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
     
@app.route('/eliminar_questao', methods=['POST'])
def eliminar_questao():
    dados = request.json
    quid = dados.get('quid')
    if quid is None:
        return jsonify({"mensagem": "O ID da questão (quid) é obrigatório."}), 400
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.eliminar_questao(%s)", (quid,))
            resultado = cursor.fetchone()[0]
            conn.commit()
            if resultado > 0:
                return jsonify({"mensagem": "Questão eliminada com sucesso!"}), 200
            else:
                return jsonify({"mensagem": "Questão não encontrada ou já eliminada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
     
@app.route('/alterar_questao', methods=['POST'])
def alterar_questao():
    dados = request.json
    quid = dados.get('quid')  
    pergunta = dados.get('pergunta')
    respostas = dados.get('respostas') 
    num_respostas = dados.get('num_respostas')
    resposta_correta = dados.get('resposta_correta')
    url = dados.get('url_imagem')
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.alterar_questao(%s, %s, %s, %s, %s, %s)", (quid, pergunta, num_respostas, respostas, resposta_correta, url))
            resultado = cursor.fetchone()[0]
            conn.commit()
            if resultado > 0:
                return jsonify({"mensagem": "Questão alterada com sucesso!"}), 200
            else:
                return jsonify({"mensagem": "Questão não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/listar_questao_id', methods=['POST'])
def listar_questao_id():
    dados = request.json
    quid = dados.get('quid')
    if quid is None:
        return jsonify({"mensagem": "O ID da questão é obrigatório"}), 400
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM public.listar_questao_id(%s)", (quid,))
            r = cursor.fetchone()
            if r:
                return jsonify({
                    "quid": r[0],
                    "pergunta": r[1],
                    "num_respostas": r[2],
                    "respostas": r[3],
                    "resposta_correta": r[4],
                    "url_imagem": r[5],
                    "quiz_qid": r[6]
                }), 200
            else:
                return jsonify({"mensagem": "Questão não encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/alterar_quiz', methods=['POST'])
def alterar_quiz():
    dados = request.json
    qid = dados.get('qid')  
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')
    tempo_max = dados.get('tempo_max')
    
    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.alterar_quiz(%s, %s, %s, %s)", (qid, titulo, descricao, tempo_max))
            resultado = cursor.fetchone()[0]
            conn.commit()
            if resultado > 0:
                return jsonify({"mensagem": "Quiz alterado com sucesso!"}), 200
            else:
                return jsonify({"mensagem": "Quiz não encontrado"}), 404
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/listar_quiz_id', methods=['POST'])
def listar_quiz_id():
    qid = request.json.get('qid')
    conn = connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM public.listar_quiz_id(%s)", (qid,))
        r = cursor.fetchone()
        if r:
            return jsonify({"qid": r[0], "titulo": r[1], "descricao": r[2], "tempo_max": r[3]}), 200
        return jsonify({"mensagem": "Quiz não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
