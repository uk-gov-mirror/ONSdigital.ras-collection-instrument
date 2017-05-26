# coding: utf-8

from __future__ import absolute_import
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class VndCollectionjsonLinks(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, href: str=None, type: str=None, rel: str=None):
        """
        VndCollectionjsonLinks - a model defined in Swagger

        :param href: The href of this VndCollectionjsonLinks.
        :type href: str
        :param type: The type of this VndCollectionjsonLinks.
        :type type: str
        :param rel: The rel of this VndCollectionjsonLinks.
        :type rel: str
        """
        self.swagger_types = {
            'href': str,
            'type': str,
            'rel': str
        }

        self.attribute_map = {
            'href': 'href',
            'type': 'type',
            'rel': 'rel'
        }

        self._href = href
        self._type = type
        self._rel = rel

    @classmethod
    def from_dict(cls, dikt) -> 'VndCollectionjsonLinks':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The vnd.collectionjson_links of this VndCollectionjsonLinks.
        :rtype: VndCollectionjsonLinks
        """
        return deserialize_model(dikt, cls)

    @property
    def href(self) -> str:
        """
        Gets the href of this VndCollectionjsonLinks.

        :return: The href of this VndCollectionjsonLinks.
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href: str):
        """
        Sets the href of this VndCollectionjsonLinks.

        :param href: The href of this VndCollectionjsonLinks.
        :type href: str
        """

        self._href = href

    @property
    def type(self) -> str:
        """
        Gets the type of this VndCollectionjsonLinks.

        :return: The type of this VndCollectionjsonLinks.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """
        Sets the type of this VndCollectionjsonLinks.

        :param type: The type of this VndCollectionjsonLinks.
        :type type: str
        """

        self._type = type

    @property
    def rel(self) -> str:
        """
        Gets the rel of this VndCollectionjsonLinks.

        :return: The rel of this VndCollectionjsonLinks.
        :rtype: str
        """
        return self._rel

    @rel.setter
    def rel(self, rel: str):
        """
        Sets the rel of this VndCollectionjsonLinks.

        :param rel: The rel of this VndCollectionjsonLinks.
        :type rel: str
        """

        self._rel = rel

