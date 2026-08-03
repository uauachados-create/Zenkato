import json
import urllib.parse
from datetime import datetime
import requests
import time
import schedule  # <-- Nova biblioteca importada aqui

# Suas Tags de Afiliado
TAG_AMAZON = "032018011983-20"
TAG_MERCADO_LIVRE = "18735177"

# Suas listas base (10 produtos por nicho)
NICHOS = {
    "Casa Inteligente": [
        "Echo Dot", "Lampada Smart Wi-Fi", "Tomada Inteligente", "Interruptor Touch", 
        "Camera de Seguranca 360", "Robo Aspirador", "Fechadura Digital", "Fita LED Smart", 
        "Hub de Automacao", "Sensor de Presenca Inteligente"
    ],
    "Beleza & Skincare": [
        "Kit Skincare", "Serum Vitamina C", "Massageador Facial Jade", "Mascara de Argila", 
        "Esponja Eletrica Facial", "Acido Hialuronico", "Protetor Solar Facial", "Creme Anti-Idade", 
        "Oleo Hidratante Corporal", "Kit Pinceis Maquiagem"
    ],
    "Fitness & Office": [
        "Halteres Emborrachados", "Whey Protein", "Creatina Pura", 
        "Faixas Elasticas", "Tapete Yoga Mat", "Cadeira Ergonomica", 
        "Suporte para Notebook", "Garrafa Termica Inox", "Mochila Executiva", "Banda de Resistencia"
    ],
    "Pets": [
        "Fonte Bebedouro Pet", "Tapete Higienico Caes", "Cama Nuvem Pet", "Arranhador para Gatos", 
        "Escova Tira Pelos", "Caixa de Transporte Pet", "Brinquedo Mordedor", "Racao Premium", 
        "Coleira Peitoral", "Comedouro Elevado"
    ],
    "Ferramentas": [
        "Maleta de Ferramentas", "Parafusadeira 12V", "Jogo de Chaves de Fenda", 
        "Trena a Laser Digital", "Kit Chaves de Precisao", "Jogo de Soquetes", 
        "Lanterna Tatica LED", "Alicate Universal", "Martelo Unha", "Sargentos Marceneiro"
    ]
}

def gerar_vitrine_diaria():
    produtos = []
    id_atual = 1

    for nicho, palavras_chave in NICHOS.items():
        print(f"\nBuscando ofertas do dia para: {nicho}...")
        
        for termo in palavras_chave:
            # 1. Puxa os 4 melhores/mais baratos anúncios do Mercado Livre para este termo
            termo_url = urllib.parse.quote(termo)
            url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={termo_url}&limit=4"
            
            try:
                resposta = requests.get(url_ml)
                dados_ml = resposta.json()
                
                if dados_ml.get("results"):
                    for item in dados_ml["results"]:
                        link_real = item["permalink"]
                        separador = "&" if "?" in link_real else "?"
                        
                        produtos.append({
                            "id": id_atual,
                            "titulo": item["title"],
                            "preco": float(item["price"]), 
                            "imagem": item["thumbnail"].replace("-I.jpg", "-O.jpg"), 
                            "origem": "Mercado Livre",
                            "nicho": nicho,
                            "link_vitrine": f"{link_real}{separador}matt_tool={TAG_MERCADO_LIVRE}",
                            "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        id_atual += 1
            except Exception as e:
                print(f"Erro ao buscar {termo} no ML: {e}")
            
            # 2. Adiciona 1 opção da Amazon para cada termo
            produtos.append({
                "id": id_atual,
                "titulo": f"{termo} (Verificar Oferta na Amazon)",
                "preco": 0.0,
                "imagem": f"https://via.placeholder.com/500?text={termo_url}+Amazon",
                "origem": "Amazon",
                "nicho": nicho,
                "link_vitrine": f"https://www.amazon.com.br/s?k={termo_url}&tag={TAG_AMAZON}",
                "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            id_atual += 1
            
            time.sleep(0.5)

    return produtos

# Nova função que executa a rotina inteira
def tarefa_agendada():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando garimpo automático de produtos...")
    vitrine = gerar_vitrine_diaria()
    
    with open("vitrine_produtos.json", "w", encoding="utf-8") as f:
        json.dump(vitrine, f, ensure_ascii=False, indent=2)
        
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Arquivo gerado com sucesso! Total: {len(vitrine)} itens.")
    print("Aguardando até amanhã às 09:00...")

if __name__ == "__main__":
    print("Robô Zenkato Iniciado!")
    print("Ele ficará em modo de espera e atualizará sua vitrine todos os dias às 09:00 da manhã.")
    print("AVISO: Mantenha esta janela aberta para que o relógio interno funcione.\n")
    
    # ---------------------------------------------------------
    # CONFIGURAÇÃO DO RELÓGIO: Define o horário para as 09:00
    # ---------------------------------------------------------
    schedule.every().day.at("09:00").do(tarefa_agendada)
    
    # Se você quiser testar se está funcionando agora mesmo, 
    # tire o "#" da linha abaixo para ele rodar a primeira vez na hora que você abrir:
    # tarefa_agendada()

    # Loop infinito que verifica o relógio a cada 1 minuto (60 segundos)
    while True:
        schedule.run_pending()
        time.sleep(60)
