import os
import market
import database


def run_test():
    # Preparar ambientes
    seller = database.Team("Seller FC", funds=50000)
    buyer = database.Team("Buyer United", funds=200000)

    # Criar jogador e adicionar ao vendedor
    player = database.Player("João Silva", "MC", fis=3, tec=3, dec=3)
    seller.add_player(player)

    # Avaliar valor sugerido
    suggested_price = market.evaluate_player_value(player)

    # Colocar no mercado
    offer = market.put_on_transfer(seller, player, suggested_price)

    # Verificações iniciais
    assert offer in market.get_offers(), "Oferta não encontrada no mercado após put_on_transfer"

    buyer_before = len(buyer.players)
    seller_before = len(seller.players)
    buyer_funds_before = buyer.funds
    seller_funds_before = seller.funds

    # Realizar compra
    ok = market.buy_player(buyer, seller, player, suggested_price)
    assert ok, "buy_player retornou False"

    # Verificações pós-compra
    assert len(buyer.players) == buyer_before + 1, "Jogador não adicionado ao time comprador"
    assert len(seller.players) == seller_before - 1, "Jogador não removido do time vendedor"
    assert buyer.funds == buyer_funds_before - suggested_price, "Fundos do comprador não foram ajustados corretamente"
    assert seller.funds == seller_funds_before + suggested_price, "Fundos do vendedor não foram ajustados corretamente"

    # Oferta foi removida do mercado
    offers = market.get_offers()
    assert all(o.get('player', {}).get('name') != player.name for o in offers), "Oferta não removida do mercado"

    # Histórico deve registrar a negociação
    history = market.get_history()
    assert any(h.get('player', {}).get('name') == player.name and h.get('price') == suggested_price for h in history), "Negociação não registrada no histórico"

    print("[TEST PASSED] test_market: negociação bem sucedida e consistência verificada.")


if __name__ == "__main__":
    # garantir arquivo market.json existe e está limpo antes do teste
    if os.path.exists(market.MARKET_FILE):
        try:
            os.remove(market.MARKET_FILE)
        except Exception:
            pass

    run_test()
