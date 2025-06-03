from flask import Flask, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app) 
@app.route('/frontend/run-script', methods=['POST'])
def run_script():
    try:
        process = subprocess.Popen(['python3', 'hand.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate() 
        
        if stderr:
            return jsonify({'output': f'Error: {stderr.decode("utf-8")}'})
        return jsonify({'output': stdout.decode('utf-8') or "Python script executed successfully"})
    
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)

