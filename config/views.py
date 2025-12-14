"""
Views for the config project.
"""
from django.http import HttpResponse


def home(request):
    """
    Simple home page view.
    This is a placeholder until the main application views are created.
    """
    return HttpResponse(
        """
        <html>
        <head>
            <title>Compozy - AI-Powered Software Development Platform</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .links {
                    margin-top: 30px;
                }
                .links a {
                    display: inline-block;
                    margin-right: 20px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .links a:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Compozy</h1>
                <p><strong>AI-Powered Software Development Platform</strong></p>
                <p>
                    Bem-vindo ao Compozy! Esta é uma plataforma que automatiza o ciclo completo 
                    de desenvolvimento de software, desde a análise de requisitos até a implementação 
                    de código com testes.
                </p>
                <p>
                    O projeto está em desenvolvimento. Em breve você poderá criar problemas, 
                    gerar PRDs, especificações técnicas e executar tarefas automaticamente.
                </p>
                <div class="links">
                    <a href="/admin/">Admin Django</a>
                </div>
            </div>
        </body>
        </html>
        """,
        content_type='text/html; charset=utf-8'
    )
