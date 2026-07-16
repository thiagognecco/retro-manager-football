import random
import json

class Player:
    def __init__(self, name, position, fis, tec, dec, star=False, morale: int = 50, injured: bool = False):
        self.name = name
        self.position = position  # 'GL', 'DF', 'MC', 'AT'
        self.fis = fis            # Físico (1 a 5)
        self.tec = tec            # Técnica (1 a 5)
        self.dec = dec            # Decisão (1 a 5)
        self.star = star          # Estrela ⭐ (True/False)
        self.morale = int(morale)
        self.injured = bool(injured)

    def get_average_force(self):
        """Calcula força média ajustando por moral e status de lesão.
        Jogadores lesionados têm força reduzida; moral aplica um multiplicador leve.
        """
        base = round((self.fis + self.tec + self.dec) / 3, 1)
        if self.injured:
            base = max(0.1, base - 1.5)
        # moral 50 => fator 1.0, moral 100 => ~1.25, moral 0 => ~0.75
        morale_factor = 1 + (self.morale - 50) / 200.0
        return round(max(0.1, base * morale_factor), 1)

    def to_dict(self):
        return {
            "name": self.name,
            "position": self.position,
            "fis": self.fis,
            "tec": self.tec,
            "dec": self.dec,
            "star": self.star,
            "morale": self.morale,
            "injured": self.injured
        }

class Team:
    def __init__(self, name, funds=100000):
        self.name = name
        self.funds = funds  
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def get_team_force(self):
        if not self.players:
            return 0
        total = sum(p.get_average_force() for p in self.players)
        return round(total / len(self.players), 1)

    def to_dict(self):
        return {
            "name": self.name,
            "funds": self.funds,
            "players": [p.to_dict() for p in self.players]
        }

# --- GERADOR DE TIMES DA 4ª DIVISÃO ---

NOME_SOBRENOME = {
    "nomes": ["Neymar", "Alisson", "Casemiro", "Danilo", "Marquinhos", "Thiago", "Lucas", "Gabriel", "Bruno", "Rodrigo", "Everton", "Yuri", "Vitor", "Pedro"],
    "sobrenomes": ["Silva", "Santos", "Souza", "Oliveira", "Pereira", "Lima", "Ferreira", "Costa", "Rodrigues", "Almeida", "Nascimento", "Barbosa"]
}

def generate_random_player(position, is_star=False):
    name = f"{random.choice(NOME_SOBRENOME['nomes'])} {random.choice(NOME_SOBRENOME['sobrenomes'])}"
    fis = random.randint(1, 3)
    tec = random.randint(1, 3)
    dec = random.randint(1, 3)
    
    if is_star:
        fis = min(5, fis + 2)
        tec = min(5, tec + 2)
        dec = min(5, dec + 2)
        
    return Player(name, position, fis, tec, dec, star=is_star)

def create_initial_database():
    teams_data = ["Tabajara FC", "Varzeano United", "Íbis Cover", "Chinelinho Esporte Clube"]
    teams = []
    
    for team_name in teams_data:
        team = Team(team_name, funds=150000)
        team.add_player(generate_random_player('GL', is_star=random.choice([True, False])))
        
        for _ in range(4):
            team.add_player(generate_random_player('DF'))
        for _ in range(4):
            team.add_player(generate_random_player('MC'))
            
        team.add_player(generate_random_player('AT', is_star=True))
        team.add_player(generate_random_player('AT'))
        teams.append(team)
        
    return teams

# --- FUNÇÕES DE SALVAMENTO (JSON) ---

def salvar_jogo(times, caminho_arquivo="savegame.json"):
    dados_para_salvar = [t.to_dict() for t in times]
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
        print(f"\n[ SALVO ] Jogo salvo com sucesso em '{caminho_arquivo}'!")

def carregar_jogo(caminho_arquivo="savegame.json"):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        times = []
        for t_dados in dados:
            time = Team(t_dados["name"], t_dados["funds"])
            for p_dados in t_dados["players"]:
                player = Player(
                    p_dados["name"],
                    p_dados["position"],
                    p_dados["fis"],
                    p_dados["tec"],
                    p_dados["dec"],
                    star=p_dados.get("star", False),
                    morale=p_dados.get("morale", 50),
                    injured=p_dados.get("injured", False)
                )
                time.add_player(player)
            times.append(time)
        print(f"\n[ CARREGADO ] Jogo carregado com sucesso de '{caminho_arquivo}'!")
        return times
    except FileNotFoundError:
        print("\n[⚠️] Nenhum save encontrado. Gerando novo campeonato...")
        return None

# --- BLOCO DE EXECUÇÃO ---
if __name__ == "__main__":
    print("=== TESTANDO SISTEMA DE SALVAMENTO ===")
    times_novos = create_initial_database()
    print(f"Times gerados: {[t.name for t in times_novos]}")
    
    salvar_jogo(times_novos)
    times_carregados = carregar_jogo()
    
    print("\n=== CONFIRMAÇÃO DO ARQUIVO SALVO ===")
    for t in times_carregados:
        print(f"Time: {t.name} | Goleiro: {t.players[0].name} (Força: {t.players[0].get_average_force()})")