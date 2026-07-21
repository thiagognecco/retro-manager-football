# v2.7 Debug & Performance Plan - Ação Completa

**Status:** Issue identificado - `simulate_match()` trava  
**Objetivo:** Identificar bottleneck e colocar simulação completa rodando  
**Baseado em:** Pesquisa - Python profiling, game loops architecture  

---

## 🎯 PROBLEMA

```
Sintoma: simulate_match() não termina em tempo razoável
- Começa normalmente
- Trava/congela após 2+ minutos
- 1 frame leva ~9 segundos (muito longo)
- 5400 frames = ~13+ horas (inviável)

Causa provável:
1. Loop infinito em algum lugar
2. Operação O(n²) ou pior dentro do loop
3. Memory leak causando GC massivo
4. Deadlock em pathfinding/behavior
```

---

## 📋 PLANO AÇÃO - FASE 1: PROFILING & DIAGNOSIS

### ETAPA 1.1: Usar cProfile para Identificar Bottleneck

**Baseado em:** Python docs cProfile - ferramenta padrão para profiling

**Arquivo:** `profile_match.py`

```python
import cProfile
import pstats
import io
from match_simulation_engine_v2 import Match, create_sample_teams

def profile_one_match():
    """Profile 1 complete match"""
    home, away = create_sample_teams()
    match = Match(home, away)
    match.simulate_match()

# Profile com saída
pr = cProfile.Profile()
pr.enable()
profile_one_match()
pr.disable()

# Mostrar resultados ordenados por tempo cumulativo
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)  # Top 20 functions
print(s.getvalue())

# Também ordenar por tempo interno (hot loop)
s2 = io.StringIO()
ps2 = pstats.Stats(pr, stream=s2).sort_stats('time')
ps2.print_stats(20)
print(s2.getvalue())
```

**O que isso mostra:**
- Função mais cara (cumulative time)
- Funções chamadas mais vezes
- Tempo gasto por função
- "Hot loops" (operações lentas)

**EXECUTAR:**
```bash
python profile_match.py > profile_output.txt 2>&1
```

**O QUE PROCURAR:**
```
Linha 1-10 (TOP CULPRITS):
cumtime | ncalls | tottime | função
  5.2   | 5400   | 0.001   | simulate_frame() <- CULPADO?
  4.8   | 27000  | 0.0002  | nearby_agents() <- CULPADO?
  3.2   | 5400   | 0.0001  | behavior_tree.tick() <- CULPADO?
  2.1   | 28000  | 0.0001  | update_agent_position() <- CULPADO?
```

---

### ETAPA 1.2: Adicionar Timing Prints Estratégicos

Se profiling não é claro, adicionar prints em pontos-chave:

**Em `match_simulation_engine_v2.py`:**

```python
def simulate_minute(self) -> None:
    """Simulate one minute (60 frames at 60 FPS)"""
    import time
    minute_start = time.perf_counter()
    
    for frame in range(60):
        frame_start = time.perf_counter()
        self.current_frame = self.current_minute * 60 + frame
        self.simulate_frame(dt=1.0/60.0)
        frame_time = time.perf_counter() - frame_start
        
        if frame_time > 0.1:  # Alerta se frame > 100ms
            print(f"SLOW FRAME {self.current_frame}: {frame_time:.3f}s")
    
    minute_time = time.perf_counter() - minute_start
    print(f"Minute {self.current_minute} took {minute_time:.2f}s")

def simulate_frame(self, dt: float = 1.0/60.0) -> None:
    """Simulate one frame with timing"""
    import time
    
    t1 = time.perf_counter()
    # ... clear grid
    t2 = time.perf_counter()
    
    # ... update behaviors (22x)
    t3 = time.perf_counter()
    
    # ... predict positions
    t4 = time.perf_counter()
    
    # ... update movement (22x)
    t5 = time.perf_counter()
    
    # ... rebuild grid
    t6 = time.perf_counter()
    
    # ... process events
    t7 = time.perf_counter()
    
    if self.current_frame % 60 == 0:
        print(f"Frame timing breakdown:")
        print(f"  Clear: {(t2-t1)*1000:.2f}ms")
        print(f"  Behaviors: {(t3-t2)*1000:.2f}ms")
        print(f"  Tactics: {(t4-t3)*1000:.2f}ms")
        print(f"  Movement: {(t5-t4)*1000:.2f}ms")
        print(f"  Rebuild: {(t6-t5)*1000:.2f}ms")
        print(f"  Events: {(t7-t6)*1000:.2f}ms")
        print(f"  Total: {(t7-t1)*1000:.2f}ms")
```

**EXECUTAR:**
```bash
python -c "from match_simulation_engine_v2 import Match, create_sample_teams; 
m = Match(*create_sample_teams()); 
m.simulate_match()" | head -100
```

**O QUE PROCURAR:**
```
Minute 0 took 45.32s  <- MUITO LONGO!
Frame timing breakdown:
  Clear: 1.23ms
  Behaviors: 15.43ms  <- CULPADO?
  Tactics: 2.11ms
  Movement: 8.92ms
  Rebuild: 0.89ms
  Events: 3.21ms
  Total: 31.79ms <- FRAME LEVA 31ms!
```

---

## 📊 PLANO AÇÃO - FASE 2: INVESTIGAÇÃO PROFUNDA

### Se Bottleneck = Behaviors (15.43ms)
```
CHECK:
1. Quantas vezes behavior_tree.tick() é chamado?
2. O seletor está fazendo busca desnecessária?
3. Há recursão profunda?
4. Há string matching ou regex dentro?

FIX Sugerido:
- Cache resultados de queries
- Lazy evaluation de condições
- Simplificar tree complexity
```

