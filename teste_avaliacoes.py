from app import create_app, db
from app.models.models import Produto, Avaliacao

app = create_app()

with app.app_context():
    produto = Produto.query.first()
    
    if produto:
        print(f"Produto: {produto.nome}")
        print(f"Avaliações atuais: {produto.avaliacoes}")
        
        avaliacao = Avaliacao(
            nota=5,
            comentario="Produto excelente! Muito fresco.",
            produto_id=produto.id,
            pedido_item_id=1  
        )
        
        db.session.add(avaliacao)
        db.session.commit()
        
        print("Avaliação adicionada!")
        print(f"Agora o produto tem {len(produto.avaliacoes)} avaliações")
        print(f"Média: {produto.media_avaliacao}")