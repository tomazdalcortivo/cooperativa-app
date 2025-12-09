"""
Testes para validar as rotas do módulo institucional (RF10)
"""

import sys
sys.path.insert(0, '.')

from app import create_app

def test_routes():
    """Testa se todas as rotas estão registradas corretamente"""
    
    app = create_app()
    client = app.test_client()
    
    # Lista de rotas a testar
    routes = [
        ('/institucional/home', 200, 'Home'),
        ('/institucional/sobre', 200, 'Sobre Nós'),
        ('/institucional/produtores', 200, 'Produtores'),
        ('/institucional/blog', 200, 'Blog'),
        ('/institucional/blog/1', 200, 'Blog Detalhes'),
        ('/institucional/contato', 200, 'Contato'),
        ('/institucional/faq', 200, 'FAQ'),
        ('/institucional/privacidade', 200, 'Privacidade'),
        ('/institucional/termos', 200, 'Termos'),
    ]
    
    print("\n" + "="*60)
    print("TESTANDO ROTAS DO MÓDULO INSTITUCIONAL (RF10)")
    print("="*60 + "\n")
    
    all_passed = True
    
    for route, expected_status, name in routes:
        try:
            response = client.get(route)
            status = "✅ PASSOU" if response.status_code == expected_status else "❌ FALHOU"
            
            if response.status_code != expected_status:
                all_passed = False
            
            print(f"{status} | {name:20} | {route:30} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ ERRO   | {name:20} | {route:30} | {str(e)}")
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    else:
        print("❌ ALGUNS TESTES FALHARAM. VERIFIQUE OS ERROS ACIMA.")
    
    print("="*60 + "\n")
    
    return all_passed

def test_blueprint_registration():
    """Testa se o blueprint foi registrado corretamente"""
    
    app = create_app()
    
    print("\n" + "="*60)
    print("VERIFICANDO REGISTRO DO BLUEPRINT")
    print("="*60 + "\n")
    
    blueprints = app.blueprints
    institucional_registered = 'institucional' in blueprints
    
    if institucional_registered:
        print("✅ Blueprint 'institucional' registrado com sucesso!")
    else:
        print("❌ Blueprint 'institucional' NÃO foi registrado!")
    
    print(f"\nBlueprints registrados na aplicação:")
    for bp_name in blueprints:
        print(f"  - {bp_name}")
    
    print("\n" + "="*60 + "\n")
    
    return institucional_registered

if __name__ == '__main__':
    print("\n🧪 INICIANDO TESTES DO MÓDULO INSTITUCIONAL (RF10)\n")
    
    # Teste 1: Verificar registro do blueprint
    bp_test = test_blueprint_registration()
    
    # Teste 2: Testar todas as rotas
    routes_test = test_routes()
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Blueprint Registration: {'✅ PASSOU' if bp_test else '❌ FALHOU'}")
    print(f"Routes Test:            {'✅ PASSOU' if routes_test else '❌ FALHOU'}")
    print("="*60 + "\n")
    
    if bp_test and routes_test:
        print("🎉 TODOS OS TESTES PASSARAM! RF10 ESTÁ FUNCIONANDO CORRETAMENTE!\n")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. VERIFIQUE OS ERROS ACIMA.\n")
