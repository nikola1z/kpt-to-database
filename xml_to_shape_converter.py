# coding: utf8
__author__ = 'nikola1z'
import io
from lxml import etree

xslt = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
'''

xml_file = open('wrong_kpt.xml', 'r')

xslt_doc = etree.parse(io.BytesIO(xslt))
transform = etree.XSLT(xslt_doc)
kpt_dom = etree.parse(xml_file)
kpt_doc = transform(kpt_dom)

kpt_dic = {}

parcels = kpt_doc.findall('//Parcel')
print len(parcels)
for parcel in parcels:
    cadastral_number = parcel.attrib['CadastralNumber']
    kpt_dic[cadastral_number] = {}

    try:
        date_created = parcel.attrib['DateCreated']
    except:
        date_created = ''
    kpt_dic[cadastral_number]['date_created'] = date_created

    try:
        area = parcel.find('Area/Area').text
    except:
        area = ''
    kpt_dic[cadastral_number]['area'] = area

    try:
        name = parcel.find('Name').text
    except:
        name = ''
    kpt_dic[cadastral_number]['name'] = name

    # адрес участка
    try:
        okato = parcel.find('Location/Address/OKATO').text
    except:
        okato = ''
    kpt_dic[cadastral_number]['okato'] = okato

    try:
        kladr = parcel.find('Location/Address/KLADR').text
    except:
        kladr = ''
    kpt_dic[cadastral_number]['kladr'] = kladr

    try:
        region = parcel.find('Location/Address/Region').text
    except:
        region = ''
    kpt_dic[cadastral_number]['region'] = region

    try:
        district = parcel.find('Location/Address/District').attrib['Name']
    except:
        district = ''
    kpt_dic[cadastral_number]['district'] = district

    try:
        locality = parcel.find('Location/Address/Locality').attrib['Name']
    except:
        locality = ''
    kpt_dic[cadastral_number]['locality'] = locality

    try:
        street = parcel.find('Location/Address/Street').attrib['Name']
    except:
        street = ''
    kpt_dic[cadastral_number]['street'] = street

    try:
        level1_type = parcel.find('Location/Address/Level1').attrib['Type']
    except:
        level1_type = ''

    try:
        level1_value = parcel.find('Location/Address/Level1').attrib['Value']
    except:
        level1_value = ''

    try:
        note = parcel.find('Location/Address/Note').text
    except:
        note = ''
    kpt_dic[cadastral_number]['note'] = note

    try:
        category = parcel.find('Category').text
    except:
        category = ''
    kpt_dic[cadastral_number]['category'] = category

    try:
        utilization = parcel.find('Utilization').attrib['Utilization']
    except:
        utilization = ''
    kpt_dic[cadastral_number]['utilization'] = utilization

    try:
        utilization_by_doc = parcel.find('Utilization').attrib['ByDoc']
    except:
        utilization_by_doc = ''
    kpt_dic[cadastral_number]['utilization_by_doc'] = utilization_by_doc

    try:
        value = parcel.find('CadastralCost').attrib['Value']
    except:
        value = ''

    kpt_dic[cadastral_number]['value'] = value

    # создаем список координат участка
    coords_list = []
    coords = parcel.findall('EntitySpatial//Ordinate')
    for item in coords:
        x_coord = item.attrib['X']
        y_coord = item.attrib['Y']
        print x_coord, y_coord
        coords_list.append([x_coord, y_coord])
    kpt_dic[cadastral_number]['coords'] = coords_list




# tree = etree.parse(xml_file)
#
# xslt_doc=etree.parse(io.BytesIO(xslt))
# transform=etree.XSLT(xslt_doc)
# dom=transform(tree)
# print etree.tostring(dom)
# f = open('new_kpt.xml', 'w')
# f.write(etree.tostring(dom))
# f.close()
# Required mapping

# xml_file = open('kpt.xml', 'r')
# root = etree.parse(xml_file)
# root = etree.fromstring(xml)

# parser = etree.XMLParser(ns_clean=True)
# print x.findall('EntitySpatial/SpatialElement/SpelementUnit')[0].attrib['TypeUnit']

# tree = etree.parse(xml_file)
# for node in tree.xpath('//xmlns:CadastralBlocks/xmlns:CadastralBlock/xmlns:SpatialData/xmlns:EntitySpatial/ns3:SpatialElement/ns3:SpelementUnit/ns3:Ordinate', namespaces=nsmap):
# for node in tree.xpath('//xmlns:CadastralBlocks/xmlns:CadastralBlock/xmlns:SpatialData/xmlns:EntitySpatial/ns3:SpatialElement', namespaces=nsmap):
#     print node
#     xynode = node.getchildren()
#
# for node in tree.xpath("//*[local-name() = 'CadastralBlock']"):
#     print node
# root  = tree.getroot()
# nodes = tree.xpath('/CadastralBlocks')

# cadastralBlockroot= root.getchildren()[0].getchildren()[0]
# for node in tree.iterfind('.//CadastralBlock'): # поиск элементов
#     print node.get('CadastralNumber')
pass
