import sqlite3
import emu_socket

def write_data(actor_name: str, action_name: str, actor1: emu_socket.ActorP1, actor2: emu_socket.ActorP2, reward: int):
    params = [actor_name, action_name, actor1.health, actor2.health, actor1.dist(actor2.x, actor2.y), actor2.state, reward]
    print(params)
    con = sqlite3.connect("data/MK.sqlite3")
    cur = con.cursor()
    cur.execute("""
                INSERT INTO REWARDS
                (Actor, Action, HealthP1, HealthP2, Distance, StateP2, Reward)
                VALUES
                (?, ?, ?, ?, ?, ?, ?)
                """, params)
    con.commit()