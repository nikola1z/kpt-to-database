import io
import arcpy
from lxml import etree
import requests
from requests.auth import HTTPBasicAuth


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [KPTfileToDatabase]


class KPTfileToDatabase(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Загрузить КПТ в базу данных"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        kpt_layer = arcpy.Parameter(
            displayName="Выберите слой ЗУ",
            name="kpt_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        items = arcpy.Parameter(
            displayName=u"ЗУ для загрузки",
            name="load_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        kpt_file = arcpy.Parameter(
            displayName="Выберите файл ЗУ",
            name="kpt_file",
            # datatype="GPString",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        items.multiValue = True
        items.filter.type = "ValueList"
        items.filter.list = []

        params = [kpt_layer, kpt_file, items]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        kpt_layer = parameters[0].valueAsText
        value_table = parameters[2]
        kpt_file_par = parameters[1].valueAsText

        kpt_in_database = []

        if kpt_layer:
            with arcpy.da.SearchCursor(kpt_layer, ['kn']) as s_cursor:
                for row in s_cursor:
                    kpt_in_database.append(row[0])

        if kpt_file_par:

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

            xml_file = open(kpt_file_par, 'r')

            xslt_doc = etree.parse(io.BytesIO(xslt))
            transform = etree.XSLT(xslt_doc)

            kpt_dom = etree.parse(xml_file)
            kpt_doc = transform(kpt_dom)

            kpt_list = []

            parcels = kpt_doc.findall('//Parcel')
            for parcel in parcels:
                cadastral_number = parcel.attrib['CadastralNumber']
                if cadastral_number in kpt_in_database:
                    condition = 'Есть в базе данных'
                else:
                    condition = 'Нет в базе данных'
                try:
                    date_created = parcel.attrib['DateCreated']
                except:
                    date_created = ''
                polygons = parcel.findall('EntitySpatial/SpatialElement')
                if len(polygons) > 0:
                    geom = 'Есть геометрия'
                else:
                    geom = 'Нет геометрии'

                output = "{:<24}{}  {}  {}".format(cadastral_number, date_created, geom, condition)
                kpt_list.append(output)


            value_table.filter.list = kpt_list


        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""  # Создаем курсор для добавления записей в рабочую схему
        arcpy.env.scratchWorkspace = "d:\\"
        arcpy.env.workspace = "d:\\"
        arcpy.env.overwriteOutput = True

        kpt_layer = parameters[0].valueAsText
        kpt_file = parameters[1].valueAsText
        kpt_names = parameters[2].valueAsText

        kpt_insert_list = []
        kpt_update_list = []
        # messages.addMessage(str(kpt_names))
        kpt_names_list = kpt_names.split(';')
        for item in kpt_names_list:
            kpt_info = item.split()
            if u'Есть в базе данных' in item:
                kpt_update_list.append(kpt_info[0][1:])
            else:
                kpt_insert_list.append(kpt_info[0][1:])

        # messages.addMessage(str(kpt_update_list))
        # messages.addMessage(str(kpt_insert_list))
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

        xml_file = open(kpt_file, 'r')

        xslt_doc = etree.parse(io.BytesIO(xslt))
        transform = etree.XSLT(xslt_doc)

        # username = "userDemo"
        # password = "demonstration"

        # response = requests.get(kpt_file, auth=HTTPBasicAuth(username, password))

        # kpt_dom = etree.parse(io.BytesIO(response.content))
        kpt_dom = etree.parse(xml_file)
        kpt_doc = transform(kpt_dom)

        kpt_dic = {}

        parcels = kpt_doc.findall('//Parcel')
        print len(parcels)
        for parcel in parcels:
            cadastral_number = parcel.attrib['CadastralNumber']
            if cadastral_number:
                kpt_dic[cadastral_number] = {}
                kpt_dic[cadastral_number]['cadastral_number'] = cadastral_number
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
                    district_type = parcel.find('Location/Address/District').attrib['Type']
                except:
                    district = ''
                    district_type = ''
                kpt_dic[cadastral_number]['district'] = district
                kpt_dic[cadastral_number]['district_type'] = district_type

                try:
                    locality = parcel.find('Location/Address/Locality').attrib['Name']
                    locality_type = parcel.find('Location/Address/Locality').attrib['Type']
                except:
                    locality = ''
                    locality_type = ''
                kpt_dic[cadastral_number]['locality'] = locality
                kpt_dic[cadastral_number]['locality_type'] = locality_type

                try:
                    street = parcel.find('Location/Address/Street').attrib['Name']
                    street_type = parcel.find('Location/Address/Street').attrib['Type']
                except:
                    street = ''
                    street_type = ''
                kpt_dic[cadastral_number]['street'] = street
                kpt_dic[cadastral_number]['street_type'] = street

                try:
                    level1_type = parcel.find('Location/Address/Level1').attrib['Type']
                except:
                    level1_type = ''
                kpt_dic[cadastral_number]['level1_type'] = level1_type

                try:
                    level1_value = parcel.find('Location/Address/Level1').attrib['Value']
                except:
                    level1_value = ''
                kpt_dic[cadastral_number]['level1_value'] = level1_value

                try:
                    address = parcel.find('Location/Address/Note').text
                except:
                    address = ''
                kpt_dic[cadastral_number]['address'] = address

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
                    value = 0

                kpt_dic[cadastral_number]['value'] = value

                # создаем список координат участка
                kpt_dic[cadastral_number]['polygon_coords'] = []
                polygons = parcel.findall('EntitySpatial/SpatialElement')
                for polygon in polygons:
                    coords_list = []
                    for item in polygon.findall('.//Ordinate'):
                        x_coord = float(item.attrib['Y'])
                        y_coord = float(item.attrib['X'])
                        # messages.addMessage(u"{0}, {1}".format(str(x_coord), str(y_coord)))
                        coords_list.append([x_coord, y_coord])
                    kpt_dic[cadastral_number]['polygon_coords'].append(coords_list)

        sr_msk_58_zone_1 = arcpy.SpatialReference("c:/workspace/arcgis projects/msk58 converter/MSK-58_Zone_1.prj")
        sr_msk_58_zone_2 = arcpy.SpatialReference("c:/workspace/arcgis projects/msk58 converter/MSK-58_Zone_2.prj")

        sr_pulkovo1942 = arcpy.SpatialReference(28408)
        sr_web_mercator_as = arcpy.SpatialReference(3857)

        insert_features = []
        update_features = []

        for feature in kpt_dic.keys():
            # Create a Polygon object based on the array of points
            # Append to the list of Polygon objects
            pol_coords = kpt_dic[feature]['polygon_coords']

            if len(pol_coords) != 0:
                # Определяем зону по первой цифре координаты Х участка
                sr = sr_msk_58_zone_1 if str(pol_coords[0][0][0])[0] == '1' else sr_msk_58_zone_2

                main_polygon = arcpy.Polygon(
                    arcpy.Array([arcpy.Point(point_coords[0], point_coords[1]) for point_coords in pol_coords[0]]), sr
                )
                if len(pol_coords) > 1:
                    for coords in pol_coords[1:]:
                        point_array = arcpy.Array([arcpy.Point(point_coords[0], point_coords[1]) for point_coords in coords])
                        new_polygon = arcpy.Polygon(point_array, sr)
                        if main_polygon.disjoint(new_polygon):
                            main_polygon = main_polygon.union(new_polygon)
                        else:
                            main_polygon = main_polygon.difference(new_polygon)


                # features.append(y)
                # messages.addMessage(str(pol_coords))
                # messages.addMessage(new_polygon.JSON)
                polygon_in_pulkovo1942 = main_polygon.projectAs(sr_pulkovo1942)
                polygon_in_web_mercator_aux_sphere = polygon_in_pulkovo1942.projectAs(sr_web_mercator_as, 'Pulkovo_1942_To_PZ_1990_1 + PZ_1990_To_WGS_1984_GOST')
                kpt_dic[feature]['geometry'] = polygon_in_web_mercator_aux_sphere
                if kpt_dic[feature]['cadastral_number'] in kpt_insert_list:
                    insert_features.append(feature)
                if kpt_dic[feature]['cadastral_number'] in kpt_update_list:
                    update_features.append(feature)
        if kpt_insert_list:
            try:
                kpt_cursor = arcpy.InsertCursor(kpt_layer)
                messages.addMessage("Начинаем добавлять записи")
                for item in insert_features:
                    row = kpt_cursor.newRow()
                    messages.addMessage(u'Добавляем {}'.format(item))
                    messages.addMessage(u"Район: {}".format(kpt_dic[item]['district']))
                    messages.addMessage(u"Категория: {}".format(kpt_dic[item]['category']))
                    messages.addMessage(u"Адрес: {}".format(kpt_dic[item]['address']))
                    messages.addMessage(u"Вид использования: {}".format(kpt_dic[item]['utilization_by_doc']))
                    messages.addMessage(u"Площадь: {}".format(kpt_dic[item]['area']))
                    messages.addMessage(u"Стоимость: {}".format(kpt_dic[item]['value']))
                    row.setValue("shape", kpt_dic[item]['geometry'])
                    row.setValue("KN", item)
                    row.setValue("Value", float(kpt_dic[item]['value']))
                    row.setValue("ray", kpt_dic[item]['district'])
                    row.setValue("category", kpt_dic[item]['category'])
                    row.setValue("adress", kpt_dic[item]['address'])
                    row.setValue("area_k", float(kpt_dic[item]['area']))
                    row.setValue("using_", kpt_dic[item]['utilization_by_doc'])
                    kpt_cursor.insertRow(row)
                    del row
                del kpt_cursor
                messages.addMessage("Все записи были успешно добавлены")
            except:
                messages.addMessage("Ошибка добавления")

        if kpt_update_list:
            try:
                kpt_update_query = '"kn" in (' + ','.join(['\'' + kpt + '\''  for kpt in kpt_update_list]) + ')'
                messages.addMessage(kpt_update_query)
                rows = arcpy.UpdateCursor(kpt_layer, kpt_update_query)
                messages.addMessage("Начинаем обновлять записи")
                for row in rows:
                    item = row.getValue('kn')
                    messages.addMessage(item)
                    row.setValue("shape", kpt_dic[item]['geometry'])
                    row.setValue("KN", item)
                    row.setValue("Value", float(kpt_dic[item]['value']))
                    row.setValue("ray", kpt_dic[item]['district'])
                    row.setValue("category", kpt_dic[item]['category'])
                    row.setValue("adress", kpt_dic[item]['address'])
                    row.setValue("area_k", float(kpt_dic[item]['area']))
                    row.setValue("using_", kpt_dic[item]['utilization_by_doc'])
                    rows.updateRow(row)
                # Delete cursor and row objects to remove locks on the data
                del row
                del rows
                messages.addMessage("Все записи были успешно обновлены")
            except:
                messages.addMessage("Ошибка обновления")

        return
