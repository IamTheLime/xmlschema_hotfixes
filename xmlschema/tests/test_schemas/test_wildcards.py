#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c), 2016-2019, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
from __future__ import print_function, unicode_literals
from xmlschema import XMLSchemaParseError
from xmlschema.tests import XsdValidatorTestCase
from xmlschema.validators import XMLSchema11, XsdDefaultOpenContent


class TestXsdWildcards(XsdValidatorTestCase):

    def test_any_wildcard(self):
        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].namespace, '##other')

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##targetNamespace" processContents="skip"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].namespace, '##targetNamespace')

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="ns ##targetNamespace" processContents="skip"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].namespace, 'ns ##targetNamespace')

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="tns2 tns1 tns3" processContents="skip"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].namespace, 'tns2 tns1 tns3')
        self.assertEqual(schema.types['taggedType'].content_type[-1].min_occurs, 1)
        self.assertEqual(schema.types['taggedType'].content_type[-1].max_occurs, 1)

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any minOccurs="10" maxOccurs="unbounded"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].namespace, '##any')
        self.assertEqual(schema.types['taggedType'].content_type[-1].min_occurs, 10)
        self.assertIsNone(schema.types['taggedType'].content_type[-1].max_occurs)

    def test_any_attribute_wildcard(self):
        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:sequence>
          <xs:anyAttribute namespace="tns1:foo"/>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].attributes[None].namespace, 'tns1:foo')

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:sequence>
          <xs:anyAttribute namespace="##targetNamespace"/>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].attributes[None].namespace, '##targetNamespace')


