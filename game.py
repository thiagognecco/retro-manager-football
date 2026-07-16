import database
import stats
import eventsimport training

class GameEngine:
    def __init__(self):
        self.teams = []
        self.player_team = None
        self.current_screen = "MENU"
        self.running = True
        self.funds = 0
        self.match_history = []  # guarda histórico de partidas
        
    def new_game(self):
        self.teams = database.create_initial_database()
        # For simplicity, let's pick the first team for the player
        self.player_team = self.teams[0]
        self.funds = self.player_team.funds
        self.current_screen = "HUB"
        print(f"Novo jogo iniciado com o time: {self.player_team.name}")

    def load_game(self):
        loaded_teams = database.carregar_jogo()
        if loaded_teams:
            self.teams = loaded_teams
            self.player_team = self.teams[0] # Assuming first team is player's
            self.funds = self.player_team.funds
            self.current_screen = "HUB"
            return True
        return False

    def save_game(self):
        database.salvar_jogo(self.teams)
        # também salva histórico de partidas se houver
        try:
            stats.salvar_carregar_historico(self.match_history)
        except Exception as e:
            # não quebra o fluxo de salvamento de jogo principal
            print(f"[WARN] falha ao salvar histórico: {e}")

    def run_training_session(self, player, training_type: str = 'fis', intensity: int = 1, cost: int = 1000):
        """Executa uma sessão de treino para um jogador específico.
        - player: database.Player (instância)
        - training_type: 'fis' | 'tec' | 'dec' (atributo a treinar)
        - intensity: número inteiro indicando intensidade (máx. alteração possível)
        - cost: custo em fundos do time

        Retorna um dicionário com detalhes do treino realizado.
        """
        # verifica fundos
        team = self.player_team
        if team is None:
            raise ValueError("Nenhum time do jogador carregado para cobrar o custo do treino.")

        if team.funds < cost:
            return {
                'ok': False,
                'reason': 'funds',
                'message': 'Fundos insuficientes para realizar o treino.'
            }

        # cobra custo
        team.funds -= cost
        self.funds = team.funds

        # aplica treino: incremento aleatório entre 0 e intensity (inteiro), máximo 5
        before = getattr(player, training_type, None)
        if before is None:
            # atributo inválido
            return {'ok': False, 'reason': 'attr', 'message': 'Atributo de treino inválido.'}

        # usa mesmo gerador de database para consistência
        incr = database.random.randint(0, max(0, int(intensity)))
        # estrelas têm pequeno bônus
        if getattr(player, 'star', False):
            if database.random.random() < 0.5:
                incr += 1

        after = min(5, before + incr)
        setattr(player, training_type, after)

        # registra no arquivo training.json
        record = {
            'player': player.name,
            'team': team.name,
            'type': training_type,
            'before': before,
            'after': after,
            'delta': after - before,
            'cost': cost
        }
        try:
            training.salvar_carregar_treinos(record)
        except Exception:
            pass

        return {'ok': True, 'record': record}

    def simulate_match(self, team1, team2):
        """Modo rápido (texto) de simulação baseado nas regras em GAME_MECHANICS.md.
        - Ataque = soma de MC + AT
        - Defesa = soma de DF + GL
        - Geramos um número fixo de "chances" e testamos cada uma ponderando pela diferença de ataque/defesa
        - Cada chance é resolvida por uma comparação entre habilidade do atacante (TEC/DEC) e capacidade do goleiro (DEC/FIS)
        O resultado é registrado em self.match_history e retornado como string.
        Também registra eventos detalhados (gols, autor, minuto) em cada partida.
        """
        # coleta por posição
        def players_by_pos(team, pos_list):
            return [p for p in team.players if p.position in pos_list]

        atk1_players = players_by_pos(team1, ['MC', 'AT'])
        def2_players = players_by_pos(team2, ['DF', 'GL'])
        atk2_players = players_by_pos(team2, ['MC', 'AT'])
        def1_players = players_by_pos(team1, ['DF', 'GL'])

        attack_power_1 = sum(p.get_average_force() for p in atk1_players) or 0.1
        defense_power_2 = sum(p.get_average_force() for p in def2_players) or 0.1
        attack_power_2 = sum(p.get_average_force() for p in atk2_players) or 0.1
        defense_power_1 = sum(p.get_average_force() for p in def1_players) or 0.1

        # Probabilidade base de criar chances
        chance_prob_1 = attack_power_1 / (attack_power_1 + defense_power_2)
        chance_prob_2 = attack_power_2 / (attack_power_2 + defense_power_1)

        # Número de oportunidades combinadas (ajustável)
        total_chances = 10

        score1 = 0
        score2 = 0
        events = []  # eventos detalhados da partida

        for _ in range(total_chances):
            # Chance para time1 tentar
            if database.random.random() < chance_prob_1:
                attacker = database.random.choice(atk1_players) if atk1_players else None
                goalkeeper = next((p for p in team2.players if p.position == 'GL'), None)
                if attacker:
                    # Probabilidade de converter o chute
                    attacker_skill = (attacker.dec + attacker.tec) / 10.0
                    if attacker.star:
                        attacker_skill += 0.1
                    base_shot = attacker.get_average_force() / 5.0
                    keeper_skill = 0.5
                    if goalkeeper:
                        keeper_skill = (goalkeeper.dec + goalkeeper.fis) / 10.0
                    # formula simples que combina fatores
                    goal_chance = max(0.02, min(0.95, attacker_skill * base_shot * (1.0 - keeper_skill * 0.7)))
                    if database.random.random() < goal_chance:
                        score1 += 1
                        minute = database.random.randint(1, 90)
                        events.append({"team": team1.name, "scorer": attacker.name, "minute": minute})

            # Chance para time2 tentar
            if database.random.random() < chance_prob_2:
                attacker = database.random.choice(atk2_players) if atk2_players else None
                goalkeeper = next((p for p in team1.players if p.position == 'GL'), None)
                if attacker:
                    attacker_skill = (attacker.dec + attacker.tec) / 10.0
                    if attacker.star:
                        attacker_skill += 0.1
                    base_shot = attacker.get_average_force() / 5.0
                    keeper_skill = 0.5
                    if goalkeeper:
                        keeper_skill = (goalkeeper.dec + goalkeeper.fis) / 10.0
                    goal_chance = max(0.02, min(0.95, attacker_skill * base_shot * (1.0 - keeper_skill * 0.7)))
                    if database.random.random() < goal_chance:
                        score2 += 1
                        minute = database.random.randint(1, 90)
                        events.append({"team": team2.name, "scorer": attacker.name, "minute": minute})

        # Resultado e registro no histórico
        if score1 > score2:
            result = f"{team1.name} {score1} x {score2} {team2.name} — {team1.name} venceu!"
            winner = team1.name
        elif score2 > score1:
            result = f"{team1.name} {score1} x {score2} {team2.name} — {team2.name} venceu!"
            winner = team2.name
        else:
            result = f"{team1.name} {score1} x {score2} {team2.name} — Empate!"
            winner = None

        match_record = {
            "team1": team1.name,
            "team2": team2.name,
            "score1": score1,
            "score2": score2,
            "winner": winner,
            "events": events
        }
        self.match_history.append(match_record)

        # registrar e processar eventos pós-jogo (lesões, moral, eventos aleatórios)
        try:
            events.record_match_events(self, match_record)
        except Exception:
            pass

        # tenta salvar histórico (não quebra se houver erro)
        try:
            stats.salvar_carregar_historico(self.match_history)
        except Exception:
            pass

        return result

    def start_season(self):
        """Inicializa a SeasonManager, gera calendário e zera a tabela de classificação."""
        from season import SeasonManager
        self.season_manager = SeasonManager(self.teams)
        self.schedule = self.season_manager.generate_schedule(self.teams)
        self.current_round_index = 0
        self.standings = self.season_manager.init_standings()
        print(f"Temporada iniciada: {len(self.schedule)} rodadas geradas.")

    def advance_round(self, mode: str = 'fast'):
        """Avança uma rodada: joga os confrontos e atualiza a tabela.

        mode: 'fast' usa simulate_match; 'visual' imprime resultados também.
        """
        if not hasattr(self, 'season_manager'):
            self.start_season()

        if self.current_round_index >= len(self.schedule):
            print("Temporada já encerrada.")
            return None

        current_round = self.schedule[self.current_round_index]
        print(f"Jogando rodada {self.current_round_index + 1}/{len(self.schedule)}")

        results = self.season_manager.play_round(current_round, self, mode=mode)

        for match_record in results:
            # atualiza tabela de classificação
            self.season_manager.apply_match_to_standings(match_record, self.standings)

        self.current_round_index += 1

        if self.current_round_index >= len(self.schedule):
            # temporada finalizada — salva tabela ordenada
            sorted_table = self.season_manager.get_sorted_standings(self.standings)
            self.season_manager.save_standings(sorted_table)
            print("Temporada encerrada. Tabela final salva em 'season.json'")

        return results
