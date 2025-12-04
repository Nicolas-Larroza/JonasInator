import requests, re, time, json

def get_links_and_content(page_title):
    #set up our request
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop":"content",
        "rvslots": "main",
        "titles": page_title
    }
    #ask the wikipedia API for what we want
    response = requests.get(url, params=params, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}) 
    #store what the API gave us in a variable
    data = response.json()
    print("STATUS CODE:", response.status_code)
    #get the page we want
    page = next(iter(data["query"]["pages"].values()))
    #get to the raw content
    content = page["revisions"][0]["slots"]["main"]["*"]

    pattern = r"\[\[(.*?)\]\]"
    #filters the content for the raw links
    matches = re.findall(pattern, content)
    links = []

    skip_namespaces = ["File", "Category", "Template", "Wikipedia", "Help", "Portal"]
    #filtering for the links aka article names
    for m in matches:
        m = m.strip() #remove whitespaces
        if any(m.startswith(ns + ":") for ns in skip_namespaces):
            continue
        if m.startswith("#"):
            continue
        if "|" in m:
            m = m.split("|")[0]
        if m:  # skip empty strings
            links.append(m.replace(" ", "_"))

    return content, links

seed = ["Nick_Jonas"]
visited = set()
to_visit = []
#opening the json file, so we can easily continue crawling even after stopping the program
with open('visit_list.json', 'r') as vl:  
    v_list = json.load(vl)
    to_visit.extend(v_list['to_visit'])
    visited.update(v_list["visited"])


while to_visit and len(visited) < 100: #setting a limit, for safety
    time.sleep(1.5) #remember to be polite!
    page = to_visit.pop(0) 
    if page in visited: 
        continue
    if isinstance(visited, set):
        visited.add(page)
    elif isinstance(visited, list):
        visited.append(page)
    
    content, links = get_links_and_content(page)
    to_visit.extend(links)
    
    with open('content.txt', 'a', encoding="utf-8") as c:
        c.write(content)
    visited = set(visited)
    visited = list(visited)
    v_list["to_visit"] = to_visit
    v_list['visited'] = visited
    with open('visit_list.json', 'w') as vl:
        json.dump(v_list, vl, indent=4)

