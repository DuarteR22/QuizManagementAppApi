from flask import Flask, jsonify, request
import  psycopg2


app = Flask(__name__)  

#app.config['SECRET_KEY'] = 'it\xb5u\xc3\xaf\xc1Q\xb9\n\x92W\tB\xe4\xfe__\x87\x8c}\xe9\x1e\xb8\x0f'


NOT_FOUND_CODE = 400
OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500

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
            result = cursor.fetchone()[0]

            if result:
                return jsonify({"mensagem": "Login efetuado com sucesso"}), 200
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
            cursor.execute("SELECT inserir_utilizador(%s,%s,%s)", (username,password))
            conn.commit()
            return jsonify({"mensagem": "Registo efetuado com sucesso!"}), 200
    except psycopg2.DatabaseError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



     
if __name__ == '__main__':
    app.run(debug=True)