import json
import os
from typing import List, Dict
import uuid
from datetime import datetime

import database

MARKET_FILE = "market.json"


def load_market() -> Dict:
    if not os.path.exists(MARKET_FILE):
        return {"offers": [], "bids": [], "history": []}
    try:
        with open(MARKET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # legacy format: list of offers
                return {"offers": data, "bids": [], "history": []}
            if isinstance(data, dict):
                return {
                    "offers": data.get("offers", []),
                    "bids": data.get("bids", []),
                    "history": data.get("history", [])
                }
            return {"offers": [], "bids": [], "history": []}
    except Exception:
        return {"offers": [], "bids": [], "history": []}


def save_market(market_data: Dict):
    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump(market_data, f, indent=4, ensure_ascii=False)


def evaluate_player_value(player: database.Player) -> int:
    """
    Avalia o valor de mercado do jogador.
    Fórmula base: (média_de_força)^2 * 10000
    Ajustes: posição e idade (idade é placeholder se não existir).
    """
    avg = player.get_average_force()
    base = (avg ** 2) * 10000
    pos = getattr(player, "position", "MC")
    pos_map = {"GL": 0.9, "DF": 1.0, "MC": 1.1, "AT": 1.3}
    pos_mul = pos_map.get(pos, 1.0)
    age = getattr(player, "age", 25)
    age_adj = 1.0 + ((25 - age) * 0.02)
    age_adj = max(0.6, min(1.4, age_adj))
    value = int(round(base * pos_mul * age_adj))
    return value


def list_free_agents(count: int = 5) -> List[database.Player]:
    """Gera uma lista curta de jogadores livres usando o gerador do database."""
    agents: List[database.Player] = []
    positions = ['GL', 'DF', 'MC', 'AT']
    for i in range(count):
        pos = positions[i % len(positions)]
        # alterna estrelas ocasionalmente
        is_star = (i % 4 == 0)
        agents.append(database.generate_random_player(pos, is_star=is_star))
    return agents


def get_offers() -> List[Dict]:
    data = load_market()
    return data.get("offers", [])


def get_bids() -> List[Dict]:
    data = load_market()
    return data.get("bids", [])


def get_history() -> List[Dict]:
    data = load_market()
    return data.get("history", [])


def put_on_transfer(team: database.Team, player: database.Player, price: int) -> Dict:
    """Coloca um jogador à venda no mercado. Não remove o jogador do elenco do vendedor.
    Retorna a oferta criada.
    """
    market_data = load_market()
    offer = {
        "offer_id": str(uuid.uuid4()),
        "seller": team.name,
        "player": player.to_dict(),
        "price": int(price),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    market_data["offers"].append(offer)
    save_market(market_data)
    return offer


def place_bid(team: database.Team, player: database.Player, price: int) -> Dict:
    """Coloca uma oferta de compra (bid) no mercado."""
    market_data = load_market()
    bid = {
        "bid_id": str(uuid.uuid4()),
        "bidder": team.name,
        "player": player.to_dict(),
        "price": int(price),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    market_data["bids"].append(bid)
    save_market(market_data)
    return bid


def accept_bid(seller_team: database.Team, bidder_team: database.Team, bid_id: str) -> bool:
    """Vendedor aceita um bid de um comprador. Transfere jogador e registra histórico."""
    market_data = load_market()
    bid = next((b for b in market_data.get("bids", []) if b.get("bid_id") == bid_id), None)
    if not bid:
        return False
    price = int(bid.get("price", 0))
    if bidder_team.funds < price:
        return False
    player_name = bid.get("player", {}).get("name")
    # verificar posse do jogador pelo vendedor
    player_obj = None
    for idx, p in enumerate(seller_team.players):
        if p.name == player_name:
            player_obj = seller_team.players.pop(idx)
            break
    if player_obj is None:
        return False
    # executar transferência
    bidder_team.add_player(player_obj)
    bidder_team.funds -= price
    seller_team.funds += price
    # remover ofertas de venda e o bid correspondente
    market_data["offers"] = [o for o in market_data.get("offers", []) if o.get("player", {}).get("name") != player_name]
    market_data["bids"] = [b for b in market_data.get("bids", []) if b.get("bid_id") != bid_id]
    # registrar histórico
    trade = {
        "trade_id": str(uuid.uuid4()),
        "seller": seller_team.name,
        "buyer": bidder_team.name,
        "player": {"name": player_obj.name, "position": player_obj.position},
        "price": price,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    market_data["history"].append(trade)
    save_market(market_data)
    return True


def buy_player(buyer_team: database.Team, seller_team: database.Team, player: database.Player, price: int) -> bool:
    """Executa a compra do jogador entre times objetivos:
    - Verifica fundos do comprador
    - Remove o jogador do time vendedor (por nome)
    - Adiciona ao time comprador
    - Ajusta fundos
    - Remove a oferta do mercado
    - Registra no histórico
    Retorna True em sucesso, False caso contrário.
    """
    market_data = load_market()
    # procura oferta que bate com seller, nome do jogador e preço
    matching = None
    for o in market_data.get("offers", []):
        if o.get("seller") == seller_team.name and o.get("player", {}).get("name") == player.name and int(o.get("price", 0)) == int(price):
            matching = o
            break

    if matching is None:
        return False

    if buyer_team.funds < price:
        return False

    # remove jogador do vendedor (por nome)
    removed = False
    for idx, p in enumerate(seller_team.players):
        if p.name == player.name:
            seller_team.players.pop(idx)
            removed = True
            break

    if not removed:
        # jogador não encontrado no elenco do vendedor
        return False

    # realizar transferência
    buyer_team.add_player(player)
    buyer_team.funds -= price
    seller_team.funds += price

    # remover oferta e salvar
    market_data["offers"] = [o for o in market_data.get("offers", []) if o.get("offer_id") != matching.get("offer_id")]
    # registrar histórico
    trade = {
        "trade_id": str(uuid.uuid4()),
        "seller": seller_team.name,
        "buyer": buyer_team.name,
        "player": {"name": player.name, "position": player.position},
        "price": int(price),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    market_data["history"].append(trade)
    save_market(market_data)

    return True


if __name__ == "__main__":
    # Pequeno demo quando executado diretamente
    print("Market demo")
    teams = database.create_initial_database()
    market_data = load_market()
    print("Ofertas atuais:", market_data.get("offers"))
    print("Histórico:", market_data.get("history"))
