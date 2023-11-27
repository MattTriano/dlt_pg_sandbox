import json
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

import dlt
import requests


MAX_MAX_RESULTS = 2000
VALID_SORT_BY_ORDERABLES = ["submittedDate", "lastUpdatedDate", "relevance"]


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
