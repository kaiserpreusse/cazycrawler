# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CazyClass(Item):
    name = Field()
    url = Field()
    type = Field()
    enzyme_classes = Field()

    # enzyme classes error handling
    enzyme_classes_full_string = Field()
    enzyme_classes_sub_strings = Field()
    enzyme_classes_parsing_error = Field()
    enzyme_classes_parsing_error_comment = Field()
