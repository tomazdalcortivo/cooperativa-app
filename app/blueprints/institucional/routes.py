from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models.models import Produtor, Usuario

institucional_bp = Blueprint('institucional', __name__, url_prefix='/institucional')


@institucional_bp.route('/sobre')
def sobre():
    """RF10.1 - Página Sobre Nós"""
    return render_template('institucional/sobre.html')


@institucional_bp.route('/produtores')
def produtores():
    """RF10.2 - Conheça os Produtores"""
    produtores = Produtor.query.join(Usuario).filter(Usuario.ativo == True).all()
    return render_template('institucional/produtores.html', produtores=produtores)


@institucional_bp.route('/blog')
def blog():
    """RF10.3 - Blog com receitas e dicas"""
    # Simulando posts de blog (em produção, seria um modelo no banco)
    posts = [
        {
            'id': 1,
            'titulo': 'Como escolher frutas e verduras frescas',
            'categoria': 'Dicas',
            'data': '15/01/2025',
            'imagem': 'https://via.placeholder.com/400x250?text=Frutas+Frescas',
            'resumo': 'Aprenda a identificar alimentos frescos e de qualidade no mercado.',
            'conteudo': 'Texto completo do artigo...'
        },
        {
            'id': 2,
            'titulo': 'Receita: Suco natural de abóbora e gengibre',
            'categoria': 'Receita',
            'data': '10/01/2025',
            'imagem': 'https://via.placeholder.com/400x250?text=Suco+Natural',
            'resumo': 'Uma receita deliciosa e saudável para toda a família.',
            'conteudo': 'Texto completo do artigo...'
        },
        {
            'id': 3,
            'titulo': 'Benefícios dos alimentos orgânicos para a saúde',
            'categoria': 'Saúde',
            'data': '05/01/2025',
            'imagem': 'https://via.placeholder.com/400x250?text=Organicos',
            'resumo': 'Descubra os benefícios de consumir alimentos 100% orgânicos.',
            'conteudo': 'Texto completo do artigo...'
        },
        {
            'id': 4,
            'titulo': 'Conservação de alimentos: técnicas ancestrais',
            'categoria': 'Dicas',
            'data': '28/12/2024',
            'imagem': 'https://via.placeholder.com/400x250?text=Conservacao',
            'resumo': 'Técnicas antigas e modernas para conservar seus alimentos.',
            'conteudo': 'Texto completo do artigo...'
        },
        {
            'id': 5,
            'titulo': 'Receita: Pão integral com sementes',
            'categoria': 'Receita',
            'data': '20/12/2024',
            'imagem': 'https://via.placeholder.com/400x250?text=Pao+Integral',
            'resumo': 'Como fazer um delicioso pão integral em casa.',
            'conteudo': 'Texto completo do artigo...'
        },
        {
            'id': 6,
            'titulo': 'Sazonalidade: qual é a melhor época para cada alimento',
            'categoria': 'Educação',
            'data': '15/12/2024',
            'imagem': 'https://via.placeholder.com/400x250?text=Sazonalidade',
            'resumo': 'Entenda quando cada alimento está na sua melhor forma.',
            'conteudo': 'Texto completo do artigo...'
        }
    ]
    return render_template('institucional/blog.html', posts=posts)


@institucional_bp.route('/blog/<int:post_id>')
def blog_detalhes(post_id):
    """Detalhes de um post do blog"""
    # Simulando dados do blog
    post = {
        'id': post_id,
        'titulo': f'Post {post_id}',
        'categoria': 'Educação',
        'data': '15/01/2025',
        'autor': 'Equipe CoopVale',
        'imagem': 'https://via.placeholder.com/800x400',
        'conteudo': 'Conteúdo completo do artigo aqui...'
    }
    return render_template('institucional/blog_detalhes.html', post=post)


@institucional_bp.route('/contato', methods=['GET', 'POST'])
def contato():
    """RF10.4 - Página Contato"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')
        
        # Aqui você pode implementar o envio de email
        # ou salvar em banco de dados
        return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso!'})
    
    return render_template('institucional/contato.html')


@institucional_bp.route('/faq')
def faq():
    """RF10.5 - FAQ"""
    faqs = [
        {
            'id': 1,
            'pergunta': 'Como faço para fazer um pedido?',
            'resposta': 'Acesse nossa seção de produtos, selecione os itens desejados, adicione ao carrinho e finalize a compra no checkout. É fácil e seguro!'
        },
        {
            'id': 2,
            'pergunta': 'Qual é o prazo de entrega?',
            'resposta': 'Os pedidos são entregues de segunda a sexta-feira, em até 3 dias úteis após a confirmação do pagamento. Frete grátis para compras acima de R$ 100.'
        },
        {
            'id': 3,
            'pergunta': 'Como faço para devolver um produto?',
            'resposta': 'Você pode devolver produtos em até 7 dias após o recebimento, desde que estejam íntegros e na embalagem original. Entre em contato conosco para solicitar o retorno.'
        },
        {
            'id': 4,
            'pergunta': 'Os produtos são 100% orgânicos?',
            'resposta': 'Sim! Todos os nossos produtores seguem práticas sustentáveis e produzem alimentos sem agrotóxicos. Cada produto tem a procedência verificada.'
        },
        {
            'id': 5,
            'pergunta': 'Vocês entregam em todo o estado?',
            'resposta': 'Entregamos em toda a região. Consulte a tabela de frete ao finalizar seu pedido para verificar a disponibilidade de entrega em sua região.'
        },
        {
            'id': 6,
            'pergunta': 'Como posso entrar em contato com o suporte?',
            'resposta': 'Utilize nosso formulário de contato, envie um email para suporte@coopvale.com ou ligue para (XX) XXXX-XXXX. Respondemos em até 24 horas.'
        },
        {
            'id': 7,
            'pergunta': 'Posso ser um produtor na CoopVale?',
            'resposta': 'Sim! Estamos sempre buscando novos produtores para nossa rede. Entre em contato conosco e saiba mais sobre nossos requisitos e benefícios.'
        },
        {
            'id': 8,
            'pergunta': 'Os dados do meu cadastro estão seguros?',
            'resposta': 'Sim, utilizamos criptografia SSL para proteger seus dados. Sua privacidade é nossa prioridade. Confira nossa Política de Privacidade para mais detalhes.'
        }
    ]
    return render_template('institucional/faq.html', faqs=faqs)


@institucional_bp.route('/privacidade')
def privacidade():
    """RF10.6 - Política de Privacidade"""
    return render_template('institucional/privacidade.html')


@institucional_bp.route('/termos')
def termos():
    """RF10.6 - Termos de Uso"""
    return render_template('institucional/termos.html')


@institucional_bp.route('/home')
def home():
    """Página inicial principal"""
    # Buscando alguns produtores destaque
    produtores_destaque = Produtor.query.join(Usuario).filter(Usuario.ativo == True).limit(3).all()
    
    return render_template('institucional/home.html', produtores=produtores_destaque)
