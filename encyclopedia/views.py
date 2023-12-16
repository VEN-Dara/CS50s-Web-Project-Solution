import re
import random
from django.shortcuts import render

from . import util
from markdown2 import Markdown


def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    html_content = convert_md_to_html(title)
    if html_content == None:
        return render(request, 'encyclopedia/error.html', {
            "message" : "No entry found!"
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title" : title,
            "content" : html_content,
        })
    
def search(request):
    if request.method == "POST":
        search_entry = request.POST['q']
        html_content = convert_md_to_html(search_entry)
        if html_content is not None:
            return render(request, "encyclopedia/entry.html", {
            "title" : search_entry,
            "content" : html_content,
            })
        else:
            recommendation = []
            for entry in util.list_entries():
                if search_entry.lower() in entry.lower():
                    recommendation.append(entry)
            if not recommendation:
                return render(request, 'encyclopedia/error.html', {
                    "message" : "No entry found!"
                })
            else:
                return render(request, "encyclopedia/search.html", {
                "entries": recommendation
            })

def new(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html")
    elif request.method == "POST":
        title = request.POST['title_entry']
        content = request.POST['content_entry']
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html", {
                "message" : "Entry already exists!"
            })
        else:
            util.save_entry(title, content)
            return entry(request,title)
        
def edit(request,title_entry):
    if request.method == "GET":
        content_entry = util.get_entry(title_entry)
        print(content_entry)
        return render(request, "encyclopedia/edit.html", {
            "title_entry" : title_entry,
            "content_entry" : content_entry,
        })

def save_edit(request):
    if request.method == "POST":
        title = request.POST['title_entry']
        content = request.POST['content_entry']
        content = re.sub(r'\n\s*\n', '\n', content)
        print(content)
        util.save_entry(title, content)
        return entry(request,title)
    
def random_page(request):
    entries = util.list_entries()
    random_entry = random.randint(0,len(entries)-1)
    title = entries[random_entry]
    return entry(request,title)




