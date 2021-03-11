
from flask import Flask, request, render_template, redirect
import engine
import scrapper
import asyncio
from functools import wraps

engine.init()


app = Flask(__name__, static_url_path="/static")


def async_action(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped


@app.route("/")
def index():
    query = request.args.get("q")
    if query:
        ctx = engine.search(query)
        if ctx['redirect']:
            return redirect(ctx['redirect'])
        return render_template("results.html", **ctx)
    return render_template("index.html")

@app.route("/count")
def count():
    count = engine.db.exe("select count(*) from sites").fetchone()[0]
    return f"There are {count} sites saved right now."


@app.route("/explore")
@async_action
async def explore():
    query = request.args.get("q")
    need_new_lang = await scrapper.search_and_index(query)
    print(need_new_lang)
    if need_new_lang:
        engine.new_tree(need_new_lang)
    return render_template("explore.html", query=query)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=8080, debug=True)
