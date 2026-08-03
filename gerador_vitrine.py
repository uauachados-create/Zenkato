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

# Caches para não sobrecarregar o buscador
CACHE_IMAGENS = {}
CACHE_LINKS = {}

def buscar_imagem_automatica(nome_produto):
    if nome_produto in CACHE_IMAGENS:
        return CACHE_IMAGENS[nome_produto]
    
    print(f"  -> Buscando foto na internet para: {nome_produto}...")
    try:
        resultados = DDGS().images(keywords=nome_produto, max_results=1)
        if resultados:
            url_imagem = resultados[0]['image']
            CACHE_IMAGENS[nome_produto] = url_imagem
            time.sleep(1.5)
            return url_imagem
    except Exception as e:
        print(f"  [!] Erro ao buscar foto de {nome_produto}: {e}")
    
    url_fallback = "https://via.placeholder.com/500?text=Imagem+Indisponivel"
    CACHE_IMAGENS[nome_produto] = url_fallback
    return url_fallback

def buscar_link_direto(nome_produto, origem):
    chave_cache = f"{origem}_{nome_produto}"
    if chave_cache in CACHE_LINKS:
        return CACHE_LINKS[chave_cache]
    
    print(f"  -> Buscando link de compra direta ({origem}) para: {nome_produto}...")
    try:
        # Força o buscador a procurar páginas de produtos específicos dentro dos sites
        if origem == "Amazon":
            query = f"site:amazon.com.br/dp/ {nome_produto}"
        else:
            query = f"site:produto.mercadolivre.com.br {nome_produto}"
            
        resultados = DDGS().text(keywords=query, max_results=1)
        
        if resultados:
            url_real = resultados[0]['href']
            
            # Injeta a sua tag de afiliado de forma inteligente na URL encontrada
            separador = "&" if "?" in url_real else "?"
            
            if origem == "Amazon":
                link_final = f"{url_real}{separador}tag={TAG_AMAZON}"
            else:
                link_final = f"{url_real}{separador}matt_tool={TAG_MERCADO_LIVRE}"
                
            CACHE_LINKS[chave_cache] = link_final
            time.sleep(1.5) # Pausa de segurança
            return link_final
            
    except Exception as e:
        print(f"  [!] Erro ao buscar link de {nome_produto}: {e}")
    
    # Se der erro na busca, faz o fallback para o link de vitrine/pesquisa
    termo_url = urllib.parse.quote(nome_produto)
    if origem == "Amazon":
        link_fallback = f"https://www.amazon.com.br/s?k={termo_url}&tag={TAG_AMAZON}"
    else:
        link_fallback = f"https://lista.mercadolivre.com.br/{termo_url}?matt_tool={TAG_MERCADO_LIVRE}"
        
    CACHE_LINKS[chave_cache] = link_fallback
    return link_fallback

def gerar_vitrine_hibrida():
    produtos = []
    id_atual = 1

    for nicho, itens_base in NICHOS.items():
        print(f"\nGerando produtos para o nicho: {nicho}...")
        
        for i in range(1, 51):
            base_nome = itens_base[(i - 1) % len(itens_base)]
            
            # Define a origem baseada no loop (Ímpar = Amazon, Par = Mercado Livre)
            origem = "Amazon" if i % 2 != 0 else "Mercado Livre"
            
            # Busca automatizada de imagem e link de compra
            imagem_produto = buscar_imagem_automatica(base_nome)
            link_afiliado = buscar_link_direto(base_nome, origem)
            
            sufixos = ["Edição Especial", "Linha Pro", "Alta Performance", "Versão Compacta", "Geração Atual"]
            sufixo_escolhido = sufixos[(i + id_atual) % len(sufixos)]
            
            # Gera o título fictício (Atenção: o link redirecionará para o produto real)
            titulo = f"{base_nome} - {sufixo_escolhido} (Ref. {i})"
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
    print("Iniciando o robô gerador de vitrine e buscador de links...")
    vitrine_completa = gerar_vitrine_hibrida()
    
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine_completa, f, ensure_ascii=False, indent=2)
        
    print(f"\nSucesso absoluto! Vitrine gerada com {len(vitrine_completa)} produtos. Arquivo salvo!")
