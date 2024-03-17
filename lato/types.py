from typing import Union

from lato.message import Message

HandlerAlias = Union[type[Message], str]
DependencyIdentifier = Union[type, str]
