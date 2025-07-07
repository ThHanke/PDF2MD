import requests
import time
from fake_useragent import UserAgent
from typing import List

def fetch_crossref_record(doi=None, query=None):
    """
    Fetches *one* record from Crossref using EITHER:
      1) a specific 'doi' (preferred if available),
      2) or a 'query' string (search by title, etc.) if no DOI is provided.

    Returns the raw JSON record (the 'message' object), or None if not found.
    """
    base_url = "https://api.crossref.org/works"
    ua = UserAgent()
    user_agent = ua.getRandom
    user_agent_header = {"User-Agent": user_agent['useragent']}
    print(user_agent_header)
    print(type(user_agent_header))
    # If we have a specific DOI, try that first
    if doi:
        #url = f"{base_url}/{doi}"
        params = {"doi": doi}
        headers = user_agent_header
        resp = requests.get(base_url, params=params, headers=headers, verify=False)
        time.sleep(0.1)  # Avoid hitting the API too hard

        if resp.status_code == 200:
            data = resp.json()
            return data.get("message")
        # If that fails, we fall back to the query approach

    # If no valid data from the DOI or no DOI given, then search by query
    if query:
        params = {"query.title": query, "rows": 1}
        resp = requests.get(base_url, params=params, headers=user_agent_header, verify=False)
        time.sleep(0.1)  # Avoid hitting the API too hard
        # Check if the response is valid
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("message", {}).get("items", [])
            for hit in items:
                print(f"hit title: {hit['title']}, query: {query}")
                if has_similar_string(query,hit['title'],threshold=0.5):
                    return hit
    return None


def build_full_record(
    doi=None,
    query=None,
    current_depth=0,
    max_depth=2
):
    """
    Recursively fetches a Crossref record and its references up to 'max_depth'.

    Returns a dictionary with:
      - 'raw_crossref_data': the *entire* record from Crossref as is.
      - 'reference_count': how many references the record claims to have (if present).
      - 'references': a list of references, each containing:
          {
            'raw_reference_entry': the original crossref reference dict from the parent,
            'fetched_data': the entire fetched record from Crossref for that reference,
            'reference_count': number of references that sub-record has,
            'reference_titles': (list of sub-reference titles, if found),
            'references': (recursive list of sub-sub references if current_depth < max_depth),
            ...
          }
    """

    # 1) Fetch the record from Crossref
    main_record = fetch_crossref_record(doi=doi, query=query)
    if not main_record:
        return None  # Or return an empty dict, e.g. {}

    # 2) Prepare the top-level dictionary
    final_dict = {}
    final_dict["raw_crossref_data"] = main_record

    # 3) The Crossref "references-count" is sometimes stored as "reference-count" or "references-count".
    #    We check both just in case:
    ref_count = main_record.get("references-count")  # common in Crossref
    if ref_count is None:
        ref_count = main_record.get("reference-count")
    final_dict["reference_count"] = ref_count

    # 4) If the item includes references themselves, process them
    ref_list = main_record.get("reference", [])
    references_output = []

    # Only proceed if we are within recursion limit
    if current_depth < max_depth:
        for ref_entry in ref_list:
            # 'ref_entry' is a dictionary describing the parent's reference entry
            # Example fields: "DOI", "key", "author", "year", "volume", "article-title", "title"...
            # We'll search by its "DOI" or "title".
            ref_doi = ref_entry.get("DOI", "")
            # If 'title' is present, it is typically a list
            ref_title_list = ref_entry.get("title", [])
            if not ref_title_list:  # Sometimes "article-title" instead
                # For older references, Crossref might use 'article-title'
                article_title = ref_entry.get("article-title", "")
                if article_title:
                    ref_title_list = [article_title]
            ref_title = ref_title_list[0] if ref_title_list else ""

            # Attempt to fetch the sub-record
            ref_sub_record = fetch_and_build_reference(
                doi=ref_doi,
                title=ref_title,
                current_depth=current_depth+1,
                max_depth=max_depth
            )

            # Add the data to references_output
            references_output.append({
                "raw_reference_entry": ref_entry,      # Exactly as it appears in the parent's record
                "fetched_data": ref_sub_record,       # Full recursion data from the reference
            })

    # Add references_output to final_dict
    final_dict["references"] = references_output

    return final_dict


def fetch_and_build_reference(doi, title, current_depth, max_depth):
    """
    Helper for a single reference re-search, returning the entire sub-record structure
    if found, or None if not found. 
    """
    # If there's no DOI or it's obviously incomplete, try the title
    if doi:
        # Attempt fetch by DOI first
        sub_record = build_full_record(doi=doi, current_depth=current_depth, max_depth=max_depth)
        if sub_record:
            return sub_record
    # If that didn't work or there's no valid DOI, try the title
    if title:
        sub_record = build_full_record(query=title, current_depth=current_depth, max_depth=max_depth)
        if sub_record:
            return sub_record

    # If neither approach found a record, return None
    return None

def jaccard_similarity(query: str, title: str) -> float:
    """
    Berechnet die Jaccard-Ähnlichkeit zwischen zwei Strings.

    :param query: Der Suchbegriff.
    :param title: Der Titel, mit dem verglichen wird.
    :return: Jaccard-Ähnlichkeit zwischen 0 und 1.
    """
    set_query = set(query.lower().split())
    set_title = set(title.lower().split())
    
    intersection = set_query.intersection(set_title)
    union = set_query.union(set_title)
    
    if not union:
        return 0.0  # Vermeide Division durch Null

    return len(intersection) / len(union)

def has_similar_string(string: str, string_list: List[str], threshold: float = 0.5) -> bool:
    """
    Überprüft, ob ein ähnlicher Titel in der Liste von Titeln gefunden wird.

    :param query: Der Suchbegriff, der mit den Titeln verglichen wird.
    :param titles: Eine Liste von Titeln, die überprüft werden.
    :param threshold: Der Schwellenwert für die Ähnlichkeit (0-1).
    :return: True, wenn ein ähnlicher Titel gefunden wird, sonst False.
    """
    for to_test in string_list:
        similarity = jaccard_similarity(string, to_test)  # Berechne die Ähnlichkeit
        print(f"Jaccard similarity between {string} and {to_test}: {similarity:.2f}")
        if similarity >= threshold:
            return True  # Finde eine Übereinstimmung
    return False  # Keine Übereinstimmung gefunden
