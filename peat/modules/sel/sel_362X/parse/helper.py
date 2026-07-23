"""
Helper functions for parsing page content

Author: Francisco Santana <fsantan@sandia.gov>
"""

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet


def ptagattr(attr: dict[str, str | list[str]]) -> str:
    """
    Pretty-print the list of tag attributes
    """
    result = ""

    for a in attr:
        if isinstance(attr[a], str):
            result += f"\n- {a}: {attr[a]}"
        else:
            possible_values = attr[a]
            out = f"{possible_values[0]}"

            if len(possible_values) > 1:
                for v in possible_values[1:]:
                    out += f" | {v}"

            result += f"\n- {a}: {out}"
    return result


def find_tag(
    source: BeautifulSoup | Tag,
    tagty: str,
    attrib: dict[str, str | list[str]] = {},
    recursive: bool = True,
) -> Tag | None:
    """
    Get a tag from a page or a group
    """

    tag = source.find(tagty, attrib, recursive)

    if not isinstance(tag, Tag):
        return None
    else:
        return tag


def find_tag_f(
    source: BeautifulSoup | Tag,
    tagty: str,
    attrib: dict[str, str | list[str]] = {},
    recursive: bool = True,
) -> Tag:
    """
    Find a tag from a page or group, or raise an exception
    """

    tag = find_tag(source, tagty, attrib, recursive)

    if not tag:
        raise Exception(f"Failed to find {tagty} with attributes {ptagattr(attrib)}")

    return tag


def find_tags(
    source: BeautifulSoup | Tag,
    tagty: str,
    attrib: dict[str, str | list[str]] = {},
    recursive: bool = True,
) -> list[Tag]:
    """
    Get every tag from a page or a group
    """

    tag = source.find_all(tagty, attrib, recursive)

    if not isinstance(tag, ResultSet):
        return []
    else:
        return [t for t in tag]


def find_table(
    source: BeautifulSoup | Tag,
    attrib: dict[str, str | list[str]] = {},
) -> Tag:
    """
    Specialization of find_tag for tables
    """
    t = find_tag(source, "table", attrib)

    if not isinstance(t, Tag):
        raise Exception(f"Failed to find table with attributes {ptagattr(attrib)}")
    else:
        return t


def get_table_rows(table: Tag, recurse: bool = False) -> list[Tag]:
    """
    Specialization of find_tags for table rows
    """
    t = find_tags(table, "tr", attrib={"class": ["odd", "even"]}, recursive=recurse)

    if not t:
        return []
    else:
        return t


def get_text_of(
    source: Tag,
    tag: str,
    attrib: dict[str, str | list[str]] = {},
    sep: str = "\n",
    strip: bool = True,
) -> str:
    """
    Specialization of find_tag which gets the text of the result

    If there is no result, it returns an empty string
    """

    t = find_tag(source, tag, attrib)

    if not t:
        return ""

    return t.get_text(sep, strip)


def get_text_of_f(
    source: Tag,
    tag: str,
    attrib: dict[str, str | list[str]] = {},
    sep: str = "\n",
    strip: bool = True,
) -> str:
    """
    Get the text of a tag or raise an exception if absent
    """

    t = find_tag(source, tag, attrib)

    if not t:
        raise Exception(f"Could not find tag {tag}")

    return t.get_text(sep, strip)


def get_attrib(tag: Tag, attr: str) -> str | None:
    """
    Get an attribute, or None if absent
    """

    v = tag.get(attr)

    return v if isinstance(v, str) else None


def get_attrib_f(tag: Tag, attr: str) -> str:
    """
    Get an attribute or raise an exception if absent
    """

    v = get_attrib(tag, attr)

    if not v:
        raise Exception(f"Attribute {attr} is not present in tag {tag.name}")
    else:
        return v


def get_value(tag: Tag) -> str:
    """
    Get the string value of a tag, else return an empty string
    """

    v = get_attrib(tag, "value")

    return v or ""
