import json
import urllib.parse
import time
from datetime import datetime
from duckduckgo_search import DDGS

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

# Dicionário vazio para guardar as imagens que o robô já encontrou (Cache)
# Isso impede que ele pesquise no buscador a mesma foto repetidas vezes
CACHE_IMAGENS = {}

def buscar_imagem_automatica(nome_produto):
    # Se já pesquisamos esse produto antes, usa a foto salva no cache
    if nome_produto in CACHE_IMAGENS:
        return CACHE_IMAGENS[nome_produto]
    
    print(f"  -> Buscando foto na internet para: {nome_produto}...")
    try:
        # Busca imagens no DuckDuckGo
        resultados = DDGS().images(keywords=nome_produto, max_results=1)
        
        if resultados:
            url_imagem = resultados[0]['image']
            CACHE_IMAGENS[nome_produto] = url_imagem
            time.sleep(1.5)  # Pausa de 1.5s para não sobrecarregar o buscador e evitar bloqueio
            return url_imagem
            
    except Exception as e:
        print(f"  [!] Erro ao buscar foto de {nome_produto}: {e}")
    
    # Se falhar ou não achar, usa um placeholder genérico
    url_fallback = "https://via.placeholder.com/500?text=Imagem+Indisponivel"
    CACHE_IMAGENS[nome_produto] = url_fallback
    return url_fallback

def gerar_vitrine_hibrida():
    produtos = []
    id_atual = 1

    for nicho, itens_base in NICHOS.items():
        print(f"\nGerando produtos para o nicho: {nicho}...")
        
        for i in range(1, 51):
            base_nome = itens_base[(i - 1) % len(itens_base)]
            
            # Aqui chamamos o robô de busca de imagens!
            imagem_produto = buscar_imagem_automatica(base_nome)
            
            sufixos = ["Edição Especial", "Linha Pro", "Alta Performance", "Versão Compacta", "Geração Atual"]
            sufixo_escolhido = sufixos[(i + id_atual) % len(sufixos)]
            
            titulo = f"{base_nome} - {sufixo_escolhido} (Ref. {i})"
            termo_url = urllib.parse.quote(titulo)
            
            if i % 2 != 0:
                origem = "Amazon"
                link_afiliado = f"https://www.amazon.com.br/s?k={termo_url}&tag={TAG_AMAZON}"
            else:
                origem = "Mercado Livre"
                link_afiliado = f"https://lista.mercadolivre.com.br/{termo_url}?matt_tool={TAG_MERCADO_LIVRE}"
            
            preco_fake = round(49.90 + ((i * 17.3) % 350.0), 2)

            produtos.append({
                "id": id_atual,
                "titulo": titulo,
                "preco": preco_fake,
                "imagem": imagem_produto,
                "origem": origem,
                "nicho": nicho,
                "link_vitrine": link_afiliado,
                "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            id_atual += 1

    return produtos

if __name__ == "__main__":
    print("Iniciando o robô gerador de vitrine e buscador de imagens...")
    vitrine_completa = gerar_vitrine_hibrida()
    
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine_completa, f, ensure_ascii=False, indent=2)
        
    print(f"\nSucesso absoluto! Vitrine gerada com {len(vitrine_completa)} produtos. Arquivo salvo!")
