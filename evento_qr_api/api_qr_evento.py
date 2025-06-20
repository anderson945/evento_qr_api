
from flask import Flask, request, render_template_string
import pandas as pd
from datetime import datetime

app = Flask(__name__)

EXCEL_FILE = 'estudiantes_con_qr.xlsx'

def cargar_datos():
    return pd.read_excel(EXCEL_FILE)

def guardar_datos(df):
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def home():
    html = """
    <h2>Escaneo de QR para Evento</h2>
    <form method='POST' action='/validar'>
        <label>Contenido del QR:</label><br>
        <input name='qrdata' style='width:400px'/><br><br>
        <input type='submit' value='Validar QR'/>
    </form>
    """
    return render_template_string(html)

@app.route('/validar', methods=['GET', 'POST'])
def validar():
    try:
        if request.method == 'POST':
            qrdata = request.form['qrdata']
            qrdata = eval(qrdata)
            token = qrdata.get('token')
            codigo = qrdata.get('codigo_estudiante')
        else:
            token = request.args.get('token')
            codigo = request.args.get('codigo_estudiante')

        if not token or not codigo:
            return "❌ Faltan parámetros en el QR."

        df = cargar_datos()
        fila = df[df['Token'] == token]

        if fila.empty:
            return "❌ QR inválido."

        if fila.iloc[0]['Usado'] == 'Sí':
            return "⚠️ Este QR ya fue usado."

        df.loc[df['Token'] == token, 'Usado'] = 'Sí'
        df.loc[df['Token'] == token, 'Fecha Ingreso'] = datetime.now()
        guardar_datos(df)

        nombre = fila.iloc[0].get('Nombre Completo', 'Estudiante')
        return f"✅ Acceso permitido a {nombre}."

    except Exception as e:
        return f"Error al validar: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