### Se Bottleneck = Movement (8.92ms)
```
CHECK:
1. A* pathfinding rodando a cada frame?
2. RVO collision avoidance é O(n²)?
3. Nearby agents queries ineficientes?
4. Há memory allocation a cada frame?

FIX Sugerido:
- Lazy pathfinding (só recalcular se target muda)
- Limit nearby agent search
- Pre-allocate arrays
- Use numpy para operações vetorizadas
```

### Se Bottleneck = Events (3.21ms)
```
CHECK:
1. Event processing é O(n²)?
2. Há iteração completa de players?
3. Há string comparisons caras?

FIX Sugerido:
- Use enum comparisons ao invés de strings
- Early exit em checks
- Cache resultados
```

---

## 🔧 PLANO AÇÃO - FASE 3: OTIMIZAÇÃO

### Otimizações Low-Hanging Fruit (fáceis)

1. **Remover Prints de Debug**
   ```python
   # ANTES:
   print(f"[MATCH START] Simulating...")
   
   # DEPOIS:
   # print(f"[MATCH START] Simulating...")  # Remover
   ```

2. **Lazy Pathfinding**
   ```python
   # ANTES:
   movement.calculate_path()  # A cada frame
   
   # DEPOIS:
   if target_changed:
       movement.calculate_path()  # Só se mudou
   ```

3. **Cache Nearby Agents**
   ```python
   # ANTES:
   nearby = grid.nearby_agents(x, y, radius)  # A cada frame
   
   # DEPOIS:
   if frame % 10 == 0:  # Recalculate every 10 frames
       nearby = grid.nearby_agents(x, y, radius)
   ```

4. **Usar Enums ao invés de Strings**
   ```python
   # ANTES:
   if player.state == "MOVING":
   
   # DEPOIS:
   if player.state == PlayerState.MOVING:  # Mais rápido
   ```

### Otimizações Medium (precisam mudança)

1. **Numba JIT para operações vetorizadas**
   ```python
   from numba import jit
   
   @jit(nopython=True)
   def fast_distance(x1, y1, x2, y2):
       return ((x2-x1)**2 + (y2-y1)**2)**0.5
   ```

2. **Reduce nearby_agents calls**
   ```python
   # Ao invés de chamar 22x por frame:
   # Grid retorna todos de uma vez
   nearby_by_player = grid.get_all_nearby_pairs(radius=15)
   ```

3. **Pre-allocate arrays**
   ```python
   # ANTES:
   velocities = []
   for player in players:
       velocities.append(player.velocity)  # Allocation
   
   # DEPOIS:
   velocities = np.zeros((22, 2))
   for i, player in enumerate(players):
       velocities[i] = player.velocity
   ```

---

## ✅ PLANO AÇÃO - FASE 4: VALIDAÇÃO

### Checkpoint 1: Frame
- [ ] 1 frame < 10ms
- [ ] Rodar 10 frames, ver tempo total

### Checkpoint 2: Minute
- [ ] 1 minuto (60 frames) < 10s
- [ ] Rodar 1 minuto completo

### Checkpoint 3: Match
- [ ] 1 match (90 min) < 3 min
- [ ] Rodar 1 match completo
- [ ] Verificar resultado final

### Checkpoint 4: Scale
- [ ] 5 matches em sequência < 15 min
- [ ] 100 matches overnight (viável)

---

## 📅 TIMELINE EXECUÇÃO

```
Dia 1 (24/07):
  Manhã (1h):  Rodar profiling, identificar bottleneck
  Tarde (2h):  Adicionar timing prints, investigar
  Noite (1h):  Fazer plano específico de otimização

Dia 2 (25/07):
  Manhã (2h):  Implementar otimizações low-hanging
  Tarde (1h):  Testar e validar
  Noite (2h):  Medium optimizations se necessário

Dia 3 (26/07):
  Manhã (1h):  Final tweaks
  Tarde (1h):  Rodar 1000 matches (overnight)
```

---

## 🎯 RESULTADO ESPERADO

```
Antes:
  1 frame: 31.79ms (TOO SLOW)
  1 match: Não termina (trava)
  
Depois:
  1 frame: <2ms (15x mais rápido)
  1 match: <3 min (SUCESSO)
  1000 matches: ~50 min (overnight viável)
```

---

## 📝 REFERÊNCIAS USADAS

1. **Python cProfile Docs** - https://docs.python.org/3/library/profile.html
   - Como usar cProfile para identificar bottlenecks
   - Stats.sort_stats() options
   - Timing breakdown por função

2. **Game Loop Architecture** - Wikipedia
   - Standard game loop: check input → update → render
   - Importance of frame timing
   - Multi-threaded optimization strategies

3. **Key Insights:**
   - Deterministic profiling mostra EXATAMENTE onde tempo é gasto
   - "Hot loops" são a prioridade #1
   - Premature optimization é inimiga, mas agora temos dados
   - Lazy evaluation é ouro em game loops

---

## 🚀 PRÓXIMO PASSO

**Executar agora:**
```bash
cd "C:\Users\gnecc\Documents\Footbal manager"
python profile_match.py > profile_output.txt 2>&1
cat profile_output.txt
```

**Análise:** Procurar top 3 funções por cumulative time
**Decision:** Qual otimização fazer primeiro
**Implementation:** Fixar e testar

---

**Pronto para começar o debug amanhã!** 🎯
