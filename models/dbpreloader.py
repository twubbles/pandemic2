# this model handles game status awareness of the engine

from gameclasses import GameVars


# Checks to see if there is an active game.
# If there is it will create a GameVars object with the vars.
# If not it creates an empty GameVars object.
try:
    games = db(db.games).select(db.games.ALL, orderby=db.games.created,cache=(cache.ram, 30), cacheable=True)
    if getEstNow() < games.last().end_at:
        gameinfo = GameVars(games.last().id, games.last().start_at, games.last().end_at, games.last().time_per_food,
                            games.last().stun_timer, games.last().cure_timer, games.last().bite_shares_per_food,
                            games.last().pause_starts_at, games.last().pause_ends_at,
                            games.last().created, games.last().posttimeout, games.last().signup_start_at,
                            games.last().signup_end_at, games.last().game_name)
    else:
        gameinfo = GameVars()
except:
    gameinfo = GameVars()

