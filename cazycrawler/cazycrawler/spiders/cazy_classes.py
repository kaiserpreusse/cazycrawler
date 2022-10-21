import scrapy
import logging
import re

from cazycrawler.items import CazyClass

log = logging.getLogger(__name__)

EC_NUMBER_RE = r"[0-9]{1,2}\.(?:[0-9]{1,2}|-)\.(?:[0-9]{1,2}|-)\.(?:[0-9]{1,2}|-)"


class CazyClassSpider(scrapy.Spider):
    name = "cazy_classes"

    def start_requests(self):
        urls = [
            'http://www.cazy.org/Glycoside-Hydrolases.html',
            'http://www.cazy.org/GlycosylTransferase-family',
            'http://www.cazy.org/Polysaccharide-Lyases.html',
            'http://www.cazy.org/Carbohydrate-Esterases.html',
            'http://www.cazy.org/Auxiliary-Activities.html',
            'http://www.cazy.org/Carbohydrate-Binding-Modules.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for class_name in response.xpath("//table/tr/td/a/@href").getall():
            if class_name[0:2] in {'AA', 'CB', 'CE', 'GH', 'GT', 'PL'}:
                cazy_class = CazyClass()
                cazy_class['name'] = class_name.split('.')[0]
                cazy_class['url'] = f"http://www.cazy.org/{class_name}"
                if '_' in cazy_class['name']:
                    cazy_class['type'] = 'subfamily'
                else:
                    cazy_class['type'] = 'family'

                request = scrapy.Request(cazy_class.get('url'), callback=self.parse_detail_page)
                request.meta['item'] = cazy_class

                yield request

    def parse_detail_page(self, response):
        cazy_class = response.meta['item']

        ec_links = []

        ec_numbers_table_cell_as_string = response.xpath("//table/tr/td[@class='tdsum']").get()

        inner_string = ""
        # try selecting the inner string
        try:
            inner_string = ec_numbers_table_cell_as_string.split(">", maxsplit=1)[1].rsplit('<', maxsplit=1)[0]
        except Exception as e:
            log.error(e)
            log.info("Store EC information as string.")
            cazy_class['enzyme_classes_full_string'] = ec_numbers_table_cell_as_string
            cazy_class['enzyme_classes_parsing_error'] = str(e)
            cazy_class['enzyme_classes_parsing_error_comment'] = 'Failed on selecting the inner string.'

        # continue only if inner string exists
        # some subfamilies have no EC data, just a comment
        # that the family has data
        if inner_string and "No known activity in this subfamily" not in inner_string:
            list_of_ec = inner_string.split(';')
            for entry in list_of_ec:
                entry = entry.strip()
                # splitting can lead to empty strings
                if entry:
                    try:
                        # some entries have a link to the EC number
                        # others just have the EC number as string
                        if '<a' in entry:
                            name = entry.split(' (')[0]
                            ec_number = entry.rsplit('<', maxsplit=1)[0].rsplit('>', maxsplit=1)[1]
                            if re.match(EC_NUMBER_RE, ec_number):
                                ec_links.append((name, ec_number))
                            else:
                                # TODO this is duplicated, make function
                                cazy_class['enzyme_classes_full_string'] = ec_numbers_table_cell_as_string
                                if not cazy_class.get('enzyme_classes_sub_strings'):
                                    cazy_class['enzyme_classes_sub_strings'] = [entry]
                                else:
                                    cazy_class['enzyme_classes_sub_strings'].append(entry)
                                cazy_class[
                                    'enzyme_classes_parsing_error_comment'] = 'Failed on parsing the EC number/EC name.'
                        else:
                            name = entry.rsplit(' (')[0]
                            ec_number = entry.rsplit('(', maxsplit=1)[1].rsplit(')', maxsplit=1)[0].replace("EC", '').strip()
                            if re.match(EC_NUMBER_RE, ec_number):
                                ec_links.append((name, ec_number))
                            else:
                                # TODO this is duplicated, make function
                                cazy_class['enzyme_classes_full_string'] = ec_numbers_table_cell_as_string
                                if not cazy_class.get('enzyme_classes_sub_strings'):
                                    cazy_class['enzyme_classes_sub_strings'] = [entry]
                                else:
                                    cazy_class['enzyme_classes_sub_strings'].append(entry)
                                cazy_class[
                                    'enzyme_classes_parsing_error_comment'] = 'Failed on parsing the EC number/EC name.'

                    except Exception as e:
                        # TODO this is duplicated, make function
                        log.error(e)
                        log.info("Store EC information as string.")
                        cazy_class['enzyme_classes_full_string'] = ec_numbers_table_cell_as_string
                        if not cazy_class.get('enzyme_classes_sub_strings'):
                            cazy_class['enzyme_classes_sub_strings'] = [entry]
                        else:
                            cazy_class['enzyme_classes_sub_strings'].append(entry)
                        cazy_class['enzyme_classes_parsing_error'] = str(e)
                        cazy_class['enzyme_classes_parsing_error_comment'] = 'Failed on parsing the EC number/EC name.'

            # only add to class if data
            if ec_links:
                cazy_class['enzyme_classes'] = ec_links

        return cazy_class
