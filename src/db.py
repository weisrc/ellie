import sqlite3
import threading
import datetime

lock = threading.Lock()

conn = sqlite3.connect("data/.db", check_same_thread=False)

c = conn.cursor()

# mtc = conn.cursor()


# def mtexe(sql, *params):
#     lock.acquire(True)
#     results = mtc.execute(sql, *params)
#     lock.release()
#     return results


def exe(sql, *params):
    # lock.acquire()
    c.execute(sql, *params)
    # lock.release()
    return c


def commit():
    conn.commit()


exe("""
create table if not exists domains (
    id char(22) primary key,
    name varchar(255),

    trust tinyint,
    privacy tinyint,
    child_safety tinyint,
    popularity tinyint,

    alexa_rank int,
    rating_good int,
    rating_bad int,

    updated date default current_timestamp
)
""")


def get_domain(id):
    return exe("select * from domains where id = ?", (id,)).fetchone()


def get_domain_by_name(name):
    return exe("select * from domains where name = ?", (name,)).fetchone()


def exist_domain(id):
    return bool(exe("select count(*) from domains where id = ?", (id,)).fetchone()[0])


def exist_domain_by_name(name):
    return exe("select * from domains where name = ?", (name,)).fetchone()


def insert_domain(id, name, trust, privacy, child_safety, popularity, alexa_rank, rating_good, rating_bad):
    exe("insert into domains (id, name, trust, privacy, child_safety, popularity, alexa_rank, rating_good, rating_bad) values (?,?,?,?,?,?,?,?,?)",
        (id, name, trust, privacy, child_safety, popularity, alexa_rank, rating_good, rating_bad))


exe("""
create table if not exists sites (
    id char(22) primary key,
    domain char(22),

    vector char(512),
    url varchar(1000),
    title varchar(255),
    description varchar(255),
    lang char(2),

    updated date default current_timestamp,
    foreign key(domain) references domains(id)
)
""")


def get_nth_site(n):
    return exe("select * from sites limit 1 order ?", (n,)).fetchone()


def get_site(id):
    return exe("select * from sites where id = ?", (id,)).fetchone()


def exist_site_by_url(url):
    res = bool(
        exe("select count(*) from sites where url = ?", (url,)).fetchone()[0])
    return res


def exist_site(id):
    return bool(exe("select count(*) from sites where id = ?", (id,)).fetchone()[0])


def insert_site(id, domain, vector, url, title, description, lang):
    exe("insert into sites (id, domain, vector, url, title, description, lang) values (?,?,?,?,?,?,?)",
        (id, domain, vector, url, title, description, lang))
