from sklearn.neighbors import BallTree
import struct
import numpy as np
from models import embed, langid
import db
import re

lang_tree_dict = {}


def init():
    langs = db.exe("select distinct lang from sites")
    for lang in langs:
        new_tree(*lang)


def create_tree(lang, leaf_size=50):
    count = db.exe("select count(*) from sites where lang = ?",
                   (lang, )).fetchone()[0]
    vecs = np.empty((count, 512))
    ids = np.empty(count, '|S22')
    for i, row in enumerate(db.exe("select vector, id from sites where lang = ?", (lang,))):
        vecs[i] = struct.unpack("512f", row[0])
        ids[i] = row[1]
    return ids, BallTree(vecs, leaf_size), count


def new_tree(lang, leaf_size=50):
    lang_tree_dict[lang] = create_tree(lang, leaf_size)


DB_SELECT_COLUMNS = "url, title, description, trust, privacy, child_safety, popularity, alexa_rank, rating_good, rating_bad"
DB_SELECTOR = f"select {DB_SELECT_COLUMNS} from sites inner join domains on sites.domain = domains.id"


def row_to_dict(row):
    return dict(zip(
        DB_SELECT_COLUMNS.split(", "), row))


def search_tree(query, ids, tree, tree_size):
    vector = embed(query)

    dd, ii = tree.query(vector, k=min(tree_size, 15))
    # ii, dd = tree.query_radius(
    #     vector, 2, return_distance=True, sort_results=True)
    distances, indexes = dd[0], ii[0]
    wanted_ids = map(lambda i: str(ids[i])[1:], indexes)
    print(distances)
    results = []
    for wanted_id in wanted_ids:
        sql = f"{DB_SELECTOR} where sites.id = {wanted_id}"
        row = db.exe(sql).fetchone()
        results.append(row_to_dict(row))
    return results


def search_match(query, lang="?"):
    use_lang = lang != "?"
    pattern = f"%{query.strip()}%"
    results = []
    sql = f"""
    {DB_SELECTOR}
    where {"sites.lang = ? and" if use_lang  else ""} (domains.name like ? or sites.url like ? or sites.title like ? or sites.description like ?)
    order by 
        case when domains.name like ? then 1 else 2 end,
        case when sites.url like ? then 2 else 3 end,
        case when sites.title like ? then 3 else 4 end,
        case when sites.description like ? then 4 else 5 end,
        domains.alexa_rank
    """
    params = (*([lang] if use_lang else []),
              *tuple(pattern for _ in range(8)))
    for row in db.exe(sql, (params)):
        results.append(row_to_dict(row))
    return results


def open_query_cmd(ctx):
    def mod():
        if len(ctx['results']):
            ctx['redirect'] = ctx['results'][0]['url']
    ctx['mods'].append(mod)


QUERY_CMDS = {
    "open": open_query_cmd,
}


def search(query):
    ctx = {"lang": "?", "query": query,
           "results": [], "redirect": False, "mods": [], "stop": False}
    if query[0] == "!":
        query = query[1:]
        cmd_string, _, query = query.partition(" ")
        cmd_names = cmd_string.split("!")
        for cmd_name in cmd_names:
            if len(cmd_name) == 2:
                ctx['lang'] = cmd_name
            else:
                query_cmd = QUERY_CMDS.get(cmd_name.lower())
                if query_cmd:
                    query_cmd(ctx)
    if ctx['stop']:
        return ctx
    if len(query.strip().split()) <= 1:
        ctx['results'] = search_match(query, ctx['lang'])
    else:
        if ctx['lang'] == "?":
            ctx['lang'] = langid(query)
        ids_tree = lang_tree_dict.get(ctx['lang'])
        if ids_tree:
            ctx['results'] = search_tree(query, *ids_tree)
    for mod in ctx['mods']:
        mod()
    return ctx
