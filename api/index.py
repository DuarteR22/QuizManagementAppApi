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
    tempo = dados.get('tempo_max')
    u_uid = dados.get('utilizador_uid')

    conn = connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT public.inserir_quiz(%s, %s, %s, %s)", 
                           (titulo, descricao, tempo, u_uid))
            novo_id = cursor.fetchone()[0]
            conn.commit()
            
            if novo_id != -1:
                return jsonify({"mensagem": "Quiz criado com sucesso", "qid": novo_id}), 201
            else:
                return jsonify({"mensagem": "Erro ao inserir na base de dados"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

     
if __name__ == '__main__':
    app.run(debug=True)
