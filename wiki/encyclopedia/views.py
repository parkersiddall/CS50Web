from django.shortcuts import render
from django.http import HttpResponse
import markdown2
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from random import choice, randint

from . import util


#class for the edit text area
class edit_form(forms.Form):
    edit_form_area = forms.CharField(widget=forms.Textarea, label="Edit Markup Content")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# renders the page for an entry given the title, no title renders and error screen
def title(request, title):
    if util.get_entry(title) != None:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": util.get_entry(title),
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message":"There is not a page for what you are searching for."
        })

def search(request):
    # if someone is submitting the form
    if request.method=="POST":
        # create a value called form and populate it with the POST content
        keyword = request.POST['searchform']
        # check to be sure entry is valid, if not return error.
        if keyword == "":
            return render(request, "encyclopedia/error.html", {
            "message":"You didn't insert anything into the search"
            })

        else:
            # if keyword already has an entry
            entries = util.list_entries()  # pulls a list of the entries

            # the section below converts everything to lowercase so that the search is not case sensitive
            keyword_lower = keyword.lower()
            entries_lower = []
            for entry in entries:
                entries_lower.append(entry.lower())

            # if the search word (keyword) is in the list of entries
            if keyword_lower in entries_lower:  # checks to see if keyword is in entries based on lowercase variables
                return render(request, "encyclopedia/entry.html", {  # if yes it renders the page and plugs in the info
                    "title": keyword,
                    "entry": util.get_entry(keyword),
                })
            else:
                # create a list of entries that have part of keyword in the entry
                similar_entries = []
                for entry in entries:
                    if keyword_lower in entry.lower():
                        similar_entries.append(entry)

                # render search page and pass through the list of similar entries
                return render(request, "encyclopedia/search.html", {
                    "keyword": keyword,
                    "similar_entries": similar_entries
                    })
    # if the form is not valid return page to user
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })


def new_entry(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_entry.html")
    if request.method == "POST":
        # check to see if the entry for the title already exists (making it case insensitive)
        new_entry = request.POST['title']  # pull out the title of the new Entry
        new_content = request.POST['content']  # pull out the content of the new Entry
        new_entry_lower = new_entry.lower()

        entries = util.list_entries()  # pulls a list of the entries

        # the section below converts everything to lowercase so that the search is not case sensitive
        entries_lower = []
        for entry in entries:
            entries_lower.append(entry.lower())

        # go through to see if the entry is already listed
        if new_entry_lower in entries_lower:

            return render(request, "encyclopedia/error.html", {
            "message": "An entry for this subject already exists"
            })

        else:
            util.save_entry(new_entry, new_content)  # saves contect to disk
            return HttpResponseRedirect(f"/{new_entry}")  # redirects to the page of the title of the new entry

def edit(request, entry):
    if request.method == "GET":

        # gather the content from the entry in order to pupulate the form
        edit_content = util.get_entry(entry)

        form = edit_form(edit_content)

        return render(request, "encyclopedia/edit.html", {
        "entry": entry,
        "edit_form": edit_form(),
        "edit_content": edit_content
        })

    else:
        # pull out the info from the edit field
        edited = request.POST['edited']

        # save the updated info, which should overide the old file on the disk.
        util.save_entry(entry, edited)
        return HttpResponseRedirect(f"/{entry}")  # redirects to the page of the title of the edited entry


def get_random_entry(request):
    entries = util.list_entries()  # pull out a list of all the entries
    random_entry = choice(entries)  # choose one of the entries at random
    return HttpResponseRedirect(f"/{random_entry}")  # return URL of random entry
