import json
import urllib.parse
import time
from datetime import datetime
import requests
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

CACHE_DDG = {}

def buscar_dados_mercadolivre(nome_produto):
    """Usa a API oficial do Mercado Livre para pegar o produto real mais relevante"""
    print(f"  -> Consultando API Mercado Livre para: {nome_produto}...")
    termo_busca = urllib.parse.quote(nome_produto)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}&limit=1"
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        
        if dados.get("results") and len(dados["results"]) > 0:
            produto = dados["results"][0]
            
            # Pega a URL real e injeta sua tag
            link_real = produto["permalink"]
            separador = "&" if "?" in link_real else "?"
            link_afiliado = f"{link_real}{separador}matt_tool={TAG_MERCADO_LIVRE}"
            
            # Troca o "I.jpg" por "O.jpg" para pegar a imagem em alta resolução do ML
            imagem_alta_qualidade = produto["thumbnail"].replace("-I.jpg", "-O.jpg")
            
            return {
                "titulo": produto["title"], # Título real do anúncio
                "preco": float(produto["price"]), # Preço real
                "imagem": imagem_alta_qualidade,
                "link": link_afiliado
            }
    except Exception as e:
        print(f"  [!] Erro na API do ML para {nome_produto}: {e}")
        
    return None

def buscar_link_amazon_duckduckgo(nome_produto):
    """Busca link e imagem via DuckDuckGo para Amazon (já que Amazon bloqueia preços)"""
    if nome_produto in CACHE_DDG:
        return CACHE_DDG[nome_produto]
        
    print(f"  -> Buscando link Amazon para: {nome_produto}...")
    try:
        # Busca Link
        query = f"site:amazon.com.br/dp/ {nome_produto}"
        resultados_txt = DDGS().text(keywords=query, max_results=1)
        link_afiliado = f"https://www.amazon.com.br/s?k={urllib.parse.quote(nome_produto)}&tag={TAG_AMAZON}" # Fallback
        
        if resultados_txt:
            url_real = resultados_txt[0]['href']
            separador = "&" if "?" in url_real else "?"
            link_afiliado = f"{url_real}{separador}tag={TAG_AMAZON}"
            
        # Busca Imagem
        resultados_img = DDGS().images(keywords=nome_produto, max_results=1)
        imagem_produto = "https://via.placeholder.com/500?text=Imagem+Indisponivel"
        if resultados_img:
            imagem_produto = resultados_img[0]['image']
            
        resultado_final = {
            "titulo": f"{nome_produto} (Verificar Modelo)",
            "preco": "Ver no site", # IMPOSSÍVEL PEGAR PREÇO DA AMAZON SEM API OFICIAL
            "imagem": imagem_produto,
            "link": link_afiliado
        }
        
        CACHE_DDG[nome_produto] = resultado_final
        time.sleep(1.5)
        return resultado_final
        
    except Exception as e:
        print(f"  [!] Erro DuckDuckGo para {nome_produto}: {e}")
        return None

def gerar_vitrine_hibrida():
    produtos = []
    id_atual = 1

    for nicho, itens_base in NICHOS.items():
        print(f"\nGerando produtos para o nicho: {nicho}...")
        
        # Como agora buscamos dados REAIS, vamos gerar 1 produto real para cada item da lista (10 por nicho = 50 no total)
        # Se você quiser repetir os itens, o ML vai sempre retornar o mesmo anúncio líder.
        for base_nome in itens_base:
            
            # Alterna a plataforma (Você pode mudar essa lógica se quiser tudo no ML)
            if id_atual % 2 != 0:
                origem = "Mercado Livre"
                dados = buscar_dados_mercadolivre(base_nome)
            else:
                origem = "Amazon"
                dados = buscar_link_amazon_duckduckgo(base_nome)
            
            # Se não encontrar dados (ex: site fora do ar), pula o produto
            if not dados:
                continue

            produtos.append({
                "id": id_atual,
                "titulo": dados["titulo"],
                "preco": dados["preco"],
                "imagem": dados["imagem"],
                "origem": origem,
                "nicho": nicho,
                "link_vitrine": dados["link"],
                "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            id_atual += 1

    return produtos

if __name__ == "__main__":
    print("Iniciando varredura de preços e links reais...")
    vitrine_completa = gerar_vitrine_hibrida()
    
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine_completa, f, ensure_ascii=False, indent=2)
        
    print(f"\nSucesso absoluto! Vitrine gerada com {len(vitrine_completa)} produtos. Arquivo salvo!")
