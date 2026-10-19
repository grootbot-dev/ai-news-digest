#!/usr/bin/env python3
"""Rebuild README.md, weekly.md, monthly.md from news.jsonl. Ratings are never printed."""
import json, glob, os, datetime as dt
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ=dt.timezone(dt.timedelta(hours=7))
M={"Mon":"Moe the Coffee Robot ☕🤖","Tue":"Turbo the Llama 🦙","Wed":"Wally the Wombat 🐨","Thu":"Thunder the Hamster ⚡🐹","Fri":"Fry the Party Penguin 🐧🎉","Sat":"Sid the Surfing Sloth 🦥🏄","Sun":"Sunny the Cat 🐱☀️"}
items=[json.loads(l) for l in open(os.path.join(R,"news.jsonl"),encoding="utf-8") if l.strip()]
today=max((i["discovered_at"][:10] for i in items),default=dt.datetime.now(TZ).date().isoformat())
td=dt.date.fromisoformat(today)
srt=lambda xs:sorted(xs,key=lambda i:-i["rating"])
def thumb(i): return f'<img src="{i["image"]}" width="80" alt=""> ' if i.get("image") and os.path.exists(os.path.join(R,i["image"])) else ""
def lst(xs): return "\n".join(f"{n}. {thumb(i)}**[{i['title']}]({i['url']})** {i.get('quip','')}" for n,i in enumerate(xs,1))
def tldr(xs): return "📰 **TL;DR:** "+" · ".join(i["title"] for i in xs[:3])+" 🔥🤯"
def win(days,top):
  lo=td-dt.timedelta(days=days-1)
  return srt([i for i in items if lo<=dt.date.fromisoformat(i["published_at"][:10])<=td])[:top]
t=srt([i for i in items if i["discovered_at"][:10]==today])[:15]
day=td.strftime("%a"); mascot=M[day]
comic=sorted(glob.glob(os.path.join(R,"comics",f"{today}-*.jpg")))
out=[f"# 🤖 AI News Digest\n\nDaily AI news from [4PDA's AI forum](https://4pda.to/forum/index.php?showforum=1240), curated with r/LocalLLaMA energy 🦾. Updated every day at 9:17 AM (UTC+7).\n\n📅 **{today}** · Mascot of the day: **{mascot}**\n\nSee also: [🗓️ Top of the week](weekly.md) · [📆 Top of the month](monthly.md)\n"]
if comic: out.append(f"![Today's comic](comics/{os.path.basename(comic[-1])})\n")
out+= [tldr(t),"",lst(t),""]
open(os.path.join(R,"README.md"),"w",encoding="utf-8").write("\n".join(out))
for fn,days,top,h in [("weekly.md",7,10,"🗓️ Top of the week"),("monthly.md",30,20,"📆 Top of the month")]:
  x=win(days,top)
  c=sorted(glob.glob(os.path.join(R,"comics",fn.split(".")[0]+"-*.jpg")))
  img=f"![{h}](comics/{os.path.basename(c[-1])})\n\n" if c else ""
  open(os.path.join(R,fn),"w",encoding="utf-8").write(f"# {h}\n\nLast {days} days up to {today} (by publication date). [⬅️ Today](README.md)\n\n{img}{tldr(x)}\n\n{lst(x)}\n")
# ---------- GitHub Pages site (docs/) ----------
import html, shutil
D=os.path.join(R,"docs"); os.makedirs(os.path.join(D,"archive"),exist_ok=True); os.makedirs(os.path.join(D,"comics"),exist_ok=True)
for f in glob.glob(os.path.join(R,"comics","*.jpg")): shutil.copy2(f,os.path.join(D,"comics"))
os.makedirs(os.path.join(D,"cards"),exist_ok=True)
for f in glob.glob(os.path.join(R,"cards","*.jpg")): shutil.copy2(f,os.path.join(D,"cards"))
open(os.path.join(D,".nojekyll"),"w").close()
BASE="https://grootbot-dev.github.io/ai-news-digest/"
E=html.escape
def comic_for(pat):
  c=sorted(glob.glob(os.path.join(R,"comics",pat))); return os.path.basename(c[-1]) if c else None
def card(i):
  q=i.get("quip",""); emo=q.split(" ")[0] if q and not q[0].isascii() else "🔥"
  return f'<article class="card"><div class="emo">{emo}</div><div><h3><a href="{E(i["url"])}" target="_blank" rel="noopener">{E(i["title"])}</a></h3><p class="quip">{E(q)}</p><p class="meta">📡 {E(i.get("source",""))}{" · ✍️ "+E(i["author"]) if i.get("author") else ""} · 📅 {E(i["published_at"][:10])}</p></div></article>'
