import sqlite3
import emu_socket

def write_data(actor_name: str, action_name: str, actor1: emu_socket.ActorP1, actor2: emu_socket.ActorP2, damage_dished: int, damage_taken: int, save_file: str, reward: int, match_id: str):
    params = [actor_name, action_name, actor1.health, actor2.health, actor1.dist(actor2.x, actor2.y), actor2.prev_state, reward, damage_dished, damage_taken, actor1.prev_state, save_file.split('/')[-1], actor1.x, actor1.y, actor2.x, actor2.y, match_id]
    # print(params)
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    cur.execute("""
                INSERT INTO REWARDS
                (Actor, Action, HealthP1, HealthP2, Distance, StateP2, Reward, DamageDished, DamageTaken, StateP1, SaveFile, XP1, YP1, XP2, YP2, MatchID)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, params)
    con.commit()

def update_results(match_id: str, match_result: bool):
    res = 1 if match_result else 0
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    query = f"""
                UPDATE REWARDS SET MatchResults={res}
                WHERE MatchID='{match_id}'
                """
    cur.execute(query)
    con.commit()


def get_training(actor, reward_threshold):
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    cur.execute(f"""
                SELECT 
                 StateP2
                , XP1
                , YP1
                , XP2
                , YP2
                , Action
                FROM Rewards
                WHERE Actor='{actor}' AND reward >= {reward_threshold}
                """)
    return cur.fetchall()