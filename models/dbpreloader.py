# coding: utf8
from gameclasses import GameObject, GameVars

# Checks to see if there is an active game. If there is it will create a GameVars object with the vars. If not it creates an empty GameVars object.
activegame = False
try:
    games = db(db.games).select(db.games.id, db.games.start_at, db.games.end_at, db.games.time_per_food,
                                db.games.signup_start_at, db.games.signup_end_at,
                                db.games.stun_timer, db.games.cure_timer, db.games.bite_shares_per_food,
                                db.games.pause_starts_at,db.games.game_name,
                                db.games.pause_ends_at, db.games.created, db.games.posttimeout, orderby=db.games.created,cache=(cache.ram, 1), cacheable=True)
    if getEstNow() < games.last().end_at:
        activegame = games.last()
    if activegame:
        gameinfo = GameVars(activegame.id, activegame.start_at, activegame.end_at, activegame.time_per_food, activegame.stun_timer,
                            activegame.cure_timer,
                            activegame.bite_shares_per_food, activegame.pause_starts_at, activegame.pause_ends_at, activegame.created,
                            activegame.posttimeout, activegame.signup_start_at, activegame.signup_end_at, activegame.game_name)
    else:
        gameinfo = GameVars()
except:
    gameinfo = GameVars()


