from dashboard import app
import os

if os.getenv('FLASK_DEBUG') == 'true':
    app.run(host="localhost", debug=True)