class TestXsd11Wildcards(TestXsdWildcards):

    schema_class = XMLSchema11

    def test_open_content_mode_interleave(self):
        schema = self.check_schema("""
        <xs:element name="Book">
          <xs:complexType>
            <xs:openContent mode="interleave">
                <xs:any />
            </xs:openContent>
            <xs:sequence>
              <xs:element name="Title" type="xs:string"/>
              <xs:element name="Author" type="xs:string" />
              <xs:element name="Date" type="xs:gYear"/>
              <xs:element name="ISBN" type="xs:string"/>
              <xs:element name="Publisher" type="xs:string"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>""")
        self.assertEqual(schema.elements['Book'].type.open_content.mode, 'interleave')
        self.assertEqual(schema.elements['Book'].type.open_content.any_element.min_occurs, 0)
        self.assertIsNone(schema.elements['Book'].type.open_content.any_element.max_occurs)

        schema = self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['name'].open_content.mode, 'interleave')

        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent />
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

    def test_open_content_mode_suffix(self):
        schema = self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="suffix">
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['name'].open_content.mode, 'suffix')
        self.assertEqual(schema.types['name'].open_content.any_element.min_occurs, 0)
        self.assertIsNone(schema.types['name'].open_content.any_element.max_occurs)

        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="suffix"/>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

    def test_open_content_mode_none(self):
        schema = self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="none"/>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['name'].open_content.mode, 'none')

        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="none">
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

    def test_open_content_allowed(self):
        self.check_schema("""
        <xs:complexType name="choiceType">
          <xs:openContent>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:choice>
            <xs:element name="a" type="xs:float"/>
            <xs:element name="b" type="xs:string"/>
            <xs:element name="c" type="xs:int"/>
          </xs:choice>
        </xs:complexType>""")

    def test_open_content_not_allowed(self):
        self.check_schema("""
        <xs:complexType name="wrongType">
          <xs:openContent>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:simpleContent>
                <xs:restriction base="xs:string" />
          </xs:simpleContent>
        </xs:complexType>""", XMLSchemaParseError)

        self.check_schema("""
        <xs:complexType name="wrongType">
          <xs:openContent>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:complexContent>
                <xs:restriction base="xs:anyType" />
          </xs:complexContent>
        </xs:complexType>""", XMLSchemaParseError)

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:openContent>
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:openContent>
                <xs:element name="root" />
            </xs:schema>""")

    def test_open_content_wrong_attributes(self):
        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="wrong"/>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="suffix">
            <xs:any minOccurs="1" namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

        self.check_schema("""
        <xs:complexType name="name">
          <xs:openContent mode="suffix">
            <xs:any maxOccurs="1000" namespace="##other" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="given" type="xs:string"/>
            <xs:element name="middle" type="xs:string" minOccurs="0"/>
            <xs:element name="family" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

    def test_default_open_content(self):
        schema = self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:defaultOpenContent>
                <xs:any namespace="##other" processContents="skip"/>
            </xs:defaultOpenContent>
            <xs:element name="root" />
        </xs:schema>""")
        self.assertIsInstance(schema.default_open_content, XsdDefaultOpenContent)
        self.assertFalse(schema.default_open_content.applies_to_empty)

        schema = self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:defaultOpenContent appliesToEmpty="true">
                <xs:any namespace="##other" processContents="skip"/>
            </xs:defaultOpenContent>
            <xs:element name="root" />
        </xs:schema>""")
        self.assertTrue(schema.default_open_content.applies_to_empty)

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:defaultOpenContent appliesToEmpty="wrong">
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:defaultOpenContent>
                <xs:element name="root" />
            </xs:schema>""")

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root" />
                <xs:defaultOpenContent>
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:defaultOpenContent>
            </xs:schema>""")

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:defaultOpenContent>
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:defaultOpenContent>
                <xs:defaultOpenContent>
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:defaultOpenContent>
                <xs:element name="root" />
            </xs:schema>""")

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root" />
                <xs:defaultOpenContent mode="wrong">
                    <xs:any namespace="##other" processContents="skip"/>
                </xs:defaultOpenContent>
            </xs:schema>""")

        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
                <xs:element name="root" />
                <xs:defaultOpenContent mode="none" />
            </xs:schema>""")

    def test_open_content_restriction(self):
        schema = self.check_schema("""
        <xs:complexType name="baseType">
          <xs:openContent>
            <xs:any namespace="tns1 tns2" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="foo" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>
        
        <xs:complexType name="derivedType">
          <xs:complexContent>
            <xs:restriction base="baseType">
              <xs:openContent>
                <xs:any namespace="tns1" processContents="skip"/>
              </xs:openContent>
              <xs:sequence>
                <xs:element name="foo" type="xs:string"/>
              </xs:sequence>
            </xs:restriction>
          </xs:complexContent>
        </xs:complexType>""")
        self.assertEqual(schema.types['derivedType'].content_type[0].name, 'foo')

        self.check_schema("""
        <xs:complexType name="baseType">
          <xs:openContent>
            <xs:any namespace="tns1 tns2" processContents="skip"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="foo" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>

        <xs:complexType name="derivedType">
          <xs:complexContent>
            <xs:restriction base="baseType">
              <xs:openContent>
                <xs:any namespace="##any" processContents="skip"/>
              </xs:openContent>
              <xs:sequence>
                <xs:element name="foo" type="xs:string"/>
              </xs:sequence>
            </xs:restriction>
          </xs:complexContent>
        </xs:complexType>""", XMLSchemaParseError)

    def test_open_content_extension(self):
        schema = self.check_schema("""
        <xs:complexType name="baseType">
          <xs:openContent mode="suffix">
            <xs:any namespace="tns1" processContents="lax"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="foo" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>

        <xs:complexType name="derivedType">
          <xs:complexContent>
            <xs:extension base="baseType">
              <xs:openContent>
                <xs:any namespace="tns1 tns2" processContents="lax"/>
              </xs:openContent>
              <xs:sequence>
                <xs:element name="bar" type="xs:string"/>
              </xs:sequence>
            </xs:extension>
          </xs:complexContent>
        </xs:complexType>""")
        self.assertEqual(schema.types['derivedType'].content_type[0][0].name, 'foo')
        self.assertEqual(schema.types['derivedType'].content_type[1][0].name, 'bar')

        self.check_schema("""
        <xs:complexType name="baseType">
          <xs:openContent mode="suffix">
            <xs:any namespace="tns1" processContents="lax"/>
          </xs:openContent>
          <xs:sequence>
            <xs:element name="foo" type="xs:string"/>
          </xs:sequence>
        </xs:complexType>

        <xs:complexType name="derivedType">
          <xs:complexContent>
            <xs:extension base="baseType">
              <xs:openContent>
                <xs:any namespace="tns1 tns2" processContents="strict"/>
              </xs:openContent>
              <xs:sequence>
                <xs:element name="bar" type="xs:string"/>
              </xs:sequence>
            </xs:extension>
          </xs:complexContent>
        </xs:complexType>""", XMLSchemaParseError)

    def test_not_qname_attribute(self):
        with self.assertRaises(XMLSchemaParseError):
            self.schema_class("""
            <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" 
                    xmlns:ns="tns1" targetNamespace="tns1">
                <xs:complexType name="type1">
                  <xs:openContent>
                   <xs:any notQName="ns:a" processContents="lax" />
                  </xs:openContent>
                </xs:complexType>            
            </xs:schema>""")

        self.assertIsInstance(self.schema_class("""
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" 
                xmlns:ns="tns1" targetNamespace="tns1">
            <xs:complexType name="type1">
              <xs:sequence>
               <xs:any notQName="ns:a" processContents="lax" />
              </xs:sequence>
            </xs:complexType>            
        </xs:schema>"""), XMLSchema11)

    def test_any_wildcard(self):
        super(TestXsd11Wildcards, self).test_any_wildcard()
        self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##other" notNamespace="##targetNamespace" />
          </xs:sequence>
        </xs:complexType>""", XMLSchemaParseError)

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any notNamespace="##targetNamespace" />
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].not_namespace, ['##targetNamespace'])

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##targetNamespace" notQName="tns1:foo tns1:bar"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].not_qname, ['tns1:foo', 'tns1:bar'])

        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##targetNamespace" notQName="##defined tns1:foo ##definedSibling"/>
          </xs:sequence>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].content_type[-1].not_qname,
                         ['##defined', 'tns1:foo', '##definedSibling'])

    def test_any_attribute_wildcard(self):
        super(TestXsd11Wildcards, self).test_any_attribute_wildcard()
        schema = self.check_schema("""
        <xs:complexType name="taggedType">
          <xs:sequence>
            <xs:element name="tag" type="xs:string"/>
            <xs:any namespace="##other" processContents="skip"/>
          </xs:sequence>
          <xs:anyAttribute notQName="tns1:foo"/>
        </xs:complexType>""")
        self.assertEqual(schema.types['taggedType'].attributes[None].namespace, '##any')
        self.assertEqual(schema.types['taggedType'].attributes[None].not_qname, ['tns1:foo'])
