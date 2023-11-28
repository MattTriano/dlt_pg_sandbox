import json
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

import dlt
import requests


MAX_MAX_RESULTS = 2000
VALID_SORT_BY_ORDERABLES = ["submittedDate", "lastUpdatedDate", "relevance"]

ATOM_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def xml_to_dict(element: str) -> Dict:
    if not element:
        return element.text
    return {child.tag: xml_to_dict(child) for child in element}


def format_arxiv_API_call_params(
    search_terms: Optional[str] = None,
    id_list: Optional[List[str]] = None,
    start: int = 0,
    max_results: Optional[int] = 10,
    sort_by: Optional[str] = None,
    ascending: bool = False,
) -> Dict:
    if search_terms is None and id_list is None:
        raise Exception(
            "search_terms and id_list can't both be None or there's nothing to request!"
        )
    if search_terms:
        params = {"search_query": search_terms}
    if id_list:
        params = {"id_list": ",".join(id_list)}
    if start is not None:
        params["start"] = start
    if max_results > MAX_MAX_RESULTS:
        raise Exception(f"Invalid max_results value entered. Must be below {MAX_MAX_RESULTS}.")
    else:
        params["max_results"] = max_results

    if sort_by not in VALID_SORT_BY_ORDERABLES and sort_by is not None:
        raise Exception(
            f"Invalid sort_by value entered. Must be None or in {VALID_SORT_BY_ORDERABLE}"
        )
    if sort_by is not None:
        sort_modes = {True: "ascending", False: "descending"}
        params["sortBy"] = sort_by
        params["sortOrder"] = sort_modes[ascending]
    return params


def format_arxiv_API_call(
    search_terms: Optional[str] = None,
    id_list: Optional[List[str]] = None,
    start: int = 0,
    max_results: Optional[int] = 10,
    sort_by: Optional[str] = None,
    ascending: bool = False,
) -> requests.models.PreparedRequest:
    base_api_call = "http://export.arxiv.org/api/query"
    params = format_arxiv_API_call_params(
        search_terms=search_terms,
        id_list=id_list,
        start=start,
        max_results=max_results,
        sort_by=sort_by,
        ascending=ascending,
    )
    req = requests.Request("GET", base_api_call, params=params).prepare()
    return req


def unpack_entry_authors(entry: ET.Element) -> Dict:
    authors = entry.findall("atom:author", ATOM_NAMESPACES)
    all_author_details = []
    for author in authors:
        author_details = {}
        author_details["name"] = author.find("atom:name", ATOM_NAMESPACES).text
        affiliations = [af.text for af in author.findall("arxiv:affiliation")]
        if len(affiliations) > 0:
            author_details["affiliation"] = affiliations
        else:
            author_details["affiliation"] = None
        all_author_details.append(author_details)
    return all_author_details


def unpack_entry_links(entry: ET.Element) -> Dict:
    links = entry.findall("atom:link", ATOM_NAMESPACES)
    article_links = {}
    for link in links:
        if link.attrib["rel"] == "alternate":
            link_type = "abstract"
        else:
            link_type = link.attrib["title"]
        article_links[link_type] = link.attrib
    return article_links


def unpack_entry_categories(entry: ET.Element) -> List[Dict]:
    """ Unpacks the primary and other categories for an arXiv article. The first in the list
          is the primary category. """
    categories = [entry.find("arxiv:primary_category", ATOM_NAMESPACES).attrib]
    other_categories = entry.findall("atom:category", ATOM_NAMESPACES)
    if len(other_categories) > 0:
        categories.extend([el.attrib for el in other_categories])
    distinct_categories = [dict(t) for t in {tuple(d.items()) for d in categories}]
    return distinct_categories