def has_img(i): return bool(i.get("image")) and os.path.exists(os.path.join(R,i["image"]))
def tile(i,pre):
  if not has_img(i): return card(i).replace('class="card"','class="card wide"',1)
  alt=(i["title"]+" — "+i.get("quip","")).strip(" —")
  return f'<a class="tile" href="{E(i["url"])}" target="_blank" rel="noopener"><img src="{pre}{E(i["image"])}" alt="{E(alt)}" title="{E(i["title"])}" loading="lazy" width="1600" height="900"></a>'
MODEJS="""<script>(function(){var q=new URLSearchParams(location.search).get('mode'),m=(q==='text'||q==='comic')?q:null;try{if(m)localStorage.setItem('mode',m);else m=localStorage.getItem('mode')}catch(e){}if(m!=='text')m='comic';document.documentElement.className='mode-'+m;window.setMode=function(x){try{localStorage.setItem('mode',x)}catch(e){}document.documentElement.className='mode-'+x;var u=new URL(location.href);if(u.searchParams.has('mode')){u.searchParams.set('mode',x);history.replaceState(null,'',u)}};})();</script>"""
def page(path,title,sub,img,xs,mascot_txt,pre):
  nav="".join(f'<a href="{pre}{h}"{" class=on" if title.startswith(n) else ""}>{l}</a>' for n,h,l in [("Today","index.html","⚡ Today"),("Week","weekly.html","🗓️ Week"),("Month","monthly.html","📆 Month"),("Archive","archive/index.html","📚 Archive")])
  og=BASE+"comics/"+img if img else ""
  body="".join(card(i) for i in xs) or '<p class="empty">Nothing worth reading. Touch grass 🌱</p>'
  grid="".join(tile(i,pre) for i in xs)
  toggle='<span class="modes"><button type="button" class="m-comic" onclick="setMode(\'comic\')">🖼️ Comic</button><button type="button" class="m-text" onclick="setMode(\'text\')">📝 Text</button></span>'
  doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · AI News Digest</title><meta name="description" content="{E(sub)}">
<meta property="og:title" content="{E(title)} · AI News Digest"><meta property="og:description" content="{E(sub)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}{path}">{f'<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{og}">' if og else ''}
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="{pre}style.css">{MODEJS}</head>
<body><header><h1><a href="{pre}index.html">🤖 AI News Digest 💥</a></h1><nav>{nav}{toggle}</nav></header><main>
<section class="hero"><h2>{E(title)}</h2><p class="sub">{E(sub)}</p>{f'<p class="mascot">🎭 Mascot of the day: <b>{E(mascot_txt)}</b></p>' if mascot_txt else ''}{f'<img class="comic" src="{pre}comics/{img}" alt="{E(title)} comic">' if img else ''}</section>
{f'<section class="grid comic-only">{grid}</section>' if grid else ''}<section class="cards{' text-only' if grid else ''}">{body}</section></main><footer>From <a href="https://4pda.to/forum/index.php?showforum=1240">4PDA's AI forum</a> with r/LocalLLaMA energy 🦾 · updated daily 9:17 AM (UTC+7) · <a href="https://github.com/grootbot-dev/ai-news-digest">GitHub</a></footer></body></html>'''
  open(os.path.join(D,path),"w",encoding="utf-8").write(doc)
page("index.html",f"Today · {today}","Today's AI news, only the good stuff 🔥",comic_for(f"{today}-*.jpg"),t,mascot,"")
page("weekly.html","Week: top of the week",f"Top 10 from the last 7 days up to {today}",comic_for("weekly-*.jpg"),win(7,10),None,"")
page("monthly.html","Month: top of the month",f"Top 20 from the last 30 days up to {today}",comic_for("monthly-*.jpg"),win(30,20),None,"")
dates=sorted({i["discovered_at"][:10] for i in items},reverse=True)
for d in dates:
  dd=dt.date.fromisoformat(d)
  page(f"archive/{d}.html",f"Archive · {d}",f"AI news discovered on {dd.strftime('%A')}, {d}",comic_for(f"{d}-*.jpg"),srt([i for i in items if i["discovered_at"][:10]==d]),M[dd.strftime("%a")],"../")
lis="".join(f'<article class="card"><div class="emo">{M[dt.date.fromisoformat(d).strftime("%a")].split(" ")[-1]}</div><div><h3><a href="{d}.html">📅 {d}</a></h3><p class="meta">{M[dt.date.fromisoformat(d).strftime("%a")]} · {sum(1 for i in items if i["discovered_at"][:10]==d)} stories</p></div></article>' for d in dates)
page("archive/index.html","Archive","Every past digest 📚",comic_for(f"{today}-*.jpg"),[],None,"../")
p=os.path.join(D,"archive","index.html"); s=open(p,encoding="utf-8").read().replace('<p class="empty">Nothing worth reading. Touch grass 🌱</p>',lis); open(p,"w",encoding="utf-8").write(s)
