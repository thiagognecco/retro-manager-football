import math
import random

# Simple player AI for visual match mode.
# API: update_player(player, ball, teammates, opponents, dt)
# player: dict with keys 'game_player' (database.Player), 'x','y','vx','vy','team', 'has_ball'
# ball: dict with keys 'x','y','vx','vy','possession' (may be player dict or None)
# teammates/opponents: lists of player dicts
# dt: seconds since last frame


def _distance(a_x, a_y, b_x, b_y):
    return math.hypot(a_x - b_x, a_y - b_y)


def _normalize(dx, dy):
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 0.0
    return dx / d, dy / d


def update_player(player, ball, teammates, opponents, dt):
    """
    Update player's velocity (vx, vy) and optionally interact with the ball.
    This function mutates `player` and `ball` in-place.
    """
    gp = player.get('game_player')
    if gp is None:
        return

    # Basic movement speed depends on physical attribute
    base_speed = 80 + (gp.fis * 20)  # pixels per second

    # If player currently has the ball, decide action: shoot, pass, or dribble
    if player.get('has_ball'):
        # Slight randomness to decisions
        dec = getattr(gp, 'dec', 1)
        tec = getattr(gp, 'tec', 1)
        shoot_bias = 0.15 + ((dec + tec) / 10.0) * 0.45  # range ~0.15-0.6
        if gp.star:
            shoot_bias += 0.05

        # Determine which direction is opponent goal based on team
        if player.get('team') == 1:
            goal_x = 800  # shoot to the right
        else:
            goal_x = 0    # shoot to the left

        # Estimate proximity to goal
        dist_to_goal = abs(goal_x - player['x'])
        near_goal = dist_to_goal < 220  # arbitrary "in shooting range"

        # Prefer shooting if near goal and random allows
        if near_goal and random.random() < shoot_bias:
            # Shoot towards goal center y=300
            dirx, diry = _normalize(goal_x - player['x'], 300 - player['y'])
            power = 320 + (tec * 90)
            ball['vx'] = dirx * power
            ball['vy'] = diry * power * 0.6
            player['has_ball'] = False
            ball['possession'] = None
            return

        # Otherwise try to pass to a forward teammate (simple heuristic)
        forward_teammates = [t for t in teammates if t is not player]
        if forward_teammates:
            # prefer teammate further towards opponent goal
            if player.get('team') == 1:
                target = max(forward_teammates, key=lambda t: (t['x'], -abs(t['y'] - player['y'])))
            else:
                target = min(forward_teammates, key=lambda t: (t['x'], abs(t['y'] - player['y'])))

            dirx, diry = _normalize(target['x'] - player['x'], target['y'] - player['y'])
            power = 220 + (tec * 70)
            # Add slight inaccuracy based on decision attribute
            inaccuracy = max(0.0, (5 - gp.dec) * 0.02)
            if random.random() < inaccuracy:
                # perturb target
                dirx += (random.random() - 0.5) * 0.3
                diry += (random.random() - 0.5) * 0.3
                dirx, diry = _normalize(dirx, diry)

            ball['vx'] = dirx * power
            ball['vy'] = diry * power * 0.6
            player['has_ball'] = False
            ball['possession'] = None
            return

        # If no pass/shoot, dribble (move forward)
        if player.get('team') == 1:
            dirx, diry = 1.0, 0.0
        else:
            dirx, diry = -1.0, 0.0
        player['vx'] = dirx * (base_speed * 0.6)
        player['vy'] = diry * 0.0
        return

    # If player doesn't have the ball, move towards it to contest
    bx, by = ball.get('x', 0.0), ball.get('y', 0.0)
    dx, dy = bx - player['x'], by - player['y']
    dist = _distance(player['x'], player['y'], bx, by)

    # If close and ball is free, attempt to take possession probabilistically
    if dist < 18 and ball.get('possession') is None:
        # Probability depends on physical and decision
        take_prob = 0.5 + ((gp.fis + gp.dec) - 2) * 0.06  # baseline ~0.5
        if random.random() < take_prob:
            player['has_ball'] = True
            ball['possession'] = player
            ball['vx'] = 0.0
            ball['vy'] = 0.0
            return

    # Otherwise move towards the ball (simple pursuit)
    if dist > 6:
        nx, ny = _normalize(dx, dy)
        speed = base_speed * (0.6 + (gp.fis / 10.0))
        player['vx'] = nx * speed
        player['vy'] = ny * speed
    else:
        # small jitter when close but not possessing
        player['vx'] *= 0.5
        player['vy'] *= 0.5

    # If opponent has the ball, and this player is close, attempt tackle
    poss = ball.get('possession')
    if poss and poss in opponents:
        dx2 = poss['x'] - player['x']
        dy2 = poss['y'] - player['y']
        dist2 = _distance(player['x'], player['y'], poss['x'], poss['y'])
        if dist2 < 22:
            # tackle success probability depends on fis
            tackle_prob = 0.25 + (gp.fis / 10.0)
            if random.random() < tackle_prob:
                # steal ball
                player['has_ball'] = True
                poss['has_ball'] = False
                ball['possession'] = player
                ball['vx'] = 0.0
                ball['vy'] = 0.0
                # small knock-back for opponent
                poss['vx'] = -dx2 * 2
                poss['vy'] = -dy2 * 2
                return
