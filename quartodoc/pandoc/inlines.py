"""
Specifition is at https://pandoc.org/lua-filters.html#inline
"""
from __future__ import annotations

import collections.abc as abc
from dataclasses import dataclass
from typing import TypeAlias, Optional, Sequence

from quartodoc.pandoc.components import Attr

__all__ = (
    "Code",
    "CodeTag",
    "Emph",
    "Inline",
    "Inlines",
    "Link",
    "Span",
    "Str",
    "Strong"
)

SEP = " "


class Inline:
    """
    Base class for inline elements
    """

    def __str__(self):
        return ""

# TypeAlias declared here to avoid forward-references which
# break beartype
InlineContent: TypeAlias = str | Inline | Sequence[Inline]


@dataclass
class Inlines(Inline):
    """
    Sequence of inline elements
    """
    elements: Optional[Sequence[InlineContent]] = None

    def __str__(self):
        if not self.elements:
            return ""
        return join_inline_content(self.elements)


@dataclass
class Str(Inline):
    """
    A String
    """
    content: Optional[str] = None

    def __str__(self):
        return self.content or ""


@dataclass
class Span(Inline):
    """
    A Span
    """
    content: Optional[InlineContent] = None
    attr: Optional[Attr] = None

    def __str__(self):
        """
        Return span content as markdown
        """
        content = inlinecontent_to_str(self.content)
        attr = self.attr or ""
        return f"[{content}]{{{attr}}}"


@dataclass
class Link(Inline):
    """
    A Link
    """
    content: Optional[InlineContent] = None
    target: Optional[str] = None
    title: Optional[str] = None
    attr: Optional[Attr] = None

    def __str__(self):
        """
        Return link as markdown
        """
        title = f' "{self.title}"' if self.title else ""
        content = inlinecontent_to_str(self.content)
        attr =  f"{{{self.attr}}}" if self.attr else ""
        return f"[{content}]({self.target}{title}){attr}"


@dataclass
class Code(Inline):
    """
    Code (inline)
    """
    text: Optional[str] = None
    attr: Optional[Attr] = None

    def __str__(self):
        """
        Return link as markdown
        """
        content = self.text or ""
        attr =  f"{{{self.attr}}}" if self.attr else ""
        return f"`{content}`{attr}"


@dataclass
class CodeTag(Inline):
    """
    Code (inline) rendered as html
    """
    text: Optional[str] = None
    attr: Optional[Attr] = None

    def __str__(self):
        """
        Return link as markdown
        """
        content = self.text or ""
        attr = f" {self.attr.as_html()}" if self.attr else ""
        return f"<code{attr}>{content}</code>"


@dataclass
class Strong(Inline):
    """
    Strongly emphasized text
    """
    content: Optional[InlineContent] = None

    def __str__(self):
        """
        Return link as markdown
        """
        content = inlinecontent_to_str(self.content)
        return f"**{content}**"


@dataclass
class Emph(Inline):
    """
    Emphasized text
    """
    content: Optional[InlineContent] = None

    def __str__(self):
        """
        Return link as markdown
        """
        content = inlinecontent_to_str(self.content)
        return f"*{content}*"


# Helper functions

def join_inline_content(content: Sequence[InlineContent]) -> str:
    """
    Join a sequence of inlines into one string
    """
    return SEP.join(str(c) for c in content if c)


def inlinecontent_to_str(content: Optional[InlineContent]):
    """
    Covert inline content to a string

    A single item block is converted to a string.
    A block sequence is coverted to a string of strings with a
    space separating the string for each item in the sequence.
    """
    if not content:
        return ""
    elif isinstance(content, (str, Inline)):
        return str(content)
    elif isinstance(content, abc.Sequence):
        return join_inline_content(content)
    else:
        raise TypeError(f"Could not process type: {type(content)}")
