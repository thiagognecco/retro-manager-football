import json
import os
from typing import List, Dict

import database

MARKET_FILE = "market.json"


def load_market() -> List[Dict]:
    if not os.path.exists(MARKET_FILE):
        return []
    try:
        with open(MARKET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_market(offers: List[Dict]):
    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump(offers, f, indent=4, ensure_ascii=False)


def evaluate_player_value(player: database.Player) -> int:
    """
    Avalia o valor de mercado do jogador.
    Fórmula: (média_de_força)^2 * 10000
    """
    avg = player.get_average_force()
    value = int(round((avg ** 2) * 10000))
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
    return load_market()


def put_on_transfer(team: database.Team, player: database.Player, price: int) -> Dict:
    """Coloca um jogador à venda no mercado. Não remove o jogador do elenco do vendedor.
    Retorna a oferta criada.
    """
    offers = load_market()
    offer = {
        "seller": team.name,
        "player": player.to_dict(),
        "price": int(price)
    }
    offers.append(offer)
    save_market(offers)
    return offer


def buy_player(buyer_team: database.Team, seller_team: database.Team, player: database.Player, price: int) -> bool:
    """Executa a compra do jogador entre times objetivos:
    - Verifica fundos do comprador
    - Remove o jogador do time vendedor (por nome)
    - Adiciona ao time comprador
    - Ajusta fundos
    - Remove a oferta do mercado
    Retorna True em sucesso, False caso contrário.
    """
    offers = load_market()
    # procura oferta que bate com seller, nome do jogador e preço
    matching = None
    for o in offers:
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
    offers.remove(matching)
    save_market(offers)

    return True


if __name__ == "__main__":
    # Pequeno demo quando executado diretamente
    print("Market demo")
    teams = database.create_initial_database()
    market_offers = get_offers()
    print("Ofertas atuais:", market_offers)
