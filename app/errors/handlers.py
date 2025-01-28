from flask import render_template, request, current_app
from datetime import datetime

# Funções de tratamento de erros

# Tratamento de erro 404
def handle_404(error):
    # Log do erro
    current_app.logger.error('Erro 404: %s - %s', 
                             request.url, 
                             request.method)    
    return render_template('errors/404.html', 
                           request=request, 
                           datetime=datetime), 404

# Tratamento de erro 500
def handle_500(error):
    # Log do erro
    current_app.logger.error('Erro 500: %s - %s', 
                             request.url, 
                             request.method)    
    return render_template('errors/500.html', 
                           request=request, 
                           datetime=datetime), 500