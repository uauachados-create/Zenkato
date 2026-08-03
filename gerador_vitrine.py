import json
import urllib.parse
from datetime import datetime

# Suas Tags de Afiliado oficiais
TAG_AMAZON = "032018011983-20"
TAG_MERCADO_LIVRE = "18735177"

# Os 5 nichos exatos do seu site e suas listas base
NICHOS = {
    "Casa Inteligente": [
        "Echo Dot Alexa", "Lampada Smart Wi-Fi", "Tomada Inteligente", "Interruptor Touch", 
        "Camera de Seguranca 360", "Robo Aspirador", "Fechadura Digital", "Fita LED Smart", 
        "Hub de Automacao", "Sensor de Presenca Inteligente"
    ],
    "Beleza & Skincare": [
        "Kit Skincare Completo", "Serum Vitamina C", "Massageador Facial Jade", "Mascara de Argila", 
        "Esponja Eletrica Facial", "Acido Hialuronico", "Protetor Solar Facial", "Creme Anti-Idade", 
        "Oleo Hidratante Corporal", "Kit Pinceis de Maquiagem Profissional"
    ],
    "Fitness & Office": [
        "Halteres Emborrachados", "Whey Protein Concentrado", "Creatina Pura Monohidratada", 
        "Faixas Elasticas Extensoras", "Tapete Yoga Mat", "Cadeira de Escritorio Ergonomica", 
        "Suporte para Notebook", "Garrafa Termica Inox", "Mochila Executiva", "Banda de Resistencia"
    ],
    "Pets": [
        "Fonte Bebedouro Automatica", "Tapete Higienico Caes", "Cama Nuvem Pet", "Arranhador para Gatos", 
        "Escova Tira Pelos", "Caixa de Transporte", "Brinquedo Mordedor Interativo", "Racao Premium", 
        "Coleira Peitoral Antipuxao", "Comedouros Elevados"
    ],
    "Ferramentas": [
        "Maleta de Ferramentas Completa", "Parafusadeira Furadeira 12V", "Jogo de Chaves de Fenda", 
        "Trena a Laser Digital", "Kit Chaves de Precisao", "Jogo de Soquetes e Catraca", 
        "Lanterna Tatica LED Recarregavel", "Alicate Universal Profissional", "Martelo Unha", "Sargentos para Marceneiro"
    ]
}

def gerar_vitrine_hibrida():
    produtos = []
    id_atual = 1

    for nicho, itens_base in NICHOS.items():
        print(f"Gerando 50 produtos mistos para o nicho: {nicho}...")
        
        # Gera exatamente 50 produtos por categoria (totalizando 250)
        for i in range(1, 51):
            base_nome = itens_base[(i - 1) % len(itens_base)]
            
            sufixos = ["Edição Especial", "Linha Pro", "Alta Performance", "Versão Compacta", "Geração Atual"]
            sufixo_escolhido = sufixos[(i + id_atual) % len(sufixos)]
            
            titulo = f"{base_nome} - {sufixo_escolhido} (Ref. {i})"
            termo_url = urllib.parse.quote(titulo)
            
            # Alterna a origem: Ímpares vão para a Amazon, Pares vão para o Mercado Livre
            if i % 2 != 0:
                origem = "Amazon"
                link_afiliado = f"https://www.amazon.com.br/s?k={termo_url}&tag={TAG_AMAZON}"
            else:
                origem = "Mercado Livre"
                link_afiliado = f"https://lista.mercadolivre.com.br/{termo_url}?matt_tool={TAG_MERCADO_LIVRE}"
            
            # Imagem ilustrativa de alta qualidade
            imagem_placeholder = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"
            
            # Preço simulado realista
            preco_fake = round(49.90 + ((i * 17.3) % 350.0), 2)

            produtos.append({
                "id": id_atual,
                "titulo": titulo,
                "preco": preco_fake,
                "imagem": imagem_placeholder,
                "origem": origem,
                "nicho": nicho,
                "link_vitrine": link_afiliado,
                "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            id_atual += 1

    return produtos

if __name__ == "__main__":
    vitrine_completa = gerar_vitrine_hibrida()
    
    # Salva o arquivo JSON final contendo os 250 produtos mistos
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine_completa, f, ensure_ascii=False, indent=2)
        
    print(f"Sucesso absoluto! Vitrine gerada com {len(vitrine_completa)} produtos (Amazon + Mercado Livre).")
