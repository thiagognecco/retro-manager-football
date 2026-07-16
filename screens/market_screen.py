import market


def list_offers():
    offers = market.get_offers()
    if not offers:
        print("[MARKET] Nenhuma oferta no momento.")
        return
    print("[MARKET] Ofertas:")
    for o in offers:
        player = o.get("player", {})
        print(f"- {o.get('offer_id')} | {player.get('name')} ({player.get('position')}) - R$ {o.get('price')} (vendedor: {o.get('seller')})")


def list_bids():
    bids = market.get_bids()
    if not bids:
        print("[MARKET] Nenhum bid no momento.")
        return
    print("[MARKET] Bids:")
    for b in bids:
        player = b.get("player", {})
        print(f"- {b.get('bid_id')} | {player.get('name')} ({player.get('position')}) - R$ {b.get('price')} (comprador: {b.get('bidder')})")


def show_history():
    history = market.get_history()
    if not history:
        print("[MARKET] Histórico vazio.")
        return
    print("[MARKET] Histórico de negociações:")
    for h in history:
        player = h.get("player", {})
        print(f"- {h.get('trade_id')}: {player.get('name')} vendido por {h.get('price')} de {h.get('seller')} para {h.get('buyer')} em {h.get('timestamp')}")


def sell_player(team, player, price):
    offer = market.put_on_transfer(team, player, price)
    print(f"[MARKET] Oferta criada: {offer.get('offer_id')}")


def buy_player(buyer_team, seller_team, player, price):
    ok = market.buy_player(buyer_team, seller_team, player, price)
    if ok:
        print(f"[MARKET] Compra realizada: {player.name} por {price} de {seller_team.name} para {buyer_team.name}")
    else:
        print("[MARKET] Compra falhou.")


def place_bid(team, player, price):
    bid = market.place_bid(team, player, price)
    print(f"[MARKET] Bid criado: {bid.get('bid_id')}")


def accept_bid(seller_team, bidder_team, bid_id):
    ok = market.accept_bid(seller_team, bidder_team, bid_id)
    if ok:
        print(f"[MARKET] Bid {bid_id} aceito.")
    else:
        print(f"[MARKET] Falha ao aceitar bid {bid_id}.")
