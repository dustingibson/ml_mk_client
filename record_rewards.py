import sqlite3
import emu_socket

def write_data(actor_name: str, action_name: str, actor1: emu_socket.ActorP1, actor2: emu_socket.ActorP2, damage_dished: int, damage_taken: int, save_file: str, reward: int):
    params = [actor_name, action_name, actor1.health, actor2.health, actor1.dist(actor2.x, actor2.y), actor2.state, reward, damage_dished, damage_taken, actor1.state, save_file.split('/')[-1], actor1.x, actor1.y, actor2.x, actor2.y]
    print(params)
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    cur.execute("""
                INSERT INTO REWARDS
                (Actor, Action, HealthP1, HealthP2, Distance, StateP2, Reward, DamageDished, DamageTaken, StateP1, SaveFile, XP1, YP1, XP2, YP2)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, params)
    con.commit()

def get_training(actor, reward_threshold):
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    cur.execute(f"""
                SELECT HealthP1 / 166.0, HealthP2 / 166.0, Distance / 255.0, StateP2 / 255.0, Action
                FROM Rewards
                WHERE Actor='{actor}' AND reward >= {reward_threshold}
                """)
    return cur.fetchall()