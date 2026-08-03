import json
import urllib.parse
import time
from datetime import datetime
import requests
from duckduckgo_search import DDGS

# Suas Tags de Afiliado oficiais
TAG_AMAZON = "032018011983-20"
TAG_MERCADO_LIVRE = "18735177"

# Os 5 nichos exatos do seu site e suas listas base (10 produtos)
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

# Caches para deixar o robô rápido e evitar bloqueios na internet
CACHE_ML = {}
CACHE_DDG = {}

def buscar_dados_mercadolivre(nome_produto):
    if nome_produto in CACHE_ML:
        return CACHE_ML[nome_produto]
        
    print(f"  -> Consultando ML para: {nome_produto}...")
    termo_busca = urllib.parse.quote(nome_produto)
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}&limit=1"
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        
        if dados.get("results") and len(dados["results"]) > 0:
            produto = dados["results"][0]
            link_real = produto["permalink"]
            separador = "&" if "?" in link_real else "?"
            
            resultado = {
                "titulo": produto["title"],
                "preco": float(produto["price"]),
                "imagem": produto["thumbnail"].replace("-I.jpg", "-O.jpg"),
                "link": f"{link_real}{separador}matt_tool={TAG_MERCADO_LIVRE}"
            }
            CACHE_ML[nome_produto] = resultado
            return resultado
    except Exception as e:
        print(f"  [!] Erro ML para {nome_produto}: {e}")
        
    return None

def buscar_link_amazon_duckduckgo(nome_produto):
    if nome_produto in CACHE_DDG:
        return CACHE_DDG[nome_produto]
        
    print(f"  -> Buscando Amazon para: {nome_produto}...")
    try:
        query = f"site:amazon.com.br/dp/ {nome_produto}"
        resultados_txt = DDGS().text(keywords=query, max_results=1)
        link_afiliado = f"https://www.amazon.com.br/s?k={urllib.parse.quote(nome_produto)}&tag={TAG_AMAZON}" 
        
        if resultados_txt:
            url_real = resultados_txt[0]['href']
            separador = "&" if "?" in url_real else "?"
            link_afiliado = f"{url_real}{separador}tag={TAG_AMAZON}"
            
        resultados_img = DDGS().images(keywords=nome_produto, max_results=1)
        imagem_produto = "https://via.placeholder.com/500?text=Imagem+Indisponivel"
        if resultados_img:
            imagem_produto = resultados_img[0]['image']
            
        resultado_final = {
            "titulo": f"{nome_produto} (Verificar Modelo)",
            "preco": 0.0, # MANTIDO COMO NÚMERO PARA NÃO QUEBRAR SEU SITE
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
        print(f"\nGerando 50 produtos para o nicho: {nicho}...")
        
        # Gera exatamente 50 produtos por categoria (totalizando 250)
        for i in range(1, 51):
            # Cicla entre os 10 itens base para chegar a 50
            base_nome = itens_base[(i - 1) % len(itens_base)]
            
            # Alterna a plataforma (Ímpar = Amazon, Par = Mercado Livre)
            if id_atual % 2 != 0:
                origem = "Amazon"
                dados = buscar_link_amazon_duckduckgo(base_nome)
            else:
                origem = "Mercado Livre"
                dados = buscar_dados_mercadolivre(base_nome)
            
            if not dados:
                # Fallback de segurança se der erro de conexão
                dados = {
                    "titulo": f"{base_nome} - Oferta",
                    "preco": 0.0,
                    "imagem": "https://via.placeholder.com/500?text=Imagem+Indisponivel",
                    "link": f"https://lista.mercadolivre.com.br/{urllib.parse.quote(base_nome)}?matt_tool={TAG_MERCADO_LIVRE}"
                }

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
    print("Iniciando robô (250 produtos)...")
    vitrine_completa = gerar_vitrine_hibrida()
    
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine_completa, f, ensure_ascii=False, indent=2)
        
    print(f"\nSucesso absoluto! Vitrine gerada com {len(vitrine_completa)} produtos. Arquivo salvo!")
